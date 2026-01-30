#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar URLs de notas de versão aos módulos descobertos.
Detecta automaticamente URLs de notas de versão para cada módulo e as adiciona
à lista de URLs para scraping.

Exemplo:
    https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/#6-10-4.htm
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import re


class ReleaseNotesDiscoverer:
    """Descobre e gerencia URLs de notas de versão"""
    
    # Padrões comuns para notas de versão em documentação Senior
    RELEASE_NOTES_PATTERNS = [
        "{slug}/notas-da-versao/",
        "{slug}/release-notes/",
        "{slug}/notas-de-versao/",
        "{slug}/changelog/",
        "{slug}/version-history/",
        "{slug}/historico-de-versoes/",
    ]
    
    @staticmethod
    def generate_release_notes_urls(module_info: Dict) -> List[str]:
        """
        Gera URLs possíveis de notas de versão para um módulo.
        
        Args:
            module_info: Dicionário com informações do módulo (url, slug, version)
        
        Returns:
            Lista de URLs de notas de versão possíveis
        """
        urls = []
        slug = module_info.get('slug', '').lower()
        base_url = "https://documentacao.senior.com.br"
        
        if not slug:
            return urls
        
        # Gerar URLs possíveis com slug substituído
        for pattern in ReleaseNotesDiscoverer.RELEASE_NOTES_PATTERNS:
            url = f"{base_url}/{pattern.replace('{slug}', slug)}"
            urls.append(url)
        
        return urls
    
    @staticmethod
    def extract_version_from_url(url: str) -> str:
        """Extrai número de versão da URL (ex: 6.10.4)"""
        match = re.search(r'/(\d+\.\d+\.\d+)/', url)
        return match.group(1) if match else "unknown"
    
    @staticmethod
    def format_module_name(name: str) -> str:
        """Formata nome do módulo para usar em paths"""
        return name.upper().replace(' ', '_')


def add_release_notes_to_modules(modulos_file: str = "modulos_descobertos.json") -> Dict:
    """
    Adiciona URLs de notas de versão aos módulos descobertos.
    
    Args:
        modulos_file: Caminho do arquivo com módulos descobertos
    
    Returns:
        Dicionário com módulos e suas notas de versão
    """
    
    modulos_path = Path(modulos_file)
    
    if not modulos_path.exists():
        print(f"[ERRO] Arquivo {modulos_file} não encontrado")
        return {}
    
    # Carregar módulos
    with open(modulos_path, 'r', encoding='utf-8') as f:
        modulos = json.load(f)
    
    # Adicionar notas de versão
    release_notes_urls = {}
    
    print("\n" + "="*80)
    print("[DESCOBRIDOR DE NOTAS DE VERSÃO]")
    print("="*80 + "\n")
    
    for module_name, module_info in modulos.items():
        print(f"[MÓDULO] {module_name}")
        print(f"  URL base: {module_info['url']}")
        print(f"  Slug: {module_info['slug']}")
        
        # Gerar URLs de notas de versão
        possible_urls = ReleaseNotesDiscoverer.generate_release_notes_urls(module_info)
        
        print(f"  URLs possíveis de notas de versão:")
        for url in possible_urls:
            print(f"    - {url}")
            
            # Armazenar informação
            if module_name not in release_notes_urls:
                release_notes_urls[module_name] = []
            
            release_notes_urls[module_name].append({
                'url': url,
                'pattern': url.split(module_info['slug'] + '/')[1] if module_info['slug'] in url else 'unknown'
            })
        
        print()
    
    # Salvar configuração
    output_file = Path("release_notes_config.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(release_notes_urls, f, ensure_ascii=False, indent=2)
    
    print("="*80)
    print(f"[SALVO] Configuração de notas de versão em: {output_file}")
    print("="*80 + "\n")
    
    return release_notes_urls


def scrape_release_notes_urls() -> List[Tuple[str, str]]:
    """
    Retorna lista de módulos + URLs de notas de versão para scraping.
    
    Returns:
        Lista de tuplas (nome_do_módulo, url) para notas de versão
    """
    
    config_file = Path("release_notes_config.json")
    
    if not config_file.exists():
        print("[AVISO] Arquivo release_notes_config.json não encontrado")
        print("        Execute primeiro: python src/adicionar_notas_versao.py")
        return []
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = []
    
    for module_name, notes_list in config.items():
        for note_info in notes_list:
            # Usar a URL mais comum (notas-da-versao/)
            if 'notas-da-versao' in note_info['url']:
                urls.append((
                    f"{module_name} (Notas de Versão)",
                    note_info['url']
                ))
    
    return urls


if __name__ == "__main__":
    import sys
    
    print("\n[SCRAPER] Descobridor de Notas de Versão")
    print("-" * 80)
    
    # Gerar configuração
    release_notes = add_release_notes_to_modules()
    
    # Exibir resumo
    print("\n[RESUMO]")
    print(f"  Módulos com notas de versão: {len(release_notes)}")
    
    if release_notes:
        print("\n[PRÓXIMO PASSO]")
        print("  Para scraping: python src/scraper_unificado.py --release-notes")
        print("  Ou integre manualmente as URLs de notas de versão ao scraper")
    
    print("\n")
