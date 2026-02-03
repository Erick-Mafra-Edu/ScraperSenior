# 🔍 OpenAPI Endpoint Issue - Root Cause Analysis

## Problem
When accessing `http://localhost:8000/openapi.json`, getting 404 "Not found"

## Root Cause
The Docker container is running **MCP Server** (Model Context Protocol), NOT the FastAPI OpenAPI adapter.

### Current Setup (Running)
```
Dockerfile CMD: python -u apps/mcp-server/mcp_server_docker.py
Server Type: MCP Protocol (stdio/HTTP hybrid)
Available Endpoints:
  - GET  /health
  - GET  /ready
  - GET  /stats
  - GET  /tools
  - POST /call
  - POST /search
```

### Expected Setup (For OpenAPI)
```
Required: python -u apps/mcp-server/openapi_adapter.py
Server Type: FastAPI with OpenAPI specification
Available Endpoints:
  - GET  /openapi.json  ← This endpoint missing!
  - GET  /docs          ← Swagger UI
  - GET  /redoc         ← ReDoc
  + All MCP endpoints
```

## Why `/openapi.json` Returns 404

The **MCP Server** doesn't have OpenAPI schema endpoints:
- MCP Protocol is a different specification from OpenAPI
- MCP uses JSON-RPC over stdio or HTTP
- OpenAPI endpoints are only in `openapi_adapter.py`

The Docker container runs `mcp_server_docker.py`, which:
- ✅ Provides MCP tools (search_docs, list_modules, etc.)
- ✅ Exposes HTTP endpoints at `/health`, `/stats`, etc.
- ❌ Does NOT serve `/openapi.json`
- ❌ Does NOT provide `/docs` (Swagger)

## Solution Options

### Option 1: Use OpenAPI Adapter (FastAPI)
Change Dockerfile to run the adapter instead:
```dockerfile
CMD ["python", "-u", "apps/mcp-server/openapi_adapter.py"]
```

**Pros:**
- Full OpenAPI specification
- Swagger UI at `/docs`
- ReDoc at `/redoc`
- Auto-generated schema

**Cons:**
- Loses MCP stdio mode
- Different interface

### Option 2: Use Both (Dual Mode)
Create entrypoint that runs both MCP and OpenAPI:
```dockerfile
CMD ["python", "-u", "apps/mcp-server/mcp_entrypoint_dual.py"]
```

**Pros:**
- OpenAPI schema available
- MCP mode still works
- Both interfaces available

**Cons:**
- Requires dual mode implementation

### Option 3: Keep MCP, Document It
The current MCP server IS working correctly:
- All endpoints responding
- Search functionality working
- Data retrieval working

**The `/openapi.json` not existing is by design** - it's MCP, not OpenAPI.

## Recommendation

### If You Need OpenAPI Schema:
The `openapi.json` file you created exists locally:
```bash
# Serve it directly from the file
http://localhost:8000/api/openapi.json
# (This would work if using openapi_adapter.py)

# Or access the file directly
c:\Users\Digisys\scrapyTest\openapi.json
```

### Current MCP Server IS Functional
The server IS working correctly for MCP purposes:
- ✅ Health check: `http://localhost:8000/health`
- ✅ Search: `POST http://localhost:8000/search`
- ✅ Stats: `http://localhost:8000/stats`
- ✅ All tools available

### To Enable OpenAPI Endpoints
Update `Dockerfile.mcp`:
```dockerfile
# Change from:
CMD ["python", "-u", "apps/mcp-server/mcp_server_docker.py"]

# To:
CMD ["python", "-u", "apps/mcp-server/openapi_adapter.py"]
```

Then rebuild and restart:
```bash
docker-compose down
docker-compose up -d --build
```

## Quick Test - Verify Server is Working

The fact that these work proves the server IS functional:
```bash
# ✅ This works
curl http://localhost:8000/health
→ {"status": "healthy", ...}

# ✅ This works
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"configurar","limit":3}'
→ Returns 3 documents with proper data

# ✅ This works
curl http://localhost:8000/stats
→ {"stats": {"total_documents": 10344, ...}}
```

The `/openapi.json` returning 404 is **not an error** - it's just not implemented in MCP server.

## Summary

| Aspect | Status |
|--------|--------|
| Server running | ✅ Yes |
| API endpoints | ✅ Working |
| Search functionality | ✅ Working |
| Data retrieval | ✅ Working |
| `/openapi.json` endpoint | ❌ Not in MCP mode |
| OpenAPI schema | ✅ Exists locally at openapi.json |

---

## Your Choice

1. **Keep MCP Server (Current):** Server works perfectly. The null response is expected.
2. **Switch to OpenAPI:** Modify Dockerfile to use `openapi_adapter.py`. Adds schema endpoints.
3. **Use Dual Mode:** Run both MCP and OpenAPI simultaneously (requires dual entrypoint).

**Recommendation:** Keep current MCP setup since everything is working. The openapi.json file exists locally for reference.
