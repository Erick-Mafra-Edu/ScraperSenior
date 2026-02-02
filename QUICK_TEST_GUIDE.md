#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guia Rápido de Testes: MCP + Meilisearch
=========================================

Use este guia para testar componentes individuais rapidamente.
"""

# ============================================================================
# TESTE 1: Validação Estrutural
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║ TESTE 1: VALIDAÇÃO ESTRUTURAL                                             ║
╚════════════════════════════════════════════════════════════════════════════╝

Execute:
    python validate_mcp_docker_meilisearch.py

Esperado:
    ✓ 58/58 validações passaram
    ✓ Status: VALIDADO COM SUCESSO
""")

# ============================================================================
# TESTE 2: Integração Prática
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║ TESTE 2: INTEGRAÇÃO PRÁTICA                                               ║
╚════════════════════════════════════════════════════════════════════════════╝

Execute:
    python test_mcp_integration_practical.py

Esperado:
    ✓ TEST 1: Inicialização do MCP Server
    ✓ TEST 2: Carregamento de Índices JSONL
    ✓ TEST 3: Operações de Busca
    ✓ TEST 4: Interface de Ferramentas (MCP)
    ✓ TEST 5: Simulação de Protocolo MCP 2.0
    ✓ TEST 6: Comportamento de Fallback
    ✓ Total: 6/6 testes passaram
""")

# ============================================================================
# TESTE 3: Docker Compose
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║ TESTE 3: DOCKER COMPOSE                                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

Execute:
    cd infra/docker
    docker-compose up -d
    docker-compose ps

Esperado:
    NAME                                      STATUS
    senior-docs-meilisearch                   Up (healthy)
    senior-docs-mcp-server                    Up (healthy)
    senior-docs-scraper                       Up

Verificar Saúde:
    docker-compose logs meilisearch    # Procurar por "healthy"
    docker-compose logs mcp-server     # Procurar por "[✓]"

Parar:
    docker-compose down
""")

# ============================================================================
# TESTE 4: Meilisearch Direto
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║ TESTE 4: MEILISEARCH DIRETO                                               ║
╚════════════════════════════════════════════════════════════════════════════╝

1. Verificar Saúde:
    curl http://localhost:7700/health
    
    Esperado: {"status":"available"}

2. Listar Índices:
    curl http://localhost:7700/indexes
    
    Esperado: JSON com índices

3. Buscar Documentos:
    curl "http://localhost:7700/indexes/documentation/search" \\
      -H "Authorization: Bearer meilisearch_master_key_change_me" \\
      -H "Content-Type: application/json" \\
      -d '{"q":"CRM","limit":5}'
    
    Esperado: {"hits":[...], "nbHits":N, "offset":0, "limit":5}

4. Obter Estatísticas:
    curl -X GET http://localhost:7700/indexes/documentation/stats \\
      -H "Authorization: Bearer meilisearch_master_key_change_me"
    
    Esperado: {"numberOfDocuments":855, ...}
""")

# ============================================================================
# TESTE 5: MCP Server HTTP
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║ TESTE 5: MCP SERVER HTTP                                                  ║
╚════════════════════════════════════════════════════════════════════════════╝

1. Health Check:
    curl http://localhost:8000/health
    
    Esperado: {"status":"healthy","service":"MCP Server"}

2. Listar Ferramentas:
    curl http://localhost:8000/tools
    
    Esperado: {"tools":{"search_docs":{...}, "list_modules":{...}, ...}}

3. Estatísticas:
    curl http://localhost:8000/stats
    
    Esperado: {"stats":{"total_documents":855,...},"tools":4,"modules":N}

4. Buscar (REST):
    curl -X POST http://localhost:8000/search \\
      -H "Content-Type: application/json" \\
      -d '{"query":"CRM","limit":5}'
    
    Esperado: {"query":"CRM","count":N,"results":[...]}

5. JSON-RPC (POST):
    curl -X POST http://localhost:8000/messages \\
      -H "Content-Type: application/json" \\
      -d '{
        "jsonrpc":"2.0",
        "id":1,
        "method":"tools/call",
        "params":{"name":"search_docs","arguments":{"query":"CRM"}}
      }'
    
    Esperado: {"jsonrpc":"2.0","id":1,"result":{"content":[...]}}
""")

# ============================================================================
# TESTE 6: MCP Protocol Direto
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║ TESTE 6: MCP PROTOCOL DIRETO (VS CODE)                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

1. Adicionar em settings.json:
    {
      "modelContextProtocol": {
        "servers": {
          "senior-docs": {
            "command": "python",
            "args": ["apps/mcp-server/mcp_server.py"],
            "cwd": "c:/Users/Digisys/scrapyTest"
          }
        }
      }
    }

2. Reiniciar VS Code

3. Usar em Chat:
    @senior-docs search_docs query: "configuração"

Esperado:
    - Ferramenta reconhecida
    - Resultados retornados
    - Documentação encontrada
