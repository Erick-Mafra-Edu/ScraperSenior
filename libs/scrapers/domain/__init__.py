"""
Domain Layer - Scrapers Domain

Este pacote contém as entidades e value objects do domínio de scraping.
São classes que representam conceitos de negócio, independentes de
frameworks ou detalhes técnicos.
"""

from libs.scrapers.domain.document import Document, DocumentType, DocumentSource
from libs.scrapers.domain.scraping_result import ScrapingResult
from libs.scrapers.domain.metadata import DocumentMetadata

__all__ = [
    "Document",
    "DocumentType",
    "DocumentSource",
    "ScrapingResult",
    "DocumentMetadata",
]
