#!/usr/bin/env python3
"""
Script para testar se o OpenAPI Server está funcionando corretamente
"""

import sys
from pathlib import Path

# Adicionar ao path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("🔍 Testando OpenAPI Server...")
print("=" * 70)

# Test 1: Verificar imports
print("\n1️⃣  Testando imports...")
try:
    from apps.mcp_server.openapi_adapter import create_app
    print("✅ openapi_adapter importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar openapi_adapter: {e}")
    sys.exit(1)

try:
    from apps.mcp_server.mcp_server import SeniorDocumentationMCP
    print("✅ SeniorDocumentationMCP importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar SeniorDocumentationMCP: {e}")
    sys.exit(1)

# Test 2: Criar app FastAPI
print("\n2️⃣  Criando aplicação FastAPI...")
try:
    app = create_app(
        meilisearch_url="http://localhost:7700",
        api_key="5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"
    )
    print("✅ Aplicação FastAPI criada com sucesso")
except Exception as e:
    print(f"❌ Erro ao criar aplicação: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Verificar endpoints
print("\n3️⃣  Verificando endpoints registrados...")
try:
    routes = [route.path for route in app.routes]
    print(f"✅ {len(routes)} endpoints encontrados:")
    for route in sorted(routes):
        print(f"   - {route}")
    
    # Verificar se /openapi.json existe
    if "/openapi.json" in routes:
        print("\n✅ /openapi.json está registrado!")
    else:
        print("\n⚠️  /openapi.json NÃO está registrado!")
        print("   Endpoints encontrados:")
        print("   - /docs (Swagger UI)")
        print("   - /redoc (ReDoc)")
        print("   - /openapi.json (Schema OpenAPI)")
except Exception as e:
    print(f"❌ Erro ao verificar endpoints: {e}")
    sys.exit(1)

# Test 4: Verificar schema OpenAPI
print("\n4️⃣  Verificando schema OpenAPI...")
try:
    schema = app.openapi()
    if schema:
        print(f"✅ Schema OpenAPI gerado com sucesso")
        print(f"   Título: {schema.get('info', {}).get('title')}")
        print(f"   Versão: {schema.get('info', {}).get('version')}")
        print(f"   Endpoints: {len(schema.get('paths', {}))}")
    else:
        print("❌ Schema OpenAPI vazio!")
except Exception as e:
    print(f"❌ Erro ao gerar schema: {e}")
    sys.exit(1)

# Test 5: Testar GET /
print("\n5️⃣  Testando GET / ...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/")
    print(f"✅ GET / respondeu com status {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Nome: {data.get('name')}")
        print(f"   Versão: {data.get('version')}")
except Exception as e:
    print(f"❌ Erro ao testar GET /: {e}")

# Test 6: Testar GET /openapi.json
print("\n6️⃣  Testando GET /openapi.json ...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/openapi.json")
    print(f"✅ GET /openapi.json respondeu com status {response.status_code}")
    if response.status_code == 200:
        schema = response.json()
        print(f"   Título: {schema.get('info', {}).get('title')}")
        print(f"   Versão: {schema.get('info', {}).get('version')}")
        print(f"   Endpoints: {len(schema.get('paths', {}))}")
    else:
        print(f"❌ Status {response.status_code}")
        print(f"   Body: {response.text}")
except Exception as e:
    print(f"❌ Erro ao testar GET /openapi.json: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ Testes concluídos!\n")
