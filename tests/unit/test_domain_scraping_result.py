"""
Testes unitários - Domain: ScrapingResult Value Object

Testa o value object ScrapingResult sem dependências externas.
"""

import pytest
from datetime import datetime
from libs.scrapers.domain import ScrapingResult, Document, DocumentType, DocumentSource


class TestScrapingResult:
    """Testes para value object ScrapingResult"""
    
    def test_create_scraping_result(self):
        """Testa criação de resultado básico"""
        started_at = datetime(2024, 1, 1, 10, 0, 0)
        finished_at = datetime(2024, 1, 1, 10, 5, 0)
        
        result = ScrapingResult(
            documents=tuple(),
            total_documents=10,
            successful_scrapes=8,
            failed_scrapes=2,
            skipped_urls=1,
            started_at=started_at,
            finished_at=finished_at,
            source_urls=("https://example.com",),
            errors=("Error 1", "Error 2"),
            warnings=("Warning 1",),
        )
        
        assert result.total_documents == 10
        assert result.successful_scrapes == 8
        assert result.failed_scrapes == 2
        assert result.skipped_urls == 1
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
    
    def test_duration(self):
        """Testa cálculo de duração"""
        started_at = datetime(2024, 1, 1, 10, 0, 0)
        finished_at = datetime(2024, 1, 1, 10, 5, 30)
        
        result = ScrapingResult(
            documents=tuple(),
            total_documents=0,
            successful_scrapes=0,
            failed_scrapes=0,
            skipped_urls=0,
            started_at=started_at,
            finished_at=finished_at,
            source_urls=tuple(),
            errors=tuple(),
            warnings=tuple(),
        )
        
        duration = result.duration_seconds
        assert duration == 330  # 5min 30s
    
    def test_success_rate(self):
        """Testa cálculo de taxa de sucesso"""
        result = ScrapingResult(
            documents=tuple(),
            total_documents=10,
            successful_scrapes=8,
            failed_scrapes=2,
            skipped_urls=0,
            started_at=datetime.now(),
            finished_at=datetime.now(),
            source_urls=tuple(),
            errors=tuple(),
            warnings=tuple(),
        )
        
        assert result.success_rate == 0.8
    
    def test_success_rate_zero_total(self):
        """Testa taxa de sucesso quando total é zero"""
        result = ScrapingResult(
            documents=tuple(),
            total_documents=0,
            successful_scrapes=0,
            failed_scrapes=0,
            skipped_urls=0,
            started_at=datetime.now(),
            finished_at=datetime.now(),
            source_urls=tuple(),
            errors=tuple(),
            warnings=tuple(),
        )
        
        assert result.success_rate == 0.0
    
    def test_is_successful(self):
        """Testa verificação de sucesso"""
        # Caso sucesso (>= 80%)
        result_success = ScrapingResult(
            documents=tuple(),
            total_documents=10,
            successful_scrapes=9,
            failed_scrapes=1,
            skipped_urls=0,
            started_at=datetime.now(),
            finished_at=datetime.now(),
            source_urls=tuple(),
            errors=tuple(),
            warnings=tuple(),
        )
        assert result_success.success_rate >= 0.8
        
        # Caso falha (< 80%)
        result_fail = ScrapingResult(
            documents=tuple(),
            total_documents=10,
            successful_scrapes=7,
            failed_scrapes=3,
            skipped_urls=0,
            started_at=datetime.now(),
            finished_at=datetime.now(),
            source_urls=tuple(),
            errors=tuple(),
            warnings=tuple(),
        )
        assert result_fail.success_rate < 0.8
    
    def test_immutability(self):
        """Testa que ScrapingResult é imutável (frozen)"""
        result = ScrapingResult(
            documents=tuple(),
            total_documents=10,
            successful_scrapes=8,
            failed_scrapes=2,
            skipped_urls=0,
            started_at=datetime.now(),
            finished_at=datetime.now(),
            source_urls=tuple(),
            errors=tuple(),
            warnings=tuple(),
        )
        
        with pytest.raises(Exception):  # dataclass frozen
            result.total_documents = 20
    
    def test_to_dict(self):
        """Testa serialização para dict"""
        started_at = datetime(2024, 1, 1, 10, 0, 0)
        finished_at = datetime(2024, 1, 1, 10, 5, 0)
        
        doc = Document(
            id="test",
            url="https://example.com",
            title="Test",
            content="Content",
            module="test",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.SENIOR_MADCAP,
            scraped_at=datetime.now(),
        )
        
        result = ScrapingResult(
            documents=(doc,),
            total_documents=1,
            successful_scrapes=1,
            failed_scrapes=0,
            skipped_urls=0,
            started_at=started_at,
            finished_at=finished_at,
            source_urls=("https://example.com",),
            errors=tuple(),
            warnings=tuple(),
        )
        
        data = result.to_dict()
        
        assert data["total_documents"] == 1
        assert data["successful_scrapes"] == 1
        assert len(data["documents"]) == 1
