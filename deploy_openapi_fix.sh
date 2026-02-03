#!/bin/bash

# Script para fazer deploy da correção do OpenAPI no servidor people-fy.com

SERVER="root@people-fy.com"
REMOTE_PATH="/root/ScraperSenior"
LOCAL_COMPOSE="docker-compose.yml"

echo "🚀 Iniciando deploy da correção OpenAPI..."
echo "=============================================================="

# Step 1: Fazer backup
echo -e "\n1️⃣  Fazendo backup do docker-compose.yml no servidor..."
ssh $SERVER "cd $REMOTE_PATH && cp docker-compose.yml docker-compose.yml.backup.\$(date +%Y%m%d_%H%M%S)" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backup criado com sucesso"
else
    echo "⚠️  Aviso ao criar backup"
fi

# Step 2: Copiar arquivo
echo -e "\n2️⃣  Copiando docker-compose.yml corrigido..."
scp "$LOCAL_COMPOSE" "${SERVER}:${REMOTE_PATH}/" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Arquivo copiado com sucesso"
else
    echo "❌ Erro ao copiar arquivo"
    exit 1
fi

# Step 3: Parar containers
echo -e "\n3️⃣  Parando containers antigos..."
ssh $SERVER "cd $REMOTE_PATH && docker-compose down" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Containers parados com sucesso"
else
    echo "⚠️  Aviso ao parar containers"
fi

# Step 4: Iniciar containers
echo -e "\n4️⃣  Iniciando novos containers..."
ssh $SERVER "cd $REMOTE_PATH && docker-compose up -d" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Containers iniciados com sucesso"
else
    echo "❌ Erro ao iniciar containers"
    exit 1
fi

# Step 5: Aguardar
echo -e "\n5️⃣  Aguardando containers ficarem prontos (15 segundos)..."
sleep 15

# Step 6: Status
echo -e "\n6️⃣  Verificando status dos containers..."
ssh $SERVER "cd $REMOTE_PATH && docker-compose ps" 2>/dev/null

# Step 7: Testar
echo -e "\n7️⃣  Testando endpoint /openapi.json..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://people-fy.com:8000/openapi.json)
echo "Resposta:"
echo "$RESPONSE"

if echo "$RESPONSE" | grep -q "HTTP_CODE:200"; then
    echo -e "\n✅ SUCESSO! OpenAPI Server está funcionando!"
    echo "   Acesse: http://people-fy.com:8000/docs"
else
    echo -e "\n⚠️  Ainda com problema. Verificar logs:"
    echo "   ssh root@people-fy.com 'cd /root/ScraperSenior && docker-compose logs mcp-server'"
fi

echo -e "\n=============================================================="
echo "✅ Deploy concluído!"
