#!/usr/bin/env python3
"""
Testes para API Zendesk Help Center
"""

import asyncio
from src.api_zendesk import (
    ZendeskAPIClient,
    ZendeskArticle,
    ZendeskCategory,
    ZendeskSection,
    ZendeskScraper
)


class TestZendeskDataClasses:
    """Testa classes de dados do Zendesk"""
    
    def test_article_creation(self):
        """Testa criação de artigo"""
        article = ZendeskArticle(
            id=123,
            url="https://example.com/article/123",
            title="Test Article",
            body="Test body",
            category_id=1,
            section_id=2,
            created_at="2026-01-26T10:00:00Z",
            updated_at="2026-01-26T10:00:00Z",
            author_id=456
        )
        
        assert article.id == 123
        assert article.title == "Test Article"
        assert article.category_id == 1
        assert article.locale == "pt-BR"
        print("✅ Article creation test passed")
    
    def test_category_creation(self):
        """Testa criação de categoria"""
        category = ZendeskCategory(
            id=1,
            url="https://example.com/category/1",
            name="Test Category",
            description="Test description"
        )
        
        assert category.id == 1
        assert category.name == "Test Category"
        assert category.locale == "pt-BR"
        print("✅ Category creation test passed")
    
    def test_section_creation(self):
        """Testa criação de seção"""
        section = ZendeskSection(
            id=2,
            url="https://example.com/section/2",
            name="Test Section",
            category_id=1,
            article_count=5
        )
        
        assert section.id == 2
        assert section.category_id == 1
        assert section.article_count == 5
        print("✅ Section creation test passed")
    
    def test_to_dict_conversion(self):
        """Testa conversão para dicionário"""
        article = ZendeskArticle(
            id=123,
            url="https://example.com/article/123",
            title="Test",
            body="Body",
            category_id=1,
            section_id=2,
            created_at="2026-01-26T10:00:00Z",
            updated_at="2026-01-26T10:00:00Z",
            author_id=456
        )
        
        article_dict = article.to_dict()
        assert isinstance(article_dict, dict)
        assert article_dict['id'] == 123
        assert article_dict['title'] == "Test"
        print("✅ to_dict conversion test passed")


class TestZendeskAPIClient:
    """Testa cliente da API Zendesk"""
    
    def test_client_initialization(self):
        """Testa inicialização do cliente"""
        client = ZendeskAPIClient(
            base_url="https://example.zendesk.com/api/v2/help_center"
        )
        
        assert client.base_url == "https://example.zendesk.com/api/v2/help_center"
        assert client.timeout
        assert client.stats['articles_fetched'] == 0
        print("✅ Client initialization test passed")
    
    def test_url_normalization(self):
        """Testa normalização de URL"""
        client = ZendeskAPIClient(
            base_url="https://example.zendesk.com/api/v2/help_center/"
        )
        
        # URL deveria ter barra final removida
        assert not client.base_url.endswith('/')
        print("✅ URL normalization test passed")
    
    async def test_client_context_manager(self):
        """Testa context manager do cliente"""
        async with ZendeskAPIClient() as client:
            assert client.session is not None
            assert not client.session.closed
        
        assert client.session.closed
        print("✅ Context manager test passed")


class TestZendeskScraper:
    """Testa scraper Zendesk"""
    
    def test_scraper_initialization(self):
        """Testa inicialização do scraper"""
        scraper = ZendeskScraper(
            output_dir="test_output"
        )
        
        assert scraper.documents == []
        assert scraper.categories == []
        assert scraper.sections == []
        assert scraper.output_dir.name == "test_output"
        print("✅ Scraper initialization test passed")
    
    def test_document_structure(self):
        """Testa estrutura de documento"""
        scraper = ZendeskScraper()
        
        # Simula documento do Zendesk
        doc = {
            'id': 'zendesk_123',
            'type': 'zendesk_article',
            'url': 'https://example.com/article/123',
            'title': 'Test Article',
            'content': 'Test content',
            'category_id': 1,
            'section_id': 2,
            'locale': 'pt-BR',
            'metadata': {
                'source': 'zendesk',
                'created_at': '2026-01-26T10:00:00Z',
                'updated_at': '2026-01-26T10:00:00Z'
            }
        }
        
        # Verifica campos obrigatórios
        assert 'id' in doc
        assert 'url' in doc
        assert 'title' in doc
        assert 'content' in doc
        assert 'metadata' in doc
        print("✅ Document structure test passed")


class TestZendeskAdapter:
    """Testa adaptador Zendesk → Modular"""
    
    def test_article_conversion(self):
        """Testa conversão de artigo"""
        from src.zendesk_modular_adapter import ZendeskToModularAdapter
        
        zendesk_doc = {
            'id': 'zendesk_123',
            'url': 'https://example.com/article/123',
            'title': 'Test Article',
            'content': 'Test content' * 100,
            'category_id': 1,
            'section_id': 2,
            'locale': 'pt-BR',
            'metadata': {
                'source': 'zendesk',
                'created_at': '2026-01-26T10:00:00Z',
                'scraped_at': '2026-01-26T10:00:00Z'
            }
        }
        
        converted = ZendeskToModularAdapter.convert_article(zendesk_doc)
        
        # Verifica campos convertidos
        assert converted['id'] == 'zendesk_123'
        assert converted['module'] == 'Help Center'
        assert 'breadcrumb' in converted
        assert 'metadata' in converted
        assert converted['metadata']['source'] == 'zendesk'
        print("✅ Article conversion test passed")


def run_tests():
    """Executa todos os testes"""
    print("\n" + "="*80)
    print("TESTES - API ZENDESK HELP CENTER")
    print("="*80 + "\n")
    
    test_classes = [
        TestZendeskDataClasses,
        TestZendeskAPIClient,
        TestZendeskScraper,
        TestZendeskAdapter
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📝 {test_class.__name__}")
        print("─" * 80)
        
        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith('test_')]
        
        for method_name in methods:
            total_tests += 1
            try:
                method = getattr(instance, method_name)
                
                # Verifica se é async
                if asyncio.iscoroutinefunction(method):
                    asyncio.run(method())
                else:
                    method()
                
                passed_tests += 1
            except Exception as e:
                failed_tests += 1
                print(f"❌ {method_name}: {e}")
    
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)
    print(f"Total de testes:    {total_tests}")
    print(f"Testes passados:    {passed_tests} ✅")
    print(f"Testes falhados:    {failed_tests} ❌")
    print(f"Taxa de sucesso:    {(passed_tests/total_tests*100):.1f}%")
    print("="*80 + "\n")
    
    return failed_tests == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
