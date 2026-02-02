#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente Python para OpenAPI Server Senior Documentation
======================================================

Exemplos de uso do MCP Server como API REST com OpenAPI.

Uso:
    python apps/mcp-server/openapi_client_example.py

Requisitos:
    pip install httpx pydantic
"""

import asyncio
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

try:
    import httpx
    from pydantic import BaseModel
except ImportError:
    print("❌ Requisitos não instalados. Execute:")
    print("   pip install httpx pydantic")
    sys.exit(1)

# ============================================================================
# Modelos (espelhando OpenAPI Server)
# ============================================================================

@dataclass
class DocumentItem:
    """Representa um documento encontrado"""
    id: str
    title: str
    module: str
    breadcrumb: Optional[str]
    content_preview: str
    url: Optional[str]
    score: Optional[float]
    
    def __str__(self):
        return f"📄 {self.title} ({self.module}) - Score: {self.score or 'N/A'}"


@dataclass
class SearchResult:
    """Resultado de uma busca"""
    success: bool
    query: str
    total: int
    limit: int
    offset: int
    results: List[DocumentItem]
    execution_time_ms: float
    
    def __str__(self):
        return (
            f"Busca: '{self.query}'\n"
            f"Resultados: {len(self.results)} de {self.total}\n"
            f"Tempo: {self.execution_time_ms:.1f}ms"
        )


@dataclass
class ModuleInfo:
    """Informações sobre um módulo"""
    name: str
    doc_count: int
    description: Optional[str] = None
    
    def __str__(self):
        return f"📦 {self.name}: {self.doc_count} documentos"


@dataclass
class Statistics:
    """Estatísticas da documentação"""
    success: bool
    total_documents: int
    total_modules: int
    modules: Dict[str, int]
    index_name: str
    meilisearch_version: Optional[str]
    last_indexed: Optional[str]
    
    def __str__(self):
        modules_str = "\n".join(
            f"  - {name}: {count}" 
            for name, count in sorted(self.modules.items())
        )
        return (
            f"📊 Estatísticas\n"
            f"Total de documentos: {self.total_documents}\n"
            f"Total de módulos: {self.total_modules}\n"
            f"Meilisearch v{self.meilisearch_version}\n"
            f"Módulos:\n{modules_str}"
        )


@dataclass
class HealthStatus:
    """Status de saúde do serviço"""
    status: str
    timestamp: str
    version: str
    meilisearch: Dict[str, Any]
    
    def __str__(self):
        healthy = "✅ Healthy" if self.status == "healthy" else "❌ Unhealthy"
        return f"{healthy} - v{self.version}"


# ============================================================================
# Cliente OpenAPI
# ============================================================================

class SeniorDocumentationClient:
    """
    Cliente para OpenAPI Server Senior Documentation
    
    Exemplo:
        async with SeniorDocumentationClient("http://localhost:8000") as client:
            results = await client.search("como configurar")
            stats = await client.get_stats()
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        verbose: bool = False
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.verbose = verbose
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Context manager entry"""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.client:
            await self.client.aclose()
    
    def _log(self, message: str):
        """Log mensagem se verbose ativo"""
        if self.verbose:
            print(f"[{datetime.now().isoformat()}] {message}")
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Faz requisição e retorna JSON"""
        if not self.client:
            raise RuntimeError("Cliente não inicializado. Use 'async with'")
        
        url = f"{self.base_url}{endpoint}"
        self._log(f"{method} {url}")
        
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._log(f"❌ HTTP {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            self._log(f"❌ Erro de requisição: {e}")
            raise
    
    async def health(self) -> HealthStatus:
        """
        Verifica saúde do serviço
        
        Returns:
            HealthStatus
        """
        self._log("Checando saúde...")
        data = await self._request("GET", "/health")
        return HealthStatus(
            status=data["status"],
            timestamp=data["timestamp"],
            version=data["version"],
            meilisearch=data["meilisearch"]
        )
    
    async def search(
        self,
        query: str,
        module: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> SearchResult:
        """
        Busca documentos
        
        Args:
            query: Texto para buscar
            module: Filtrar por módulo (opcional)
            limit: Máximo de resultados (1-100)
            offset: Offset para paginação
        
        Returns:
            SearchResult com documentos encontrados
        """
        self._log(f"Buscando '{query}' (módulo: {module}, limit: {limit})")
        
        payload = {
            "query": query,
            "limit": min(limit, 100),
            "offset": offset
        }
        if module:
            payload["module"] = module
        
        data = await self._request("POST", "/search", json=payload)
        
        results = [
            DocumentItem(
                id=doc["id"],
                title=doc["title"],
                module=doc["module"],
                breadcrumb=doc.get("breadcrumb"),
                content_preview=doc["content_preview"],
                url=doc.get("url"),
                score=doc.get("score")
            )
            for doc in data["results"]
        ]
        
        return SearchResult(
            success=data["success"],
            query=data["query"],
            total=data["total"],
            limit=data["limit"],
            offset=data["offset"],
            results=results,
            execution_time_ms=data["execution_time_ms"]
        )
    
    async def get_modules(self) -> List[ModuleInfo]:
        """
        Lista todos os módulos disponíveis
        
        Returns:
            Lista de ModuleInfo
        """
        self._log("Obtendo módulos...")
        data = await self._request("GET", "/modules")
        
        return [
            ModuleInfo(
                name=m["name"],
                doc_count=m["doc_count"],
                description=m.get("description")
            )
            for m in data["modules"]
        ]
    
    async def get_module_docs(self, module_name: str) -> List[DocumentItem]:
        """
        Obtém toda a documentação de um módulo
        
        Args:
            module_name: Nome do módulo (ex: 'RH')
        
        Returns:
            Lista de documentos do módulo
        """
        self._log(f"Obtendo docs do módulo '{module_name}'...")
        data = await self._request("GET", f"/modules/{module_name}")
        
        return [
            DocumentItem(
                id=doc["id"],
                title=doc["title"],
                module=doc["module"],
                breadcrumb=doc.get("breadcrumb"),
                content_preview=doc["content_preview"],
                url=doc.get("url"),
                score=doc.get("score")
            )
            for doc in data["documents"]
        ]
    
    async def get_stats(self) -> Statistics:
        """
        Obtém estatísticas da documentação
        
        Returns:
            Statistics com totais e contagem por módulo
        """
        self._log("Obtendo estatísticas...")
        data = await self._request("GET", "/stats")
        
        return Statistics(
            success=data["success"],
            total_documents=data["total_documents"],
            total_modules=data["total_modules"],
            modules=data["modules"],
            index_name=data["index_name"],
            meilisearch_version=data.get("meilisearch_version"),
            last_indexed=data.get("last_indexed")
        )


# ============================================================================
# Exemplos de Uso
# ============================================================================

async def example_basic_search():
    """Exemplo 1: Busca básica"""
    print("\n" + "="*60)
    print("Exemplo 1: Busca Básica")
    print("="*60 + "\n")
    
    async with SeniorDocumentationClient(verbose=True) as client:
        # Verificar saúde
        health = await client.health()
        print(f"Status: {health}\n")
        
        # Buscar
        result = await client.search("como configurar banco de dados")
        print(f"\n{result}\n")
        
        for doc in result.results[:3]:  # Primeiros 3
            print(doc)
            print(f"  Preview: {doc.content_preview[:100]}...\n")


async def example_filtered_search():
    """Exemplo 2: Busca com filtro de módulo"""
    print("\n" + "="*60)
    print("Exemplo 2: Busca com Filtro")
    print("="*60 + "\n")
    
    async with SeniorDocumentationClient(verbose=True) as client:
        result = await client.search(
            query="folha de pagamento",
            module="RH",
            limit=5
        )
        
        print(f"Encontrados: {len(result.results)} de {result.total}")
        for doc in result.results:
            print(doc)


async def example_modules_and_stats():
    """Exemplo 3: Listar módulos e estatísticas"""
    print("\n" + "="*60)
    print("Exemplo 3: Módulos e Estatísticas")
    print("="*60 + "\n")
    
    async with SeniorDocumentationClient(verbose=True) as client:
        # Módulos
        modules = await client.get_modules()
        print(f"📦 {len(modules)} módulos encontrados:\n")
        for module in modules[:5]:  # Primeiros 5
            print(f"  {module}")
        print()
        
        # Estatísticas
        stats = await client.get_stats()
        print(f"\n{stats}")


async def example_pagination():
    """Exemplo 4: Paginação de resultados"""
    print("\n" + "="*60)
    print("Exemplo 4: Paginação")
    print("="*60 + "\n")
    
    async with SeniorDocumentationClient(verbose=False) as client:
        query = "configurar"
        page_size = 5
        
        for page in range(3):
            offset = page * page_size
            result = await client.search(
                query=query,
                limit=page_size,
                offset=offset
            )
            
            print(f"📄 Página {page + 1} (offset: {offset}):")
            if not result.results:
                print("  Sem mais resultados")
                break
            
            for i, doc in enumerate(result.results, 1):
                print(f"  {i}. {doc.title} ({doc.module})")


async def example_module_docs():
    """Exemplo 5: Obter todos os docs de um módulo"""
    print("\n" + "="*60)
    print("Exemplo 5: Documentação Completa de Módulo")
    print("="*60 + "\n")
    
    async with SeniorDocumentationClient(verbose=True) as client:
        docs = await client.get_module_docs("RH")
        
        print(f"📦 Módulo RH: {len(docs)} documentos\n")
        for doc in docs[:5]:
            print(f"  - {doc.title}")


async def example_performance():
    """Exemplo 6: Teste de performance"""
    print("\n" + "="*60)
    print("Exemplo 6: Performance")
    print("="*60 + "\n")
    
    import time
    
    async with SeniorDocumentationClient(verbose=False) as client:
        start = time.time()
        
        # 10 buscas consecutivas
        for i in range(10):
            await client.search(f"teste {i}")
        
        elapsed = time.time() - start
        
        print(f"10 buscas em {elapsed:.2f}s")
        print(f"Média: {elapsed/10*1000:.1f}ms por request")


async def main():
    """Executa todos os exemplos"""
    
    print("╔" + "="*58 + "╗")
    print("║ Cliente OpenAPI - Senior Documentation             ║")
    print("║ Exemplos de Uso                                    ║")
    print("╚" + "="*58 + "╝")
    
    try:
        await example_basic_search()
        await example_filtered_search()
        await example_modules_and_stats()
        await example_pagination()
        await example_module_docs()
        await example_performance()
        
        print("\n" + "="*60)
        print("✅ Todos os exemplos executados com sucesso!")
        print("="*60 + "\n")
        
    except httpx.ConnectError:
        print("\n❌ Erro de conexão. Verifique se o servidor está rodando:")
        print("   docker-compose up -d mcp-server")
        print("   http://localhost:8000\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
