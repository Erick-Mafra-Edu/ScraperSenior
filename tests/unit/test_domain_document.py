"""
Testes unitários - Domain: Document Entity

Testa a entidade Document sem dependências externas.
"""

import pytest
from datetime import datetime
from libs.scrapers.domain import Document, DocumentType, DocumentSource


class TestDocument:
    """Testes para entidade Document"""
    
    def test_create_document(self):
        """Testa criação de documento básico"""
        doc = Document(
            id="test-123",
            url="https://example.com/doc",
            title="Test Document",
            content="This is test content.",
            module="test-module",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.SENIOR_MADCAP,
            scraped_at=datetime.now(),
        )
        
        assert doc.id == "test-123"
        assert doc.title == "Test Document"
        assert doc.module == "test-module"
        assert doc.doc_type == DocumentType.TECHNICAL_DOC
        assert doc.source == DocumentSource.SENIOR_MADCAP
    
    def test_word_count(self):
        """Testa contagem de palavras"""
        doc = Document(
            id="test",
            url="https://example.com",
            title="Test",
            content="One two three four five",
            module="test",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.SENIOR_MADCAP,
            scraped_at=datetime.now(),
        )
        
        assert doc.word_count() == 5
    
    def test_char_count(self):
        """Testa contagem de caracteres"""
        doc = Document(
            id="test",
            url="https://example.com",
            title="Test",
            content="Hello World",
            module="test",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.SENIOR_MADCAP,
            scraped_at=datetime.now(),
        )
        
        assert doc.char_count() == 11
    
    def test_to_dict(self):
        """Testa serialização para dict"""
        scraped_at = datetime.now()
        doc = Document(
            id="test-123",
            url="https://example.com/doc",
            title="Test Document",
            content="Content",
            module="test-module",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.SENIOR_MADCAP,
            scraped_at=scraped_at,
            metadata={"key": "value"}
        )
        
        data = doc.to_dict()
        
        assert data["id"] == "test-123"
        assert data["title"] == "Test Document"
        assert data["doc_type"] == "technical_doc"
        assert data["source"] == "senior_madcap"
        assert data["metadata"] == {"key": "value"}
    
    def test_from_dict(self):
        """Testa desserialização de dict"""
        data = {
            "id": "test-123",
            "url": "https://example.com/doc",
            "title": "Test Document",
            "content": "Content",
            "module": "test-module",
            "doc_type": "technical_doc",
            "source": "senior_madcap",
            "scraped_at": "2024-01-01T10:00:00",
            "metadata": {"key": "value"}
        }
        
        doc = Document.from_dict(data)
        
        assert doc.id == "test-123"
        assert doc.title == "Test Document"
        assert doc.doc_type == DocumentType.TECHNICAL_DOC
        assert doc.source == DocumentSource.SENIOR_MADCAP
        assert doc.metadata == {"key": "value"}
    
    def test_document_types(self):
        """Testa todos os tipos de documentos"""
        types = [
            DocumentType.TECHNICAL_DOC,
            DocumentType.RELEASE_NOTE,
            DocumentType.API_DOC,
            DocumentType.TUTORIAL,
            DocumentType.HELP_ARTICLE,
            DocumentType.UNKNOWN,
        ]
        
        for doc_type in types:
            doc = Document(
                id="test",
                url="https://example.com",
                title="Test",
                content="Content",
                module="test",
                doc_type=doc_type,
                source=DocumentSource.SENIOR_MADCAP,
                scraped_at=datetime.now(),
            )
            assert doc.doc_type == doc_type
    
    def test_document_sources(self):
        """Testa todas as fontes de documentos"""
        sources = [
            DocumentSource.SENIOR_MADCAP,
            DocumentSource.SENIOR_ASTRO,
            DocumentSource.ZENDESK,
            DocumentSource.SUPPORT_SENIOR,
            DocumentSource.UNKNOWN,
        ]
        
        for source in sources:
            doc = Document(
                id="test",
                url="https://example.com",
                title="Test",
                content="Content",
                module="test",
                doc_type=DocumentType.TECHNICAL_DOC,
                source=source,
                scraped_at=datetime.now(),
            )
            assert doc.source == source
