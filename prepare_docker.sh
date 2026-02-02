#!/bin/bash
# Script para preparar o ambiente Docker
# Corrige permissões e variáveis de ambiente

set -e

echo "🔧 Preparando ambiente Docker..."

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p docs_estruturado
mkdir -p docs_unified

# Definir permissões corretas (777 para diretórios, 666 para arquivos)
echo "🔐 Corrigindo permissões..."
chmod -R 777 docs_estruturado
chmod -R 777 docs_unified

# Criar .env com variáveis padrão se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cat > .env << 'EOF'
# Meilisearch Configuration
MEILISEARCH_KEY=5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa
MEILI_LOG_LEVEL=info
LOG_LEVEL=info

# MCP Configuration
MCP_MODE=openapi
OPENAPI_HOST=0.0.0.0
OPENAPI_PORT=8000
EOF
    echo "✅ Arquivo .env criado"
fi

echo ""
echo "✅ Ambiente preparado com sucesso!"
echo ""
echo "Próximo passo:"
echo "  docker-compose build"
echo "  docker-compose up -d"
