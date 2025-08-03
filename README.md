# 🚀 Mkt Places Analyzer: Análise Inteligente de Preços para Marketplaces

![Versão](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.9-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Uma aplicação full-stack containerizada que utiliza Machine Learning para analisar dados de preços de marketplaces, fornecendo insights acionáveis para otimização de estratégias de precificação com interface moderna e arquitetura escalável.

---

## 🎯 O Problema Resolvido

Em ambientes de e-commerce e marketplaces, a precificação é um dos fatores mais críticos para o sucesso. Lojistas precisam constantemente monitorar concorrentes para se manterem competitivos, mas também precisam identificar oportunidades para aumentar a margem de lucro sem perder vendas.

O **Mkt Places Analyzer** resolve esse problema ao automatizar a análise de grandes volumes de dados de preços. A ferramenta processa arquivos CSV, identifica produtos onde o lojista está "perdendo" para a concorrência e, mais importante, aponta oportunidades onde o preço pode ser otimizado para cima, tudo isso dentro de um limite de ajuste seguro (3%) para evitar mudanças drásticas.

### 🆕 Novidades da Versão 2.0
- **Arquitetura Containerizada Completa**: Frontend, Backend, Banco de Dados e Cache
- **Interface Moderna**: Dashboard responsivo com React e design moderno
- **Configuração CORS Otimizada**: Suporte para desenvolvimento e produção
- **Banco PostgreSQL**: Preparado para armazenamento de dados históricos
- **Cache Redis**: Performance otimizada para análises frequentes

---

## ✨ Funcionalidades Principais

*   **🧠 Análise Inteligente de Dados:** Processa arquivos CSV com dados de produtos, preços e concorrentes para gerar sugestões de ajuste automatizadas.
*   **🤖 Machine Learning Integrado:** Treina um modelo de Árvore de Decisão em tempo real a cada análise para identificar quais fatores (preço, diferença para o concorrente, etc.) são mais importantes para definir uma estratégia de ajuste.
*   **📊 Dashboard Interativo:** Interface moderna com React apresentando resultados em cards de resumo, tabelas detalhadas e insights do modelo de ML.
*   **🌐 Interface Web Responsiva:** Frontend construído com React e Vite, proporcionando uma experiência de usuário fluida em qualquer dispositivo.
*   **🐳 Arquitetura Containerizada:** Aplicação completa com Docker Compose incluindo frontend, backend, banco PostgreSQL, cache Redis e interface de administração.
*   **⚡ Performance Otimizada:** Cache Redis para análises frequentes e Nginx para servir o frontend com alta performance.
*   **🔧 Configuração Flexível:** Suporte para desenvolvimento local e produção com variáveis de ambiente configuráveis.

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
git clone https://github.com/pietrogmedeiros/Analyzer-price-mktplaces.git
cd Analyzer-price-mktplaces

# 2. Construa e inicie os contêineres
docker-compose up --build -d

# 3. Acesse a aplicação
# Abra seu navegador e acesse: http://localhost
```

### 🐳 Serviços Docker Disponíveis

A aplicação agora inclui os seguintes serviços containerizados:

| Serviço | Imagem | Porta | Descrição |
|---------|--------|-------|-----------|
| **Frontend** | `nginx:stable-alpine` | `80` | Interface React servida pelo Nginx |
| **Backend** | `python:3.9-slim` | `5000` | API Flask com Gunicorn |
| **Database** | `postgres:15-alpine` | `5432` | Banco de dados PostgreSQL |
| **Cache** | `redis:7-alpine` | `6379` | Cache Redis para performance |
| **DB Admin** | `adminer:4-standalone` | `8081` | Interface web para gerenciar o banco |

### 🔧 Comandos Úteis

```bash
# Ver status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Parar todos os serviços
docker-compose down

# Reiniciar com rebuild
docker-compose up --build -d

# Resolver problemas de containers órfãos
./restart-docker.sh

# Limpeza completa (remove containers, imagens e volumes)
./docker-cleanup.sh
```


### 🎯 Exemplo de Uso

1. Faça upload de um arquivo CSV com dados de preços
2. A aplicação processará os dados e identificará oportunidades
3. Visualize os resultados no dashboard interativo
4. Analise os insights de Machine Learning para tomada de decisão

---

## 📬 Contato

**Pietro Medeiros**

-   **LinkedIn:** [Meu Linkedin](https://www.linkedin.com/in/pietro-medeiros-770bba162/)
