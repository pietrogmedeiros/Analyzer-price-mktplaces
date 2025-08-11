from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import io

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'status': 'running', 'message': 'Servidor de análise CSV ativo'})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        print("=== NOVA ANÁLISE INICIADA ===")
        
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nome de arquivo vazio'}), 400
        
        print(f"Arquivo recebido: {file.filename}")
        
        # Lê o arquivo CSV
        raw_bytes = file.read()
        try:
            text = raw_bytes.decode('utf-8-sig')
        except UnicodeDecodeError:
            text = raw_bytes.decode('latin-1', errors='ignore')
        
        print(f"Bytes lidos: {len(text)}")
        
        # Tenta detectar onde começam os dados reais
        linhas = text.split('\n')
        header_line = 0
        
        for i, linha in enumerate(linhas[:10]):
            if 'PRODUTO' in linha.upper() and ('STATUS' in linha.upper() or 'PRECO' in linha.upper()):
                header_line = i
                print(f"Header encontrado na linha {i}")
                break
        
        # Lê o CSV
        df = pd.read_csv(io.StringIO(text), sep=';', skiprows=header_line, decimal=',')
        print(f"CSV carregado: {len(df)} linhas, {len(df.columns)} colunas")
        
        # Limpa nomes das colunas
        df.columns = [str(c).replace('\ufeff', '').strip().upper() for c in df.columns]
        print(f"Colunas: {list(df.columns)[:10]}...")  # Mostra primeiras 10 colunas
        
        # Mapeia colunas conhecidas
        column_mapping = {
            'PRODUTO': 'Produto',
            'STATUS': 'Status', 
            'PRECO': 'Preço',
            'PREÇO': 'Preço',
            'MAIS BARATO': 'Preço_Concorrente',
            'LOJISTA': 'Lojista',
            'RANKING': 'Ranking'
        }
        
        # Aplica mapeamento
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        print(f"Colunas após mapeamento: {[c for c in df.columns if c in ['Produto', 'Status', 'Preço', 'Preço_Concorrente', 'Lojista']]}")
        
        # Converte colunas numéricas
        numeric_cols = ['Preço', 'Preço_Concorrente', 'Ranking']
        for col in numeric_cols:
            if col in df.columns:
                try:
                    # Remove vírgulas e converte para float
                    df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    print(f"{col}: convertido, min={df[col].min():.2f}, max={df[col].max():.2f}")
                except Exception as e:
                    print(f"Erro ao converter {col}: {e}")
                    df[col] = 0
        
        # Limpa status
        if 'Status' in df.columns:
            df['Status'] = df['Status'].astype(str).str.strip().str.upper()
            status_counts = df['Status'].value_counts()
            print(f"Status encontrados: {dict(status_counts)}")
            # Converte para tipos Python nativos
            status_counts = {str(k): int(v) for k, v in status_counts.items()}
        else:
            df['Status'] = 'ANALISAR'
            status_counts = {'ANALISAR': int(len(df))}
        
        # PROCESSA DADOS - VERSÃO GARANTIDA
        suggestions = []
        
        # Filtra produtos GANHANDO ou pega uma amostra
        if 'Status' in df.columns and 'GANHANDO' in df['Status'].values:
            target_df = df[df['Status'] == 'GANHANDO'].copy()
            print(f"Produtos GANHANDO: {len(target_df)}")
        else:
            target_df = df.head(20).copy()  # Pega primeiros 20 para análise
            print(f"Usando amostra de {len(target_df)} produtos")
        
        # Processa cada produto
        for idx, row in target_df.iterrows():
            try:
                produto = str(row.get('Produto', f'Produto_{idx}'))[:100]  # Limita tamanho
                preco_atual = float(row.get('Preço', 0))
                preco_concorrente = float(row.get('Preço_Concorrente', 0))
                status = str(row.get('Status', 'ANALISAR'))
                lojista = str(row.get('Lojista', 'N/A'))[:50]
                
                # Só processa se tiver preços válidos
                if preco_atual > 0:
                    # Se não tem preço concorrente, estima um baseado no atual
                    if preco_concorrente <= 0:
                        preco_concorrente = preco_atual * 1.15  # Assume 15% mais caro
                    
                    # Calcula preço otimizado (5% abaixo do concorrente)
                    preco_sugerido = round(preco_concorrente * 0.95, 2)
                    
                    # Verifica se há oportunidade de aumento
                    if preco_sugerido > preco_atual:
                        valor_ajuste = round(preco_sugerido - preco_atual, 2)
                        percentual_ajuste = round((valor_ajuste / preco_atual) * 100, 2)
                        estrategia = f'Otimização: 5% abaixo de R$ {preco_concorrente:.2f}'
                    else:
                        valor_ajuste = 0
                        percentual_ajuste = 0
                        preco_sugerido = preco_atual
                        estrategia = 'Preço já competitivo'
                    
                    suggestions.append({
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
                    })
            
            except Exception as e:
                print(f"Erro na linha {idx}: {e}")
                continue
        
        # Ordena por maior ganho
        suggestions = sorted(suggestions, key=lambda x: x.get('Margem_Extra_RS', 0), reverse=True)
        
        # Limita a 50 produtos para performance
        suggestions = suggestions[:50]
        
        # Calcula estatísticas
        total_ganho = sum(s.get('Margem_Extra_RS', 0) for s in suggestions)
        com_oportunidade = len([s for s in suggestions if s.get('Valor_Ajuste', 0) > 0])
        
        print(f"Sugestões criadas: {len(suggestions)}")
        print(f"Com oportunidade: {com_oportunidade}")
        print(f"Ganho total: R$ {total_ganho:.2f}")
        
        result = {
            'data': suggestions,
            'ml_insights': {
                'total_produtos_analisados': len(suggestions),
                'produtos_com_oportunidade_margem': com_oportunidade,
                'ganho_potencial_total_rs': round(total_ganho, 2),
                'ganho_medio_por_produto': round(total_ganho / max(len(suggestions), 1), 2),
                'strategy': f'Análise de {len(target_df)} produtos do CSV real'
            },
            'status_counts': dict(status_counts)
        }
        
        print("=== ANÁLISE CONCLUÍDA COM SUCESSO ===")
        return jsonify(result)
        
    except Exception as e:
        print(f"ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro ao processar: {str(e)}'}), 500

if __name__ == '__main__':
    print("🔥 SERVIDOR CSV REAL - PORTA 8000 🔥")
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
