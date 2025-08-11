"""
🎯 SERVIDOR COM COLUNAS CORRETAS
Baseado nas colunas exatas que estão na segunda linha do CSV
"""

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

print("🎯 SERVIDOR COM COLUNAS CORRETAS INICIANDO...")

def convert_brazilian_price(price_str):
    """Converte preços no formato brasileiro para float"""
    if pd.isna(price_str) or price_str == '' or price_str is None:
        return 0.0
    
    try:
        # Convert to string
        price_str = str(price_str).strip()
        
        # Remove quotes and extra spaces
        price_str = price_str.replace('"', '').replace("'", '').strip()
        
        # Handle empty strings
        if not price_str or price_str.lower() in ['nan', 'null', 'none']:
            return 0.0
        
        # Remove currency symbols
        price_str = price_str.replace('R$', '').replace('$', '').strip()
        
        # Brazilian format: 1.234,56 -> 1234.56
        if ',' in price_str:
            parts = price_str.split(',')
            if len(parts) == 2 and len(parts[1]) <= 3:  # Decimal part
                integer_part = parts[0].replace('.', '')  # Remove thousand separators
                decimal_part = parts[1]
                price_str = f"{integer_part}.{decimal_part}"
            else:
                price_str = price_str.replace(',', '.')
        
        # Remove any remaining non-numeric characters except . and -
        cleaned = ''
        for char in price_str:
            if char.isdigit() or char in '.-':
                cleaned += char
        
        if cleaned and cleaned != '-' and cleaned != '.':
            return float(cleaned)
        
        return 0.0
        
    except Exception as e:
        print(f"⚠️ Erro ao converter preço '{price_str}': {e}")
        return 0.0

