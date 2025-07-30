# --- Estágio 1: Build (Construção) ---
# Usa uma imagem Node.js completa para instalar dependências e construir o projeto
FROM node:18-alpine AS build

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de manifesto de pacotes
COPY package.json yarn.lock* package-lock.json* ./

# Instala as dependências
RUN npm install

# Copia o resto do código do frontend
COPY . .

# Executa o build de produção do Vite
RUN npm run build

# --- Estágio 2: Production (Produção) ---
# Usa uma imagem de servidor web super leve (nginx) para servir os arquivos estáticos
FROM nginx:stable-alpine

# Copia os arquivos estáticos gerados no estágio de build para a pasta do nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Expõe a porta 80 (padrão do nginx)
EXPOSE 80

# O comando padrão do nginx já inicia o servidor, então não precisamos de um CMD