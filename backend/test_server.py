from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import io

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'status': 'running', 'message': 'Servidor ativo'})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nome de arquivo vazio'}), 400
        
        # Lê o arquivo CSV
        raw_bytes = file.read()
        try:
            text = raw_bytes.decode('utf-8-sig')
        except UnicodeDecodeError:
            text = raw_bytes.decode('latin-1', errors='ignore')
        
        # Processa CSV
        df = pd.read_csv(io.StringIO(text), sep=';')
        
        # Dados de exemplo com valores reais
        suggestions = []
        
        # Cria pelo menos 5 produtos de exemplo para testar
        for i in range(min(5, len(df))):
            suggestions.append({
                'Produto': f'Produto Teste {i+1}',
                'Status': 'GANHANDO',
                'Preço_Atual': 100.0 + i * 10,
                'Preço_Sugerido': 120.0 + i * 10,
                'Valor_Ajuste': 20.0,
                'Margem_Extra_RS': 20.0,
                'Percentual_Ajuste': 20.0,
                'Lojista': 'Teste Loja',
                'Preço_Concorrente': 130.0 + i * 10,
                'Estrategia': 'Teste de funcionamento'
            })
        
        result = {
            'data': suggestions,
            'ml_insights': {
                'total_produtos_analisados': len(suggestions),
                'produtos_com_oportunidade_margem': len(suggestions),
                'ganho_potencial_total_rs': 100.0,
                'ganho_medio_por_produto': 20.0,
                'strategy': 'Teste com dados fixos'
            },
            'status_counts': {'GANHANDO': len(suggestions)}
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 SERVIDOR DE TESTE ATIVO - PORTA 8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
