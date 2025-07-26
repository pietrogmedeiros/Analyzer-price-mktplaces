# Price MktPlace Analyzer

Um projeto backend para analisar dados de preços a partir de arquivos CSV, extraídos de um relatório de preço por categoria em marketplaces.

## 📜 Sobre o Projeto

Este projeto consiste em um script de análise de dados e uma aplicação web. O componente principal (`analyze_csv_standalone.py`) processa arquivos CSV para extrair e analisar informações de preços, enquanto a aplicação web (`app.py`) serve como uma interface para interagir com esses dados.

## ✨ Funcionalidades

- Análise de dados de preços a partir de arquivos `.csv`.
- Estrutura de backend com WSGI, pronta para deploy.
- Ambiente de desenvolvimento isolado com Conda.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python
- **Ambiente:** Conda
- **Dependências:** Pandas e Fask

## 🚀 Como Executar

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

- [Python 3.x](https://www.python.org/)
- [Conda](https://docs.conda.io/en/latest/miniconda.html) (ou Anaconda)

### Instalação e Configuração

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/SEU-USUARIO/webprice-analyzer.git
    cd webprice-analyzer
    ```

2.  **Crie e ative o ambiente Conda:**
    ```bash
    # O nome do ambiente está no seu comando.txt
    conda activate webprice_analyzer_env 
    
    # Se o ambiente não existir, crie-o primeiro:
    # conda create --name webprice_analyzer_env python=3.9
    # conda activate webprice_analyzer_env
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r backend/requirements.txt
    ```

### Uso

Para executar a análise de CSV de forma independente:
```bash
python backend/analyze_csv_standalone.py# Analyzer-price-mktplaces
