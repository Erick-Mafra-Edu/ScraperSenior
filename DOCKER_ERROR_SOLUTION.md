# 🔧 Solução Rápida: Erro Docker Build "Snapshot Not Found"

**Erro**: 
```
ERROR: failed to prepare extraction snapshot "extract-841438503-5VSj...": 
parent snapshot does not exist: not found
```

**Causa**: Cache de build Docker corrompido ou inconsistente

---

## ⚡ Solução Rápida (3 minutos)

### Opção 1: Limpeza Completa (Recomendado)

```bash
# 1. Parar tudo
cd infra/docker
docker-compose down

# 2. Remover imagens
docker rmi senior-docs-mcp:latest 2>/dev/null || true
docker rmi senior-docs-scraper:latest 2>/dev/null || true

# 3. Limpar cache
docker buildx prune -af

# 4. Rebuildar sem cache
docker-compose build --no-cache

# 5. Verificar
docker images | grep senior-docs
```

**Tempo**: ~10-15 minutos (depende da internet)

---

### Opção 2: Solução via Script Python

```bash
python fix_docker_snapshot_error.py
```

Script automático que:
1. ✅ Para containers
2. ✅ Remove imagens antigas
3. ✅ Limpa cache buildx
4. ✅ Rebuilda do zero
5. ✅ Valida resultado

---

## 🔍 Diagnóstico Rápido

```bash
# Verificar espaço em disco
docker system df

# Ver tamanho do cache buildx
docker buildx du

# Verificar integridade
docker system prune -a
```

---

## 📊 Causa Raiz

Comum quando:
- ❌ Docker Desktop reiniciou durante build
- ❌ Docker volume foi movido
- ❌ Espaço em disco cheio durante build
- ❌ Múltiplos buildx/builders conflitando

---

## ✅ Prevenção

Para evitar no futuro:

```dockerfile
# Usar --no-cache em builds sensíveis
docker-compose build --no-cache

# Ou em Dockerfile
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y curl
```

---

## 🚀 Após Solucionar

1. **Testar containers**:
   ```bash
   docker-compose ps
   ```

2. **Verificar saúde**:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:7700/health
   ```

3. **Validar integração**:
   ```bash
   python validate_mcp_docker_meilisearch.py
   ```

---

## 💡 Se Continuar com Erro

### Opção A: Usar Docker sem Buildx
```bash
cd infra/docker
docker-compose build --no-cache --progress=plain
```

### Opção B: Aumentar espaço
```bash
# Windows (Docker Desktop)
# Settings → Resources → Disk image size → Aumentar para 100GB
```

### Opção C: Limpeza Nuclear
```bash
# ⚠️ Isso remove TUDO (use com cuidado!)
docker system prune -a --volumes
docker builder prune -a

# Depois rebuildar
docker-compose build --no-cache
```

---

## 📞 Se Precisar de Ajuda

- Erro persiste? Verifique espaço em disco: `docker system df`
- Muita memória? Reduza workers: `docker buildx create --use --driver docker-container`
- Offline? Use imagens pre-built: `docker load < image.tar`

---

**Tempo estimado para resolver**: 10-20 minutos

**Próximo passo**: Execute a solução e valide!
