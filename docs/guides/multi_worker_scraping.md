# Multi-Worker Scraping Guide

## 🚀 Overview

O sistema de scraper agora suporta **múltiplos workers paralelos** usando Playwright para processar URLs de forma muito mais rápida.

**Benefícios:**
- ✅ **2-3x mais rápido** que scraping sequencial
- ✅ Melhor utilização de CPU/RAM
- ✅ Configuração simples via JSON
- ✅ Retry automático com fallback
- ✅ Logging detalhado de progresso

---

## 📋 Arquitetura

```
PlaywrightWorkerPool (IBrowserWorkerPool)
├── Browser Instance (1)
│   └── Context (compartilhado = cookies/cache)
│       ├── Page 1 (Worker 0)
│       ├── Page 2 (Worker 1)
│       └── Page 3 (Worker 2)
│
├── asyncio.Queue
│   └── Distribuir URLs entre workers
│
└── asyncio.Semaphore
    └── Limitar concorrência
```

**Características:**
- Múltiplas **páginas no mesmo contexto** (evita re-login)
- **asyncio.Semaphore** para limite suave de concorrência
- **asyncio.Queue** para distribuição de trabalho
- **retry automático** com exponential backoff
- **logging detalhado** por worker

---

## ⚙️ Configuração

### 1. Via `scraper_config.json`

```json
{
  "concurrency": {
    "num_workers": 3,
    "enable_worker_pool": true,
    "max_urls_per_worker": 50,
    "worker_timeout_ms": 30000,
    "fallback_to_sequential": true
  }
}
```

**Parâmetros:**
- `num_workers` (int): Número de páginas paralelas (recomendado: 2-5)
- `enable_worker_pool` (bool): Ativar/desativar worker pool
- `max_urls_per_worker` (int): Máx. URLs por worker antes de avisos
- `worker_timeout_ms` (int): Timeout para operações de worker
- `fallback_to_sequential` (bool): Voltar para sequencial em caso de erro

### 2. Via Python

```python
from libs.scrapers.adapters import PlaywrightWorkerPool

# Criar pool
pool = PlaywrightWorkerPool(headless=True, timeout=30000)

# Inicializar com 3 workers
await pool.initialize(num_workers=3)

# Processar URLs
results = await pool.process_urls(
    urls=["https://example.com/1", "https://example.com/2"],
    worker_func=lambda url, worker_id: scrape(url, worker_id),
    show_progress=True
)

# Fechar
await pool.close()
```

---

## 📊 Recomendações de Workers

| Cenário | Workers | Notas |
|---------|---------|-------|
| Desenvolvimento | 1-2 | Menos memória, mais fácil debug |
| Scraping normal | 3-4 | Bom balance velocidade/estabilidade |
| Servidor poderoso | 5-8 | Mais paralelismo, maior throughput |
| Modo agressivo | 10+ | Alto risco de timeout/crash |

**Fórmula aproximada:**
```
num_workers ≈ (available_RAM_GB / 0.5) - 1
```

Cada worker Playwright consome ~500MB em média.

---

## 🔧 Exemplo: Integração com Scraper Existente

### Antes (Sequencial)
```python
async def scrape_urls(urls):
    results = []
    for url in urls:
        try:
            doc = await scrape_single_url(url)
            results.append(doc)
        except Exception as e:
            logger.error(f"Error: {e}")
    return results

# ⏱️ Lento: processa URLs uma por uma
result = asyncio.run(scrape_urls(urls))
```

### Depois (Com Workers)
```python
from libs.scrapers.adapters import PlaywrightWorkerPool

async def scrape_urls_with_workers(urls, num_workers=3):
    pool = PlaywrightWorkerPool(headless=True)
    
    try:
        await pool.initialize(num_workers=num_workers)
        
        results = await pool.process_urls(
            urls,
            worker_func=lambda url, wid: scrape_single_url(url, wid),
            show_progress=True
        )
        
        return results
        
    finally:
        await pool.close()

# ⚡ Rápido: processa URLs em paralelo
result = asyncio.run(scrape_urls_with_workers(urls, num_workers=3))
```

---

## 📈 Benchmark

### Exemplo: Scraping 100 URLs

```
Sequential (1 worker):
├── Total Time: 250s
├── Throughput: 0.4 URLs/s
└── Status: ⏳ Lento

With 3 Workers:
├── Total Time: 95s
├── Throughput: 1.05 URLs/s
└── Status: ✅ 2.6x mais rápido!

With 5 Workers:
├── Total Time: 65s
├── Throughput: 1.54 URLs/s
└── Status: ✅ 3.8x mais rápido!
```

---

## 🛡️ Tratamento de Erros

### Retry Automático

```python
# Retry com até 3 tentativas
results = await pool.process_urls_with_retry(
    urls=urls,
    worker_func=scrape_func,
    max_retries=3,
    show_progress=True
)

# Resultado incluirá todas as tentativas
successful = [r for r in results if r.success]
failed = [r for r in results if not r.success]
```

**Estratégia de Retry:**
1. Tentativa 1: Imediato
2. Tentativa 2: Aguarda 2s (exponential backoff)
3. Tentativa 3: Aguarda 4s

