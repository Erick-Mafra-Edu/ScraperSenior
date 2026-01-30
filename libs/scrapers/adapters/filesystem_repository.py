"""
Adapter - FileSystem Repository

Implementação concreta de IDocumentRepository usando sistema de arquivos.
Salva documentos como arquivos JSON organizados por módulo.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from libs.scrapers.domain import Document, DocumentMetadata
from libs.scrapers.ports import IDocumentRepository


class FileSystemRepository(IDocumentRepository):
    """
    Adapter que implementa IDocumentRepository usando filesystem.
    
    Organiza documentos em estrutura de pastas por módulo,
    salvando cada documento como arquivo JSON individual.
    """
    
    def __init__(self, base_dir: str = "data/scraped/estruturado"):
        """
        Inicializa repositório.
        
        Args:
            base_dir: Diretório base para armazenar documentos
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache em memória (opcional, para performance)
        self._cache: Dict[str, Document] = {}
    
    def _get_document_path(self, doc_id: str, module: str) -> Path:
        """Retorna path do arquivo para um documento"""
        module_dir = self.base_dir / module
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # Usar hash do ID para nome de arquivo (evita caracteres inválidos)
        filename = f"{hashlib.md5(doc_id.encode()).hexdigest()}.json"
        return module_dir / filename
    
    async def save(self, document: Document) -> None:
        """
        Salva um documento.
        
        Args:
            document: Document a ser salvo
        """
        file_path = self._get_document_path(document.id, document.module)
        
        # Salvar como JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(document.to_dict(), f, ensure_ascii=False, indent=2)
        
        # Atualizar cache
        self._cache[document.id] = document
    
    async def save_many(self, documents: List[Document]) -> None:
        """
        Salva múltiplos documentos em batch.
        
        Args:
            documents: Lista de Documents
        """
        for doc in documents:
            await self.save(doc)
    
    async def find_by_id(self, doc_id: str) -> Optional[Document]:
        """
        Busca documento por ID.
        
        Args:
            doc_id: ID do documento
        
        Returns:
            Optional[Document]: Document se encontrado
        """
        # Verificar cache primeiro
        if doc_id in self._cache:
            return self._cache[doc_id]
        
        # Buscar em todos os módulos
        for module_dir in self.base_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            for file_path in module_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if data.get("id") == doc_id:
                        doc = Document.from_dict(data)
                        self._cache[doc_id] = doc
                        return doc
                except Exception:
                    continue
        
        return None
    
    async def find_by_url(self, url: str) -> Optional[Document]:
        """
        Busca documento por URL.
        
        Args:
            url: URL do documento
        
        Returns:
            Optional[Document]: Document se encontrado
        """
        all_docs = await self.get_all()
        for doc in all_docs:
            if doc.url == url:
                return doc
        return None
    
    async def find_by_module(self, module: str) -> List[Document]:
        """
        Busca todos os documentos de um módulo.
        
        Args:
            module: Nome do módulo
        
        Returns:
            List[Document]: Lista de documentos
        """
        documents = []
        module_dir = self.base_dir / module
        
        if not module_dir.exists():
            return documents
        
        for file_path in module_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                doc = Document.from_dict(data)
                documents.append(doc)
                self._cache[doc.id] = doc
                
            except Exception:
                continue
        
        return documents
    
    async def get_all(self) -> List[Document]:
        """
        Retorna todos os documentos.
        
        Returns:
            List[Document]: Lista de todos os documentos
        """
        documents = []
        
        for module_dir in self.base_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            module_docs = await self.find_by_module(module_dir.name)
            documents.extend(module_docs)
        
        return documents
    
    async def delete(self, doc_id: str) -> bool:
        """
        Remove um documento por ID.
        
        Args:
            doc_id: ID do documento
        
        Returns:
            bool: True se removido
        """
        doc = await self.find_by_id(doc_id)
        if not doc:
            return False
        
        file_path = self._get_document_path(doc_id, doc.module)
        
        try:
            file_path.unlink()
            if doc_id in self._cache:
                del self._cache[doc_id]
            return True
        except Exception:
            return False
    
    async def exists(self, doc_id: str) -> bool:
        """
        Verifica se documento existe.
        
        Args:
            doc_id: ID do documento
        
        Returns:
            bool: True se existe
        """
        return await self.find_by_id(doc_id) is not None
    
    async def count(self) -> int:
        """
        Retorna total de documentos.
        
        Returns:
            int: Número de documentos
        """
        count = 0
        for module_dir in self.base_dir.iterdir():
            if module_dir.is_dir():
                count += len(list(module_dir.glob("*.json")))
        return count
    
    async def save_metadata(self, metadata: DocumentMetadata) -> None:
        """
        Salva metadados agregados.
        
        Args:
            metadata: DocumentMetadata
        """
        metadata_path = self.base_dir.parent / "metadata" / "docs_metadata.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata.to_dict(), f, ensure_ascii=False, indent=2)
    
    async def get_metadata(self) -> Optional[DocumentMetadata]:
        """
        Recupera metadados agregados.
        
        Returns:
            Optional[DocumentMetadata]: Metadados se existirem
        """
        metadata_path = self.base_dir.parent / "metadata" / "docs_metadata.json"
        
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Criar DocumentMetadata a partir do dict
            # (simplificado, pode precisar de from_dict personalizado)
            return None  # TODO: implementar from_dict em DocumentMetadata
            
        except Exception:
            return None
    
    async def export_to_jsonl(self, filepath: str) -> int:
        """
        Exporta todos os documentos para arquivo JSONL.
        
        Args:
            filepath: Caminho do arquivo de saída
        
        Returns:
            int: Número de documentos exportados
        """
        documents = await self.get_all()
        
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for doc in documents:
                json.dump(doc.to_dict(), f, ensure_ascii=False)
                f.write('\n')
        
        return len(documents)
    
    async def clear(self) -> None:
        """
        Remove todos os documentos do repositório.
        
        Use com cuidado!
        """
        import shutil
        
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)
            self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self._cache.clear()
