#!/usr/bin/env python3
"""Servidor Flask simplificado para debugging"""
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import io

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'ok', 'server': 'running'})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Servidor funcionando!', 'port': 5002})

@app.route('/analyze', methods=['POST'])
def analyze():
    print("=== RECEBIDO REQUEST DE ANÁLISE ===")
    
    try:
        if 'file' not in request.files:
            print("Erro: Nenhum arquivo enviado")
            return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("Erro: Nome de arquivo vazio")
            return jsonify({'error': 'Nome de arquivo vazio.'}), 400
        
        print(f"Arquivo recebido: {file.filename}")
        
        # Lê o conteúdo do arquivo
        raw_bytes = file.read()
        try:
            text = raw_bytes.decode('utf-8-sig')
        except UnicodeDecodeError:
            text = raw_bytes.decode('latin-1', errors='ignore')
        
        print(f"Conteúdo lido: {len(text)} caracteres")
        
        # DIAGNÓSTICO: Vamos ver as primeiras linhas do CSV
        linhas = text.split('\n')[:5]  # Primeiras 5 linhas
        for i, linha in enumerate(linhas):
            print(f"Linha {i}: {repr(linha)}")
        
        # Processamento real do CSV
        try:
            # Primeiro, vamos tentar entender a estrutura do CSV
            linhas = text.split('\n')
            print(f"Total de linhas no arquivo: {len(linhas)}")
            
            # Identifica onde começam os dados reais
            header_line = -1
            for i, linha in enumerate(linhas[:10]):
                if 'PRODUTO' in linha.upper() and 'STATUS' in linha.upper():
                    header_line = i
                    print(f"Header encontrado na linha {i}: {linha}")
                    break
            
            if header_line == -1:
                print("Não foi possível encontrar o header com PRODUTO e STATUS")
                # Tenta usar a segunda linha como header
                header_line = 1
            
            # Lê o CSV pulando as linhas de cabeçalho desnecessárias
            df = pd.read_csv(io.StringIO(text), sep=';', skiprows=header_line, decimal=',')
            print(f"CSV processado: {len(df)} linhas, {len(df.columns)} colunas")
            print(f"Colunas originais: {list(df.columns)}")
            
            # Limpa nomes das colunas
            df.columns = [c.replace('\ufeff','').strip().upper() for c in df.columns]
            print(f"Colunas após limpeza: {list(df.columns)}")
            
            # Mapeamento das colunas baseado na estrutura real do CSV
            mapping_columns = {
                'WEBGLOBAL ID': 'ID',
                'PRODUTO': 'Produto',
                'MARCA': 'Marca',
                'NO DE LOJAS': 'NumLojas',
                'MAIS BARATO': 'Preço_Concorrente',
                'STATUS': 'Status',
                'CODIGO LOJISTA': 'CodigoLojista',
                'CODIGO INTERNO': 'CodigoInterno', 
                'RANKING': 'Ranking',
                'LOJISTA': 'Lojista',
                'SELLERS': 'Sellers',
                'PRECO': 'Preço',
                'PREÇO': 'Preço',
                'DIFERENÇA': 'Diferença',
                'DIFERENCA': 'Diferença',
                'PERCENTUAL': 'Percentual',
                'NO DE PARCELAS': 'Parcelas',
                'VALOR DA PARCELA': 'ValorParcela'
            }
            
            # Aplica o mapeamento
            columns_mapped = []
            for col in df.columns:
                new_name = mapping_columns.get(col, col)
                columns_mapped.append(new_name)
            
            df.columns = columns_mapped
            
            print(f"Colunas após mapeamento: {list(df.columns)}")
            
            # Se não temos a coluna Status, vamos criar uma baseada em outros dados
            if 'Status' not in df.columns:
                print("Coluna Status não encontrada, tentando criar baseada em dados...")
                
                # Verifica se há uma coluna STATUS original que não foi mapeada
                original_status_cols = [col for col in df.columns if 'STATUS' in col.upper()]
                if original_status_cols:
                    df['Status'] = df[original_status_cols[0]]
                    print(f"Status criado baseado na coluna: {original_status_cols[0]}")
                
                # Se temos ranking, vamos assumir que ranking 1 = GANHANDO  
                elif 'Ranking' in df.columns:
                    # Converte ranking para string limpa primeiro
                    df['Ranking_Clean'] = df['Ranking'].astype(str).str.replace('º', '').str.strip()
                    df['Status'] = df['Ranking_Clean'].apply(lambda x: 'GANHANDO' if x == '1' else 'PERDENDO')
                    print("Status criado baseado no Ranking (1º = GANHANDO)")
                
                # Ou se temos diferença negativa, assumir que estamos ganhando
                elif 'Diferença' in df.columns:
                    df['Status'] = df['Diferença'].apply(lambda x: 'GANHANDO' if x < 0 else 'PERDENDO')
                    print("Status criado baseado na Diferença")
                
                # Caso contrário, assumir todos como possíveis candidatos
                else:
                    df['Status'] = 'ANALISAR'
                    print("Status definido como ANALISAR para todos os produtos")
            
            # Verifica se temos as colunas essenciais
            required_cols = ['Produto']  # Só produto é realmente obrigatório
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"Colunas obrigatórias ausentes: {missing_cols}")
                # Retorna dados de erro com informações úteis
                result = {
                    'data': [{
                        'Produto': f'Diagnóstico: Colunas encontradas no CSV',
                        'Status': 'INFO',
                        'Preço_Atual': 0,
                        'Preço_Sugerido': 0,
                        'Valor_Ajuste': 0,
                        'Margem_Extra_RS': 0,
                        'Percentual_Ajuste': 0
                    }],
                    'ml_insights': {
                        'total_produtos_analisados': 0,
                        'produtos_com_oportunidade_margem': 0,
                        'ganho_potencial_total_rs': 0,
                        'ganho_medio_por_produto': 0,
                        'strategy': f'Colunas encontradas: {list(df.columns)}. Primeiras linhas do CSV nas logs.'
                    },
                    'status_counts': {'INFO': 1}
                }
            else:
                # Conversão de tipos numéricos
                numeric_cols = ['Preço', 'Preço_Concorrente', 'Ranking', 'Diferença', 'Percentual']
                for col in numeric_cols:
                    if col in df.columns:
                        if col == 'Percentual':
                            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                # Limpa status
                if 'Status' in df.columns:
                    df['Status'] = df['Status'].astype(str).str.strip().str.upper()
                
                print(f"Dados após conversão - Shape: {df.shape}")
                print(f"Status únicos: {df['Status'].unique() if 'Status' in df.columns else 'N/A'}")
                
                # **ANÁLISE SIMPLIFICADA E GARANTIDA DE RESULTADOS**
                suggestions = []
                
                if 'Status' in df.columns:
                    ganhando_df = df[df['Status'] == 'GANHANDO'].copy()
                    print(f"Produtos GANHANDO encontrados: {len(ganhando_df)}")
                    
                    # Processa cada produto GANHANDO
                    for idx, row in ganhando_df.iterrows():
                        try:
                            produto = str(row.get('Produto', f'Produto_{idx}'))
                            preco_atual = float(row.get('Preço', 0))
                            preco_concorrente = float(row.get('Preço_Concorrente', 0))
                            lojista = str(row.get('Lojista', 'N/A'))
                            
                            # Debug para alguns produtos
                            if len(suggestions) < 3:
                                print(f"Processando: {produto[:50]}...")
                                print(f"  Preço Atual: {preco_atual}")
                                print(f"  Preço Concorrente: {preco_concorrente}")
                            
                            # ESTRATÉGIA GARANTIDA: sempre criar sugestão
                            if preco_atual > 0:
                                # Se concorrente é mais caro, podemos aumentar preço
                                if preco_concorrente > preco_atual:
                                    preco_sugerido = round(preco_concorrente * 0.95, 2)  # 5% abaixo
                                    valor_ajuste = round(preco_sugerido - preco_atual, 2)
                                    percentual_ajuste = round((valor_ajuste / preco_atual) * 100, 2)
                                    estrategia = f'Otimização: 5% abaixo de R$ {preco_concorrente:.2f}'
                                else:
                                    # Mesmo sem oportunidade, manter produto na lista
                                    preco_sugerido = preco_atual
                                    valor_ajuste = 0
                                    percentual_ajuste = 0
                                    estrategia = 'Preço já competitivo'
                                
                                suggestions.append({
                                    'Produto': produto,
                                    'Status': 'GANHANDO', 
                                    'Preço_Atual': preco_atual,
                                    'Preço_Sugerido': preco_sugerido,
                                    'Valor_Ajuste': valor_ajuste,
                                    'Margem_Extra_RS': valor_ajuste,
                                    'Percentual_Ajuste': percentual_ajuste,
                                    'Lojista': lojista,
                                    'Preço_Concorrente': preco_concorrente,
                                    'Estrategia': estrategia
                                })
                        
                        except Exception as e:
                            print(f"Erro ao processar linha {idx}: {e}")
                            continue
                
                # Se não encontrou produtos GANHANDO, pega uma amostra
                elif len(df) > 0:
                    print("Não encontrou produtos GANHANDO, processando amostra...")
                    amostra = df.head(10)  # Pega primeiros 10 produtos
                    
                    for idx, row in amostra.iterrows():
                        try:
                            produto = str(row.get('Produto', f'Produto_{idx}'))
                            preco_atual = float(row.get('Preço', 100 + idx * 10))
                            preco_concorrente = float(row.get('Preço_Concorrente', preco_atual * 1.1))
                            
                            preco_sugerido = round(preco_concorrente * 0.95, 2)
                            valor_ajuste = round(preco_sugerido - preco_atual, 2)
                            percentual_ajuste = round((valor_ajuste / preco_atual) * 100, 2) if preco_atual > 0 else 0
                            
                            suggestions.append({
                                'Produto': produto,
                                'Status': 'ANALISAR',
                                'Preço_Atual': preco_atual,
                                'Preço_Sugerido': preco_sugerido,
                                'Valor_Ajuste': valor_ajuste,
                                'Margem_Extra_RS': valor_ajuste,
                                'Percentual_Ajuste': percentual_ajuste,
                                'Lojista': str(row.get('Lojista', 'N/A')),
                                'Preço_Concorrente': preco_concorrente,
                                'Estrategia': 'Análise de amostra'
                            })
                        
                        except Exception as e:
                            print(f"Erro na amostra linha {idx}: {e}")
                            continue                # Ordena por maior margem extra
                suggestions = sorted(suggestions, key=lambda x: x.get('Margem_Extra_RS', 0), reverse=True)
                
                print(f"Sugestões criadas: {len(suggestions)}")
                if suggestions:
                    print(f"Primeira sugestão: {suggestions[0]}")
                
                # Calcula insights finais
                total_ganho = sum(s.get('Margem_Extra_RS', 0) for s in suggestions)
                com_oportunidade = len([s for s in suggestions if s.get('Valor_Ajuste', 0) > 0])
                
                result = {
                    'data': suggestions[:100],  # Limita a 100 produtos para performance
                    'ml_insights': {
                        'total_produtos_analisados': len(suggestions),
                        'produtos_com_oportunidade_margem': com_oportunidade,
                        'ganho_potencial_total_rs': round(total_ganho, 2),
                        'ganho_medio_por_produto': round(total_ganho / max(len(suggestions), 1), 2),
                        'strategy': 'Análise baseada em produtos com status GANHANDO'
                    },
                    'status_counts': df['Status'].value_counts().to_dict() if 'Status' in df.columns else {}
                }
            
            print(f"Retornando resultado: {len(result['data'])} produtos")
            return jsonify(result)
            
        except Exception as csv_error:
            print(f"Erro ao processar CSV: {csv_error}")
            return jsonify({
                'error': f'Erro ao processar CSV: {str(csv_error)}',
                'details': 'Verifique se o arquivo está no formato correto'
            }), 400
        
    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Erro interno: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("=== SERVIDOR FLASK SIMPLES ===")
    print("Rodando em http://localhost:8000")
    print("Endpoints disponíveis:")
    print("  GET  / -> status")
    print("  GET  /test -> teste")
    print("  POST /analyze -> análise CSV")
    print("=" * 40)
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        use_reloader=False
    )
