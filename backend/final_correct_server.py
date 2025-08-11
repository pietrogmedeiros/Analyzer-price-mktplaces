"""
🚀 SERVIDOR FINAL CORRIGIDO - COLUNAS CORRETAS
Procura exatamente pelas colunas que o usuário especificou
"""

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

print("🚀 SERVIDOR FINAL CORRIGIDO INICIANDO...")

def convert_brazilian_price(price_str):
    """Converte preços no formato brasileiro para float"""
    if pd.isna(price_str) or price_str == '' or price_str is None:
        return 0.0
    
    try:
        price_str = str(price_str).strip()
        price_str = price_str.replace('"', '').replace("'", '').strip()
        
        if not price_str or price_str.lower() in ['nan', 'null', 'none']:
            return 0.0
        
        # Remove currency symbols
        price_str = price_str.replace('R$', '').replace('$', '').strip()
        
        # Handle percentage
        if '%' in price_str:
            price_str = price_str.replace('%', '')
        
        # Brazilian format: 1.234,56 -> 1234.56
        if ',' in price_str:
            parts = price_str.split(',')
            if len(parts) == 2 and len(parts[1]) <= 3:
                integer_part = parts[0].replace('.', '')
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

def analyze_csv_correct_columns(csv_content):
    """Análise do CSV procurando pelas colunas corretas especificadas pelo usuário"""
    
    print("\n" + "="*80)
    print("🔍 ANÁLISE COM COLUNAS CORRETAS ESPECIFICADAS")
    print("="*80)
    
    try:
        lines = csv_content.strip().split('\n')
        print(f"📝 Total de linhas no arquivo: {len(lines)}")
        
        # Show first few lines for debugging
        print("\n🔍 PRIMEIRAS 5 LINHAS:")
        for i, line in enumerate(lines[:5]):
            print(f"  [{i}]: {repr(line[:150])}")
        
        # Detect separator
        first_data_line = lines[1] if len(lines) > 1 else lines[0]
        separators = {';': first_data_line.count(';'), 
                     ',': first_data_line.count(','),
                     '\t': first_data_line.count('\t'),
                     '|': first_data_line.count('|')}
        
        separator = max(separators.items(), key=lambda x: x[1])[0]
        print(f"🔧 Separador detectado: '{separator}' ({separators[separator]} ocorrências)")
        
        # Try reading CSV with different approaches
        df = None
        
        # Method 1: Try reading with skiprows=0 (header on first line)
        try:
            df = pd.read_csv(io.StringIO(csv_content), sep=separator, skiprows=0, decimal=',', encoding='utf-8')
            print(f"✅ Método 1 (header linha 0): {df.shape[0]} linhas, {df.shape[1]} colunas")
            
            # Check if first row looks like actual data (not header)
            first_row_values = df.iloc[0].tolist() if len(df) > 0 else []
            looks_like_data = any(str(val).replace(',', '.').replace('.', '').isdigit() for val in first_row_values if pd.notna(val))
            
            if looks_like_data:
                print("⚠️ Primeira linha parece ser dados, não header. Tentando método 2...")
                raise Exception("Header provavelmente não está na primeira linha")
                
        except Exception as e:
            print(f"❌ Método 1 falhou: {e}")
            
            # Method 2: Try reading with skiprows=1 (header on second line)
            try:
                df = pd.read_csv(io.StringIO(csv_content), sep=separator, skiprows=1, decimal=',', encoding='utf-8')
                print(f"✅ Método 2 (header linha 1): {df.shape[0]} linhas, {df.shape[1]} colunas")
            except Exception as e2:
                print(f"❌ Método 2 falhou: {e2}")
                
                # Method 3: Manual parsing - try line 0 as header
                try:
                    header_line = [col.strip().replace('"', '') for col in lines[0].split(separator)]
                    data_lines = []
                    for line in lines[1:]:
                        if line.strip():
                            row = [col.strip().replace('"', '') for col in line.split(separator)]
                            while len(row) < len(header_line):
                                row.append('')
                            data_lines.append(row[:len(header_line)])
                    
                    df = pd.DataFrame(data_lines, columns=header_line)
                    print(f"✅ Método 3 manual (linha 0): {df.shape[0]} linhas, {df.shape[1]} colunas")
                except Exception as e3:
                    print(f"❌ Método 3 falhou: {e3}")
                    
                    # Method 4: Manual parsing - try line 1 as header
                    try:
                        header_line = [col.strip().replace('"', '') for col in lines[1].split(separator)]
                        data_lines = []
                        for line in lines[2:]:
                            if line.strip():
                                row = [col.strip().replace('"', '') for col in line.split(separator)]
                                while len(row) < len(header_line):
                                    row.append('')
                                data_lines.append(row[:len(header_line)])
                        
                        df = pd.DataFrame(data_lines, columns=header_line)
                        print(f"✅ Método 4 manual (linha 1): {df.shape[0]} linhas, {df.shape[1]} colunas")
                    except Exception as e4:
                        print(f"❌ Método 4 falhou: {e4}")
                        raise Exception("Todos os métodos de leitura falharam")
        
        print(f"\n📊 COLUNAS ORIGINAIS DO CSV:")
        for i, col in enumerate(df.columns):
            print(f"  [{i}]: '{col}'")
        
        # Clean column names
        df.columns = [str(col).replace('\ufeff', '').strip() for col in df.columns]
        
        print(f"\n📊 COLUNAS APÓS LIMPEZA:")
        for i, col in enumerate(df.columns):
            print(f"  [{i}]: '{col}'")
        
        # Map columns to the exact names specified by user
        column_map = {}
        
        # Exact mapping based on user specification
        expected_columns = [
            'PRODUTO', 'MARCA', 'N° DE LOJAS', 'MAIS BARATO', 'STATUS', 
            'CÓDIGO CLUSTER', 'CÓDIGO INTERNO', 'RANKING', 'LOJISTA', 
            'SELLERS', 'PREÇO', 'DIFERENÇA', 'PERCENTUAL'
        ]
        
        for col in df.columns:
            col_upper = col.upper()
            col_clean = col_upper.replace('Nº', 'N°').replace('NUMERO', 'N°').replace('NUM', 'N°')
            
            if 'PRODUTO' in col_upper:
                column_map['Produto'] = col
            elif 'MAIS BARATO' in col_clean or 'MAISBARATO' in col_clean:
                column_map['Preço_Concorrente'] = col
            elif 'STATUS' in col_upper:
                column_map['Status'] = col
            elif 'RANKING' in col_upper:
                column_map['Ranking'] = col
            elif 'LOJISTA' in col_upper:
                column_map['Lojista'] = col
            elif 'PREÇO' in col_upper or 'PRECO' in col_upper:
                column_map['Preço'] = col
            elif 'DIFERENÇA' in col_upper or 'DIFERENCA' in col_upper:
                column_map['Diferença'] = col
            elif 'PERCENTUAL' in col_upper:
                column_map['Percentual'] = col
        
        print(f"\n🔗 MAPEAMENTO DE COLUNAS ENCONTRADO:")
        for key, value in column_map.items():
            print(f"  {key} → {value}")
        
        # Rename columns
        df.rename(columns={v: k for k, v in column_map.items()}, inplace=True)
        
        # Check essential columns
        essential_cols = ['Produto', 'Preço', 'Status']
        missing_cols = [col for col in essential_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Colunas essenciais faltando: {missing_cols}")
            print(f"📋 Colunas disponíveis: {list(df.columns)}")
            return {"error": f"Colunas essenciais não encontradas: {missing_cols}. Disponíveis: {list(df.columns)}"}
        
        print(f"✅ Colunas essenciais encontradas!")
        
        # Show sample data
        print(f"\n🔍 AMOSTRA DOS DADOS (3 primeiras linhas):")
        for i in range(min(3, len(df))):
            row_data = {}
            for col in ['Produto', 'Status', 'Lojista', 'Preço', 'Preço_Concorrente']:
                if col in df.columns:
                    row_data[col] = df.iloc[i][col]
            print(f"  Linha {i}: {row_data}")
        
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
        
        # Clean status
        if 'Status' in df.columns:
            df['Status'] = df['Status'].astype(str).str.strip().str.upper()
            status_counts = df['Status'].value_counts()
            print(f"\n📊 CONTAGEM DE STATUS:")
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
        
        # Create suggestions
        print(f"\n🎯 CRIANDO SUGESTÕES DE OTIMIZAÇÃO...")
        suggestions = []
        
        # Filter products with status GANHANDO
        ganhando_df = df[df['Status'] == 'GANHANDO'].copy() if 'Status' in df.columns else df.copy()
        print(f"🏆 Produtos GANHANDO encontrados: {len(ganhando_df)}")
        
        if len(ganhando_df) > 0:
            print(f"📋 AMOSTRA DE PRODUTOS GANHANDO (5 primeiros):")
            for i in range(min(5, len(ganhando_df))):
                row = ganhando_df.iloc[i]
                print(f"  {i+1}. {row.get('Produto', 'N/A')} - R$ {row.get('Preço', 0)} vs R$ {row.get('Preço_Concorrente', 0)}")
            
            processed = 0
            for idx, row in ganhando_df.head(100).iterrows():
                produto = row.get('Produto', f'Produto_{idx}')
                preco_atual = row.get('Preço', 0)
                preco_concorrente = row.get('Preço_Concorrente', 0)
                lojista = row.get('Lojista', 'N/A')
                
                if preco_atual > 0 and preco_concorrente > 0:
                    # Strategy: 95% of competitor price
                    preco_sugerido = round(preco_concorrente * 0.95, 2)
                    
                    if preco_sugerido > preco_atual:
                        valor_ajuste = preco_sugerido - preco_atual
                        percentual_ajuste = (valor_ajuste / preco_atual) * 100
                        
                        suggestions.append({
                            'Produto': str(produto)[:100],
                            'Lojista': str(lojista)[:50],
                            'Preço_Atual': float(preco_atual),
                            'Preço_Concorrente': float(preco_concorrente),
                            'Preço_Sugerido': float(preco_sugerido),
                            'Valor_Ajuste': float(round(valor_ajuste, 2)),
                            'Percentual_Ajuste': float(round(percentual_ajuste, 2)),
                            'Margem_Extra_RS': float(round(valor_ajuste, 2)),
                            'Status': 'GANHANDO',
                            'Tipo_Ajuste': 'Proteção da Margem'
                        })
                        processed += 1
                    else:
                        # Product with good positioning
                        suggestions.append({
                            'Produto': str(produto)[:100],
                            'Lojista': str(lojista)[:50],
                            'Preço_Atual': float(preco_atual),
                            'Preço_Concorrente': float(preco_concorrente),
                            'Preço_Sugerido': float(preco_atual),
                            'Valor_Ajuste': 0.0,
                            'Percentual_Ajuste': 0.0,
                            'Margem_Extra_RS': 0.0,
                            'Status': 'GANHANDO',
                            'Tipo_Ajuste': 'Manter Preço'
                        })
                        processed += 1
                
                if processed >= 50:  # Limit to avoid timeout
                    break
        
        print(f"💡 Sugestões criadas: {len(suggestions)}")
        
        if len(suggestions) > 0:
            print(f"🔍 PRIMEIRAS 3 SUGESTÕES:")
            for i, sugg in enumerate(suggestions[:3]):
                print(f"  {i+1}. {sugg['Produto']} - Atual: R${sugg['Preço_Atual']} → Sugerido: R${sugg['Preço_Sugerido']} (Ganho: R${sugg['Margem_Extra_RS']})")
        
        # Calculate insights
        total_ganho = sum(s['Margem_Extra_RS'] for s in suggestions)
        produtos_com_oportunidade = len([s for s in suggestions if s['Valor_Ajuste'] > 0])
        
        ml_insights = {
            'total_produtos_analisados': len(df),
            'produtos_ganhando': len(ganhando_df),
            'produtos_com_oportunidade_margem': produtos_com_oportunidade,
            'sugestoes_criadas': len(suggestions),
            'ganho_potencial_total_rs': round(total_ganho, 2),
            'ganho_medio_por_produto': round(total_ganho / max(len(suggestions), 1), 2),
            'estrategia': 'Otimização baseada nas colunas corretas especificadas'
        }
        
        print(f"\n🎊 RESULTADO FINAL:")
        print(f"  📊 {len(df)} produtos analisados")
        print(f"  🏆 {len(ganhando_df)} produtos GANHANDO")
        print(f"  💡 {len(suggestions)} sugestões")
        print(f"  💰 R$ {total_ganho:.2f} ganho potencial")
        print(f"  🎯 {produtos_com_oportunidade} produtos com oportunidade")
        
        return suggestions, ml_insights
        
    except Exception as e:
        error_msg = f"Erro na análise: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {"error": error_msg}

@app.route('/')
def health_check():
    return jsonify({
        'status': 'Servidor Final Corrigido - Colunas Específicas',
        'version': '2.0',
        'timestamp': '2025-08-11',
        'message': 'Backend procurando pelas colunas corretas!'
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    print("\n🔥 RECEBENDO REQUISIÇÃO DE ANÁLISE COM COLUNAS CORRETAS...")
    
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
        result = analyze_csv_correct_columns(text)
        
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
    print("\n" + "="*60)
    print("🚀 SERVIDOR FINAL CORRIGIDO")
    print("🎯 Procurando pelas colunas corretas:")
    print("   - PRODUTO → Produto")
    print("   - MAIS BARATO → Preço_Concorrente") 
    print("   - STATUS → Status")
    print("   - LOJISTA → Lojista")
    print("   - PREÇO → Preço")
    print("   - RANKING → Ranking")
    print("="*60)
    print("🌐 Iniciando na porta 5001...")
    
    app.run(host='127.0.0.1', port=5001, debug=True)
