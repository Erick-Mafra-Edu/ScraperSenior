#!/bin/bash
# -*- coding: utf-8 -*-
#
# Script de Validação e Exemplos OpenAPI
# ======================================
#
# Valida o arquivo openapi.json e gera exemplos curl para os novos endpoints
# de validação de respostas.
#
# Autor: Sistema de Validação Senior
# Data: 2026-02-05

set -e  # Sair em caso de erro

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "================================================"
echo "OpenAPI Validation & Examples Generator"
echo "================================================"
echo ""

# Verificar se openapi.json existe
if [ ! -f "openapi.json" ]; then
    echo -e "${RED}✗ Erro: openapi.json não encontrado${NC}"
    exit 1
fi

echo -e "${GREEN}✓ openapi.json encontrado${NC}"

# Validar JSON syntax
echo ""
echo "Validando sintaxe JSON..."
if python3 -m json.tool openapi.json > /dev/null 2>&1; then
    echo -e "${GREEN}✓ JSON syntax válido${NC}"
else
    echo -e "${RED}✗ Erro: JSON inválido${NC}"
    python3 -m json.tool openapi.json
    exit 1
fi

# Verificar se novos endpoints existem
echo ""
echo "Verificando novos endpoints..."

ENDPOINTS=(
    "/model/validate-response"
    "/model/generate-and-validate"
    "/mcp/validate-response"
)

for endpoint in "${ENDPOINTS[@]}"; do
    if grep -q "\"$endpoint\"" openapi.json; then
        echo -e "${GREEN}✓ $endpoint encontrado${NC}"
    else
        echo -e "${RED}✗ $endpoint não encontrado${NC}"
    fi
done

# Gerar exemplos curl
echo ""
echo "================================================"
echo "Exemplos de Uso (curl)"
echo "================================================"
echo ""

echo -e "${YELLOW}1. Validar Resposta Existente${NC}"
echo ""
cat << 'EOF'
curl -X POST http://localhost:8000/model/validate-response \
  -H "Content-Type: application/json" \
  -d '{
    "response": "O CRM Senior permite configurar notificações automáticas por email.",
    "retrieved_passages": [
      {
        "id": "doc_123",
        "text": "O módulo CRM da Senior oferece configuração de notificações por email e SMS."
      }
    ],
    "threshold": 0.75
  }'
EOF
echo ""

echo -e "${YELLOW}2. Gerar e Validar Resposta Completa${NC}"
echo ""
cat << 'EOF'
curl -X POST http://localhost:8000/model/generate-and-validate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Como configurar notificações no CRM?",
    "limit": 5,
    "module_filter": null,
    "generation_config": {
      "temperature": 0.1,
      "top_p": 0.8,
      "max_tokens": 1000
    },
    "validation_threshold": 0.75
  }'
EOF
echo ""

echo -e "${YELLOW}3. Validar via MCP${NC}"
echo ""
cat << 'EOF'
curl -X POST http://localhost:8000/mcp/validate-response \
  -H "Content-Type: application/json" \
  -d '{
    "response": "O sistema permite exportar relatórios em PDF e Excel.",
    "retrieved_passages": [
      {
        "id": "doc_456",
        "text": "Relatórios podem ser exportados nos formatos PDF, Excel e CSV."
      }
    ],
    "threshold": 0.75
  }'
EOF
echo ""

echo "================================================"
echo "Exemplos Python"
echo "================================================"
echo ""

echo -e "${YELLOW}1. Validação Direta (Python)${NC}"
echo ""
cat << 'EOF'
from libs.validators.hallucination_guard import verify_response

result = verify_response(
    response="O CRM permite configurar notificações.",
    retrieved_passages=[
        {"id": "doc_123", "text": "CRM oferece notificações..."}
    ],
    threshold=0.75
)

print(f"Verificado: {result['verified']}")
print(f"Confiança: {result['overall_confidence']}")
EOF
echo ""

echo -e "${YELLOW}2. Pipeline Completo (Python)${NC}"
echo ""
cat << 'EOF'
import asyncio
from services.model_pipeline import ModelPipeline

async def main():
    pipeline = ModelPipeline(validation_threshold=0.75)
    result = await pipeline.generate_and_validate(
        query="Como configurar notificações?",
        limit=5
    )
    print(f"Success: {result.success}")
    print(f"Response: {result.response}")

asyncio.run(main())
EOF
echo ""

# Verificar schemas
echo "================================================"
echo "Schemas Definidos"
echo "================================================"
echo ""

SCHEMAS=(
    "ValidateResponseRequest"
    "ValidateResponseResult"
    "GenerateAndValidateRequest"
    "GenerateAndValidateResult"
)

for schema in "${SCHEMAS[@]}"; do
    if grep -q "\"$schema\"" openapi.json; then
        echo -e "${GREEN}✓ $schema${NC}"
    else
        echo -e "${RED}✗ $schema não encontrado${NC}"
    fi
done

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Validação completa!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

# Informações adicionais
echo "Para testar os endpoints:"
echo "1. Inicie o servidor: python apps/mcp-server/mcp_server.py"
echo "2. Use os exemplos curl acima"
echo "3. Verifique a documentação completa em docs/prompt_templates/"
echo ""
echo "Para executar testes:"
echo "  pytest tests/integration/test_grounding.py -v"
echo "  pytest tests/unit/test_hallucination_guard.py -v"
echo ""
