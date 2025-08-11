"""
🚀 SERVIDOR CORRIGIDO - COLUNAS CERTAS
Análise das colunas corretas da segunda linha do CSV
"""

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

print("🚀 SERVIDOR CORRIGIDO - COLUNAS CERTAS")

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
        
        # Handle percentage
        if '%' in price_str:
            price_str = price_str.replace('%', '')
        
        # Brazilian format: 1.234,56 -> 1234.56
        if ',' in price_str and '.' in price_str:
            # Format like 1.234,56
            parts = price_str.rsplit(',', 1)  # Split from the right
            if len(parts) == 2 and len(parts[1]) <= 3:
                integer_part = parts[0].replace('.', '')  # Remove thousand separators
                decimal_part = parts[1]
                price_str = f"{integer_part}.{decimal_part}"
        elif ',' in price_str:
            # Simple comma as decimal separator
            price_str = price_str.replace(',', '.')
        
        # Remove any remaining non-numeric characters except . and -
        cleaned = ''
        for char in price_str:
            if char.isdigit() or char in '.-':
                cleaned += char
        
        if cleaned and cleaned not in ['-', '.', '-.']:
            return float(cleaned)
        
        return 0.0
        
    except Exception as e:
        print(f"⚠️ Erro ao converter preço '{price_str}': {e}")
        return 0.0

