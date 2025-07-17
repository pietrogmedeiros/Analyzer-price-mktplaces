import pandas as pd
import os
import sys # Importado para ler argumentos da linha de comando
import glob # Novo import para encontrar arquivos por padrão

# Importações para Machine Learning
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np

# Função para formatar valores monetários no padrão brasileiro (R$ 1.234,56)
def format_currency_br(value):
    # Garante que o valor é um float e formata com 2 casas decimais.
    # Usa um "hack" comum: formata com separador de milhares padrão (vírgula) e decimal (ponto),
    # depois troca-os para o padrão brasileiro.
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def analyze_webprice_data(csv_filepath):
    """
    Avalia um arquivo CSV com informações de webprice,
    identifica produtos "Perdendo" (para baixar preço)
    e produtos com preço abaixo do concorrente (para aumentar preço),
    e sugere ajustes, e inclui um modelo de ML para aprendizado.

    Args:
        csv_filepath (str): Caminho para o arquivo CSV de entrada.

    Returns:
        tuple: (list, dict) com lista de dicionários do Top X produtos,
               e um dicionário com insights do ML, ou uma mensagem de erro/informação.
    """
    ml_insights = {} # Dicionário para armazenar os insights do ML

    if not os.path.exists(csv_filepath):
        return {"error": f"Arquivo CSV não encontrado: {csv_filepath}"}

    try:
        # Lê o CSV com as configurações do seu arquivo:
        # sep=';' para ponto e vírgula como separador
        # skiprows=[0] para pular a primeira linha (metadados como "Filtros")
        # decimal=',' para entender números com vírgula como separador decimal (e.g., 295,90)
        df = pd.read_csv(csv_filepath, sep=';', skiprows=[0], decimal=',')

        # Mapeia os nomes das colunas do seu CSV
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
            return {"error": f"Colunas essenciais ausentes após renomeio: {', '.join(missing_columns)}. "}

        df['Preço'] = pd.to_numeric(df['Preço'], errors='coerce').fillna(0)
        df['Preço_Concorrente'] = pd.to_numeric(df['Preço_Concorrente'], errors='coerce').fillna(0)
        df['Diferença_Raw_CSV'] = pd.to_numeric(df['Diferença_Raw_CSV'], errors='coerce').fillna(0)
        df['Percentual_Raw_CSV'] = pd.to_numeric(df['Percentual_Raw_CSV'], errors='coerce').fillna(0)
        
        # --- Processamento para "ABAJAR PREÇO" ---
        df_abaixar = df[df['Status'].astype(str).str.lower() == 'perdendo'].copy()

        if not df_abaixar.empty:
            df_abaixar['Tipo_Ajuste'] = 'Abaixar Preço para Competitividade'
            df_abaixar['Sugestao_Preco'] = (df_abaixar['Preço_Concorrente'] * 0.99).round(2)
            df_abaixar['Prioridade_Valor'] = df_abaixar['Diferença_Raw_CSV'].abs()
            df_abaixar['Valor_Ajuste'] = (df_abaixar['Preço'] - df_abaixar['Sugestao_Preco']).abs().round(2)
            df_abaixar['Percentual_Ajuste'] = ((df_abaixar['Preço'] - df_abaixar['Sugestao_Preco']) / df_abaixar['Preço'] * 100).abs().round(2)
            df_abaixar['Status_Original'] = df_abaixar['Status']


        # --- Processamento para "AUMENTAR PREÇO" ---
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

                if 'model' not in ml_insights:
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

        result = top_results[[
            'Produto', 'Tipo_Ajuste', 'Lojista', 'Preço', 'Preço_Concorrente',
            'Valor_Ajuste', 'Percentual_Ajuste', 'Sugestao_Preco', 'Status_Original'
        ]].to_dict(orient='records')

        return result, ml_insights

    except Exception as e:
        return {"error": f"Erro interno ao processar o CSV: {str(e)}"}

