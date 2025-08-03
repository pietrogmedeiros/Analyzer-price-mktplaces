import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import io

# Importações para Machine Learning
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np

# 1. INICIALIZAÇÃO DO FLASK E CONFIGURAÇÃO DO CORS
app = Flask(__name__)
# Permite requisições da origem do seu frontend para TODAS as rotas
# Configurado para aceitar tanto desenvolvimento (5173) quanto produção (80)
CORS(app, resources={r"/*": {"origins": ["http://localhost", "http://localhost:5173", "http://127.0.0.1", "http://127.0.0.1:5173"]}})

# Função para formatar valores monetários (não usada na resposta da API, mas pode ser útil)
def format_currency_br(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função principal de análise
def analyze_webprice_data_internal(csv_content_stream):
    ml_insights = {}

    try:
        df = pd.read_csv(csv_content_stream, sep=';', skiprows=[0], decimal=',')
        column_mapping = {
            "PRODUTO": "Produto", "STATUS": "Status", "LOJISTA": "Lojista",
            "PRECO": "Preço", "MAIS BARATO": "Preço_Concorrente",
            "DIFERENÇA": "Diferença_Raw_CSV", "PERCENTUAL": "Percentual_Raw_CSV"
        }
        df.rename(columns=column_mapping, inplace=True)

        required_columns = [
            'Produto', 'Status', 'Lojista', 'Preço', 'Preço_Concorrente',
            'Diferença_Raw_CSV', 'Percentual_Raw_CSV'
        ]
        if any(col not in df.columns for col in required_columns):
            return {"error": "Colunas essenciais ausentes."}

        for col in ['Preço', 'Preço_Concorrente', 'Diferença_Raw_CSV', 'Percentual_Raw_CSV']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df_abaixar = df[df['Status'].astype(str).str.lower() == 'perdendo'].copy()
        if not df_abaixar.empty:
            df_abaixar['Tipo_Ajuste'] = 'Abaixar Preço'
            df_abaixar['Sugestao_Preco'] = (df_abaixar['Preço_Concorrente'] * 0.99).round(2)
            df_abaixar['Prioridade_Valor'] = df_abaixar['Diferença_Raw_CSV'].abs()
            df_abaixar['Valor_Ajuste'] = (df_abaixar['Preço'] - df_abaixar['Sugestao_Preco']).abs().round(2)
            df_abaixar['Percentual_Ajuste'] = ((df_abaixar['Preço'] - df_abaixar['Sugestao_Preco']) / df_abaixar['Preço'] * 100).abs().round(2)
            df_abaixar['Status_Original'] = df_abaixar['Status']
            
            # --- CORREÇÃO APLICADA AQUI ---
            df_abaixar = df_abaixar[df_abaixar['Percentual_Ajuste'] <= 3]

        df_aumentar = df[(df['Preço'] < df['Preço_Concorrente']) & (df['Status'].astype(str).str.lower() != 'perdendo')].copy()
        if not df_aumentar.empty:
            df_aumentar['Tipo_Ajuste'] = 'Otimizar Margem'
            df_aumentar['Sugestao_Preco'] = (df_aumentar['Preço_Concorrente'] * 0.99).round(2)
            df_aumentar['Prioridade_Valor'] = (df_aumentar['Preço_Concorrente'] - df_aumentar['Preço']).round(2)
            df_aumentar['Valor_Ajuste'] = df_aumentar['Prioridade_Valor']
            df_aumentar['Percentual_Ajuste'] = ((df_aumentar['Valor_Ajuste'] / df_aumentar['Preço']) * 100).round(2)
            df_aumentar['Status_Original'] = df_aumentar['Status']

            # --- CORREÇÃO APLICADA AQUI ---
            df_aumentar = df_aumentar[df_aumentar['Percentual_Ajuste'] <= 3]

        common_cols = ['Produto', 'Lojista', 'Preço', 'Preço_Concorrente', 'Sugestao_Preco', 'Tipo_Ajuste', 'Prioridade_Valor', 'Valor_Ajuste', 'Percentual_Ajuste', 'Status_Original']
        final_df = pd.DataFrame(columns=common_cols)
        if not df_abaixar.empty:
            final_df = pd.concat([final_df, df_abaixar[common_cols]], ignore_index=True)
        if not df_aumentar.empty:
            final_df = pd.concat([final_df, df_aumentar[common_cols]], ignore_index=True)

        if final_df.empty:
            return {"message": "Nenhum produto encontrado para ajuste dentro do limite de 3%."}

        ml_df = final_df.copy()
        features = ['Preço', 'Preço_Concorrente', 'Valor_Ajuste', 'Percentual_Ajuste', 'Prioridade_Valor']
        target = 'Tipo_Ajuste'
        ml_df = ml_df.dropna(subset=features + [target])

        if len(ml_df) > 1 and len(ml_df[target].unique()) > 1:
            le = LabelEncoder()
            ml_df['target_encoded'] = le.fit_transform(ml_df[target])
            X = ml_df[features]
            y = ml_df['target_encoded']
            try:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
                model = DecisionTreeClassifier(random_state=42).fit(X_train, y_train)
                ml_insights = {
                    "status": "Modelo treinado com sucesso!",
                    "features_usadas": features,
                    "classes_preditas": list(le.classes_),
                    "importancia_das_features": dict(zip(features, model.feature_importances_.round(4)))
                }
            except ValueError:
                 ml_insights = {"message": "Não foi possível dividir os dados para ML."}
        else:
            ml_insights = {"message": "Dados insuficientes para treinar o modelo."}

        final_df = final_df.sort_values(by='Prioridade_Valor', ascending=False)
        top_results = final_df.head(20)
        result_list = top_results.to_dict(orient='records')
        return result_list, ml_insights

    except Exception as e:
        print(f"Erro ao processar o CSV: {e}")
        return {"error": f"Erro ao processar o CSV: {str(e)}"}

@app.route('/analyze', methods=['POST'])
def analyze_csv_route():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Formato de arquivo inválido. Apenas CSV."}), 400

    try:
        csv_content = file.stream.read().decode('utf-8')
        analysis_output = analyze_webprice_data_internal(io.StringIO(csv_content))

        if isinstance(analysis_output, dict) and "error" in analysis_output:
            return jsonify(analysis_output), 400
        if isinstance(analysis_output, dict) and "message" in analysis_output:
            return jsonify(analysis_output), 200
        
        results, ml_insights = analysis_output

        summary_data = {
            "total_products": len(results),
            "average_price": pd.DataFrame(results)['Preço'].mean() if results else 0
        }
        
        return jsonify({"data": results, "summary": summary_data, "ml_insights": ml_insights})

    except Exception as e:
        print(f"Erro inesperado no servidor: {e}")
        return jsonify({"error": f"Erro inesperado no servidor: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "WebPrice Analyzer API está funcionando!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)