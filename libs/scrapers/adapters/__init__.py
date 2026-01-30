"""
Adapters Layer - Scrapers Adapters

Este pacote contém as implementações concretas dos ports (interfaces).
Adapters conectam o core da aplicação com tecnologias específicas.

Adapters disponíveis:
- PlaywrightExtractor: Extração de conteúdo web usando Playwright
- UrlResolver: Manipulação de URLs usando urllib
- FileSystemRepository: Persistência em sistema de arquivos
- SeniorDocAdapter: Scraper para documentação Senior (TODO)
- ZendeskAdapter: Scraper para Zendesk (TODO)
"""

from libs.scrapers.adapters.playwright_extractor import PlaywrightExtractor
from libs.scrapers.adapters.url_resolver import UrlResolver
from libs.scrapers.adapters.filesystem_repository import FileSystemRepository

__all__ = [
    "PlaywrightExtractor",
    "UrlResolver",
    "FileSystemRepository",
]