# Código de execução principal quando o script é rodado diretamente
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files_to_analyze = []

    # Verifica se um nome de arquivo foi passado como argumento
    if len(sys.argv) > 1:
        # User specified a particular file
        csv_file_name = sys.argv[1]
        csv_file_path = os.path.join(current_dir, csv_file_name)
        csv_files_to_analyze.append(csv_file_path)
    else:
        # User wants to analyze all CSVs in the current directory
        print("Buscando todos os arquivos CSV no diretório atual...")
        found_csvs = glob.glob(os.path.join(current_dir, '*.csv'))
        if not found_csvs:
            print("INFO: Nenhum arquivo CSV encontrado no diretório atual para análise.")
            sys.exit(0) # Exit gracefully if no files found
        csv_files_to_analyze.extend(found_csvs)
        
        print(f"Encontrados {len(csv_files_to_analyze)} arquivo(s) CSV para análise.")

    for csv_file_path in csv_files_to_analyze:
        csv_file_name = os.path.basename(csv_file_path)
        print(f"\n======== Iniciando análise: {csv_file_name} ========")
        
        analysis_data = analyze_webprice_data(csv_file_path)

        if isinstance(analysis_data, dict) and "error" in analysis_data:
            print(f"ERRO ao analisar '{csv_file_name}': {analysis_data['error']}")
        else:
            results, ml_insights = analysis_data

            if isinstance(results, dict) and "message" in results:
                print(f"INFO para '{csv_file_name}': {results['message']}")
            else:
                top_results_count = len(results)
                print(f"\n--- Top {top_results_count} Produtos para Ajuste em '{csv_file_name}' ---")
                if not results:
                    print(f"Nenhum produto qualificado para o Top X neste arquivo '{csv_file_name}'.")
                else:
                    for i, item in enumerate(results):
                        print(f"\n{i+1}. Produto: {item['Produto']}")
                        print(f"   Status Original: {item['Status_Original']}")
                        print(f"   Tipo Ajuste: {item['Tipo_Ajuste']}")
                        print(f"   Lojista (Concorrente): {item['Lojista']}")
                        print(f"   Seu Preço Atual: {format_currency_br(item['Preço'])}")
                        print(f"   Preço Concorrente (MAIS BARATO): {format_currency_br(item['Preço_Concorrente'])}")
                        
                        if item['Tipo_Ajuste'] == 'Abaixar Preço para Competitividade':
                            print(f"   Valor a Abaixar: {format_currency_br(item['Valor_Ajuste'])}")
                            print(f"   Percentual de Ajuste: {item['Percentual_Ajuste']:.2f}%")
                        elif item['Tipo_Ajuste'] == 'Otimizar Margem para Lucratividade':
                            print(f"   Ganho de Margem Otimizável: {format_currency_br(item['Valor_Ajuste'])}")
                            print(f"   Percentual de Margem Otimizável: {item['Percentual_Ajuste']:.2f}%")
                        else: # 'Oportunidade de Aumento de Preço'
                            print(f"   Ganho de Margem Potencial: {format_currency_br(item['Valor_Ajuste'])}")
                            print(f"   Percentual de Margem Potencial: {item['Percentual_Ajuste']:.2f}%")
                        
                        print(f"   SUGESTÃO NOVO PREÇO: {format_currency_br(item['Sugestao_Preco'])}")
            
            # Exibe os insights do ML, se disponíveis para o arquivo atual
            print("\n--------------------------------------")
            print(f" Insights do Modelo de ML para '{csv_file_name}'")
            print("--------------------------------------")
            if ml_insights:
                if "status" in ml_insights: # Se o modelo foi treinado
                    for key, value in ml_insights.items():
                        print(f"- {key.replace('_', ' ').capitalize()}: {value}")
                else: # Se houver uma mensagem, mas não um modelo treinado
                    print(f"{ml_insights['message']}")
            else:
                print("Nenhum insight de ML disponível (dados insuficientes ou erro).")
        print("\n========================================================\n") # Separador entre análises de arquivos
