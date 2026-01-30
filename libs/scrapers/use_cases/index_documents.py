"""
Use Case - Index Documents

Orquestra o processo de indexação de documentos para busca.
Prepara documentos para indexadores (JSONL, Meilisearch, etc.).
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from libs.scrapers.domain import Document, DocumentMetadata
from libs.scrapers.ports import IDocumentRepository


class IndexDocuments:
    """
    Use Case: Index Documents
    
    Coordena o processo de indexação:
    1. Recupera documentos do repositório
    2. Prepara dados para indexação
    3. Gera arquivos de índice (JSONL)
    4. Gera metadados agregados
    5. Exporta para diferentes formatos
    
    Separa a lógica de indexação da persistência.
    """
    
    def __init__(self, repository: IDocumentRepository):
        """
        Inicializa use case.
        
        Args:
            repository: Repositório de documentos
        """
        self.repository = repository
    
    async def execute(
        self,
        output_dir: Path,
        include_metadata: bool = True,
        format: str = "jsonl",
    ) -> Dict[str, Any]:
        """
        Executa indexação de todos os documentos.
        
        Args:
            output_dir: Diretório de saída
            include_metadata: Se True, gera arquivo de metadados
            format: Formato de saída ("jsonl", "json", etc.)
        
        Returns:
            Dict: Estatísticas da indexação
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Recuperar todos os documentos
        documents = await self.repository.get_all()
        
        if not documents:
            return {
                "total_documents": 0,
                "files_generated": [],
                "error": "No documents found",
            }
        
        files_generated = []
        
        # Exportar para JSONL
        if format == "jsonl":
            jsonl_path = output_dir / "docs_indexacao_detailed.jsonl"
            count = await self.repository.export_to_jsonl(str(jsonl_path))
            files_generated.append(str(jsonl_path))
        
        # Gerar metadados
        metadata = None
        if include_metadata:
            metadata = DocumentMetadata.from_documents(
                documents,
                output_dir=str(output_dir)
            )
            await self.repository.save_metadata(metadata)
            
            # Salvar metadados em arquivo JSON
            metadata_path = output_dir / "docs_metadata.json"
            await self._save_metadata_file(metadata, metadata_path)
            files_generated.append(str(metadata_path))
        
        # Gerar índice por módulo
        by_module_path = await self._generate_module_index(documents, output_dir)
        files_generated.append(str(by_module_path))
        
        return {
            "total_documents": len(documents),
            "files_generated": files_generated,
            "metadata": metadata.to_dict() if metadata else None,
            "by_module": metadata.documents_by_module if metadata else {},
        }
    
    async def reindex(
        self,
        output_dir: Path,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Reindexar todos os documentos.
        
        Args:
            output_dir: Diretório de saída
            force: Se True, força reindexação mesmo se arquivos existirem
        
        Returns:
            Dict: Estatísticas da reindexação
        """
        output_dir = Path(output_dir)
        
        # Verificar se já existe
        if not force and (output_dir / "docs_indexacao_detailed.jsonl").exists():
            return {
                "status": "skipped",
                "message": "Index already exists. Use force=True to reindex.",
            }
        
        return await self.execute(output_dir, include_metadata=True)
    
    async def index_module(
        self,
        module: str,
        output_dir: Path,
    ) -> Dict[str, Any]:
        """
        Indexa documentos de um módulo específico.
        
        Args:
            module: Nome do módulo
            output_dir: Diretório de saída
        
        Returns:
            Dict: Estatísticas da indexação
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Recuperar documentos do módulo
        documents = await self.repository.find_by_module(module)
        
        if not documents:
            return {
                "module": module,
                "total_documents": 0,
                "error": f"No documents found for module {module}",
            }
        
        # Exportar para JSONL
        jsonl_path = output_dir / f"{module}_docs.jsonl"
        await self._export_documents_jsonl(documents, jsonl_path)
        
        # Gerar metadados do módulo
        metadata = DocumentMetadata.from_documents(documents, str(output_dir))
        metadata_path = output_dir / f"{module}_metadata.json"
        await self._save_metadata_file(metadata, metadata_path)
        
        return {
            "module": module,
            "total_documents": len(documents),
            "files_generated": [str(jsonl_path), str(metadata_path)],
            "metadata": metadata.to_dict(),
        }
    
    async def get_indexation_status(self) -> Dict[str, Any]:
        """
        Retorna status da indexação atual.
        
        Returns:
            Dict: Status com estatísticas
        """
        total = await self.repository.count()
        metadata = await self.repository.get_metadata()
        
        status = {
            "total_documents": total,
            "is_indexed": total > 0,
            "metadata_available": metadata is not None,
        }
        
        if metadata:
            status.update({
                "total_modules": metadata.total_modules,
                "total_sources": metadata.total_sources,
                "last_indexed": metadata.last_scraped.isoformat() if metadata.last_scraped else None,
            })
        
        return status
    
    async def validate_index(self) -> Dict[str, Any]:
        """
        Valida integridade do índice.
        
        Returns:
            Dict: Relatório de validação
        """
        documents = await self.repository.get_all()
        
        errors = []
        warnings = []
        
        # Validar documentos
        for doc in documents:
            # Verificar campos obrigatórios
            if not doc.title:
                errors.append(f"Document {doc.id} has no title")
            if not doc.content:
                warnings.append(f"Document {doc.id} has empty content")
            if not doc.url:
                errors.append(f"Document {doc.id} has no URL")
        
        # Verificar duplicatas
        urls = [doc.url for doc in documents]
        duplicates = [url for url in urls if urls.count(url) > 1]
        if duplicates:
            warnings.append(f"Found duplicate URLs: {len(set(duplicates))}")
        
        return {
            "total_documents": len(documents),
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
    
    async def _generate_module_index(
        self,
        documents: List[Document],
        output_dir: Path,
    ) -> Path:
        """Gera índice agrupado por módulo"""
        import json
        
        by_module = {}
        for doc in documents:
            if doc.module not in by_module:
                by_module[doc.module] = []
            by_module[doc.module].append({
                "id": doc.id,
                "title": doc.title,
                "url": doc.url,
            })
        
        index_path = output_dir / "index_by_module.json"
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(by_module, f, ensure_ascii=False, indent=2)
        
        return index_path
    
    async def _export_documents_jsonl(
        self,
        documents: List[Document],
        filepath: Path,
    ) -> None:
        """Exporta documentos para JSONL"""
        import json
        
        with open(filepath, "w", encoding="utf-8") as f:
            for doc in documents:
                json.dump(doc.to_dict(), f, ensure_ascii=False)
                f.write("\n")
    
    async def _save_metadata_file(
        self,
        metadata: DocumentMetadata,
        filepath: Path,
    ) -> None:
        """Salva metadados em arquivo JSON"""
        import json
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metadata.to_dict(), f, ensure_ascii=False, indent=2)
