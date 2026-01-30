"""
Port - URL Resolver Interface

Define o contrato para resolução e normalização de URLs.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class IUrlResolver(ABC):
    """
    Port (Interface) para resolvedores de URL.
    
    Abstrai lógica de manipulação de URLs, permitindo diferentes
    estratégias para diferentes tipos de documentação.
    """
    
    @abstractmethod
    def resolve(self, base_url: str, relative_url: str) -> Optional[str]:
        """
        Resolve URL relativa para absoluta.
        
        Args:
            base_url: URL base
            relative_url: URL relativa (pode ser #hash, /path, etc.)
        
        Returns:
            Optional[str]: URL absoluta ou None se inválida
        """
        pass
    
    @abstractmethod
    def normalize(self, url: str) -> str:
        """
        Normaliza URL removendo duplicatas, ordenando query params, etc.
        
        Args:
            url: URL a ser normalizada
        
        Returns:
            str: URL normalizada
        """
        pass
    
    @abstractmethod
    def extract_module(self, url: str) -> str:
        """
        Extrai nome do módulo da URL.
        
        Exemplo: "https://doc.senior.com.br/crm/..." → "crm"
        
        Args:
            url: URL completa
        
        Returns:
            str: Nome do módulo
        """
        pass
    
    @abstractmethod
    def is_valid(self, url: str) -> bool:
        """
        Valida se URL tem formato válido.
        
        Args:
            url: URL a ser validada
        
        Returns:
            bool: True se válida, False caso contrário
        """
        pass
    
    @abstractmethod
    def is_same_domain(self, url1: str, url2: str) -> bool:
        """
        Verifica se duas URLs são do mesmo domínio.
        
        Args:
            url1: Primeira URL
            url2: Segunda URL
        
        Returns:
            bool: True se mesmo domínio
        """
        pass
    
    @abstractmethod
    def parse(self, url: str) -> Dict[str, Any]:
        """
        Parseia URL em componentes (scheme, host, path, query, fragment).
        
        Args:
            url: URL a ser parseada
        
        Returns:
            Dict[str, Any]: Componentes da URL
        """
        pass
    
    @abstractmethod
    def build(self, scheme: str, host: str, path: str, query: str = "", fragment: str = "") -> str:
        """
        Constrói URL a partir de componentes.
        
        Args:
            scheme: Protocolo (http, https)
            host: Domínio
            path: Caminho
            query: Query string (opcional)
            fragment: Fragment/hash (opcional)
        
        Returns:
            str: URL completa
        """
        pass
