"""
🔍 ULTIMATE DEBUG SERVER - RESOLUÇÃO DEFINITIVA DO PROBLEMA DOS ZEROS
"""

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def analyze_csv_ultimate_debug(csv_content_stream):
    try:
        # 🔍 DEBUGGING COMPLETO DO CSV
        print("\n" + "="*80)
        print("🔍 ULTIMATE DEBUG - ANÁLISE COMPLETA DO CSV")
        print("="*80)
        
        # Ler o conteúdo bruto primeiro
        csv_content_stream.seek(0)
        raw_content = csv_content_stream.read()
        print(f"📊 TAMANHO DO ARQUIVO: {len(raw_content)} caracteres")
        
        # Mostrar as primeiras linhas brutas
        lines = raw_content.split('\n')
        print(f"📝 TOTAL DE LINHAS: {len(lines)}")
        print("\n🔍 PRIMEIRAS 5 LINHAS BRUTAS:")
        for i, line in enumerate(lines[:5]):
            print(f"  [{i}]: {repr(line[:200])}")
        
        # Detectar separador
        first_data_line = lines[1] if len(lines) > 1 else lines[0]
        semicolon_count = first_data_line.count(';')
        comma_count = first_data_line.count(',')
        pipe_count = first_data_line.count('|')
        tab_count = first_data_line.count('\t')
        
        print(f"\n🔍 ANÁLISE DE SEPARADORES:")
        print(f"  Ponto-e-vírgula (;): {semicolon_count}")
        print(f"  Vírgula (,): {comma_count}")
        print(f"  Pipe (|): {pipe_count}")
        print(f"  Tab: {tab_count}")
        
        # Escolher separador
        if semicolon_count >= 10:
            separator = ';'
            print(f"✅ SEPARADOR ESCOLHIDO: ';' ({semicolon_count} ocorrências)")
        elif comma_count >= 10:
            separator = ','
            print(f"✅ SEPARADOR ESCOLHIDO: ',' ({comma_count} ocorrências)")
        elif pipe_count >= 10:
            separator = '|'
            print(f"✅ SEPARADOR ESCOLHIDO: '|' ({pipe_count} ocorrências)")
        else:
            separator = ';'  # default
            print(f"⚠️  SEPARADOR DEFAULT: ';'")
        
        # Tentar diferentes métodos de leitura
        csv_content_stream.seek(0)
        
        print(f"\n🔄 TENTATIVA 1 - Ler com separador '{separator}' e skiprows=1")
        try:
            df1 = pd.read_csv(csv_content_stream, sep=separator, skiprows=1, decimal=',')
            print(f"✅ SUCESSO: {df1.shape[0]} linhas, {df1.shape[1]} colunas")
            print(f"📋 COLUNAS: {df1.columns.tolist()}")
            if df1.shape[1] >= 10:
                print("🎯 RESULTADO PROMISSOR!")
                df = df1
            else:
                raise Exception("Poucas colunas")
        except Exception as e:
            print(f"❌ FALHOU: {e}")
            
            # Tentativa 2
            csv_content_stream.seek(0)
            print(f"\n🔄 TENTATIVA 2 - Ler sem skiprows")
            try:
                df2 = pd.read_csv(csv_content_stream, sep=separator, decimal=',')
                print(f"✅ SUCESSO: {df2.shape[0]} linhas, {df2.shape[1]} colunas")
                print(f"📋 COLUNAS: {df2.columns.tolist()}")
                if df2.shape[1] >= 10:
                    print("🎯 RESULTADO PROMISSOR!")
                    df = df2
                else:
                    raise Exception("Poucas colunas")
            except Exception as e2:
                print(f"❌ FALHOU: {e2}")
                
                # Tentativa 3 - Manual
                csv_content_stream.seek(0)
                print(f"\n🔄 TENTATIVA 3 - Parsing manual das linhas")
                
                # Encontrar linha do header
                header_line = None
                header_idx = 0
                
                for i, line in enumerate(lines[:10]):
                    if 'PRODUTO' in line.upper() and 'PRECO' in line.upper():
                        header_line = line
                        header_idx = i
                        print(f"✅ HEADER ENCONTRADO NA LINHA {i}: {repr(line[:200])}")
                        break
                
                if header_line:
                    headers = [col.strip().replace('"', '') for col in header_line.split(separator)]
                    print(f"📋 HEADERS EXTRAÍDOS: {headers}")
                    
                    # Processar dados
                    data_lines = []
                    for line in lines[header_idx + 1:]:
                        if line.strip() and separator in line:
                            row = [col.strip().replace('"', '') for col in line.split(separator)]
                            if len(row) == len(headers):
                                data_lines.append(row)
                            elif len(row) > len(headers):
                                data_lines.append(row[:len(headers)])  # Truncar
                    
                    print(f"✅ DADOS PROCESSADOS: {len(data_lines)} linhas")
                    
                    if data_lines:
                        df = pd.DataFrame(data_lines, columns=headers)
                        print(f"🎯 DATAFRAME FINAL: {df.shape[0]} linhas, {df.shape[1]} colunas")
                    else:
                        raise Exception("Nenhum dado válido encontrado")
                else:
                    raise Exception("Header não encontrado")
        
        # 🔍 ANÁLISE DAS COLUNAS
        print(f"\n📊 ANÁLISE FINAL DO DATAFRAME:")
        print(f"  Formato: {df.shape[0]} linhas × {df.shape[1]} colunas")
        print(f"  Colunas: {df.columns.tolist()}")
        
        # Mostrar amostra dos dados
        print(f"\n🔍 AMOSTRA DOS DADOS (5 primeiras linhas):")
        for i in range(min(5, len(df))):
            print(f"  Linha {i}: {dict(df.iloc[i])}")
        
        # 🔧 MAPEAMENTO E LIMPEZA DAS COLUNAS
        print(f"\n🔧 MAPEANDO COLUNAS...")
        
        # Limpar nomes das colunas
        df.columns = [str(col).replace('\ufeff', '').strip().upper() for col in df.columns]
        
        # Mapeamento inteligente
        column_mapping = {}
        
        for col in df.columns:
            col_upper = col.upper()
            if 'PRODUTO' in col_upper and 'PRODUTO' not in column_mapping:
                column_mapping['PRODUTO'] = col
            elif 'PRECO' in col_upper and 'PRECO' not in column_mapping:
                column_mapping['PRECO'] = col
            elif 'MAIS BARATO' in col_upper or 'MAISBARATO' in col_upper:
                column_mapping['MAIS_BARATO'] = col
            elif 'STATUS' in col_upper:
                column_mapping['STATUS'] = col
            elif 'LOJISTA' in col_upper:
                column_mapping['LOJISTA'] = col
            elif 'RANKING' in col_upper:
                column_mapping['RANKING'] = col
        
        print(f"🔗 MAPEAMENTO ENCONTRADO:")
        for key, value in column_mapping.items():
            print(f"  {key} → {value}")
        
        # Renomear colunas
        df.rename(columns={
            column_mapping.get('PRODUTO', ''): 'Produto',
            column_mapping.get('PRECO', ''): 'Preço',
            column_mapping.get('MAIS_BARATO', ''): 'Preço_Concorrente', 
            column_mapping.get('STATUS', ''): 'Status',
            column_mapping.get('LOJISTA', ''): 'Lojista',
            column_mapping.get('RANKING', ''): 'Ranking'
        }, inplace=True)
        
        # Verificar colunas essenciais
        essential_cols = ['Produto', 'Preço', 'Status']
        missing_cols = [col for col in essential_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ COLUNAS ESSENCIAIS FALTANDO: {missing_cols}")
            print(f"📋 COLUNAS DISPONÍVEIS: {df.columns.tolist()}")
            return {"error": f"Colunas essenciais não encontradas: {missing_cols}"}
        
        print(f"✅ COLUNAS ESSENCIAIS ENCONTRADAS!")
        
        # 🔧 CONVERSÃO DOS PREÇOS
        print(f"\n🔧 CONVERTENDO PREÇOS...")
        
        def convert_price(price_str):
            if pd.isna(price_str) or price_str == '':
                return 0.0
            
            price_str = str(price_str).strip()
            # Remove aspas, espaços e caracteres especiais
            price_str = price_str.replace('"', '').replace("'", '').replace(' ', '')
            
            # Se já é número
            if price_str.replace(',', '.').replace('-', '').isdigit():
                return float(price_str.replace(',', '.'))
            
            # Remove símbolos monetários
            price_str = price_str.replace('R$', '').replace('$', '').replace('€', '')
            
            # Substitui vírgula por ponto para decimal
            if ',' in price_str and '.' not in price_str:
                price_str = price_str.replace(',', '.')
            elif ',' in price_str and '.' in price_str:
                # Formato brasileiro: 1.234,56 → 1234.56
                parts = price_str.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    price_str = parts[0].replace('.', '') + '.' + parts[1]
            
            try:
                return float(price_str)
            except:
                print(f"⚠️  Falha ao converter preço: {repr(price_str)}")
                return 0.0
        
        # Converter colunas de preço
        for col in ['Preço', 'Preço_Concorrente']:
            if col in df.columns:
                print(f"🔄 Convertendo coluna: {col}")
                original_sample = df[col].head(3).tolist()
                df[col] = df[col].apply(convert_price)
                converted_sample = df[col].head(3).tolist()
                print(f"  Exemplo: {original_sample} → {converted_sample}")
        
        # Status cleanup
        if 'Status' in df.columns:
            df['Status'] = df['Status'].astype(str).str.strip().str.upper()
        
        # 🎯 ANÁLISE FINAL E CRIAÇÃO DE SUGESTÕES
        print(f"\n🎯 CRIANDO SUGESTÕES DE OTIMIZAÇÃO...")
        
        suggestions = []
        
        # Filtrar produtos com status "GANHANDO"
        if 'Status' in df.columns:
            ganhando_df = df[df['Status'] == 'GANHANDO'].copy()
            print(f"🏆 PRODUTOS GANHANDO ENCONTRADOS: {len(ganhando_df)}")
            
            if len(ganhando_df) > 0:
                print(f"📋 AMOSTRA DE PRODUTOS GANHANDO:")
                for i in range(min(3, len(ganhando_df))):
                    row = ganhando_df.iloc[i]
                    print(f"  {i+1}. {row.get('Produto', 'N/A')} - R$ {row.get('Preço', 0)}")
                
                # Criar sugestões para produtos GANHANDO
                for idx, row in ganhando_df.iterrows():
                    produto = row.get('Produto', 'N/A')
                    preco_atual = row.get('Preço', 0)
                    preco_concorrente = row.get('Preço_Concorrente', 0)
                    lojista = row.get('Lojista', 'N/A')
                    
                    if preco_atual > 0 and preco_concorrente > 0:
                        # Estratégia: ajustar para 95% do preço do concorrente
                        preco_sugerido = round(preco_concorrente * 0.95, 2)
                        
                        # Só sugerir se pudermos aumentar o preço
                        if preco_sugerido > preco_atual:
                            valor_ajuste = preco_sugerido - preco_atual
                            percentual_ajuste = (valor_ajuste / preco_atual) * 100
                            
                            suggestions.append({
                                'Produto': produto,
                                'Lojista': lojista,
                                'Preço_Atual': preco_atual,
                                'Preço_Concorrente': preco_concorrente,
                                'Preço_Sugerido': preco_sugerido,
                                'Valor_Ajuste': round(valor_ajuste, 2),
                                'Percentual_Ajuste': round(percentual_ajuste, 2),
                                'Margem_Extra_RS': round(valor_ajuste, 2),
                                'Status': 'GANHANDO',
                                'Tipo_Ajuste': 'Proteção da Margem',
                                'Competitividade': 'Mantida (5% abaixo do concorrente)'
                            })
                        else:
                            # Produto já bem posicionado
                            suggestions.append({
                                'Produto': produto,
                                'Lojista': lojista,
                                'Preço_Atual': preco_atual,
                                'Preço_Concorrente': preco_concorrente,
                                'Preço_Sugerido': preco_atual,
                                'Valor_Ajuste': 0,
                                'Percentual_Ajuste': 0,
                                'Margem_Extra_RS': 0,
                                'Status': 'GANHANDO',
                                'Tipo_Ajuste': 'Manter Preço',
                                'Competitividade': 'Ótima'
                            })
        
        print(f"🎉 SUGESTÕES CRIADAS: {len(suggestions)}")
        
        # Ordenar por maior ganho de margem
        suggestions = sorted(suggestions, key=lambda x: x.get('Margem_Extra_RS', 0), reverse=True)
        
        # ML Insights
        total_ganho = sum(s.get('Margem_Extra_RS', 0) for s in suggestions)
        produtos_com_oportunidade = len([s for s in suggestions if s.get('Valor_Ajuste', 0) > 0])
        
        ml_insights = {
            'total_produtos_analisados': len(df),
            'produtos_ganhando': len(ganhando_df) if 'ganhando_df' in locals() else 0,
            'produtos_com_oportunidade_margem': produtos_com_oportunidade,
            'sugestoes_criadas': len(suggestions),
            'ganho_potencial_total_rs': round(total_ganho, 2),
            'ganho_medio_por_produto': round(total_ganho / max(len(suggestions), 1), 2),
            'estrategia': 'Proteção de margem mantendo competitividade',
            'metodo': 'ULTIMATE DEBUG - Parsing avançado com múltiplas tentativas'
        }
        
        print(f"\n🎊 RESULTADO FINAL:")
        print(f"  📊 {len(df)} produtos analisados")
        print(f"  🏆 {ml_insights.get('produtos_ganhando', 0)} produtos GANHANDO")
        print(f"  💡 {len(suggestions)} sugestões criadas")
        print(f"  💰 R$ {total_ganho:.2f} de ganho potencial")
        
        return suggestions, ml_insights
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return {'error': f'Erro no processamento: {str(e)}'}

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio.'}), 400
    
    try:
        # Ler arquivo
        raw_bytes = file.read()
        
        # Tentar diferentes encodings
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        text = None
        
        for encoding in encodings:
            try:
                text = raw_bytes.decode(encoding)
                print(f"✅ ENCODING DETECTADO: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if text is None:
            return jsonify({'error': 'Não foi possível decodificar o arquivo'}), 400
        
        # Processar
        result = analyze_csv_ultimate_debug(io.StringIO(text))
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify(result), 400
        
        suggestions, ml_insights = result
        
        return jsonify({
            'data': suggestions,
            'ml_insights': ml_insights,
            'status_counts': {'GANHANDO': ml_insights.get('produtos_ganhando', 0)}
        })
        
    except Exception as e:
        print(f"❌ ERRO NA ROTA: {e}")
        return jsonify({'error': f'Erro no servidor: {str(e)}'}), 500

@app.route('/')
def root():
    return jsonify({'status': 'Ultimate Debug Server - Resolução dos Zeros', 'version': '3.0'})

if __name__ == '__main__':
    print("\n🚀 ULTIMATE DEBUG SERVER - PORTA 8000")
    print("🎯 RESOLUÇÃO DEFINITIVA DO PROBLEMA DOS ZEROS")
    print("🔍 ANÁLISE AVANÇADA DE CSV COM MÚLTIPLAS TENTATIVAS")
    app.run(host='0.0.0.0', port=8000, debug=True)
