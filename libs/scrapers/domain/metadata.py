"""
Domain Layer - Document Metadata Value Object

Representa metadados agregados de uma coleção de documentos.
Usado para análise e indexação.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import Counter


@dataclass
class DocumentMetadata:
    """
    Value Object para metadados de documentação.
    
    Agregação de informações sobre uma coleção de documentos,
    útil para análise, relatórios e configuração de indexadores.
    """
    
    # Informações gerais
    total_documents: int
    total_modules: int
    total_sources: int
    
    # Agregações
    documents_by_module: Dict[str, int] = field(default_factory=dict)
    documents_by_source: Dict[str, int] = field(default_factory=dict)
    documents_by_type: Dict[str, int] = field(default_factory=dict)
    
    # Estatísticas de conteúdo
    total_words: int = 0
    total_chars: int = 0
    avg_words_per_doc: float = 0.0
    avg_chars_per_doc: float = 0.0
    
    # Keywords mais comuns
    top_keywords: List[tuple] = field(default_factory=list)  # [(keyword, count), ...]
    
    # Timestamps
    first_scraped: Optional[datetime] = None
    last_scraped: Optional[datetime] = None
    generated_at: datetime = field(default_factory=datetime.now)
    
    # Configurações
    output_directory: Optional[str] = None
    index_name: Optional[str] = None
    
    # Dados adicionais
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_documents(cls, documents: List, output_dir: str = None) -> "DocumentMetadata":
        """
        Cria metadados a partir de uma lista de documentos.
        
        Args:
            documents: Lista de Document entities
            output_dir: Diretório de output (opcional)
        
        Returns:
            DocumentMetadata instance
        """
        if not documents:
            return cls(
                total_documents=0,
                total_modules=0,
                total_sources=0,
                output_directory=output_dir,
            )
        
        # Contadores
        by_module = Counter(doc.module for doc in documents)
        by_source = Counter(doc.source.value for doc in documents)
        by_type = Counter(doc.doc_type.value for doc in documents)
        
        # Estatísticas de conteúdo
        total_words = sum(doc.word_count() for doc in documents)
        total_chars = sum(doc.char_count() for doc in documents)
        
        # Keywords agregadas
        all_keywords = []
        for doc in documents:
            all_keywords.extend(doc.keywords)
        top_keywords = Counter(all_keywords).most_common(50)
        
        # Timestamps
        scraped_times = [doc.scraped_at for doc in documents]
        first_scraped = min(scraped_times) if scraped_times else None
        last_scraped = max(scraped_times) if scraped_times else None
        
        return cls(
            total_documents=len(documents),
            total_modules=len(by_module),
            total_sources=len(by_source),
            documents_by_module=dict(by_module),
            documents_by_source=dict(by_source),
            documents_by_type=dict(by_type),
            total_words=total_words,
            total_chars=total_chars,
            avg_words_per_doc=total_words / len(documents),
            avg_chars_per_doc=total_chars / len(documents),
            top_keywords=top_keywords,
            first_scraped=first_scraped,
            last_scraped=last_scraped,
            output_directory=output_dir,
        )
    
    def get_module_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas por módulo"""
        return {
            "total_modules": self.total_modules,
            "documents_by_module": self.documents_by_module,
            "largest_module": max(
                self.documents_by_module.items(),
                key=lambda x: x[1]
            )[0] if self.documents_by_module else None,
        }
    
    def get_content_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de conteúdo"""
        return {
            "total_documents": self.total_documents,
            "total_words": self.total_words,
            "total_chars": self.total_chars,
            "avg_words_per_doc": round(self.avg_words_per_doc, 2),
            "avg_chars_per_doc": round(self.avg_chars_per_doc, 2),
            "total_size_kb": round(self.total_chars / 1024, 2),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário (para serialização)"""
        return {
            "total_documents": self.total_documents,
            "total_modules": self.total_modules,
            "total_sources": self.total_sources,
            "documents_by_module": self.documents_by_module,
            "documents_by_source": self.documents_by_source,
            "documents_by_type": self.documents_by_type,
            "total_words": self.total_words,
            "total_chars": self.total_chars,
            "avg_words_per_doc": round(self.avg_words_per_doc, 2),
            "avg_chars_per_doc": round(self.avg_chars_per_doc, 2),
            "top_keywords": [
                {"keyword": kw, "count": count}
                for kw, count in self.top_keywords[:20]
            ],
            "first_scraped": self.first_scraped.isoformat() if self.first_scraped else None,
            "last_scraped": self.last_scraped.isoformat() if self.last_scraped else None,
            "generated_at": self.generated_at.isoformat(),
            "output_directory": self.output_directory,
            "index_name": self.index_name,
            "additional_info": self.additional_info,
        }
    
    def __repr__(self) -> str:
        return (
            f"DocumentMetadata("
            f"documents={self.total_documents}, "
            f"modules={self.total_modules}, "
            f"sources={self.total_sources})"
        )
