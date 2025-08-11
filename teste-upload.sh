#!/bin/bash

echo "🧪 Testando upload de arquivo CSV..."

# Verifica se existe um arquivo CSV de exemplo
if [ -f "webpricecombr-price-2094-42-20250719173910-3ed5ae79069e79e7109a8318acfc782e947f1ab4.csv" ]; then
    echo "📁 Arquivo CSV encontrado, testando upload..."
    
    # Testa o upload
    curl -X POST \
      -F "file=@webpricecombr-price-2094-42-20250719173910-3ed5ae79069e79e7109a8318acfc782e947f1ab4.csv" \
      http://localhost:5000/analyze \
      -H "Content-Type: multipart/form-data" \
      | jq '.' 2>/dev/null || echo "Resposta recebida (sem formatação JSON)"
      
else
    echo "❌ Arquivo CSV de exemplo não encontrado"
    echo "📋 Arquivos disponíveis:"
    ls -la *.csv 2>/dev/null || echo "Nenhum arquivo CSV encontrado"
fi

echo ""
echo "✅ Teste concluído!"
