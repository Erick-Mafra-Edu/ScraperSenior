#!/usr/bin/env python3
"""
Testes para o Cliente API Suporte Senior
"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.suporte_senior_api import (
    SupportArticle,
    SupportSeniorAPI,
    SupportArticleIndexer
)
from src.suporte_senior_integration import SuporteSeniorIntegration


class TestSupportArticle:
    """Testa modelo de artigo"""
    
    def test_create_article(self):
        """Testa criação de artigo"""
        article = SupportArticle(
            id="123",
            title="Test Article",
            body="Test content",
            category="Test Category"
        )
        
        assert article.id == "123"
        assert article.title == "Test Article"
        assert article.body == "Test content"
        assert article.category == "Test Category"
    
    def test_article_to_dict(self):
        """Testa conversão para dicionário"""
        article = SupportArticle(
            id="123",
            title="Test",
            body="Content",
            category="Cat"
        )
        
        data = article.to_dict()
        
        assert isinstance(data, dict)
        assert data['id'] == "123"
        assert data['title'] == "Test"


class TestSupportSeniorAPI:
    """Testa cliente da API"""
    
    @pytest.mark.asyncio
    async def test_api_initialization(self):
        """Testa inicialização da API"""
        api = SupportSeniorAPI()
        
        assert api.BASE_URL == "https://suporte.senior.com.br/api/v2/help_center"
        assert api.LOCALE == "pt-br"
        
        await api.close()
    
    @pytest.mark.asyncio
    async def test_build_url(self):
        """Testa construção de URL"""
        api = SupportSeniorAPI()
        
        url = api._build_url("articles.json")
        
        assert "https://suporte.senior.com.br/api/v2/help_center/pt-br/" in url
        assert "articles.json" in url
        
        await api.close()
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Testa context manager"""
        async with SupportSeniorAPI() as api:
            assert api is not None
            assert hasattr(api, 'get_articles')
    
    def test_parse_article(self):
        """Testa parsing de artigo"""
        api = SupportSeniorAPI()
        
        raw_data = {
            'id': 123,
            'title': 'Test Article',
            'body': 'Test content',
            'section_id': 'cat-1',
            'html_url': 'https://example.com/article',
            'views': 100,
            'helpful_count': 10
        }
        
        article = api._parse_article(raw_data)
        
        assert article.id == "123"
        assert article.title == "Test Article"
        assert article.body == "Test content"
        assert article.views == 100


class TestSupportArticleIndexer:
    """Testa indexador de artigos"""
    
    def test_indexer_initialization(self, tmp_path):
        """Testa inicialização do indexador"""
        indexer = SupportArticleIndexer(str(tmp_path))
        
        assert indexer.output_dir.exists()
        assert indexer.output_dir == tmp_path
    
    @pytest.mark.asyncio
    async def test_index_articles(self, tmp_path):
        """Testa indexação de artigos"""
        indexer = SupportArticleIndexer(str(tmp_path))
        
        # Mock da API
        mock_api = AsyncMock()
        mock_api.get_all_articles = AsyncMock(return_value=[
            SupportArticle(
                id="1",
                title="Article 1",
                body="Content 1",
                category="Category 1",
                url="https://example.com/1"
            ),
            SupportArticle(
                id="2",
                title="Article 2",
                body="Content 2",
                category="Category 2",
                url="https://example.com/2"
            )
        ])
        
        stats = await indexer.index_all_articles(mock_api)
        
        assert stats['total_articles'] == 2
        assert 'output_file' in stats
        assert 'by_category' in stats
        
        # Verifica se arquivo foi criado
        assert any(tmp_path.glob('suporte_senior_*.jsonl'))


class TestSuporteSeniorIntegration:
    """Testa integração completa"""
    
    def test_integration_initialization(self, tmp_path):
        """Testa inicialização da integração"""
        integration = SuporteSeniorIntegration(output_dir=str(tmp_path))
        
        assert integration.output_dir.exists()
        assert hasattr(integration, 'gc')
        assert hasattr(integration, 'config')
    
    def test_generate_stats(self, tmp_path):
        """Testa geração de estatísticas"""
        integration = SuporteSeniorIntegration(output_dir=str(tmp_path))
        
        docs = [
            {'module': 'Cat1', 'content': 'x' * 100},
            {'module': 'Cat1', 'content': 'x' * 200},
            {'module': 'Cat2', 'content': 'x' * 300},
        ]
        
        stats = integration._generate_stats(docs, "test.jsonl")
        
        assert stats['total_documents'] == 3
        assert stats['total_content_length'] == 600
        assert 'by_category' in stats
        assert 'Cat1' in stats['by_category']
        assert 'Cat2' in stats['by_category']


def test_main():
    """Testa função main"""
    # Apenas verifica se a função existe
    from src.suporte_senior_api import main
    assert callable(main)


# Testes de integração
@pytest.mark.asyncio
async def test_api_real_call():
    """Testa chamada real à API (comentado para CI/CD)"""
    # Este teste é para uso manual
    # Descomente para testar contra API real
    
    # async with SupportSeniorAPI() as api:
    #     articles = await api.get_articles(page=1, per_page=5)
    #     
    #     assert 'articles' in articles
    #     assert len(articles['articles']) > 0


if __name__ == "__main__":
    # Executa testes
    pytest.main([__file__, "-v"])
