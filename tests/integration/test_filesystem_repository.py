"""
Testes de integração - FileSystemRepository

Testa o adapter FileSystemRepository com sistema de arquivos real.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from libs.scrapers.adapters import FileSystemRepository
from libs.scrapers.domain import Document, DocumentType, DocumentSource


class TestFileSystemRepositoryIntegration:
    """Testes de integração para FileSystemRepository"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def repository(self, temp_dir):
        """Cria repositório com diretório temporário"""
        return FileSystemRepository(base_path=temp_dir)
    
    @pytest.fixture
    def sample_document(self):
        """Cria documento de exemplo"""
        return Document(
            id="test-123",
            url="https://documentacao.senior.com.br/gestao-pessoal/6.10.4/index.html",
            title="Test Document",
            content="This is test content for integration test.",
            module="gestao-pessoal",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.SENIOR_MADCAP,
            scraped_at=datetime.now(),
            metadata={"version": "6.10.4"}
        )
    
    @pytest.mark.asyncio
    async def test_save_document(self, repository, sample_document, temp_dir):
        """Testa salvar documento no filesystem"""
        # Act
        saved_path = await repository.save(sample_document)
        
        # Assert
        assert saved_path is not None
        assert Path(saved_path).exists()
        assert "gestao-pessoal" in saved_path
        assert saved_path.endswith(".json")
    
    @pytest.mark.asyncio
    async def test_save_and_load_document(self, repository, sample_document):
        """Testa salvar e carregar documento"""
        # Act - Save
        await repository.save(sample_document)
        
        # Act - Load
        loaded = await repository.load(sample_document.id)
        
        # Assert
        assert loaded is not None
        assert loaded.id == sample_document.id
        assert loaded.title == sample_document.title
        assert loaded.content == sample_document.content
        assert loaded.module == sample_document.module
    
    @pytest.mark.asyncio
    async def test_save_batch(self, repository, temp_dir):
        """Testa salvar lote de documentos"""
        # Arrange
        docs = [
            Document(
                id=f"test-{i}",
                url=f"https://example.com/doc{i}",
                title=f"Document {i}",
                content=f"Content {i}",
                module="test-module",
                doc_type=DocumentType.TECHNICAL_DOC,
                source=DocumentSource.SENIOR_MADCAP,
                scraped_at=datetime.now(),
            )
            for i in range(5)
        ]
        
        # Act
        saved_paths = await repository.save_batch(docs)
        
        # Assert
        assert len(saved_paths) == 5
        for path in saved_paths:
            assert Path(path).exists()
    
    @pytest.mark.asyncio
    async def test_list_by_module(self, repository):
        """Testa listar documentos por módulo"""
        # Arrange - Criar docs de diferentes módulos
        modules = ["modulo-a", "modulo-b", "modulo-a"]
        docs = [
            Document(
                id=f"test-{i}",
                url=f"https://example.com/doc{i}",
                title=f"Document {i}",
                content=f"Content {i}",
                module=modules[i],
                doc_type=DocumentType.TECHNICAL_DOC,
                source=DocumentSource.SENIOR_MADCAP,
                scraped_at=datetime.now(),
            )
            for i in range(3)
        ]
        
        for doc in docs:
            await repository.save(doc)
        
        # Act
        modulo_a_docs = await repository.list_by_module("modulo-a")
        
        # Assert
        assert len(modulo_a_docs) == 2
        assert all(doc.module == "modulo-a" for doc in modulo_a_docs)
    
    @pytest.mark.asyncio
    async def test_delete_document(self, repository, sample_document):
        """Testa deletar documento"""
        # Arrange
        await repository.save(sample_document)
        
        # Act
        deleted = await repository.delete(sample_document.id)
        
        # Assert
        assert deleted is True
        loaded = await repository.load(sample_document.id)
        assert loaded is None
    
    @pytest.mark.asyncio
    async def test_export_to_jsonl(self, repository, temp_dir):
        """Testa exportar para JSONL"""
        # Arrange - Criar alguns docs
        docs = [
            Document(
                id=f"test-{i}",
                url=f"https://example.com/doc{i}",
                title=f"Document {i}",
                content=f"Content {i}",
                module="test-module",
                doc_type=DocumentType.TECHNICAL_DOC,
                source=DocumentSource.SENIOR_MADCAP,
                scraped_at=datetime.now(),
            )
            for i in range(3)
        ]
        
        for doc in docs:
            await repository.save(doc)
        
        # Act
        output_file = Path(temp_dir) / "export.jsonl"
        count = await repository.export_to_jsonl(str(output_file))
        
        # Assert
        assert count == 3
        assert output_file.exists()
        
        # Verificar conteúdo
        lines = output_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3
    
    @pytest.mark.asyncio
    async def test_count_documents(self, repository):
        """Testa contar documentos"""
        # Arrange
        docs = [
            Document(
                id=f"test-{i}",
                url=f"https://example.com/doc{i}",
                title=f"Document {i}",
                content=f"Content {i}",
                module="test-module",
                doc_type=DocumentType.TECHNICAL_DOC,
                source=DocumentSource.SENIOR_MADCAP,
                scraped_at=datetime.now(),
            )
            for i in range(7)
        ]
        
        for doc in docs:
            await repository.save(doc)
        
        # Act
        total = await repository.count()
        
        # Assert
        assert total == 7
