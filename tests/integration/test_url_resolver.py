"""
Testes de integração - UrlResolver

Testa o adapter UrlResolver com URLs reais.
"""

import pytest
from libs.scrapers.adapters import UrlResolver


class TestUrlResolverIntegration:
    """Testes de integração para UrlResolver"""
    
    @pytest.fixture
    def resolver(self):
        """Cria instância do resolver"""
        return UrlResolver()
    
    def test_resolve_relative_url(self, resolver):
        """Testa resolver URL relativa"""
        base = "https://documentacao.senior.com.br/gestao-pessoal/6.10.4/"
        relative = "../6.10.3/index.html"
        
        result = resolver.resolve(base, relative)
        
        assert result == "https://documentacao.senior.com.br/gestao-pessoal/6.10.3/index.html"
    
    def test_resolve_absolute_url(self, resolver):
        """Testa resolver URL absoluta"""
        base = "https://documentacao.senior.com.br/gestao-pessoal/6.10.4/"
        absolute = "https://example.com/other"
        
        result = resolver.resolve(base, absolute)
        
        assert result == absolute
    
    def test_normalize_url(self, resolver):
        """Testa normalização de URL"""
        url = "https://example.com/path/../other/./file.html?query=1#fragment"
        
        result = resolver.normalize(url)
        
        assert result == "https://example.com/other/file.html?query=1#fragment"
    
    def test_is_same_domain(self, resolver):
        """Testa verificação de mesmo domínio"""
        url1 = "https://documentacao.senior.com.br/gestao-pessoal/6.10.4/"
        url2 = "https://documentacao.senior.com.br/financeiro/5.0.0/"
        url3 = "https://example.com/other"
        
        assert resolver.is_same_domain(url1, url2) is True
        assert resolver.is_same_domain(url1, url3) is False
    
    def test_extract_domain(self, resolver):
        """Testa extração de domínio"""
        url = "https://documentacao.senior.com.br/gestao-pessoal/6.10.4/index.html"
        
        result = resolver.extract_domain(url)
        
        assert result == "documentacao.senior.com.br"
    
    def test_extract_path(self, resolver):
        """Testa extração de path"""
        url = "https://documentacao.senior.com.br/gestao-pessoal/6.10.4/index.html?query=1"
        
        result = resolver.extract_path(url)
        
        assert result == "/gestao-pessoal/6.10.4/index.html"
    
    def test_build_url(self, resolver):
        """Testa construção de URL"""
        result = resolver.build_url(
            scheme="https",
            netloc="documentacao.senior.com.br",
            path="/gestao-pessoal/6.10.4/index.html",
            query="page=1",
            fragment="section-2"
        )
        
        assert result == "https://documentacao.senior.com.br/gestao-pessoal/6.10.4/index.html?page=1#section-2"
    
    def test_remove_fragment(self, resolver):
        """Testa remoção de fragmento"""
        url = "https://example.com/page.html#section-2"
        
        result = resolver.remove_fragment(url)
        
        assert result == "https://example.com/page.html"
    
    def test_remove_query(self, resolver):
        """Testa remoção de query string"""
        url = "https://example.com/page.html?query=1&page=2"
        
        result = resolver.remove_query(url)
        
        assert result == "https://example.com/page.html"
    
    def test_is_valid_url(self, resolver):
        """Testa validação de URL"""
        assert resolver.is_valid_url("https://example.com/page") is True
        assert resolver.is_valid_url("http://example.com") is True
        assert resolver.is_valid_url("ftp://example.com") is True
        assert resolver.is_valid_url("not-a-url") is False
        assert resolver.is_valid_url("") is False
    
    def test_madcap_flare_hash_urls(self, resolver):
        """Testa resolução de URLs com hash do MadCap Flare"""
        base = "https://documentacao.senior.com.br/gestao-pessoal/6.10.4/index.html"
        hash_path = "#Content/modulos/doc.htm"
        
        # MadCap usa hash navigation, então resolve mantém hash
        result = resolver.resolve(base, hash_path)
        
        # Deve incluir o hash
        assert "#Content/modulos/doc.htm" in result