def analyze_csv_with_correct_columns(csv_content):
    """Análise do CSV procurando pelas colunas corretas na segunda linha"""
    
    print("\n" + "="*80)
    print("🎯 ANÁLISE COM COLUNAS CORRETAS")
    print("="*80)
    
    try:
        # Split lines
        lines = csv_content.strip().split('\n')
        print(f"📝 Total de linhas: {len(lines)}")
        
        # Show first few lines for debugging
        print(f"\n🔍 PRIMEIRAS 3 LINHAS:")
        for i, line in enumerate(lines[:3]):
            print(f"  [{i}]: {repr(line)}")
        
        # The REAL header is in line 1 (second line), not line 0
        if len(lines) < 2:
            raise Exception("CSV deve ter pelo menos 2 linhas")
        
        header_line = lines[1]  # Segunda linha = header real
        data_lines = lines[2:]  # A partir da terceira linha = dados
        
        print(f"\n📋 HEADER (linha 1): {repr(header_line)}")
        
        # Detect separator from header
        separators = {';': header_line.count(';'), 
                     ',': header_line.count(','),
                     '\t': header_line.count('\t')}
        
        separator = max(separators.items(), key=lambda x: x[1])[0]
        print(f"🔧 Separador detectado: '{separator}' ({separators[separator]} ocorrências)")
        
        # Parse header
        headers = [col.strip().replace('"', '') for col in header_line.split(separator)]
        print(f"🏷️  COLUNAS ENCONTRADAS: {headers}")
        
        # Parse data lines
        data_rows = []
        for i, line in enumerate(data_lines):
            if line.strip():
                row = [col.strip().replace('"', '') for col in line.split(separator)]
                # Ensure same number of columns
                while len(row) < len(headers):
                    row.append('')
                if len(row) > len(headers):
                    row = row[:len(headers)]
                data_rows.append(row)
        
        print(f"📊 DADOS PROCESSADOS: {len(data_rows)} linhas")
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=headers)
        print(f"✅ DataFrame criado: {df.shape[0]} linhas × {df.shape[1]} colunas")
        
        # Show sample data
        print(f"\n🔍 AMOSTRA DOS DADOS:")
        for i in range(min(3, len(df))):
            print(f"  Linha {i}: {dict(df.iloc[i])}")
        
        # Map columns to standard names
        # Procurar pelas colunas exatas que você mencionou
        column_mapping = {}
        
        for col in df.columns:
            col_upper = col.upper().strip()
            print(f"🔍 Analisando coluna: '{col}' -> '{col_upper}'")
            
            if 'PRODUTOS' in col_upper and 'DISPONÍVEIS' in col_upper:
                column_mapping['Produto'] = col
                print(f"  ✅ Mapeado como 'Produto'")
            elif col_upper == 'STATUS':
                column_mapping['Status'] = col
                print(f"  ✅ Mapeado como 'Status'")
            elif col_upper == 'RANKING':
                column_mapping['Ranking'] = col
                print(f"  ✅ Mapeado como 'Ranking'")
            elif col_upper == 'LOJISTA':
                column_mapping['Lojista'] = col
                print(f"  ✅ Mapeado como 'Lojista'")
            elif col_upper == 'PRECO':
                column_mapping['Preço'] = col
                print(f"  ✅ Mapeado como 'Preço'")
            elif 'MAIS' in col_upper and 'BARATO' in col_upper:
                column_mapping['Preço_Concorrente'] = col
                print(f"  ✅ Mapeado como 'Preço_Concorrente'")
        
        print(f"\n🔗 MAPEAMENTO FINAL:")
        for standard_name, original_name in column_mapping.items():
            print(f"  {standard_name} ← {original_name}")
        
        # Rename columns
        df.rename(columns={v: k for k, v in column_mapping.items()}, inplace=True)
        
        # Check essential columns
        essential_cols = ['Produto', 'Status', 'Preço']
        missing_cols = [col for col in essential_cols if col not in df.columns]
        
        if missing_cols:
            return {"error": f"Colunas essenciais faltando: {missing_cols}. Mapeamento atual: {column_mapping}"}
        
        print(f"✅ Todas as colunas essenciais encontradas!")
        
        # Convert prices
        print(f"\n💰 CONVERTENDO PREÇOS...")
        price_columns = ['Preço', 'Preço_Concorrente']
        
        for col in price_columns:
            if col in df.columns:
                print(f"🔄 Convertendo: {col}")
                original_sample = df[col].head(3).tolist()
                df[col] = df[col].apply(convert_brazilian_price)
                converted_sample = df[col].head(3).tolist()
                print(f"  Exemplo: {original_sample} → {converted_sample}")
        
        # Clean status and ranking
        if 'Status' in df.columns:
            df['Status'] = df['Status'].astype(str).str.strip().str.upper()
        
        if 'Ranking' in df.columns:
            df['Ranking'] = pd.to_numeric(df['Ranking'], errors='coerce')
        
        # Create suggestions
        print(f"\n🎯 CRIANDO SUGESTÕES...")
        suggestions = []
        
        # Filter products with status GANHANDO
        if 'Status' in df.columns:
            ganhando_df = df[df['Status'] == 'GANHANDO'].copy()
            print(f"🏆 Produtos GANHANDO encontrados: {len(ganhando_df)}")
            
            if len(ganhando_df) > 0:
                print(f"📋 AMOSTRA DE PRODUTOS GANHANDO:")
                for i in range(min(3, len(ganhando_df))):
                    row = ganhando_df.iloc[i]
                    print(f"  {i+1}. {row.get('Produto', 'N/A')} - R$ {row.get('Preço', 0)} (Status: {row.get('Status', 'N/A')})")
                
                for idx, row in ganhando_df.iterrows():
                    produto = row.get('Produto', f'Produto_{idx}')
                    preco_atual = row.get('Preço', 0)
                    preco_concorrente = row.get('Preço_Concorrente', 0)
                    lojista = row.get('Lojista', 'N/A')
                    ranking = row.get('Ranking', 0)
                    
                    print(f"  📝 Processando: {produto} - Preço: {preco_atual} - Concorrente: {preco_concorrente}")
                    
                    if preco_atual > 0 and preco_concorrente > 0:
                        # Strategy: 95% of competitor price
                        preco_sugerido = round(preco_concorrente * 0.95, 2)
                        
                        if preco_sugerido > preco_atual:
                            valor_ajuste = preco_sugerido - preco_atual
                            percentual_ajuste = (valor_ajuste / preco_atual) * 100
                            
                            suggestions.append({
                                'Produto': str(produto)[:100],
                                'Lojista': str(lojista)[:50],
                                'Ranking': int(ranking) if ranking else 0,
                                'Preço_Atual': float(preco_atual),
                                'Preço_Concorrente': float(preco_concorrente),
                                'Preço_Sugerido': float(preco_sugerido),
                                'Valor_Ajuste': float(round(valor_ajuste, 2)),
                                'Percentual_Ajuste': float(round(percentual_ajuste, 2)),
                                'Margem_Extra_RS': float(round(valor_ajuste, 2)),
                                'Status': 'GANHANDO',
                                'Tipo_Ajuste': 'Proteção da Margem',
                                'Estrategia': '5% abaixo do concorrente'
                            })
                            print(f"    ✅ Sugestão criada: +R$ {valor_ajuste:.2f}")
                        else:
                            # Produto já bem posicionado
                            suggestions.append({
                                'Produto': str(produto)[:100],
                                'Lojista': str(lojista)[:50],
                                'Ranking': int(ranking) if ranking else 0,
                                'Preço_Atual': float(preco_atual),
                                'Preço_Concorrente': float(preco_concorrente),
                                'Preço_Sugerido': float(preco_atual),
                                'Valor_Ajuste': 0.0,
                                'Percentual_Ajuste': 0.0,
                                'Margem_Extra_RS': 0.0,
                                'Status': 'GANHANDO',
                                'Tipo_Ajuste': 'Manter Preço',
                                'Estrategia': 'Preço ótimo'
                            })
                            print(f"    ✅ Manter preço atual")
                    else:
                        print(f"    ❌ Preços inválidos (atual: {preco_atual}, concorrente: {preco_concorrente})")
        
        print(f"\n💡 TOTAL DE SUGESTÕES CRIADAS: {len(suggestions)}")
        
        # Sort by highest margin gain
        suggestions = sorted(suggestions, key=lambda x: x.get('Margem_Extra_RS', 0), reverse=True)
        
        # Calculate insights
        total_ganho = sum(s['Margem_Extra_RS'] for s in suggestions)
        produtos_com_oportunidade = len([s for s in suggestions if s['Valor_Ajuste'] > 0])
        
        ml_insights = {
            'total_produtos_analisados': len(df),
            'produtos_ganhando': len(ganhando_df) if 'ganhando_df' in locals() else 0,
            'produtos_com_oportunidade_margem': produtos_com_oportunidade,
            'sugestoes_criadas': len(suggestions),
            'ganho_potencial_total_rs': round(total_ganho, 2),
            'ganho_medio_por_produto': round(total_ganho / max(len(suggestions), 1), 2),
            'estrategia': 'Proteção de margem para produtos líderes',
            'metodo': 'Colunas corretas da segunda linha'
        }
        
        print(f"\n🎊 RESULTADO FINAL:")
        print(f"  📊 {len(df)} produtos analisados")
        print(f"  🏆 {ml_insights['produtos_ganhando']} produtos GANHANDO")
        print(f"  💡 {len(suggestions)} sugestões")
        print(f"  💰 R$ {total_ganho:.2f} ganho potencial")
        
        return suggestions, ml_insights
        
    except Exception as e:
        error_msg = f"Erro na análise: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {"error": error_msg}

