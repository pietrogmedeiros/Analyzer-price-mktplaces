"""
🚀 SERVIDOR DEBUG ESPECÍFICO - PARA ENTENDER PROBLEMA DAS COLUNAS
"""

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import io

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/analyze', methods=['POST'])
def analyze():
    print("\n🔥 ANALISANDO ESTRUTURA DO CSV...")
    
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio.'}), 400
    
    print(f"📁 Arquivo: {file.filename}")
    
    try:
        raw_bytes = file.read()
        print(f"📊 Tamanho: {len(raw_bytes)} bytes")
        
        # Decode
        text = raw_bytes.decode('utf-8-sig')
        print(f"✅ Encoding: utf-8-sig")
        
        # Analyze structure
        lines = text.strip().split('\n')
        print(f"📝 Total de linhas: {len(lines)}")
        
        print(f"\n🔍 ESTRUTURA DETALHADA:")
        for i, line in enumerate(lines[:10]):
            line_clean = line.strip()
            print(f"  Linha {i}: {repr(line_clean)}")
            if ';' in line_clean:
                parts = line_clean.split(';')
                print(f"    → {len(parts)} colunas: {parts}")
            print()
        
        # Try different separators
        print(f"🔧 ANÁLISE DE SEPARADORES:")
        first_line = lines[0] if lines else ""
        print(f"  Ponto-e-vírgula (;): {first_line.count(';')}")
        print(f"  Vírgula (,): {first_line.count(',')}")
        print(f"  Tab: {first_line.count(chr(9))}")
        
        # Try reading as CSV
        separator = ';'
        
        print(f"\n📊 TENTANDO PANDAS COM SEPARADOR '{separator}':")
        
        # Method 1: Read normally
        print("🔄 Método 1 - Header na linha 0:")
        try:
            df1 = pd.read_csv(io.StringIO(text), sep=separator, decimal=',')
            print(f"  ✅ Sucesso: {df1.shape}")
            print(f"  📋 Colunas: {list(df1.columns)}")
            print(f"  🔍 Primeira linha de dados: {df1.iloc[0].tolist() if len(df1) > 0 else 'Vazio'}")
        except Exception as e:
            print(f"  ❌ Falhou: {e}")
        
        # Method 2: Skip first row
        print("\n🔄 Método 2 - Header na linha 1 (skiprows=1):")
        try:
            df2 = pd.read_csv(io.StringIO(text), sep=separator, skiprows=1, decimal=',')
            print(f"  ✅ Sucesso: {df2.shape}")
            print(f"  📋 Colunas: {list(df2.columns)}")
            print(f"  🔍 Primeira linha de dados: {df2.iloc[0].tolist() if len(df2) > 0 else 'Vazio'}")
        except Exception as e:
            print(f"  ❌ Falhou: {e}")
        
        # Manual analysis
        print(f"\n🔍 ANÁLISE MANUAL DAS LINHAS:")
        if len(lines) >= 2:
            line0_parts = lines[0].split(separator)
            line1_parts = lines[1].split(separator)
            
            print(f"  Linha 0 ({len(line0_parts)} partes): {line0_parts}")
            print(f"  Linha 1 ({len(line1_parts)} partes): {line1_parts}")
            
            # Check which looks more like a header
            def looks_like_header(parts):
                return any(word.upper() in ['PRODUTO', 'STATUS', 'PRECO', 'PREÇO', 'LOJISTA', 'RANKING'] for word in parts)
            
            def looks_like_data(parts):
                return any(part.replace(',', '.').replace('.', '').isdigit() for part in parts)
            
            line0_is_header = looks_like_header(line0_parts)
            line0_is_data = looks_like_data(line0_parts)
            line1_is_header = looks_like_header(line1_parts)
            line1_is_data = looks_like_data(line1_parts)
            
            print(f"  Linha 0 - Parece header: {line0_is_header}, Parece dados: {line0_is_data}")
            print(f"  Linha 1 - Parece header: {line1_is_header}, Parece dados: {line1_is_data}")
        
        return jsonify({
            'debug': 'Análise completa nos logs do servidor',
            'lines_count': len(lines),
            'first_line': lines[0] if lines else '',
            'separator_analysis': {
                'semicolon': first_line.count(';'),
                'comma': first_line.count(','),
                'tab': first_line.count('\t')
            }
        })
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/')
def health():
    return jsonify({'status': 'Debug Server para análise de CSV'})

if __name__ == '__main__':
    print("🔍 SERVIDOR DEBUG - ANÁLISE DE ESTRUTURA CSV")
    print("🌐 Porta 5001")
    app.run(host='127.0.0.1', port=5001, debug=True)