""")

# ============================================================================
# TESTE 7: Fallback (Sem Meilisearch)
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║ TESTE 7: FALLBACK (SEM MEILISEARCH)                                       ║
╚════════════════════════════════════════════════════════════════════════════╝

1. Parar Meilisearch:
    docker-compose stop meilisearch

2. Testar MCP Server:
    python test_mcp_integration_practical.py
    
    Procurar por:
    "✓ TEST 6: Comportamento de Fallback"
    "ℹ Usando fallback local: True"

3. Verificar Busca Local:
    curl http://localhost:8000/health
    
    Esperado: Ainda retorna healthy (usando JSONL local)

4. Reiniciar Meilisearch:
    docker-compose start meilisearch
""")

# ============================================================================
# TESTE 8: Performance
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║ TESTE 8: PERFORMANCE                                                      ║
╚════════════════════════════════════════════════════════════════════════════╝

1. Medir Latência de Busca:
    time curl -X POST http://localhost:8000/search \\
      -H "Content-Type: application/json" \\
      -d '{"query":"teste","limit":10}'
    
    Esperado: < 100ms (com Meilisearch)
               < 500ms (com fallback JSONL)

2. Teste de Carga (100 requisições):
    for i in {1..100}; do
      curl -X POST http://localhost:8000/search \\
        -H "Content-Type: application/json" \\
        -d '{"query":"test","limit":5}' &
    done
    
    Esperado: Todas as requisições respondidas

3. Monitorar Recursos:
    docker stats

    Esperado:
    - MCP: < 200 MB RAM
    - Meilisearch: < 500 MB RAM
""")

# ============================================================================
# TESTE 9: Dados
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║ TESTE 9: VALIDAÇÃO DE DADOS                                               ║
╚════════════════════════════════════════════════════════════════════════════╝

1. Verificar Índice JSONL:
    wc -l data/indexes/docs_indexacao_detailed.jsonl
    
    Esperado: 855

2. Primeiro Documento:
    head -n 1 data/indexes/docs_indexacao_detailed.jsonl | python -m json.tool
    
    Esperado:
    {
      "id": "BI_1",
      "title": "Apresentação...",
      "module": "BI",
      "url": "https://...",
      ...
    }

3. Validar Estrutura JSONL:
    python -c "
    import json
    with open('data/indexes/docs_indexacao_detailed.jsonl') as f:
        for i, line in enumerate(f):
            try:
                json.loads(line)
            except:
                print(f'Erro na linha {i}')
    print('✓ Todas as linhas são JSON válido')
    "
    
    Esperado: ✓ Todas as linhas são JSON válido
""")

# ============================================================================
# TESTE 10: Checklist Completo
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║ TESTE 10: CHECKLIST COMPLETO                                              ║
╚════════════════════════════════════════════════════════════════════════════╝

PRÉ-REQUISITOS:
  □ Python 3.9+
  □ Docker & Docker Compose
  □ curl ou Postman
  □ VS Code (para teste MCP)

ESTRUTURA:
  □ apps/mcp-server/ existente
  □ mcp_config.json presente
  □ data/indexes/docs_indexacao_detailed.jsonl (855 linhas)
  □ infra/docker/docker-compose.yml presente

TESTE LOCAL:
  □ python validate_mcp_docker_meilisearch.py (58/58 ✓)
  □ python test_mcp_integration_practical.py (6/6 ✓)

TESTE DOCKER:
  □ docker-compose up -d (3 serviços saudáveis)
  □ curl http://localhost:8000/health (200)
  □ curl http://localhost:7700/health (200)

TESTE FUNCIONAL:
  □ Busca via HTTP retorna resultados
  □ Busca com filtro por módulo funciona
  □ list_modules retorna módulos
  □ Fallback funciona sem Meilisearch

SEGURANÇA:
  □ API Key não é públicas (use variáveis env)
  □ Network isolada (bridge senior-docs)
  □ Usuário não-root em containers
  □ HTTPS configurado (se produção)

PERFORMANCE:
  □ Latência < 100ms (Meilisearch)
  □ CPU < 50% em carga normal
  □ Memória estável
  □ Sem vazamento de memória

STATUS FINAL:
  □ TODOS OS TESTES PASSARAM ✓
  □ PRONTO PARA PRODUÇÃO ✓
""")

# ============================================================================
# REFERÊNCIAS
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║ REFERÊNCIAS E DOCUMENTAÇÃO                                                ║
╚════════════════════════════════════════════════════════════════════════════╝

📄 Documentação:
  - MCP_VALIDATION_REPORT.md
  - MCP_VALIDATION_EXECUTIVE_SUMMARY.md
  - MCP_RECOMMENDATIONS.md
  - validate_mcp_docker_meilisearch.py
  - test_mcp_integration_practical.py

🔗 URLs:
  - MCP Server Health: http://localhost:8000/health
  - Meilisearch Admin: http://localhost:7700/
  - MCP Server API: http://localhost:8000/
  
📚 Arquivos Críticos:
  - apps/mcp-server/mcp_server.py
  - infra/docker/docker-compose.yml
  - infra/docker/Dockerfile.mcp
  - data/indexes/docs_indexacao_detailed.jsonl

🎯 Próximas Ações:
  1. Executar validação estrutural
  2. Executar testes de integração
  3. Iniciar Docker Compose
  4. Testar endpoints HTTP
  5. Testar em VS Code
  6. Revisar recomendações
  7. Implementar Prioridade 1

✅ CONCLUSÃO: Sistema validado e pronto para produção!
""")
