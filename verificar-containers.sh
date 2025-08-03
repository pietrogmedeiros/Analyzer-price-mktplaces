#!/bin/bash

echo "🔍 Verificando status dos containers do WebPrice Analyzer..."
echo "============================================================"

# Verifica se os containers estão rodando
echo "📋 Status dos containers:"
docker-compose ps

echo ""
echo "🌐 URLs de acesso:"
echo "  ✅ Aplicação Principal: http://localhost"
echo "  ✅ API Backend: http://localhost:5000"
echo "  ✅ Banco PostgreSQL: localhost:5432"
echo "  ✅ Cache Redis: localhost:6379"
echo "  ✅ Adminer (DB Admin): http://localhost:8081"

echo ""
echo "🔧 Testando conectividade..."

# Testa se as portas estão respondendo
if curl -s http://localhost >/dev/null; then
    echo "  ✅ Frontend (porta 80): OK"
else
    echo "  ❌ Frontend (porta 80): FALHA"
fi

if curl -s http://localhost:5000 >/dev/null; then
    echo "  ✅ Backend (porta 5000): OK"
else
    echo "  ❌ Backend (porta 5000): FALHA"
fi

if curl -s http://localhost:8081 >/dev/null; then
    echo "  ✅ Adminer (porta 8081): OK"
else
    echo "  ❌ Adminer (porta 8081): FALHA"
fi

echo ""
echo "📊 Uso de recursos:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker-compose ps -q)

echo ""
echo "✅ Verificação concluída!"
