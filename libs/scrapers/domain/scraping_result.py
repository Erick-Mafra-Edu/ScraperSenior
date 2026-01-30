"""
Domain Layer - Scraping Result Value Object

Representa o resultado de uma operação de scraping.
Value Object imutável que encapsula documentos extraídos e estatísticas.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
from libs.scrapers.domain.document import Document


@dataclass(frozen=True)
class ScrapingResult:
    """
    Value Object que representa o resultado de um scraping.
    
    Imutável e contém todos os documentos extraídos mais metadados
    sobre a operação de scraping.
    """
    
    # Documentos extraídos
    documents: tuple  # tuple de Documents (imutável)
    
    # Estatísticas
    total_documents: int
    successful_scrapes: int
    failed_scrapes: int
    skipped_urls: int
    
    # Timestamps
    started_at: datetime
    finished_at: datetime
    
    # Origem
    source_urls: tuple  # tuple de URLs (imutável)
    
    # Erros e avisos
    errors: tuple = field(default_factory=tuple)  # tuple de strings
    warnings: tuple = field(default_factory=tuple)
    
    # Metadados adicionais
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Converte listas para tuplas (imutabilidade)"""
        if isinstance(self.documents, list):
            object.__setattr__(self, 'documents', tuple(self.documents))
        if isinstance(self.source_urls, list):
            object.__setattr__(self, 'source_urls', tuple(self.source_urls))
        if isinstance(self.errors, list):
            object.__setattr__(self, 'errors', tuple(self.errors))
        if isinstance(self.warnings, list):
            object.__setattr__(self, 'warnings', tuple(self.warnings))
    
    @property
    def duration_seconds(self) -> float:
        """Duração total do scraping em segundos"""
        return (self.finished_at - self.started_at).total_seconds()
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso (0.0 a 1.0)"""
        total = self.successful_scrapes + self.failed_scrapes
        if total == 0:
            return 0.0
        return self.successful_scrapes / total
    
    @property
    def has_errors(self) -> bool:
        """Verifica se houve erros"""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Verifica se houve avisos"""
        return len(self.warnings) > 0
    
    def get_documents_by_module(self) -> Dict[str, List[Document]]:
        """Agrupa documentos por módulo"""
        by_module: Dict[str, List[Document]] = {}
        for doc in self.documents:
            if doc.module not in by_module:
                by_module[doc.module] = []
            by_module[doc.module].append(doc)
        return by_module
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas"""
        by_module = self.get_documents_by_module()
        
        return {
            "total_documents": self.total_documents,
            "successful_scrapes": self.successful_scrapes,
            "failed_scrapes": self.failed_scrapes,
            "skipped_urls": self.skipped_urls,
            "success_rate": f"{self.success_rate * 100:.2f}%",
            "duration_seconds": self.duration_seconds,
            "duration_formatted": self._format_duration(),
            "total_words": sum(doc.word_count() for doc in self.documents),
            "total_chars": sum(doc.char_count() for doc in self.documents),
            "by_module": {
                module: len(docs) for module, docs in by_module.items()
            },
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
        }
    
    def _format_duration(self) -> str:
        """Formata duração para string legível"""
        seconds = self.duration_seconds
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário (para serialização)"""
        return {
            "documents": [doc.to_dict() for doc in self.documents],
            "total_documents": self.total_documents,
            "successful_scrapes": self.successful_scrapes,
            "failed_scrapes": self.failed_scrapes,
            "skipped_urls": self.skipped_urls,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "source_urls": list(self.source_urls),
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "metadata": self.metadata,
            "statistics": self.get_statistics(),
        }
    
    def __repr__(self) -> str:
        return (
            f"ScrapingResult("
            f"documents={len(self.documents)}, "
            f"success_rate={self.success_rate:.2%}, "
            f"duration={self._format_duration()})"
        )
