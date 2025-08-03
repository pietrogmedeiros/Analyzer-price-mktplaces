#!/bin/bash

echo "🧹 Limpando containers antigos do webprice-analyzer..."

# Para todos os containers relacionados ao projeto
echo "Parando containers..."
docker stop webprice-backend webprice-frontend webprice-database webprice-redis webprice-adminer webprice-analyz 2>/dev/null || true

# Remove containers antigos
echo "Removendo containers antigos..."
docker rm webprice-backend webprice-frontend webprice-database webprice-redis webprice-adminer webprice-analyz 2>/dev/null || true

# Remove imagens órfãs
echo "Removendo imagens órfãs..."
docker image prune -f

# Remove volumes órfãos (cuidado: isso remove dados!)
echo "Removendo volumes órfãos..."
docker volume prune -f

echo "✅ Limpeza concluída!"
echo ""
echo "🚀 Agora execute:"
echo "docker-compose up --build -d"
