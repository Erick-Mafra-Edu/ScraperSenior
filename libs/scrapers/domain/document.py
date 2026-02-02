"""
Domain Layer - Document Entity

Entidade central do domínio de scraping de documentação.
Representa um documento extraído de qualquer fonte (Senior Docs, Zendesk, etc.).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class DocumentType(Enum):
    """Tipos de documento suportados"""
    TECHNICAL_DOC = "technical_doc"
    RELEASE_NOTE = "release_note"
    HELP_ARTICLE = "help_article"
    API_DOC = "api_doc"
    TUTORIAL = "tutorial"
    UNKNOWN = "unknown"


class DocumentSource(Enum):
    """Fontes de documentação"""
    SENIOR_MADCAP = "senior_madcap"
    SENIOR_ASTRO = "senior_astro"
    ZENDESK = "zendesk"
    SUPPORT_SENIOR = "support_senior"
    UNKNOWN = "unknown"


@dataclass
class Document:
    """
    Entidade Document - Representa um documento scraped.
    
    Esta é a entidade central do domínio, agnóstica à fonte de dados.
    Contém apenas informações de negócio, sem detalhes técnicos de scraping.
    """
    
    # Identificadores
    id: str  # Unique identifier (hash ou ID da fonte)
    url: str  # URL original do documento
    
    # Conteúdo
    title: str
    content: str  # Texto completo do documento
    
    # Metadados de negócio
    module: str  # Módulo/categoria (ex: "crm", "gestao-pessoas")
    doc_type: DocumentType
    source: DocumentSource
    
    # Hierarquia e navegação
    breadcrumb: List[str] = field(default_factory=list)  # Caminho de navegação
    parent_id: Optional[str] = None
    section: Optional[str] = None
    
    # Estrutura do conteúdo
    headers: List[str] = field(default_factory=list)  # H1, H2, H3...
    keywords: List[str] = field(default_factory=list)
    
    # Timestamps
    scraped_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    # Dados adicionais (extensível)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Metadados de scraping (worker pool)
    processed_by_worker: int = -1  # ID do worker que processou este doc (-1 = não usado worker)
    scraping_duration_seconds: float = 0.0  # Tempo total de scraping deste doc
    
    def __post_init__(self):
        """Validações após inicialização"""
        if not self.id:
            raise ValueError("Document ID cannot be empty")
        if not self.url:
            raise ValueError("Document URL cannot be empty")
        if not self.title:
            raise ValueError("Document title cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte documento para dicionário (para serialização)"""
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "module": self.module,
            "doc_type": self.doc_type.value,
            "source": self.source.value,
            "breadcrumb": self.breadcrumb,
            "parent_id": self.parent_id,
            "section": self.section,
            "headers": self.headers,
            "keywords": self.keywords,
            "scraped_at": self.scraped_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "metadata": self.metadata,
            "processed_by_worker": self.processed_by_worker,
            "scraping_duration_seconds": self.scraping_duration_seconds,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Cria documento a partir de dicionário"""
        return cls(
            id=data["id"],
            url=data["url"],
            title=data["title"],
            content=data["content"],
            module=data["module"],
            doc_type=DocumentType(data["doc_type"]),
            source=DocumentSource(data["source"]),
            breadcrumb=data.get("breadcrumb", []),
            parent_id=data.get("parent_id"),
            section=data.get("section"),
            headers=data.get("headers", []),
            keywords=data.get("keywords", []),
            scraped_at=datetime.fromisoformat(data["scraped_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            published_at=datetime.fromisoformat(data["published_at"]) if data.get("published_at") else None,
            metadata=data.get("metadata", {}),
            processed_by_worker=data.get("processed_by_worker", -1),
            scraping_duration_seconds=data.get("scraping_duration_seconds", 0.0),
        )
    
    def get_breadcrumb_path(self) -> str:
        """Retorna breadcrumb como string formatada"""
        return " > ".join(self.breadcrumb)
    
    def word_count(self) -> int:
        """Retorna contagem de palavras do conteúdo"""
        return len(self.content.split())
    
    def char_count(self) -> int:
        """Retorna contagem de caracteres do conteúdo"""
        return len(self.content)
    
    def is_release_note(self) -> bool:
        """Verifica se é nota de versão"""
        return self.doc_type == DocumentType.RELEASE_NOTE
    
    def __repr__(self) -> str:
        return f"Document(id={self.id}, title={self.title[:50]}..., source={self.source.value})"