def analyze_csv_corrected(csv_content):
    """Análise corrigida do CSV com as colunas certas"""
    
    print("\n" + "="*80)
    print("🔍 ANÁLISE CORRIGIDA - COLUNAS DA SEGUNDA LINHA")
    print("="*80)
    
    try:
        # Read CSV lines
        lines = csv_content.strip().split('\n')
        print(f"📝 Total de linhas no arquivo: {len(lines)}")
        
        # Show first few lines for debugging
        print("\n🔍 PRIMEIRAS 5 LINHAS:")
        for i, line in enumerate(lines[:5]):
            print(f"  [{i}]: {repr(line)}")
        
        # *** CORREÇÃO: Usar a SEGUNDA linha como header ***
        if len(lines) < 2:
            raise Exception("CSV deve ter pelo menos 2 linhas")
        
        # A segunda linha (índice 1) contém os headers reais
        header_line = lines[1] if len(lines) > 1 else lines[0]
        
        # Detect separator from header line
        separators = {';': header_line.count(';'), 
                     ',': header_line.count(','),
                     '\t': header_line.count('\t'),
                     '|': header_line.count('|')}
        
        separator = max(separators.items(), key=lambda x: x[1])[0]
        print(f"🔧 Separador detectado: '{separator}' ({separators[separator]} ocorrências)")
        print(f"📋 Header line (linha 1): {repr(header_line)}")
        
        # Parse header
        headers = [col.strip().replace('"', '') for col in header_line.split(separator)]
        print(f"📊 Headers extraídos: {headers}")
        
        # Parse data from line 2 onwards (skip line 0 and 1)
        data_rows = []
        for i, line in enumerate(lines[2:], start=2):  # Start from line 2
            if line.strip():
                row = [col.strip().replace('"', '') for col in line.split(separator)]
                # Ensure same number of columns
                while len(row) < len(headers):
                    row.append('')
                if len(row) > len(headers):
                    row = row[:len(headers)]
                data_rows.append(row)
                
                # Show first few rows for debugging
                if i < 7:  # Show first 5 data rows
                    print(f"  Data row {i}: {row}")
        
        print(f"📊 Total data rows parsed: {len(data_rows)}")
        
        # Create DataFrame
        if not data_rows:
            raise Exception("Nenhum dado encontrado após o header")
            
        df = pd.DataFrame(data_rows, columns=headers)
        print(f"\n📊 DATAFRAME CRIADO:")
        print(f"  Dimensões: {df.shape}")
        print(f"  Colunas: {list(df.columns)}")
        
        # Show sample data
        print(f"\n🔍 AMOSTRA DOS DADOS (primeiras 3 linhas):")
        for i in range(min(3, len(df))):
            row_dict = dict(df.iloc[i])
            print(f"  Linha {i}: {row_dict}")
        
        # *** CORREÇÃO: Mapear as colunas corretas ***
        # Baseado no que vimos: "Produtos Disponíveis;STATUS;RANKING;LOJISTA;PRECO;MAIS BARATO"
        column_map = {}
        
        for col in df.columns:
            col_upper = col.upper().strip()
            print(f"🔍 Analisando coluna: '{col}' -> '{col_upper}'")
            
            if 'PRODUTO' in col_upper or col_upper == 'PRODUTOS DISPONÍVEIS':
                column_map['Produto'] = col
                print(f"  ✅ Mapeada como 'Produto'")
            elif col_upper == 'STATUS':
                column_map['Status'] = col
                print(f"  ✅ Mapeada como 'Status'")
            elif col_upper == 'RANKING':
                column_map['Ranking'] = col
                print(f"  ✅ Mapeada como 'Ranking'")
            elif col_upper == 'LOJISTA':
                column_map['Lojista'] = col
                print(f"  ✅ Mapeada como 'Lojista'")
            elif col_upper == 'PRECO':
                column_map['Preço'] = col
                print(f"  ✅ Mapeada como 'Preço'")
            elif 'MAIS BARATO' in col_upper or 'MAISBARATO' in col_upper:
                column_map['Preço_Concorrente'] = col
                print(f"  ✅ Mapeada como 'Preço_Concorrente'")
        
        print(f"\n🔗 MAPEAMENTO FINAL:")
        for key, value in column_map.items():
            print(f"  {key} → {value}")
        
        # Rename columns
        df_renamed = df.rename(columns={v: k for k, v in column_map.items()})
        print(f"\n📋 Colunas após rename: {list(df_renamed.columns)}")
        
        # Check essential columns
        essential_cols = ['Produto', 'Preço', 'Status']
        available_cols = [col for col in essential_cols if col in df_renamed.columns]
        missing_cols = [col for col in essential_cols if col not in df_renamed.columns]
        
        print(f"✅ Colunas essenciais disponíveis: {available_cols}")
        if missing_cols:
            print(f"❌ Colunas essenciais faltando: {missing_cols}")
            return {"error": f"Colunas essenciais faltando: {missing_cols}. Disponíveis: {list(df_renamed.columns)}"}
        
        # Convert prices
        print(f"\n💰 CONVERTENDO PREÇOS...")
        price_columns = ['Preço', 'Preço_Concorrente']
        
        for col in price_columns:
            if col in df_renamed.columns:
                print(f"🔄 Convertendo: {col}")
                original_sample = df_renamed[col].head(3).tolist()
                df_renamed[col] = df_renamed[col].apply(convert_brazilian_price)
                converted_sample = df_renamed[col].head(3).tolist()
                print(f"  Exemplo: {original_sample} → {converted_sample}")
        
        # Clean status
        if 'Status' in df_renamed.columns:
            df_renamed['Status'] = df_renamed['Status'].astype(str).str.strip().str.upper()
            print(f"🔧 Status values: {df_renamed['Status'].unique()}")
        
        # Create suggestions
        print(f"\n🎯 CRIANDO SUGESTÕES...")
        suggestions = []
        
        # Filter products with status GANHANDO
        if 'Status' in df_renamed.columns:
            ganhando_df = df_renamed[df_renamed['Status'] == 'GANHANDO'].copy()
            print(f"🏆 Produtos GANHANDO encontrados: {len(ganhando_df)}")
            
            if len(ganhando_df) > 0:
                print(f"📋 Detalhes dos produtos GANHANDO:")
                for idx, row in ganhando_df.head(5).iterrows():
                    produto = row.get('Produto', 'N/A')
                    preco = row.get('Preço', 0)
                    status = row.get('Status', 'N/A')
                    print(f"  - {produto}: R$ {preco} (Status: {status})")
                
                # Create suggestions for GANHANDO products
                for idx, row in ganhando_df.iterrows():
                    produto = row.get('Produto', f'Produto_{idx}')
                    preco_atual = row.get('Preço', 0)
                    preco_concorrente = row.get('Preço_Concorrente', 0)
                    lojista = row.get('Lojista', 'N/A')
                    
                    print(f"🔍 Processando: {produto} - Preço atual: {preco_atual}, Concorrente: {preco_concorrente}")
                    
                    if preco_atual > 0 and preco_concorrente > 0:
                        # Strategy: 95% of competitor price
                        preco_sugerido = round(preco_concorrente * 0.95, 2)
                        
                        if preco_sugerido > preco_atual:
                            valor_ajuste = preco_sugerido - preco_atual
                            percentual_ajuste = (valor_ajuste / preco_atual) * 100
                            
                            suggestions.append({
                                'Produto': str(produto)[:100],  # Limit length
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
                            print(f"  ✅ Sugestão criada: +R$ {valor_ajuste:.2f}")
                        else:
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
                                'Tipo_Ajuste': 'Manter Preço - Já bem posicionado'
                            })
                            print(f"  ✅ Produto já bem posicionado")
                    else:
                        print(f"  ⚠️ Preços inválidos - pulando")
        else:
            print(f"❌ Coluna 'Status' não encontrada")
        
        print(f"💡 Total de sugestões criadas: {len(suggestions)}")
        
        # Calculate insights
        total_ganho = sum(s['Margem_Extra_RS'] for s in suggestions)
        produtos_com_oportunidade = len([s for s in suggestions if s['Valor_Ajuste'] > 0])
        
        ml_insights = {
            'total_produtos_analisados': len(df_renamed),
            'produtos_ganhando': len(ganhando_df) if 'ganhando_df' in locals() else 0,
            'produtos_com_oportunidade_margem': produtos_com_oportunidade,
            'sugestoes_criadas': len(suggestions),
            'ganho_potencial_total_rs': round(total_ganho, 2),
            'ganho_medio_por_produto': round(total_ganho / max(len(suggestions), 1), 2),
            'estrategia': 'Análise corrigida - colunas da segunda linha',
            'metodo': 'Header da linha 1, dados da linha 2+'
        }
        
        print(f"\n🎊 RESULTADO FINAL:")
        print(f"  📊 {len(df_renamed)} produtos analisados")
        print(f"  🏆 {ml_insights.get('produtos_ganhando', 0)} produtos GANHANDO")
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
        'status': 'Servidor Corrigido - Colunas Certas',
        'version': '2.0',
        'timestamp': '2025-08-11',
        'message': 'Analisando colunas da segunda linha!'
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
        result = analyze_csv_corrected(text)
        
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
    print("🚀 SERVIDOR CORRIGIDO - COLUNAS CERTAS")
    print("🎯 Análise da segunda linha como header")
    print("📊 Dados a partir da terceira linha")
    print("💰 Sugestões de otimização corrigidas")
    print("="*60)
    print("🌐 Iniciando na porta 5001...")
    
    app.run(host='127.0.0.1', port=5001, debug=True)
