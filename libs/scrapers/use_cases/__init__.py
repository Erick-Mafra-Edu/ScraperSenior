"""
Use Cases Layer - Scrapers Use Cases

Este pacote contém os casos de uso (application services) que orquestram
a lógica de negócio usando os ports (interfaces).

Use cases são independentes de frameworks e implementações específicas,
dependendo apenas das interfaces definidas nos ports.
"""

from libs.scrapers.use_cases.scrape_documentation import ScrapeDocumentation
from libs.scrapers.use_cases.extract_release_notes import ExtractReleaseNotes
from libs.scrapers.use_cases.index_documents import IndexDocuments

__all__ = [
    "ScrapeDocumentation",
    "ExtractReleaseNotes",
    "IndexDocuments",
]
