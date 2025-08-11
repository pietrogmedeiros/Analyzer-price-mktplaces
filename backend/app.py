import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np
import io

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def analyze_webprice_data_internal(csv_content_stream):
    """Lógica de otimização de preços baseada em análise competitiva:
    1) Filtra produtos com status "GANHANDO" (onde já somos líderes)
    2) Identifica o concorrente imediatamente abaixo no ranking
    3) Sugere preço otimizado para proteger margem mantendo competitividade
    4) Calcula ganho potencial de margem
    """
    try:
        df = pd.read_csv(csv_content_stream, sep=';', skiprows=[0], decimal=',')
        df.columns = [c.replace('\ufeff','').strip().upper() for c in df.columns]

        # Mapeamentos básicos
        mapping_basic = {'PRODUTO':'Produto','STATUS':'Status','LOJISTA':'Lojista','PRECO':'Preço','MAIS BARATO':'Preço_Concorrente'}
        df.rename(columns={c: mapping_basic[c] for c in mapping_basic if c in df.columns}, inplace=True)

        # Detecta diferença / percentual se existir
        for c in list(df.columns):
            uc = c.upper()
            if 'DIFEREN' in uc and 'DIFERENÇA_RAW_CSV' not in uc:
                df.rename(columns={c:'Diferença_Raw_CSV'}, inplace=True)
            if 'PERCENT' in uc and 'PERCENTUAL_RAW_CSV' not in uc:
                df.rename(columns={c:'Percentual_Raw_CSV'}, inplace=True)

        essential = ['Produto','Lojista','Preço']
        miss = [c for c in essential if c not in df.columns]
        if miss:
            return {"error": f"Colunas essenciais ausentes: {miss}. Colunas disponíveis: {df.columns.tolist()}"}

        # Conversões numéricas
        num_cols = ['Preço','Preço_Concorrente','Diferença_Raw_CSV','Percentual_Raw_CSV']
        for c in num_cols:
            if c in df.columns:
                if c == 'Percentual_Raw_CSV':
                    df[c] = df[c].astype(str).str.replace('%','', regex=False)
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        if 'Status' in df.columns:
            df['Status'] = df['Status'].astype(str).str.strip().str.upper()
        else:
            df['Status'] = ''

        suggestions = []
        status_counts = df['Status'].value_counts().to_dict() if 'Status' in df.columns else {}

        # **NOVA LÓGICA BASEADA NAS SUAS REGRAS DE NEGÓCIO**
        if 'RANKING' in df.columns:
            # Lógica principal: análise por ranking
            df['RANKING'] = pd.to_numeric(df['RANKING'], errors='coerce')
            
            # Filtra apenas produtos onde estamos GANHANDO (ranking = 1)
            ganhando_df = df[df['RANKING'] == 1].copy()
            
            if not ganhando_df.empty:
                # Para cada produto ganhando, encontra o concorrente logo abaixo (ranking = 2)
                for _, produto_ganhando in ganhando_df.iterrows():
                    produto_nome = produto_ganhando['Produto']
                    nosso_preco = produto_ganhando['Preço']
                    
                    # Busca o concorrente de ranking 2 para o mesmo produto
                    concorrente_abaixo = df[
                        (df['Produto'] == produto_nome) & 
                        (df['RANKING'] == 2)
                    ]
                    
                    if not concorrente_abaixo.empty:
                        preco_concorrente = concorrente_abaixo.iloc[0]['Preço']
                        
                        # Calcula preço otimizado (entre nosso preço e o do concorrente)
                        # Sugestão: ajustar para 90% do preço do concorrente
                        preco_otimo = round(preco_concorrente * 0.90, 2)
                        
                        # Só sugere se pudermos aumentar o preço (proteger margem)
                        if preco_otimo > nosso_preco:
                            valor_ajuste = preco_otimo - nosso_preco
                            percentual_ajuste = (valor_ajuste / nosso_preco) * 100
                            margem_extra = valor_ajuste  # Ganho direto de margem
                            
                            suggestions.append({
                                'Produto': produto_nome,
                                'Lojista': produto_ganhando['Lojista'],
                                'Ranking_Atual': 1,
                                'Preço_Atual': nosso_preco,
                                'Preço_Concorrente_Abaixo': preco_concorrente,
                                'Preço_Sugerido': preco_otimo,
                                'Valor_Ajuste': round(valor_ajuste, 2),
                                'Percentual_Ajuste': round(percentual_ajuste, 2),
                                'Margem_Extra_RS': round(margem_extra, 2),
                                'Diferença_vs_Concorrente': round(preco_concorrente - preco_otimo, 2),
                                'Status': 'GANHANDO',
                                'Tipo_Ajuste': 'Proteção da Margem',
                                'Competitividade': 'Mantida (10% abaixo do concorrente)'
                            })
                        else:
                            # Produto já está bem precificado
                            suggestions.append({
                                'Produto': produto_nome,
                                'Lojista': produto_ganhando['Lojista'],
                                'Ranking_Atual': 1,
                                'Preço_Atual': nosso_preco,
                                'Preço_Concorrente_Abaixo': preco_concorrente,
                                'Preço_Sugerido': nosso_preco,
                                'Valor_Ajuste': 0,
                                'Percentual_Ajuste': 0,
                                'Margem_Extra_RS': 0,
                                'Diferença_vs_Concorrente': round(preco_concorrente - nosso_preco, 2),
                                'Status': 'GANHANDO',
                                'Tipo_Ajuste': 'Manter Preço',
                                'Competitividade': 'Ótima - preço já bem posicionado'
                            })

        # Fallback: análise por status "GANHANDO" sem ranking
        elif 'Status' in df.columns and 'Preço_Concorrente' in df.columns:
            df_ganhando = df[df['Status'] == 'GANHANDO'].copy()
            
            if not df_ganhando.empty:
                for _, row in df_ganhando.iterrows():
                    nosso_preco = row['Preço']
                    preco_concorrente = row['Preço_Concorrente']
                    
                    # Preço otimizado: 5% abaixo do concorrente
                    preco_otimo = round(preco_concorrente * 0.95, 2)
                    
                    if preco_otimo > nosso_preco:
                        valor_ajuste = preco_otimo - nosso_preco
                        percentual_ajuste = (valor_ajuste / nosso_preco) * 100
                        
                        suggestions.append({
                            'Produto': row['Produto'],
                            'Lojista': row['Lojista'],
                            'Preço_Atual': nosso_preco,
                            'Preço_Concorrente': preco_concorrente,
                            'Preço_Sugerido': preco_otimo,
                            'Valor_Ajuste': round(valor_ajuste, 2),
                            'Percentual_Ajuste': round(percentual_ajuste, 2),
                            'Margem_Extra_RS': round(valor_ajuste, 2),
                            'Status': 'GANHANDO',
                            'Tipo_Ajuste': 'Proteção da Margem',
                            'Competitividade': 'Mantida (5% abaixo do concorrente)'
                        })

        # Ordena por maior ganho de margem primeiro
        if suggestions:
            suggestions = sorted(suggestions, key=lambda x: x.get('Margem_Extra_RS', 0), reverse=True)

        # ML insights simplificado
        total_ganho = sum(s.get('Margem_Extra_RS', 0) for s in suggestions)
        produtos_com_oportunidade = len([s for s in suggestions if s.get('Valor_Ajuste', 0) > 0])
        
        ml_insights = {
            'total_produtos_analisados': len(suggestions),
            'produtos_com_oportunidade_margem': produtos_com_oportunidade,
            'ganho_potencial_total_rs': round(total_ganho, 2),
            'ganho_medio_por_produto': round(total_ganho / max(len(suggestions), 1), 2),
            'strategy': 'Proteção de margem mantendo competitividade',
            'target_discount': '5-10% abaixo do concorrente imediato'
        }

        return suggestions, ml_insights, status_counts
        
    except Exception as e:
        print('Erro ao processar CSV:', e)
        return {'error': f'Erro ao processar o CSV: {e}'}

@app.route('/analyze', methods=['POST'])
def analyze_route():
    if 'file' not in request.files:
        return jsonify({'error':'Nenhum arquivo enviado.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error':'Nome de arquivo vazio.'}), 400
    raw_bytes = file.read()
    try:
        text = raw_bytes.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw_bytes.decode('latin-1', errors='ignore')
    result = analyze_webprice_data_internal(io.StringIO(text))
    if isinstance(result, tuple):
        data, ml_insights, status_counts = result
        return jsonify({'data': data, 'ml_insights': ml_insights, 'status_counts': status_counts})
    else:
        if 'error' in result:
            return jsonify(result), 400
        if 'message' in result:
            return jsonify({'data': [], 'ml_insights': result, 'status_counts': {}})
        return jsonify({'error':'Retorno inesperado.'}), 500

@app.route('/')
def root():
    return jsonify({'status':'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
