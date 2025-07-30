# 1. Imagem base do Python
FROM python:3.9-slim

# 2. Define o diretório de trabalho
WORKDIR /app

# 3. Copia o arquivo de dependências
COPY requirements.txt .

# 4. Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia o código da aplicação
COPY . .

# 6. Expõe a porta que o Flask vai rodar
EXPOSE 5000

# 7. Comando para iniciar a aplicação
# Usamos Gunicorn como um servidor WSGI de produção
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]