#!/bin/bash
# Script para debugar o OpenAPI Server no servidor

echo "🔍 Debugando OpenAPI Server no servidor..."
echo "=========================================="
echo ""

# Teste 1: Verificar se o endpoint responde
echo "1️⃣  Testando endpoint /openapi.json..."
HTTP_CODE=$(curl -s -o /tmp/response.txt -w "%{http_code}" http://people-fy.com:8000/openapi.json)
echo "Status HTTP: $HTTP_CODE"
echo "Resposta:"
cat /tmp/response.txt
echo ""
echo ""

# Teste 2: Verificar /docs
echo "2️⃣  Testando endpoint /docs..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://people-fy.com:8000/docs)
echo "Status HTTP: $HTTP_CODE"
echo ""

# Teste 3: Verificar /health
echo "3️⃣  Testando endpoint /health..."
curl -s http://people-fy.com:8000/health | jq . 2>/dev/null || curl -s http://people-fy.com:8000/health
echo ""
echo ""

# Teste 4: Verificar status dos containers (pode ser feito no servidor)
echo "4️⃣  Para ver logs do servidor, execute:"
echo "    ssh seu_usuario@people-fy.com"
echo "    cd /caminho/do/projeto"
echo "    docker-compose logs mcp-server"
echo ""

echo "=========================================="
