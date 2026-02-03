#!/bin/bash

# Script para sincronizar docker-compose.yml corrigido para o servidor

if [ $# -lt 2 ]; then
    echo "❌ Uso: bash sync_compose.sh <usuario> <servidor> [caminho_remoto]"
    echo ""
    echo "Exemplo:"
    echo "  bash sync_compose.sh deploy people-fy.com /home/deploy/ScraperSenior"
    echo "  bash sync_compose.sh ubuntu people-fy.com"
    echo ""
    exit 1
fi

USER=$1
SERVER=$2
REMOTE_PATH=${3:-.}  # Usa diretório atual do servidor se não especificado

echo "📋 Sincronizando docker-compose.yml..."
echo "  Usuário: $USER"
echo "  Servidor: $SERVER"
echo "  Caminho remoto: $REMOTE_PATH"
echo ""

# Step 1: Backup
echo "1️⃣  Criando backup..."
ssh $USER@$SERVER "cd $REMOTE_PATH && cp docker-compose.yml docker-compose.yml.bak.\$(date +%s)" 2>/dev/null || true

# Step 2: Copiar arquivo
echo "2️⃣  Copiando docker-compose.yml..."
scp docker-compose.yml $USER@$SERVER:$REMOTE_PATH/docker-compose.yml
if [ $? -ne 0 ]; then
    echo "❌ Erro ao copiar arquivo"
    exit 1
fi

# Step 3: Parar containers
echo "3️⃣  Parando containers..."
ssh $USER@$SERVER "cd $REMOTE_PATH && docker-compose down" 2>/dev/null || ssh $USER@$SERVER "cd $REMOTE_PATH && podman-compose down" 2>/dev/null || true

# Step 4: Iniciar containers
echo "4️⃣  Iniciando containers..."
ssh $USER@$SERVER "cd $REMOTE_PATH && docker-compose up -d" 2>/dev/null || ssh $USER@$SERVER "cd $REMOTE_PATH && podman-compose up -d" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Erro ao iniciar containers"
    exit 1
fi

# Step 5: Aguardar
echo "5️⃣  Aguardando (20 segundos)..."
sleep 20

# Step 6: Testar
echo "6️⃣  Testando endpoint /openapi.json..."
RESPONSE=$(curl -s -w "\n%{http_code}" http://people-fy.com:8000/openapi.json)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCESSO! OpenAPI respondendo corretamente"
    echo "   Acesse: http://people-fy.com:8000/docs"
else
    echo "⚠️  Status $HTTP_CODE"
    echo "   Resposta: $BODY"
    echo ""
    echo "Para debugar, execute:"
    echo "  ssh $USER@$SERVER 'cd $REMOTE_PATH && docker-compose logs mcp-server' | tail -30"
fi
