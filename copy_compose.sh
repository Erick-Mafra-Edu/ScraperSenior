#!/bin/bash

# Script simples para copiar docker-compose.yml corrigido
# Use: bash copy_compose.sh [USER] [SERVER] [REMOTE_PATH]

USER=${1:-usuario}
SERVER=${2:-people-fy.com}
REMOTE_PATH=${3:-/home/usuario/ScraperSenior}

echo "📋 Parametros:"
echo "  Usuário: $USER"
echo "  Servidor: $SERVER"
echo "  Caminho remoto: $REMOTE_PATH"
echo ""

# Copiar arquivo
echo "Copiando docker-compose.yml..."
scp docker-compose.yml "${USER}@${SERVER}:${REMOTE_PATH}/"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Arquivo copiado com sucesso!"
    echo ""
    echo "Agora execute no servidor:"
    echo "  ssh ${USER}@${SERVER}"
    echo "  cd $REMOTE_PATH"
    echo "  docker-compose down"
    echo "  docker-compose up -d"
    echo ""
    echo "Depois teste:"
    echo "  curl http://${SERVER}:8000/openapi.json"
else
    echo "❌ Erro ao copiar arquivo"
fi
