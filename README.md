# 🚀 Mkt Place Analyzer: Análise Inteligente de Preços

![Versão](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.9-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0-black?logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Uma aplicação full-stack que utiliza Machine Learning para analisar dados de preços de marketplaces, fornecendo insights acionáveis para otimização de estratégias de precificação.

---

## 🎯 O Problema Resolvido

Em ambientes de e-commerce e marketplaces, a precificação é um dos fatores mais críticos para o sucesso. Lojistas precisam constantemente monitorar concorrentes para se manterem competitivos, mas também precisam identificar oportunidades para aumentar a margem de lucro sem perder vendas.

O **Mkt Place Analyzer** resolve esse problema ao automatizar a análise de grandes volumes de dados de preços. A ferramenta processa um arquivo CSV, identifica produtos onde o lojista está "perdendo" para a concorrência e, mais importante, aponta oportunidades onde o preço pode ser otimizado para cima, tudo isso dentro de um limite de ajuste seguro (ex: 3%) para evitar mudanças drásticas.

---

## ✨ Funcionalidades Principais

*   **🧠 Análise Inteligente de Dados:** Processa arquivos CSV com dados de produtos, preços e concorrentes para gerar sugestões de ajuste.
*   **🤖 Machine Learning Integrado:** Treina um modelo de Árvore de Decisão em tempo real a cada análise para identificar quais fatores (preço, diferença para o concorrente, etc.) são mais importantes para definir uma estratégia de ajuste.
*   **📊 Dashboard Interativo:** Apresenta os resultados em um dashboard limpo e moderno, com cards de resumo, uma tabela detalhada das sugestões e insights do modelo de ML.
*   **🌐 Interface Web Moderna:** Frontend construído com React, proporcionando uma experiência de usuário fluida e responsiva.
*   **🐳 Containerização Completa:** Com Docker e Docker Compose, a aplicação (backend e frontend) pode ser executada em qualquer ambiente com um único comando, garantindo consistência e facilidade de implantação.

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando as seguintes tecnologias:

### **Backend (Análise e API)**
*   ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) - Linguagem principal para a lógica de análise.
*   ![Flask](https://img.shields.io/badge/Flask-black?logo=flask&logoColor=white) - Micro-framework para a construção da API RESTful.
*   ![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white) - Para manipulação e análise de dados de alta performance.
*   ![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?logo=scikit-learn&logoColor=white) - Para o treinamento do modelo de Machine Learning.
*   ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?logo=gunicorn&logoColor=white) - Servidor WSGI para rodar a aplicação Flask em produção.

### **Frontend (Interface do Usuário)**
*   ![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=white) - Biblioteca para a construção da interface de usuário.
*   ![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white) - Ferramenta de build para um desenvolvimento frontend rápido.
*   ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) - Linguagem de programação do frontend.
*   ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white) - Para estilização customizada da aplicação.
*   ![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white) - Servidor web de alta performance para servir o frontend em produção.

### **Containerização e Implantação**
*   ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white) - Para criar contêineres isolados para o backend e frontend.
*   **Docker Compose** - Para orquestrar e gerenciar os múltiplos contêineres da aplicação.

---

## 🚀 Como Executar

Para executar o projeto, siga as instruções no arquivo `comandos.txt` ou no guia rápido abaixo.

**Pré-requisitos:**
- Git
- Docker e Docker Compose

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO

# 2. Construa e inicie os contêineres
docker-compose up --build -d

# 3. Acesse a aplicação
# Abra seu navegador e acesse: http://localhost
```

---

## 📬 Contato

**Pietro Medeiros**

-   **LinkedIn:** [Meu Linkedin](https://www.linkedin.com/in/pietro-medeiros-770bba162/)
