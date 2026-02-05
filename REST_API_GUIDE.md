# MCP HTTP Server - REST API Guide

## Overview

The MCP HTTP Server provides **two complementary interfaces**:

1. **JSON-RPC 2.0** (POST /mcp) - Full MCP protocol support
2. **REST API** (GET /api/*) - Simple HTTP GET endpoints

The REST API makes it easy to integrate with tools like Open WebUI, frontend applications, and simple HTTP clients.

---

## Quick Start

### 1. Health Check
```bash
curl -X GET http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2024-12-19T14:30:45.123456"
}
```

### 2. Search Documentation
```bash
curl -X GET "http://localhost:8000/api/search?query=configurar+LSP&limit=5"
```

Response:
```json
{
  "status": "success",
  "query": "configurar LSP",
  "parsed_query": "\"configurar LSP\"",
  "strategy": "auto",
  "module_filter": null,
  "count": 3,
  "results": [
    {
      "id": "doc_123",
      "title": "Configurar LSP",
      "url": "https://...",
      "module": "Help Center",
      "snippet": "..."
    },
    ...
  ]
}
```

### 3. List Available Modules
```bash
curl -X GET http://localhost:8000/api/modules
```

Response:
```json
{
  "status": "success",
  "total_modules": 12,
  "modules": [
    "Help Center",
    "Releases",
    "API Documentation",
    ...
  ]
}
```

### 4. Get Docs from Specific Module
```bash
curl -X GET "http://localhost:8000/api/modules/Help%20Center?limit=10"
```

Response:
```json
{
  "status": "success",
  "module": "Help Center",
  "count": 10,
  "docs": [
    {
      "id": "doc_456",
      "title": "Getting Started",
      "url": "https://...",
      "summary": "..."
    },
    ...
  ]
}
```

### 5. Get Documentation Statistics
```bash
curl -X GET http://localhost:8000/api/stats
```

Response:
```json
{
  "status": "success",
  "data": {
    "total_documents": 10456,
    "total_modules": 12,
    "indexed_date": "2024-12-19",
    "index_size": "45.3 MB"
  }
}
```

---

## Endpoints Reference

### GET /api/search

Search the documentation with optional query parsing.

**Parameters:**
- `query` (required): Search term(s)
  - Example: `query=configurar+LSP`
  - Supports multiple words: `query=setup+environment+variables`
- `limit` (optional): Max results to return (default: 5, max: 100)
- `module` (optional): Filter by module name
  - Example: `module=Help%20Center`
- `strategy` (optional): Query parsing strategy (default: `auto`)
  - `auto` - Intelligent selection based on query structure
  - `quoted` - Wrap query in quotes for exact phrase matching: `"configurar LSP"`
  - `and` - Insert AND operator between terms: `configurar AND LSP`

**Examples:**

Search for exact phrase:
```bash
curl -X GET "http://localhost:8000/api/search?query=configurar+LSP&strategy=quoted"
```

Search with AND operator:
```bash
curl -X GET "http://localhost:8000/api/search?query=setup+environment&strategy=and&limit=10"
```

Filter by module:
```bash
curl -X GET "http://localhost:8000/api/search?query=LSP&module=Help%20Center&limit=20"
```

**Response:**
```json
{
  "status": "success" | "error",
  "query": "original query",
  "parsed_query": "transformed query",
  "strategy": "strategy used",
  "module_filter": "module or null",
  "count": 5,
  "results": [
    {
      "id": "document id",
      "title": "Document Title",
      "url": "https://...",
      "module": "Module Name",
      "snippet": "relevant excerpt"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Missing query parameter
- `500 Internal Server Error` - Server error (check logs)

---

### GET /api/modules

List all available documentation modules.

**Parameters:** None

**Example:**
```bash
curl -X GET http://localhost:8000/api/modules
```

**Response:**
```json
{
  "status": "success",
  "total_modules": 12,
  "modules": [
    "Help Center",
    "Release Notes",
    "API Documentation",
    "Installation Guide",
    ...
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

---

### GET /api/modules/{module_name}

Get all documentation for a specific module.

**Parameters:**
- `module_name` (required): Name of the module (URL encoded)
- `limit` (optional): Max results to return (default: 20, max: 100)

**Examples:**

Get all Help Center docs:
```bash
curl -X GET "http://localhost:8000/api/modules/Help%20Center"
```

Get first 10 Release Notes docs:
```bash
curl -X GET "http://localhost:8000/api/modules/Release%20Notes?limit=10"
```

**Response:**
```json
{
  "status": "success",
  "module": "Help Center",
  "count": 15,
  "docs": [
    {
      "id": "doc_id",
      "title": "Document Title",
      "url": "https://...",
      "summary": "Document summary",
      "date": "2024-12-19"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid module name
- `500 Internal Server Error` - Server error

---

### GET /api/stats

Get statistics about the documentation database.

**Parameters:** None

**Example:**
```bash
curl -X GET http://localhost:8000/api/stats
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_documents": 10456,
    "total_modules": 12,
    "indexed_date": "2024-12-19T14:30:45",
    "index_size": "45.3 MB",
    "languages": ["pt-BR", "en"],
    "last_update": "2024-12-19T15:45:30"
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

---

## Query Parsing Strategies

The `/api/search` endpoint supports three query parsing strategies:

### Strategy: `auto` (Default)
Intelligently selects the best parsing strategy based on query structure.
- **Multi-word queries** → uses `quoted` strategy
- **Single-word queries** → passes through unchanged

Examples:
```bash
# "configurar LSP" → searches for exact phrase
curl "http://localhost:8000/api/search?query=configurar+LSP&strategy=auto"

# "LSP" → searches for term as-is
curl "http://localhost:8000/api/search?query=LSP&strategy=auto"
```

### Strategy: `quoted`
Wraps the query in quotes for exact phrase matching.

Transforms:
- `configurar LSP` → `"configurar LSP"`
- `setup environment` → `"setup environment"`

Use when you want exact phrase matches:
```bash
curl "http://localhost:8000/api/search?query=configurar+LSP&strategy=quoted"
```

### Strategy: `and`
Inserts AND operator between terms for boolean search.

Transforms:
- `configurar LSP` → `configurar AND LSP`
- `setup environment variables` → `setup AND environment AND variables`

Use when you want all terms to be present:
```bash
curl "http://localhost:8000/api/search?query=configurar+LSP&strategy=and"
```

---

## CORS Support

All REST endpoints support **CORS (Cross-Origin Resource Sharing)**:

- **Allowed Origins:** All (`*`)
- **Allowed Methods:** GET, POST, DELETE, OPTIONS
- **Preflight Cache:** 3600 seconds (1 hour)

This means you can call these endpoints from:
- Frontend applications (JavaScript/React/Vue)
- Open WebUI
- Any browser-based tools
- Mobile apps

Example from JavaScript:
```javascript
// Browser-based search
const response = await fetch(
  'http://localhost:8000/api/search?query=LSP&limit=5'
);
const data = await response.json();
console.log(data.results);
```

---

## Integration Examples

### JavaScript/React
```javascript
// React hook for searching
function useDocSearch(query, limit = 5) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) return;
    
    setLoading(true);
    fetch(`/api/search?query=${encodeURIComponent(query)}&limit=${limit}`)
      .then(r => r.json())
      .then(data => setResults(data.results))
      .finally(() => setLoading(false));
  }, [query, limit]);

  return { results, loading };
}
```

### Python
```python
import requests

# Search documentation
response = requests.get(
    'http://localhost:8000/api/search',
    params={
        'query': 'configurar LSP',
        'limit': 10,
        'strategy': 'auto'
    }
)
results = response.json()
print(f"Found {results['count']} results")
for doc in results['results']:
    print(f"- {doc['title']}")
```

### cURL
```bash
# Search
curl "http://localhost:8000/api/search?query=LSP&limit=5"

# With module filter
curl "http://localhost:8000/api/search?query=setup&module=Help%20Center"

# With different strategy
curl "http://localhost:8000/api/search?query=setup+environment&strategy=and"

# List modules
curl http://localhost:8000/api/modules

# Get module docs
curl "http://localhost:8000/api/modules/Help%20Center?limit=10"

# Get stats
curl http://localhost:8000/api/stats
```

---

## Comparison: REST vs JSON-RPC

| Aspect | REST API | JSON-RPC |
|--------|----------|----------|
| **Interface** | Simple HTTP GET | POST with JSON payload |
| **Learning Curve** | Easy (standard HTTP) | Steeper (protocol knowledge) |
| **Best For** | Frontend, simple tools | Complex workflows, scripts |
| **Example** | `GET /api/search?q=...` | `POST /mcp` with JSON body |
| **CORS** | Built-in ✓ | Requires setup |
| **Browser Usage** | Direct ✓ | Requires wrapper |

**Use REST API when:**
- ✓ Integrating with Open WebUI
- ✓ Building frontend applications
- ✓ Using simple HTTP clients
- ✓ Need browser-based access

**Use JSON-RPC when:**
- ✓ Need full MCP protocol features
- ✓ Building complex automation
- ✓ Need resource streams
- ✓ Working with older clients

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message explaining what went wrong"
}
```

Common HTTP status codes:
- **200** - Success
- **400** - Bad request (invalid parameters)
- **404** - Not found (endpoint doesn't exist)
- **500** - Internal server error (check server logs)
- **502** - Bad gateway (server not running)

Example error:
```bash
$ curl "http://localhost:8000/api/search"
# Missing 'query' parameter

{"detail":"query parameter is required"}
```

---

## Performance & Limits

- **Default result limit:** 5 documents
- **Maximum result limit:** 100 documents
- **Request timeout:** 30 seconds
- **CORS preflight cache:** 1 hour
- **Server response time:** ~100-500ms for typical searches

---

## Debugging

### Enable debug logging
Set environment variable:
```bash
export LOG_LEVEL=debug
python apps/mcp-server/mcp_server_http.py
```

### Check server logs
```bash
# Docker
docker-compose logs -f mcp-server

# Direct Python
# Logs appear in console output
```

### Test connectivity
```bash
curl -v http://localhost:8000/health
```

---

## See Also

- [MCP Server Documentation](./MCP_ARCHITECTURE_CORRECTED.md)
- [OpenAPI Specification](./openapi.json)
- [Query Parsing Guide](./OPENAPI_SETUP_GUIDE.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
