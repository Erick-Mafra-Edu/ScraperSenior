"""
Testes unitários - Use Cases: ScrapeDocumentation

Testa o use case ScrapeDocumentation com mocks (sem dependências externas).
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from libs.scrapers.use_cases import ScrapeDocumentation
from libs.scrapers.domain import Document, DocumentType, DocumentSource, ScrapingResult


class TestScrapeDocumentationUseCase:
    """Testes para use case ScrapeDocumentation"""
    
    @pytest.fixture
    def mock_scraper(self):
        """Mock de IDocumentScraper"""
        scraper = Mock()
        scraper.supports_url = Mock(return_value=True)
        scraper.scrape = AsyncMock()
        scraper.scrape_all = AsyncMock()
        return scraper
    
    @pytest.fixture
    def mock_repository(self):
        """Mock de IDocumentRepository"""
        repo = Mock()
        repo.save = AsyncMock()
        repo.save_batch = AsyncMock()
        return repo
    
    @pytest.fixture
    def use_case(self, mock_scraper, mock_repository):
        """Cria use case com mocks"""
        return ScrapeDocumentation(
            scrapers=[mock_scraper],
            repository=mock_repository,
        )
    
    @pytest.mark.asyncio
    async def test_scrape_single_url(self, use_case, mock_scraper, mock_repository):
        """Testa scraping de uma URL"""
        # Arrange
        doc = Document(
            id="test-123",
            url="https://example.com/doc",
            title="Test Document",
            content="Content",
            module="test",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.SENIOR_MADCAP,
            scraped_at=datetime.now(),
        )
        mock_scraper.scrape.return_value = doc
        
        # Act
        result = await use_case.execute(urls=["https://example.com/doc"])
        
        # Assert
        assert result.total_documents == 1
        assert result.successful_scrapes == 1
        assert result.failed_scrapes == 0
        mock_scraper.scrape.assert_called_once()
        mock_repository.save.assert_called_once_with(doc)
    
    @pytest.mark.asyncio
    async def test_scrape_multiple_urls(self, use_case, mock_scraper, mock_repository):
        """Testa scraping de múltiplas URLs"""
        # Arrange
        docs = [
            Document(
                id=f"test-{i}",
                url=f"https://example.com/doc{i}",
                title=f"Document {i}",
                content="Content",
                module="test",
                doc_type=DocumentType.TECHNICAL_DOC,
                source=DocumentSource.SENIOR_MADCAP,
                scraped_at=datetime.now(),
            )
            for i in range(3)
        ]
        mock_scraper.scrape.side_effect = docs
        
        # Act
        urls = [f"https://example.com/doc{i}" for i in range(3)]
        result = await use_case.execute(urls=urls)
        
        # Assert
        assert result.total_documents == 3
        assert result.successful_scrapes == 3
        assert result.failed_scrapes == 0
        assert mock_scraper.scrape.call_count == 3
        assert mock_repository.save.call_count == 3
    
    @pytest.mark.asyncio
    async def test_scrape_with_errors(self, use_case, mock_scraper, mock_repository):
        """Testa scraping com erros"""
        # Arrange
        doc = Document(
            id="test-1",
            url="https://example.com/doc1",
            title="Document 1",
            content="Content",
            module="test",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.SENIOR_MADCAP,
            scraped_at=datetime.now(),
        )
        
        # Primeira URL sucesso, segunda falha
        mock_scraper.scrape.side_effect = [doc, Exception("Network error")]
        
        # Act
        urls = ["https://example.com/doc1", "https://example.com/doc2"]
        result = await use_case.execute(urls=urls)
        
        # Assert
        assert result.total_documents == 2
        assert result.successful_scrapes == 1
        assert result.failed_scrapes == 1
        assert len(result.errors) == 1
        assert "Network error" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_no_scraper_supports_url(self, mock_repository):
        """Testa quando nenhum scraper suporta a URL"""
        # Arrange
        scraper = Mock()
        scraper.supports_url = Mock(return_value=False)
        use_case = ScrapeDocumentation(
            scrapers=[scraper],
            repository=mock_repository,
        )
        
        # Act
        result = await use_case.execute(urls=["https://unknown.com/doc"])
        
        # Assert
        assert result.total_documents == 1
        assert result.successful_scrapes == 0
        assert result.skipped_urls == 1
    
    @pytest.mark.asyncio
    async def test_scrape_all_mode(self, use_case, mock_scraper, mock_repository):
        """Testa modo scrape_all"""
        # Arrange
        docs = [
            Document(
                id=f"test-{i}",
                url=f"https://example.com/doc{i}",
                title=f"Document {i}",
                content="Content",
                module="test",
                doc_type=DocumentType.TECHNICAL_DOC,
                source=DocumentSource.SENIOR_MADCAP,
                scraped_at=datetime.now(),
            )
            for i in range(5)
        ]
        
        scrape_result = ScrapingResult(
            documents=tuple(docs),
            total_documents=5,
            successful_scrapes=5,
            failed_scrapes=0,
            skipped_urls=0,
            started_at=datetime.now(),
            finished_at=datetime.now(),
            source_urls=("https://example.com",),
            errors=tuple(),
            warnings=tuple(),
        )
        
        mock_scraper.scrape_all.return_value = scrape_result
        
        # Act
        result = await use_case.execute(
            urls=["https://example.com"],
            scrape_all=True,
        )
        
        # Assert
        assert result.total_documents == 5
        assert result.successful_scrapes == 5
        mock_scraper.scrape_all.assert_called_once()
        mock_repository.save_batch.assert_called_once()
