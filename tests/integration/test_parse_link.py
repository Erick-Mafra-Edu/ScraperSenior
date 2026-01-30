#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from scraper_unificado import SeniorDocScraper

url = 'https://documentacao.senior.com.br/tecnologia/5.10.4/#lsp/funcoes/gerais.html%3FTocPath%3DTecnologia%7CFerramentas%2520de%2520Apoio%7CLSP%2520-%2520Linguagem%2520Senior%2520de%2520Programa%25C3%25A7%25C3%25A3o%7CFun%25C3%25A7%25C3%25B5es%7CFun%25C3%25A7%25C3%25B5es%2520Gerais%7C_____0'

scraper = SeniorDocScraper()
info = scraper.parse_senior_doc_link(url)

print('=' * 80)
print('PARSING RESULTS')
print('=' * 80)
print(f'Módulo: {info["module"]}')
print(f'Versão: {info["version"]}')
print(f'Arquivo: {info["file_path"]}')
print(f'TocPath: {info["toc_path"]}')
if info['breadcrumb']:
    print(f'Breadcrumb: {" > ".join(info["breadcrumb"])}')
print()
