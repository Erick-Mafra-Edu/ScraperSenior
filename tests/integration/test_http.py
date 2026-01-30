#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples de extração usando BeautifulSoup
"""

import requests
from bs4 import BeautifulSoup

url = "https://documentacao.senior.com.br/gestao-de-pessoas-hcm/6.10.4/"

print("\n[TESTE] Fazendo requisição HTTP...")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Tamanho: {len(response.content)} bytes")
    
    # Procurar títulos
    print("\n[TÍTULOS ENCONTRADOS]")
    print(f"  <title>: {soup.title.string if soup.title else 'NÃO'}")
    
    h1 = soup.find('h1')
    print(f"  <h1>: {h1.text if h1 else 'NÃO'}")
    
    # Procurar iframes
    print("\n[IFRAMES]")
    iframes = soup.find_all('iframe')
    print(f"  Total: {len(iframes)}")
    for iframe in iframes[:3]:
        print(f"    - id: {iframe.get('id')}, src: {iframe.get('src')[:60]}...")
    
    # Procurar menus/navegação
    print("\n[NAVEGAÇÃO]")
    toc = soup.find(id='toc')
    if toc:
        links = toc.find_all('a')
        print(f"  TOC encontrado com {len(links)} links")
        print(f"  Primeiros 3:")
        for link in links[:3]:
            print(f"    - {link.text[:40]} -> {link.get('href', 'N/A')[:40]}")
    else:
        print("  TOC NÃO ENCONTRADO!")
    
    # Links gerais
    print("\n[LINKS NA PÁGINA]")
    all_links = soup.find_all('a')
    print(f"  Total de links: {len(all_links)}")
    
except Exception as e:
    print(f"✗ Erro: {e}")
