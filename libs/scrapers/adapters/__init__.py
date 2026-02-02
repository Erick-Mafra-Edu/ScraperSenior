"""
Adapters Layer - Scrapers Adapters

Este pacote contém as implementações concretas dos ports (interfaces).
Adapters conectam o core da aplicação com tecnologias específicas.

Adapters disponíveis:
- PlaywrightExtractor: Extração de conteúdo web usando Playwright
- UrlResolver: Manipulação de URLs usando urllib
- FileSystemRepository: Persistência em sistema de arquivos
- SeniorDocAdapter: Scraper para documentação Senior (MadCap + Astro)
- ZendeskAdapter: Scraper para Zendesk Help Center
"""

from libs.scrapers.adapters.playwright_extractor import PlaywrightExtractor
from libs.scrapers.adapters.url_resolver import UrlResolver
from libs.scrapers.adapters.filesystem_repository import FileSystemRepository
from libs.scrapers.adapters.senior_doc_adapter import SeniorDocAdapter
from libs.scrapers.adapters.zendesk_adapter import ZendeskAdapter
from libs.scrapers.adapters.playwright_worker_pool import PlaywrightWorkerPool
from libs.scrapers.adapters.docker_worker_orchestrator import DockerWorkerOrchestrator

__all__ = [
    "PlaywrightExtractor",
    "UrlResolver",
    "FileSystemRepository",
    "SeniorDocAdapter",
    "ZendeskAdapter",
    "PlaywrightWorkerPool",
    "DockerWorkerOrchestrator",
]
