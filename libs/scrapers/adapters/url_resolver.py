"""
Adapter - URL Resolver

Implementação concreta de IUrlResolver.
Resolve e normaliza URLs usando urllib.
"""

from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode
import re
from libs.scrapers.ports import IUrlResolver


class UrlResolver(IUrlResolver):
    """
    Adapter que implementa IUrlResolver.
    
    Fornece funcionalidades para manipulação de URLs,
    incluindo resolução, normalização e parsing.
    """
    
    def resolve(self, base_url: str, relative_url: str) -> Optional[str]:
        """
        Resolve URL relativa para absoluta.
        
        Args:
            base_url: URL base
            relative_url: URL relativa
        
        Returns:
            Optional[str]: URL absoluta ou None se inválida
        """
        try:
            # Se já é absoluta, retorna
            if relative_url.startswith(('http://', 'https://')):
                return relative_url
            
            # Trata âncoras especiais (MadCap Flare com hash navigation)
            if relative_url.startswith('#'):
                # Para URLs com #hash, mantém base e adiciona hash
                parsed = urlparse(base_url)
                base_without_hash = parsed.scheme + '://' + parsed.netloc + parsed.path
                return base_without_hash + relative_url
            
            # Resolução padrão
            resolved = urljoin(base_url, relative_url)
            return resolved if self.is_valid(resolved) else None
            
        except Exception:
            return None
    
    def normalize(self, url: str) -> str:
        """
        Normaliza URL.
        
        Remove duplicatas, ordena query params, normaliza path.
        
        Args:
            url: URL a ser normalizada
        
        Returns:
            str: URL normalizada
        """
        try:
            parsed = urlparse(url)
            
            # Normalizar scheme e netloc (lowercase)
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()
            
            # Normalizar path (remove //)
            path = parsed.path
            while '//' in path:
                path = path.replace('//', '/')
            
            # Normalizar query (ordenar params)
            query = parsed.query
            if query:
                params = parse_qs(query, keep_blank_values=True)
                # Ordenar params alfabeticamente
                sorted_params = sorted(params.items())
                query = urlencode(sorted_params, doseq=True)
            
            # Reconstruir URL
            normalized = urlunparse((
                scheme,
                netloc,
                path,
                parsed.params,
                query,
                parsed.fragment
            ))
            
            return normalized
            
        except Exception:
            return url
    
    def extract_module(self, url: str) -> str:
        """
        Extrai nome do módulo da URL.
        
        Assume padrão: https://doc.senior.com.br/MODULO/...
        
        Args:
            url: URL completa
        
        Returns:
            str: Nome do módulo
        """
        try:
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            
            # Para Senior Docs, o módulo é geralmente o primeiro segmento
            if 'documentacao.senior.com.br' in parsed.netloc:
                if len(path_parts) > 0:
                    # Remove versão se presente (ex: "crm/5.10.4" -> "crm")
                    module = path_parts[0]
                    # Remove números de versão
                    module = re.sub(r'/\d+\.\d+.*', '', module)
                    return module
            
            # Para outros, pegar primeiro segmento ou netloc
            if len(path_parts) > 0:
                return path_parts[0]
            
            # Fallback: usar netloc
            return parsed.netloc.split('.')[0]
            
        except Exception:
            return "unknown"
    
    def is_valid(self, url: str) -> bool:
        """
        Valida se URL tem formato válido.
        
        Args:
            url: URL a ser validada
        
        Returns:
            bool: True se válida
        """
        try:
            parsed = urlparse(url)
            # URL válida deve ter scheme e netloc
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def is_same_domain(self, url1: str, url2: str) -> bool:
        """
        Verifica se duas URLs são do mesmo domínio.
        
        Args:
            url1: Primeira URL
            url2: Segunda URL
        
        Returns:
            bool: True se mesmo domínio
        """
        try:
            parsed1 = urlparse(url1)
            parsed2 = urlparse(url2)
            
            # Comparar netloc (domínio)
            return parsed1.netloc.lower() == parsed2.netloc.lower()
            
        except Exception:
            return False
    
    def parse(self, url: str) -> Dict[str, Any]:
        """
        Parseia URL em componentes.
        
        Args:
            url: URL a ser parseada
        
        Returns:
            Dict: Componentes da URL
        """
        try:
            parsed = urlparse(url)
            
            # Parse query params
            query_params = {}
            if parsed.query:
                query_params = parse_qs(parsed.query, keep_blank_values=True)
            
            return {
                "scheme": parsed.scheme,
                "netloc": parsed.netloc,
                "host": parsed.netloc.split(':')[0] if ':' in parsed.netloc else parsed.netloc,
                "port": parsed.port,
                "path": parsed.path,
                "params": parsed.params,
                "query": parsed.query,
                "query_params": query_params,
                "fragment": parsed.fragment,
                "username": parsed.username,
                "password": parsed.password,
            }
            
        except Exception:
            return {}
    
    def build(
        self,
        scheme: str,
        host: str,
        path: str,
        query: str = "",
        fragment: str = ""
    ) -> str:
        """
        Constrói URL a partir de componentes.
        
        Args:
            scheme: Protocolo
            host: Domínio
            path: Caminho
            query: Query string
            fragment: Fragment
        
        Returns:
            str: URL completa
        """
        try:
            return urlunparse((
                scheme,
                host,
                path,
                "",  # params (deprecated)
                query,
                fragment
            ))
        except Exception:
            return ""
    
    def extract_anchor(self, url: str) -> Optional[str]:
        """
        Extrai âncora/fragment da URL.
        
        Args:
            url: URL completa
        
        Returns:
            Optional[str]: Âncora ou None
        """
        try:
            parsed = urlparse(url)
            return parsed.fragment if parsed.fragment else None
        except Exception:
            return None
    
    def remove_anchor(self, url: str) -> str:
        """
        Remove âncora/fragment da URL.
        
        Args:
            url: URL completa
        
        Returns:
            str: URL sem âncora
        """
        try:
            parsed = urlparse(url)
            return urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                ""  # Remove fragment
            ))
        except Exception:
            return url
