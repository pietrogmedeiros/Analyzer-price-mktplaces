#!/bin/bash

echo "🔧 Corrigindo containers do WebPrice Analyzer..."

# Para e remove todos os containers
docker-compose down

# Remove o container problemático específico
docker rm -f webprice-analyz 2>/dev/null || true

# Reconstrói e inicia
docker-compose up --build -d

echo "✅ Containers reiniciados com sucesso!"
echo ""
echo "🌐 Acesse:"
echo "  - App: http://localhost"
echo "  - API: http://localhost:5000" 
echo "  - DB Admin: http://localhost:8080"
