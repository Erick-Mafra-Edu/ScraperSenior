"""
Port - Document Repository Interface

Define o contrato para persistência de documentos.
Pode ser implementado como FileSystem, Database, S3, etc.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from libs.scrapers.domain import Document, DocumentMetadata


class IDocumentRepository(ABC):
    """
    Port (Interface) para repositório de documentos.
    
    Define operações de persistência agnósticas à tecnologia de storage.
    Permite trocar implementação (FileSystem, DB, S3) sem afetar o core.
    """
    
    @abstractmethod
    async def save(self, document: Document) -> None:
        """
        Salva um documento.
        
        Args:
            document: Document a ser salvo
        
        Raises:
            RepositoryError: Se houver erro ao salvar
        """
        pass
    
    @abstractmethod
    async def save_many(self, documents: List[Document]) -> None:
        """
        Salva múltiplos documentos em batch.
        
        Args:
            documents: Lista de Documents a serem salvos
        
        Raises:
            RepositoryError: Se houver erro ao salvar
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, doc_id: str) -> Optional[Document]:
        """
        Busca documento por ID.
        
        Args:
            doc_id: ID do documento
        
        Returns:
            Optional[Document]: Document se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    async def find_by_url(self, url: str) -> Optional[Document]:
        """
        Busca documento por URL.
        
        Args:
            url: URL do documento
        
        Returns:
            Optional[Document]: Document se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    async def find_by_module(self, module: str) -> List[Document]:
        """
        Busca todos os documentos de um módulo.
        
        Args:
            module: Nome do módulo
        
        Returns:
            List[Document]: Lista de documentos do módulo
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Document]:
        """
        Retorna todos os documentos.
        
        Returns:
            List[Document]: Lista de todos os documentos
        """
        pass
    
    @abstractmethod
    async def delete(self, doc_id: str) -> bool:
        """
        Remove um documento por ID.
        
        Args:
            doc_id: ID do documento
        
        Returns:
            bool: True se removido, False se não encontrado
        """
        pass
    
    @abstractmethod
    async def exists(self, doc_id: str) -> bool:
        """
        Verifica se documento existe.
        
        Args:
            doc_id: ID do documento
        
        Returns:
            bool: True se existe, False caso contrário
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Retorna total de documentos armazenados.
        
        Returns:
            int: Número de documentos
        """
        pass
    
    @abstractmethod
    async def save_metadata(self, metadata: DocumentMetadata) -> None:
        """
        Salva metadados agregados.
        
        Args:
            metadata: DocumentMetadata a ser salvo
        """
        pass
    
    @abstractmethod
    async def get_metadata(self) -> Optional[DocumentMetadata]:
        """
        Recupera metadados agregados.
        
        Returns:
            Optional[DocumentMetadata]: Metadados se existirem
        """
        pass
    
    @abstractmethod
    async def export_to_jsonl(self, filepath: str) -> int:
        """
        Exporta todos os documentos para arquivo JSONL.
        
        Args:
            filepath: Caminho do arquivo de saída
        
        Returns:
            int: Número de documentos exportados
        """
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """
        Remove todos os documentos do repositório.
        
        Use com cuidado!
        """
        pass
