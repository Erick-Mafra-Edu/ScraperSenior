"""
Ports Layer - Scrapers Ports

Este pacote contém as interfaces (ports) que definem os contratos
entre o core da aplicação e as implementações externas (adapters).

Seguindo a Arquitetura Hexagonal:
- O core depende apenas destas interfaces
- Os adapters implementam estas interfaces
- Permite trocar implementações sem afetar o core
"""

from libs.scrapers.ports.document_scraper import IDocumentScraper
from libs.scrapers.ports.document_repository import IDocumentRepository
from libs.scrapers.ports.content_extractor import IContentExtractor
from libs.scrapers.ports.url_resolver import IUrlResolver
from libs.scrapers.ports.browser_worker_pool import IBrowserWorkerPool, WorkerResult

__all__ = [
    "IDocumentScraper",
    "IDocumentRepository",
    "IContentExtractor",
    "IUrlResolver",
    "IBrowserWorkerPool",
    "WorkerResult",
]