### Fallback para Sequencial

Se `fallback_to_sequential=true` em `scraper_config.json`:

```python
try:
    results = await pool.process_urls(urls, func)
except Exception as e:
    logger.warning("Worker pool failed, falling back to sequential")
    results = await process_sequentially(urls, func)
```

---

## 📊 Monitoramento

### Logs Detalhados

```
INFO: ✅ Initialized PlaywrightWorkerPool with 3 workers
INFO: Progress: 10/100 (10.0%) - Last: https://example.com/page1
DEBUG: ✅ Worker 0: https://example.com/page1... (1.23s)
DEBUG: ✅ Worker 1: https://example.com/page2... (1.45s)
DEBUG: ✅ Worker 2: https://example.com/page3... (0.98s)
...
INFO: ✅ Completed processing 100 URLs (98 successful)
```

### Estatísticas

```python
results = await pool.process_urls(urls, func)

# Calcular métricas
total_time = sum(r.duration_seconds for r in results)
success_rate = sum(1 for r in results if r.success) / len(results)
avg_time = total_time / len(results)
throughput = len(results) / total_time

print(f"Success Rate: {success_rate * 100:.1f}%")
print(f"Avg Time/URL: {avg_time:.2f}s")
print(f"Throughput: {throughput:.2f} URLs/s")
```

---

## ⚠️ Troubleshooting

### Problema: "Worker pool failed to initialize"

**Causa:** Falta de Playwright/Chromium instalado

```bash
# Solução
playwright install chromium
```

### Problema: "Out of memory"

**Causa:** Muitos workers para a memória disponível

```python
# Solução: Reduzir workers
await pool.initialize(num_workers=2)  # Ao invés de 5
```

### Problema: "Timeouts frequentes"

**Causa:** Worker timeout muito curto para URLs lentas

```json
{
  "concurrency": {
    "worker_timeout_ms": 60000
  }
}
```

### Problema: "Alguns URLs não são processados"

**Causa:** Worker travado ou exceção não capturada

**Solução:** Usar retry automático

```python
results = await pool.process_urls_with_retry(urls, func, max_retries=3)
```

---

## 🔍 WorkerResult

Cada URL processada retorna um `WorkerResult`:

```python
@dataclass
class WorkerResult:
    url: str                      # URL processada
    success: bool                 # Se foi bem sucedido
    result: Any = None            # Resultado (Document, etc)
    error: Optional[str] = None   # Mensagem de erro (se falho)
    worker_id: int = -1           # ID do worker que processou
    duration_seconds: float = 0.0 # Tempo total
```

**Exemplo de análise:**

```python
results = await pool.process_urls(urls, func)

# Analisar por worker
for worker_id in range(pool.get_num_workers()):
    worker_results = [r for r in results if r.worker_id == worker_id]
    avg_time = sum(r.duration_seconds for r in worker_results) / len(worker_results)
    print(f"Worker {worker_id}: {len(worker_results)} URLs, avg {avg_time:.2f}s")

# Encontrar URLs lentas
slow_urls = [r for r in results if r.duration_seconds > 5.0]
for result in slow_urls:
    print(f"Slow: {result.url} ({result.duration_seconds:.2f}s)")

# Encontrar erros comuns
error_counts = {}
for result in results:
    if not result.success:
        error = result.error.split(":")[0]  # Tipo de erro
        error_counts[error] = error_counts.get(error, 0) + 1

for error, count in error_counts.items():
    print(f"{error}: {count} occurrences")
```

---

## 🎯 Best Practices

### ✅ DO

```python
# ✅ Usar num_workers baseado em disponibilidade
num_workers = min(4, len(urls) // 10 + 1)

# ✅ Sempre fechar pool (use try/finally)
try:
    await pool.initialize(num_workers=3)
    results = await pool.process_urls(urls, func)
finally:
    await pool.close()

# ✅ Usar retry para URLs não confiáveis
results = await pool.process_urls_with_retry(urls, func, max_retries=3)

# ✅ Monitorar sucesso
success_rate = sum(1 for r in results if r.success) / len(results)
if success_rate < 0.95:
    logger.warning(f"Low success rate: {success_rate * 100:.1f}%")
```

### ❌ DON'T

```python
# ❌ Usar muitos workers
await pool.initialize(num_workers=20)  # Muito!

# ❌ Esquecer de fechar
pool = PlaywrightWorkerPool()
await pool.initialize(3)
await pool.process_urls(urls, func)
# Pool não foi fechado! 🔴

# ❌ Ignorar timeouts
# Sem configurar timeout apropriado para URLs lentas

# ❌ Processar URLs não validadas
# Validar URLs antes de enviar ao pool
```

---

## 📚 Referências

- [Playwright Python Docs](https://playwright.dev/python/)
- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [IBrowserWorkerPool Interface](../../libs/scrapers/ports/browser_worker_pool.py)
- [PlaywrightWorkerPool Implementation](../../libs/scrapers/adapters/playwright_worker_pool.py)
- [Worker Pool Examples](../../examples/worker_pool_usage.py)
