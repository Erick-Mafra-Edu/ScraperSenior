# 🧪 Testes de Validação - Senior Documentation API

## Visão Geral

Suite completa de testes para validar a conformidade da API Senior Documentation com o schema OpenAPI 3.1.0.

## 📋 O que é testado

### 1. **Validação do Schema OpenAPI**
   - ✅ Estrutura básica (openapi, info, paths, components)
   - ✅ Versão OpenAPI 3.x
   - ✅ Campos obrigatórios na seção `info`
   - ✅ Definição de endpoints

### 2. **Endpoints Disponíveis**
   - 📍 `/health` - Health Check
   - 📍 `/search` - Buscar Documentação (POST)
   - 📍 `/modules` - Listar Módulos
   - 📍 `/modules/{module_name}` - Documentação de Módulo
   - 📍 `/stats` - Estatísticas da Base

### 3. **Testes Funcionais por Endpoint**

#### `/health` (GET)
- ✅ Retorna status 200
- ✅ Campos obrigatórios presentes
- ✅ Status válido (healthy/unhealthy)

#### `/stats` (GET)
- ✅ Retorna status 200
- ✅ total_documents presente
- ✅ total_modules presente
- ✅ Módulos listados corretamente

#### `/modules` (GET)
- ✅ Retorna status 200
- ✅ Lista de módulos em formato correto
- ✅ Cada módulo tem name e doc_count

#### `/search` (POST)
- ✅ Aceita query obrigatória
- ✅ Aceita módulo opcional
- ✅ Aceita limit opcional
- ✅ Retorna resultados ordenados por relevância
- ✅ Paginação com offset funciona
- ✅ Rejeita query vazia (HTTP 400)

## 🚀 Como Executar

### Opção 1: Executar todos os testes
```bash
python test_senior_api.py
```

### Opção 2: Executar com pytest
```bash
# Instalar pytest se necessário
pip install pytest

# Executar testes
pytest test_senior_api.py -v
```

### Opção 3: Testar contra servidor específico
```bash
python -c "from test_senior_api import SeniorAPITester; tester = SeniorAPITester('http://localhost:8000'); tester.run_all_tests()"
```

## 📊 Interpretando os Resultados

### Saída esperada (sucesso):
```
============================================================
📋 RESUMO DOS TESTES
============================================================
✅ PASSOU: schema_structure
✅ PASSOU: endpoints_defined
✅ PASSOU: health
✅ PASSOU: stats
✅ PASSOU: modules
✅ PASSOU: search_valid
✅ PASSOU: search_with_module
✅ PASSOU: search_pagination
============================================================
Total: 8 PASSOU | 0 FALHOU
Taxa de sucesso: 100.0%
============================================================
```

### Códigos de Status HTTP Esperados

| Endpoint | Método | Status Esperado | Descrição |
|----------|--------|-----------------|-----------|
| `/health` | GET | 200 | Serviço saudável |
| `/stats` | GET | 200 | Estatísticas obtidas |
| `/modules` | GET | 200 | Lista de módulos |
| `/modules/{name}` | GET | 200 | Documentação do módulo |
| `/modules/{name}` | GET | 404 | Módulo não encontrado |
| `/search` | POST | 200 | Busca realizada |
| `/search` | POST | 400 | Parâmetros inválidos |
| `/search` | POST | 503 | Meilisearch indisponível |

## 📝 Exemplos de Queries de Teste

```python
from test_senior_api import SeniorAPITester

# Criar testador
tester = SeniorAPITester('http://localhost:8000')

# Testar search com query específica
tester.test_search_endpoint_valid_query("como fazer backup")

# Testar search com filtro de módulo
tester.test_search_endpoint_with_module("configurar", "TECNOLOGIA")

# Executar todos os testes
results = tester.run_all_tests()
```

## 🔧 Configuração

### Variáveis de Ambiente (Futuros)
```bash
export SENIOR_API_URL=http://localhost:8000
export SENIOR_OPENAPI_PATH=./openapi.json
```

### Arquivo de Configuração (test_config.json)
```json
{
  "api_url": "http://localhost:8000",
  "openapi_path": "./openapi.json",
  "timeout": 10,
  "test_queries": [
    "configurar",
    "como fazer",
    "backup",
    "ntlm",
    "implantação"
  ]
}
```

## ⚠️ Falhas Comuns

### Erro: "Nenhuma conexão pôde ser feita"
- **Causa**: API não está rodando
- **Solução**: Verificar se a API está iniciada em `localhost:8000`

### Erro: "Conexão recusada (port 8000)"
- **Causa**: Porta 8000 não está acessível
- **Solução**: Verificar Docker, porta, firewall

### Teste "search_empty" falha
- **Causa**: API aceita query vazia em vez de rejeitar
- **Solução**: Validação no servidor precisa ser mais rigorosa

### Teste "search_pagination" mostra sobreposição
- **Causa**: Resultados não são determinísticos
- **Solução**: Normal em buscas por relevância

## 📈 Métricas de Qualidade

- **Taxa de sucesso esperada**: > 90%
- **Tempo de resposta esperado**: < 5s por endpoint
- **Cobertura de endpoints**: 100%
- **Validação de schema**: 100%

## 🐛 Reportar Problemas

Se um teste falhar:

1. **Anote o nome do teste**: Ex: "health"
2. **Copie a mensagem de erro**
3. **Verifique o servidor**:
   ```bash
   curl http://localhost:8000/health
   ```
4. **Verifique o schema**:
   ```bash
   curl http://localhost:8000/openapi.json
   ```

## 🔄 Testes Contínuos

Para executar os testes periodicamente:

```bash
# A cada 5 minutos
watch -n 300 'python test_senior_api.py'

# Com histórico
while true; do
  echo "=== Teste em $(date) ==="
  python test_senior_api.py
  sleep 300
done
```

## 📚 Referências

- OpenAPI 3.1.0: https://spec.openapis.org/
- Pytest: https://docs.pytest.org/
- Requests: https://requests.readthedocs.io/
