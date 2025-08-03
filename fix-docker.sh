#!/bin/bash

echo "🔧 Corrigindo problemas do Docker - WebPrice Analyzer"
echo "=================================================="

# Para todos os containers
echo "1. Parando todos os containers..."
docker-compose down 2>/dev/null || true

# Remove containers órfãos/problemáticos
echo "2. Removendo containers problemáticos..."
docker rm -f webprice-analyz 2>/dev/null || true
docker rm -f webprice-backend 2>/dev/null || true
docker rm -f webprice-frontend 2>/dev/null || true
docker rm -f webprice-database 2>/dev/null || true
docker rm -f webprice-redis 2>/dev/null || true
docker rm -f webprice-adminer 2>/dev/null || true

# Remove imagens órfãs
echo "3. Limpando imagens órfãs..."
docker image prune -f

# Reconstrói e inicia os containers
echo "4. Reconstruindo e iniciando containers..."
docker-compose up --build -d

echo ""
echo "✅ Processo concluído!"
echo ""
echo "🌐 Serviços disponíveis:"
echo "  - Frontend: http://localhost"
echo "  - Backend API: http://localhost:5000"
echo "  - Banco PostgreSQL: localhost:5432"
echo "  - Cache Redis: localhost:6379"
echo "  - Adminer (DB Admin): http://localhost:8080"
echo ""
echo "📊 Para verificar o status:"
echo "  docker-compose ps"
echo ""
echo "📋 Para ver logs:"
echo "  docker-compose logs -f"
