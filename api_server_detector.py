"""
Utilitário para detectar automaticamente o servidor disponível
"""

import requests
import sys
from typing import Optional, Tuple


def detect_api_server() -> Tuple[str, bool]:
    """
    Detecta qual servidor está disponível (localhost ou people-fy.com)
    
    Returns:
        Tuple[str, bool]: (url_do_servidor, servidor_encontrado)
    """
    servers = [
        ("http://localhost:8000", "localhost"),
        ("http://127.0.0.1:8000", "127.0.0.1"),
        ("http://people-fy.com:8000", "people-fy.com"),
    ]
    
    for url, name in servers:
        try:
            response = requests.get(f"{url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ API detectada em: {url}")
                return url, True
        except:
            pass
    
    # Se nenhum servidor for encontrado, retornar localhost como padrão
    print("⚠️  Nenhum servidor detectado. Usando localhost:8000 como padrão.")
    return "http://localhost:8000", False


def get_api_url(force_url: Optional[str] = None) -> str:
    """
    Obtém a URL da API
    
    Args:
        force_url: URL forçada (se fornecida, ignora auto-detecção)
    
    Returns:
        str: URL da API
    """
    if force_url:
        return force_url
    
    url, found = detect_api_server()
    return url


if __name__ == "__main__":
    # Testar detecção
    url, found = detect_api_server()
    print(f"URL: {url}")
    print(f"Encontrado: {found}")
