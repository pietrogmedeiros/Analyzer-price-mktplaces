import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import io

# Importações para Machine Learning
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np

app = Flask(__name__)
CORS(app) # Habilita CORS para permitir que o frontend (React) acesse a API

# Função para formatar valores monetários no padrão brasileiro (R$ 1.234,56)
# OBS: No JSON para o frontend, enviaremos os números brutos, pois a formatação
# será feita no JavaScript do React para melhor controle na UI.
def format_currency_br(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Função principal de análise (agora incorporada para ser usada pela rota Flask)
def analyze_webprice_data_internal(csv_content_stream):
    """
    Avalia o conteúdo de um arquivo CSV com informações de webprice,
    identifica produtos "Perdendo" e com oportunidade de aumento,
    sugere ajustes, e inclui um modelo de ML para aprendizado.

    Args:
        csv_content_stream: Um io.StringIO contendo o conteúdo do CSV.

    Returns:
        tuple: (list_of_results, ml_insights_dict)
               list_of_results: Lista de dicionários com o Top X produtos para ajuste.
               ml_insights_dict: Dicionário com insights do modelo de ML.
               Ou um dicionário de erro/mensagem.
    """
    ml_insights = {}

    try:
        # Lê o CSV com as configurações personalizadas
        df = pd.read_csv(csv_content_stream, sep=';', skiprows=[0], decimal=',')

        # Mapeia os nomes das colunas
        column_mapping = {
            "PRODUTO": "Produto",
            "STATUS": "Status",
            "LOJISTA": "Lojista",
            "PRECO": "Preço",
            "MAIS BARATO": "Preço_Concorrente",
            "DIFERENÇA": "Diferença_Raw_CSV",
            "PERCENTUAL": "Percentual_Raw_CSV"
        }
        df.rename(columns=column_mapping, inplace=True)

        required_columns = [
            'Produto', 'Status', 'Lojista', 'Preço',
            'Preço_Concorrente', 'Diferença_Raw_CSV', 'Percentual_Raw_CSV'
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {"error": f"Colunas essenciais ausentes após renomeio: {', '.join(missing_columns)}."}

        df['Preço'] = pd.to_numeric(df['Preço'], errors='coerce').fillna(0)
        df['Preço_Concorrente'] = pd.to_numeric(df['Preço_Concorrente'], errors='coerce').fillna(0)
        df['Diferença_Raw_CSV'] = pd.to_numeric(df['Diferença_Raw_CSV'], errors='coerce').fillna(0)
        df['Percentual_Raw_CSV'] = pd.to_numeric(df['Percentual_Raw_CSV'], errors='coerce').fillna(0)
        
        # Processamento para "ABAJAR PREÇO"
        df_abaixar = df[df['Status'].astype(str).str.lower() == 'perdendo'].copy()
        if not df_abaixar.empty:
            df_abaixar['Tipo_Ajuste'] = 'Abaixar Preço para Competitividade'
            df_abaixar['Sugestao_Preco'] = (df_abaixar['Preço_Concorrente'] * 0.99).round(2)
            df_abaixar['Prioridade_Valor'] = df_abaixar['Diferença_Raw_CSV'].abs()
            df_abaixar['Valor_Ajuste'] = (df_abaixar['Preço'] - df_abaixar['Sugestao_Preco']).abs().round(2)
            df_abaixar['Percentual_Ajuste'] = ((df_abaixar['Preço'] - df_abaixar['Sugestao_Preco']) / df_abaixar['Preço'] * 100).abs().round(2)
            df_abaixar['Status_Original'] = df_abaixar['Status']

        # Processamento para "AUMENTAR PREÇO" (Oportunidade de Margem)
        df_aumentar = df[
            (df['Preço'] < df['Preço_Concorrente']) &
            (df['Status'].astype(str).str.lower() != 'perdendo')
        ].copy()

        if not df_aumentar.empty:
            df_aumentar['Tipo_Ajuste'] = 'Oportunidade de Aumento de Preço'
            df_aumentar['Sugestao_Preco'] = (df_aumentar['Preço_Concorrente'] * 0.99).round(2)
            df_aumentar['Ganho_Margem_Diferenca'] = (df_aumentar['Preço_Concorrente'] - df_aumentar['Preço']).round(2)
            df_aumentar['Ganho_Margem_Percentual'] = ((df_aumentar['Ganho_Margem_Diferenca'] / df_aumentar['Preço']) * 100).round(2)
            
            df_aumentar['Prioridade_Valor'] = df_aumentar['Ganho_Margem_Diferenca'] 
            df_aumentar['Valor_Ajuste'] = df_aumentar['Ganho_Margem_Diferenca']
            df_aumentar['Percentual_Ajuste'] = df_aumentar['Ganho_Margem_Percentual']
            df_aumentar['Status_Original'] = df_aumentar['Status']

        # Concatena os DataFrames de ajustes
        common_cols = [
            'Produto', 'Lojista', 'Preço', 'Preço_Concorrente',
            'Sugestao_Preco', 'Tipo_Ajuste', 'Prioridade_Valor',
            'Valor_Ajuste', 'Percentual_Ajuste', 'Status_Original'
        ]
        
        final_df = pd.DataFrame(columns=common_cols)

        if not df_abaixar.empty:
            final_df = pd.concat([final_df, df_abaixar[common_cols]], ignore_index=True)
        
        if not df_aumentar.empty:
            final_df = pd.concat([final_df, df_aumentar[common_cols]], ignore_index=True)

        if final_df.empty:
            return {"message": "Nenhum produto encontrado para ajuste de preço (nem para abaixar, nem para aumentar)."}

        # Ajustar nomenclatura de Tipo_Ajuste para "Otimizar Margem"
        cond_otimizar = (final_df['Tipo_Ajuste'] == 'Oportunidade de Aumento de Preço') & \
                        (final_df['Status_Original'].astype(str).str.lower().isin(['ganhando', 'empatando', 'neutro', 'competitivo']))
        
        final_df.loc[cond_otimizar, 'Tipo_Ajuste'] = 'Otimizar Margem para Lucratividade'

        # ====================================================================
        # INÍCIO DA SEÇÃO DE MACHINE LEARNING
        # ====================================================================

        ml_df = final_df.copy()

        features = ['Preço', 'Preço_Concorrente', 'Valor_Ajuste', 'Percentual_Ajuste', 'Prioridade_Valor']
        target = 'Tipo_Ajuste'

        ml_df = ml_df.dropna(subset=features + [target])

        if ml_df.empty:
            ml_insights = {"message": "Dados insuficientes para treinar o modelo de ML após limpeza."}
        else:
            for feature in features:
                ml_df[feature] = pd.to_numeric(ml_df[feature], errors='coerce').fillna(0)
            
            le = LabelEncoder()
            ml_df['target_encoded'] = le.fit_transform(ml_df[target])

            X = ml_df[features]
            y = ml_df['target_encoded']

            if len(y.unique()) < 2 or len(X) < 2:
                ml_insights = {"message": "Apenas um tipo de ajuste ou dados insuficientes para treinar modelo de ML."}
            else:
                try:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
                except ValueError as e:
                    ml_insights = {"message": f"Não foi possível dividir os dados para ML: {e}. Pode ser que uma classe tenha poucas amostras."}
                    X_train, y_train = X, y

                if 'model' not in ml_insights: # If splitting was skipped or successful
                    model = DecisionTreeClassifier(random_state=42)
                    model.fit(X_train, y_train)

                    ml_insights = {
                        "status": "Modelo de ML treinado com sucesso!",
                        "features_usadas": features,
                        "classes_preditas": list(le.classes_),
                        "importancia_das_features": dict(zip(features, model.feature_importances_.round(4)))
                    }

        # ====================================================================
        # FIM DA SEÇÃO DE MACHINE LEARNING
        # ====================================================================

        final_df = final_df.sort_values(by='Prioridade_Valor', ascending=False)

        top_x_count = 20
        top_results = final_df.head(top_x_count)

        result_list = top_results[[
            'Produto', 'Tipo_Ajuste', 'Lojista', 'Preço', 'Preço_Concorrente',
            'Valor_Ajuste', 'Percentual_Ajuste', 'Sugestao_Preco', 'Status_Original'
        ]].to_dict(orient='records')

        return result_list, ml_insights # Retorna a lista de resultados e os insights ML

    except Exception as e:
        app.logger.error(f"Erro ao processar o CSV: {e}", exc_info=True)
        return {"error": f"Erro ao processar o CSV: {str(e)}"}


# Rota da API Flask
@app.route('/analyze_csv', methods=['POST'])
def analyze_csv():
    # Verifica se um arquivo foi enviado na requisição
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files['file']

    # Verifica se o nome do arquivo não está vazio
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    # Valida o tipo de arquivo
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Formato de arquivo inválido. Apenas arquivos CSV são aceitos."}), 400

    try:
        # Passa o conteúdo do arquivo para a função interna de análise
        analysis_output = analyze_webprice_data_internal(io.StringIO(file.stream.read().decode('utf-8')))

        # Verifica se analyze_webprice_data_internal retornou um erro ou mensagem
        if isinstance(analysis_output, dict) and ("error" in analysis_output or "message" in analysis_output):
            return jsonify(analysis_output), 400 if "error" in analysis_output else 200
        
        # Se tudo ocorreu bem, desempacota resultados e insights ML
        results, ml_insights = analysis_output

        # Retorna ambos em um único JSON para o frontend
        return jsonify({"results": results, "ml_insights": ml_insights}), 200

    except Exception as e:
        app.logger.error(f"Erro inesperado no servidor: {e}", exc_info=True)
        return jsonify({"error": f"Erro inesperado no servidor: {str(e)}"}), 500

# Para rodar localmente
if __name__ == '__main__':
    app.run(debug=True, port=5000)