@app.route('/')
def health_check():
    return jsonify({
        'status': 'Servidor com Colunas Corretas - OK',
        'version': '2.0',
        'colunas_esperadas': [
            'Produtos Disponíveis (segunda linha)',
            'STATUS (segunda linha)',
            'RANKING (segunda linha)', 
            'LOJISTA (segunda linha)',
            'PRECO (segunda linha)',
            'MAIS BARATO (segunda linha)'
        ],
        'message': 'Procurando colunas na segunda linha do CSV'
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    print("\n🔥 RECEBENDO REQUISIÇÃO DE ANÁLISE...")
    
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio.'}), 400
    
    print(f"📁 Arquivo recebido: {file.filename}")
    
    try:
        # Read file with proper encoding
        raw_bytes = file.read()
        print(f"📊 Tamanho do arquivo: {len(raw_bytes)} bytes")
        
        # Try different encodings
        text = None
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                text = raw_bytes.decode(encoding)
                print(f"✅ Encoding detectado: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if text is None:
            return jsonify({'error': 'Não foi possível decodificar o arquivo'}), 400
        
        # Analyze CSV
        result = analyze_csv_with_correct_columns(text)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify(result), 400
        
        suggestions, ml_insights = result
        
        response_data = {
            'data': suggestions,
            'ml_insights': ml_insights,
            'status_counts': {'GANHANDO': ml_insights.get('produtos_ganhando', 0)}
        }
        
        print(f"✅ Resposta enviada: {len(suggestions)} sugestões")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Erro no servidor: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎯 SERVIDOR COM COLUNAS CORRETAS")
    print("📋 Procura colunas na SEGUNDA linha do CSV:")
    print("   • Produtos Disponíveis")
    print("   • STATUS") 
    print("   • RANKING")
    print("   • LOJISTA")
    print("   • PRECO")
    print("   • MAIS BARATO")
    print("="*70)
    print("🌐 Iniciando na porta 5001...")
    
    app.run(host='127.0.0.1', port=5001, debug=True)
