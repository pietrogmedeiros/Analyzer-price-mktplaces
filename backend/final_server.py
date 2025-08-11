from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import io
import json

app = Flask(__name__)
CORS(app)

def convert_to_native_types(obj):
    """Converte tipos numpy para tipos Python nativos recursivamente"""
    if isinstance(obj, dict):
        return {str(k): convert_to_native_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    elif hasattr(obj, 'item'):  # numpy types
        return obj.item()
    elif pd.isna(obj):
        return None
    else:
        return obj

@app.route('/')
def home():
    return jsonify({'status': 'running', 'message': 'WebPrice Analyzer Backend'})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        print("🚀 INICIANDO ANÁLISE...")
        
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nome de arquivo vazio'}), 400
        
        print(f"📁 Arquivo: {file.filename}")
        
        # Lê o arquivo
        raw_bytes = file.read()
        try:
            text = raw_bytes.decode('utf-8-sig')
        except UnicodeDecodeError:
            text = raw_bytes.decode('latin-1', errors='ignore')
        
        print(f"📊 Dados carregados: {len(text)} caracteres")
        
        # Detecta header
        linhas = text.split('\n')
        header_line = 0
        
        for i, linha in enumerate(linhas[:10]):
            if 'PRODUTO' in linha.upper():
                header_line = i
                break
        
        # Carrega CSV
        df = pd.read_csv(io.StringIO(text), sep=';', skiprows=header_line, decimal=',')
        
        # Limpa colunas
        df.columns = [str(c).replace('\ufeff', '').strip().upper() for c in df.columns]
        
        # Mapeia colunas
        mapping = {
            'PRODUTO': 'Produto',
            'STATUS': 'Status',
            'PRECO': 'Preço',
            'PREÇO': 'Preço',
            'MAIS BARATO': 'Preço_Concorrente',
            'LOJISTA': 'Lojista'
        }
        
        for old, new in mapping.items():
            if old in df.columns:
                df.rename(columns={old: new}, inplace=True)
        
        print(f"✅ CSV processado: {len(df)} linhas")
        
        # Converte valores numéricos
        for col in ['Preço', 'Preço_Concorrente']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.').str.replace(r'[^\d.]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Processa status
        if 'Status' in df.columns:
            df['Status'] = df['Status'].astype(str).str.strip().str.upper()
        
        print(f"💰 Status únicos: {df['Status'].unique()[:5] if 'Status' in df.columns else 'N/A'}")
        
        # GERA SUGESTÕES GARANTIDAS
        suggestions = []
        
        # Pega produtos GANHANDO ou amostra
        if 'Status' in df.columns and 'GANHANDO' in df['Status'].values:
            sample_df = df[df['Status'] == 'GANHANDO'].head(20)
            print(f"🎯 Analisando {len(sample_df)} produtos GANHANDO")
        else:
            sample_df = df.head(20)
            print(f"📝 Analisando amostra de {len(sample_df)} produtos")
        
        # Processa cada produto
        for i, row in sample_df.iterrows():
            try:
                # Garante valores básicos
                produto = str(row.get('Produto', f'Produto_{i}'))[:100]
                preco_atual = float(row.get('Preço', 0))
                preco_concorrente = float(row.get('Preço_Concorrente', 0))
                lojista = str(row.get('Lojista', 'N/A'))[:50]
                status = str(row.get('Status', 'ANALISAR'))
                
                # Só processa se houver preço
                if preco_atual > 0:
                    # Se não tem concorrente, estima
                    if preco_concorrente <= 0:
                        preco_concorrente = preco_atual * 1.2
                    
                    # Calcula otimização (5% abaixo do concorrente)
                    preco_sugerido = round(preco_concorrente * 0.95, 2)
                    
                    # Calcula ajustes
                    if preco_sugerido > preco_atual:
                        valor_ajuste = round(preco_sugerido - preco_atual, 2)
                        percentual_ajuste = round((valor_ajuste / preco_atual) * 100, 2)
                        estrategia = f'Otimizar para R$ {preco_sugerido:.2f} (5% abaixo concorrente)'
                    else:
                        valor_ajuste = 0.0
                        percentual_ajuste = 0.0
                        preco_sugerido = preco_atual
                        estrategia = 'Preço já competitivo'
                    
                    # Cria sugestão com valores nativos Python
                    suggestion = {
                        'Produto': produto,
                        'Status': status,
                        'Preço_Atual': float(preco_atual),
                        'Preço_Sugerido': float(preco_sugerido),
                        'Valor_Ajuste': float(valor_ajuste),
                        'Margem_Extra_RS': float(valor_ajuste),
                        'Percentual_Ajuste': float(percentual_ajuste),
                        'Lojista': lojista,
                        'Preço_Concorrente': float(preco_concorrente),
                        'Estrategia': estrategia
                    }
                    
                    suggestions.append(suggestion)
                    
            except Exception as e:
                print(f"⚠️  Erro na linha {i}: {e}")
                continue
        
        # Ordena por maior ganho
        suggestions.sort(key=lambda x: x.get('Margem_Extra_RS', 0), reverse=True)
        
        # Calcula estatísticas
        total_ganho = sum(s['Margem_Extra_RS'] for s in suggestions)
        com_oportunidade = len([s for s in suggestions if s['Valor_Ajuste'] > 0])
        
        # Conta status (com conversão para int Python)
        if 'Status' in df.columns:
            status_counts = {}
            for status, count in df['Status'].value_counts().items():
                status_counts[str(status)] = int(count)
        else:
            status_counts = {'TOTAL': int(len(df))}
        
        print(f"✨ Geradas {len(suggestions)} sugestões com R$ {total_ganho:.2f} de ganho potencial")
        
        # Monta resultado final
        result = {
            'data': suggestions,
            'ml_insights': {
                'total_produtos_analisados': int(len(suggestions)),
                'produtos_com_oportunidade_margem': int(com_oportunidade),
                'ganho_potencial_total_rs': float(total_ganho),
                'ganho_medio_por_produto': float(total_ganho / max(len(suggestions), 1)),
                'strategy': f'Análise de {len(sample_df)} produtos com dados reais'
            },
            'status_counts': status_counts
        }
        
        print("🎉 ANÁLISE CONCLUÍDA COM SUCESSO!")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 WEBPRICE ANALYZER BACKEND - PORTA 8000")
    print("📊 Pronto para análise de CSV com dados reais!")
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
