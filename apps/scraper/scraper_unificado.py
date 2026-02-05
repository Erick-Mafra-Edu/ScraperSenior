#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAPER UNIFICADO - Senior Documentation
=========================================

Sistema completo de scraping para documentação Senior em:
- MadCap Flare (iframe#topic + hash navigation)
- Astro moderno (aside#sidebar + hierarquia de menu)

Features:
- Detecção automática de tipo
- Extração hierárquica de conteúdo
- Organização em estrutura de pastas
- Geração de JSONL para indexação (Meilisearch)
- Metadados completos para busca

Output:
- docs_estruturado/: Documentação organizada em pastas
- docs_indexacao.jsonl: Arquivo JSONL para indexadores
- docs_metadata.json: Metadados e análise completa
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse, unquote
import re
from typing import Dict, List, Optional, Tuple


class SeniorDocScraper:
    """Scraper unificado para documentação Senior"""
    
    def __init__(self, save_html: bool = False):
        self.output_dir = Path("docs_estruturado")
        self.output_dir.mkdir(exist_ok=True)
        self.save_html = save_html
        self.documents = []
        self.metadata = {
            'timestamp': datetime.now().isoformat(),
            'save_html': save_html,
            'statistics': {
                'total_pages': 0,
                'total_chars': 0,
                'by_module': {},
                'by_type': {'madcap': 0, 'astro': 0, 'unknown': 0},
                'navigation_stats': {
                    'successful': 0,
                    'failed': 0,
                    'skipped': 0
                }
            }
        }
    
    def build_absolute_url(self, base_url: str, link_url: str) -> Optional[str]:
        """Constrói URL absoluta a partir de base + link. Trata URLs MadCap com hash e notas de versão."""
        if not link_url:
            return None
        
        if link_url.startswith('http'):
            return link_url
        
        if link_url.startswith('#'):
            parsed = urlparse(base_url)
            base_path = parsed.scheme + '://' + parsed.netloc + parsed.path
            hash_part = link_url[1:]
            
            if '?' in hash_part or '%3F' in hash_part:
                return base_path + '#' + hash_part
            else:
                return base_url + link_url
        
        return urljoin(base_url, link_url)
    
    def normalize_anchor_url(self, url: str) -> str:
        """Normaliza URLs com âncoras para extração de conteúdo (notas de versão, etc)."""
        if '#' not in url:
            return url
        
        # Para URLs de notas de versão com âncoras como #6-10-4.htm
        # Converte para um anchor válido removendo .htm e ajustando formato
        base, anchor = url.rsplit('#', 1)
        
        # Remove .htm/.html do final da âncora
        anchor = anchor.replace('.htm', '').replace('.html', '')
        
        # Padroniza formato de versão (6-10-4 → 6-10-4)
        return base + '#' + anchor
    
    def parse_senior_doc_link(self, url: str) -> Dict[str, str]:
        """
        Parseia links diretos de documentação Senior.
        
        Exemplo:
        https://documentacao.senior.com.br/tecnologia/5.10.4/#lsp/funcoes/gerais.html%3FTocPath%3DTecnologia%7CFerramentas...
        
        Retorna:
        {
            'base_url': 'https://documentacao.senior.com.br/tecnologia/5.10.4/',
            'file_path': 'lsp/funcoes/gerais.html',
            'toc_path': 'Tecnologia|Ferramentas de Apoio|...',
            'module': 'tecnologia',
            'version': '5.10.4',
            'breadcrumb': ['Tecnologia', 'Ferramentas de Apoio', 'LSP - Linguagem Senior de Programação', ...]
        }
        """
        result = {
            'base_url': '',
            'file_path': '',
            'toc_path': '',
            'module': '',
            'version': '',
            'breadcrumb': []
        }
        
        try:
            # Dividir URL em base e hash
            if '#' not in url:
                return result
            
            base_part, hash_part = url.rsplit('#', 1)
            
            # Extrair módulo e versão da URL base
            # Padrão: https://documentacao.senior.com.br/{modulo}/{versao}/
            parsed = urlparse(base_part)
            path_parts = parsed.path.strip('/').split('/')
            
            if len(path_parts) >= 2:
                result['module'] = path_parts[0]  # 'tecnologia'
                result['version'] = path_parts[1]  # '5.10.4'
            
            result['base_url'] = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            # Parsear hash: lsp/funcoes/gerais.html%3FTocPath%3D...
            if '%3F' in hash_part:
                # Contains URL-encoded ?
                file_part, query_part = hash_part.split('%3F', 1)
            elif '?' in hash_part:
                # Contains literal ?
                file_part, query_part = hash_part.split('?', 1)
            else:
                file_part = hash_part
                query_part = ''
            
            result['file_path'] = file_part  # 'lsp/funcoes/gerais.html'
            
            # Decode da query_part completa para processar %XX
            query_part_decoded = unquote(query_part)
            
            # Extrair TocPath se existir
            # TocPath%3D significa TocPath= ou TocPath=
            if 'TocPath' in query_part_decoded:
                # Encontrar posição do TocPath
                toc_idx = query_part_decoded.find('TocPath')
                toc_start = toc_idx + len('TocPath')
                
                # Verificar se é = (já decodificado)
                if toc_start < len(query_part_decoded) and query_part_decoded[toc_start] == '=':
                    toc_value = query_part_decoded[toc_start+1:]
                else:
                    toc_value = ''
                
                # Remove qualquer parâmetro adicional
                if '&' in toc_value:
                    toc_value = toc_value.split('&')[0]
                
                if toc_value:
                    result['toc_path'] = toc_value
                    
                    # Parsear breadcrumb: Tecnologia|Ferramentas de Apoio|...
                    if '|' in toc_value:
                        breadcrumbs = []
                        for b in toc_value.split('|'):
                            # Decodificar cada breadcrumb item completamente
                            b = unquote(b.strip())
                            if b:
                                # Remover sufixos como _____0, _____1 etc
                                if '____' in b:
                                    b = b.split('____')[0].strip()
                                if b:
                                    breadcrumbs.append(b)
                        result['breadcrumb'] = breadcrumbs
            
            # Se não temos breadcrumb da TocPath, criar a partir do file_path
            if not result['breadcrumb'] and result['file_path']:
                # lsp/funcoes/gerais.html → ['lsp', 'funcoes']
                parts = result['file_path'].split('/')
                result['breadcrumb'] = [p.replace('-', ' ').replace('.html', '').replace('.htm', '').title() 
                                       for p in parts if p and not p.endswith('.html') and not p.endswith('.htm')]
        
        except Exception as e:
            print(f"[AVISO] Erro ao parsear link Senior: {e}")
        
        return result
    
    def identify_senior_doc_links(self, url: str) -> bool:
        """Identifica se uma URL é um link direto de documentação Senior."""
        return 'documentacao.senior.com.br' in url and '#' in url and ('lsp' in url.lower() or 'funcoes' in url.lower())
    
    async def detect_doc_type(self, page) -> str:
        """Detecta tipo de documentação"""
        is_astro = await page.evaluate("() => !!document.getElementById('new-toc')")
        is_madcap = await page.evaluate("() => !!document.getElementById('topic')")
        
        return 'astro' if is_astro else 'madcap' if is_madcap else 'unknown'
    
    async def extract_release_notes_anchors(self, page) -> List[Dict]:
        """Extrai âncoras de notas de versão (ex: #6-10-4.htm) como seções."""
        anchors = await page.evaluate("""
            () => {
                const result = [];
                const seen = new Set();
                
                // Estratégia 1: Procurar por links com âncoras de versão (padrão: #X-X-X.htm)
                const versionLinks = document.querySelectorAll('a[href*="#"]');
                versionLinks.forEach(link => {
                    const href = link.getAttribute('href');
                    // Padrão: seções/versões como #6-10-4.htm
                    if (href && /^#[\\d\\-]+\\.htm/.test(href)) {
                        const text = link.textContent?.trim() || href.replace('#', '').replace('.htm', '');
                        if (!seen.has(href)) {
                            result.push({
                                text: text,
                                href: href,
                                children: [],
                                type: 'version'
                            });
                            seen.add(href);
                        }
                    }
                });
                
                // Estratégia 2: Procurar por headings que parecem versões
                const headings = document.querySelectorAll('h1, h2, h3, h4');
                headings.forEach(h => {
                    const text = h.textContent?.trim();
                    if (text && /^\\d+\\.\\d+\\.\\d+/.test(text)) {
                        if (!seen.has(text)) {
                            result.push({
                                text: text,
                                href: '#' + text.replace(/\\./g, '-') + '.htm',
                                children: [],
                                type: 'heading'
                            });
                            seen.add(text);
                        }
                    }
                });
                
                return result;
            }
        """)
        
        return anchors
    
    async def extract_astro_menu(self, page) -> List[Dict]:
        """Extrai hierarquia do menu Astro"""
        menu_data = await page.evaluate("""
            () => {
                const result = [];
                const sidebar = document.getElementById('sidebar-menu');
                
                if (!sidebar) return result;
                
                function extractMenuItems(container, level = 0) {
                    const items = [];
                    
                    container.querySelectorAll(':scope > .menu-item').forEach(menuItem => {
                        const header = menuItem.querySelector('.item-header');
                        const link = header?.querySelector('a, span');
                        const href = link?.href || null;
                        const text = link?.textContent?.trim() || '';
                        
                        const submenu = menuItem.querySelector(':scope > .submenu');
                        
                        const item = {
                            text,
                            href,
                            level,
                            children: []
                        };
                        
                        if (submenu) {
                            item.children = extractMenuItems(submenu, level + 1);
                        }
                        
                        items.push(item);
                    });
                    
                    return items;
                }
                
                return extractMenuItems(sidebar);
            }
        """)
        
        return menu_data
    
    async def extract_madcap_seções(self, page) -> List[Dict]:
        """Extrai seções do MadCap Flare com expansão agressiva de menus collapsed e suporte a notas de versão"""
        import asyncio
        
        # Primeiro, detectar se é página de notas de versão
        is_release_notes_page = await page.evaluate("""
            () => {
                const title = document.title.toLowerCase();
                const url = window.location.href.toLowerCase();
                const bodyText = document.body.textContent.toLowerCase();
                return (title.includes('versão') || title.includes('release') || title.includes('nota') ||
                        url.includes('notas-da-versao') || url.includes('notas-de-versao') || url.includes('release') ||
                        bodyText.includes('notas da versão'));
            }
        """)
        
        # Se for página de notas de versão, extrair âncoras de versão primeiro
        if is_release_notes_page:
            release_anchors = await self.extract_release_notes_anchors(page)
            if release_anchors and len(release_anchors) > 0:
                print(f"    [NOTAS DE VERSÃO] Encontradas {len(release_anchors)} versões como âncoras")
                return release_anchors
        
        # Expandir TODOS os menus collapsed iterativamente
        # Pode ser necessário múltiplas rodadas em menus aninhados
        for round_num in range(5):  # Até 5 rodadas para cobrir aninhamento profundo
            collapsed_count = await page.evaluate("""
                () => {
                    const toc = document.getElementById('toc');
                    if (!toc) return 0;
                    
                    const collapsedItems = toc.querySelectorAll('li.tree-node-collapsed');
                    let clickedCount = 0;
                    
                    collapsedItems.forEach(item => {
                        const link = item.querySelector('a');
                        if (link) {
                            const href = link.getAttribute('href');
                            // Clicar em links que são menus de navegação ou estão collapsed
                            if (!href || href.startsWith('javascript:') || !href.startsWith('#')) {
                                link.click();
                                clickedCount++;
                            }
                        }
                    });
                    
                    return clickedCount;
                }
            """)
            
            if collapsed_count == 0:
                # Nenhum item collapsed encontrado, parar
                break
            
            # Aguardar abertura
            await asyncio.sleep(0.5)
        
        # Aguardar fim de todas as expansões
        await asyncio.sleep(1)
        
        # Extrair TODOS os links após expansão completa
        seções = await page.evaluate("""
            () => {
                const result = [];
                const links = document.querySelectorAll('a[href*="#"]');
                const seen = new Set();
                
                links.forEach(link => {
                    const href = link.getAttribute('href');
                    const text = link.textContent?.trim();
                    
                    // Filtrar: apenas links com href # e text não vazio
                    if (href && text && text.length > 0 && href.includes('#') && !seen.has(href)) {
                        result.push({
                            text: text,
                            href: href,
                            children: []
                        });
                        seen.add(href);
                    }
                });
                
                return result;
            }
        """)
        
        return seções
    
    async def scrape_page(self, page, url: str, base_url: str = None) -> Optional[Dict]:
        """Scrapa conteúdo de uma página com tratamento de erro para URLs inválidas e âncoras"""
        # Normalizar URL se contiver âncoras (notas de versão)
        url = self.normalize_anchor_url(url)
        
        try:
            # Primeira tentativa com timeout estendido para iframes MadCap
            try:
                await page.goto(url, wait_until="networkidle", timeout=20000)
            except Exception as timeout_err:
                # Se timeout, tenta com wait_until="domcontentloaded" (mais rápido)
                if "timeout" in str(timeout_err).lower():
                    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                else:
                    raise
            await asyncio.sleep(1)  # Aumentado para dar mais tempo ao iframe carregar
        except Exception as e:
            error_msg = str(e).lower()
            
            # Se é erro de URL inválida e temos base_url, tenta voltar para base
            if ('invalid url' in error_msg or 'cannot navigate' in error_msg) and base_url:
                try:
                    await page.goto(base_url, wait_until="networkidle", timeout=15000)
                    await asyncio.sleep(0.5)
                except:
                    return None
            else:
                return None
        
        content = await page.evaluate("""
            () => {
                // Função auxiliar para extrair título
                const extractTitle = () => {
                    // Primeiro, tentar encontrar h1 dentro do iframe#topic
                    try {
                        const iframeTitle = document.querySelector('iframe#topic')?.contentDocument
                            ?.querySelector('h1')?.textContent?.trim();
                        if (iframeTitle) return iframeTitle;
                    } catch (e) {
                        // CORS ou iframe não acessível
                    }
                    
                    // Se não encontrou no iframe, tentar h1 no document raiz
                    const h1 = document.querySelector('h1')?.textContent?.trim();
                    if (h1) return h1;
                    
                    // Fallback para document.title
                    const docTitle = document.title?.trim();
                    if (docTitle && docTitle.length > 0) return docTitle;
                    
                    // Último recurso: tentar qualquer h2 se não houver h1
                    const h2 = document.querySelector('h2')?.textContent?.trim();
                    if (h2) return h2;
                    
                    return '';
                };
                
                const result = {
                    title: extractTitle(),
                    url: window.location.href,
                    text_content: '',
                    html_content: '',
                    headers: [],
                    paragraphs: [],
                    lists: [],
                    links: [],
                    total_chars: 0
                };
                
                let main = document.querySelector('iframe#topic')?.contentDocument?.body;
                
                if (!main) {
                    main = document.querySelector('main') || 
                           document.querySelector('[data-role="main"]') ||
                           document.querySelector('[role="main"]') ||
                           document.querySelector('article') ||
                           document.querySelector('.page-content') ||
                           document.querySelector('.document-content') ||
                           document.querySelector('[class*="content"]');
                }
                
                if (!main) {
                    result.text_content = document.body.textContent;
                    result.total_chars = result.text_content.length;
                    return result;
                }
                
                result.text_content = main.textContent;
                result.html_content = main.innerHTML;
                result.total_chars = result.text_content.length;
                
                main.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {
                    const text = h.textContent.trim();
                    if (text.length > 0) result.headers.push(text);
                });
                
                main.querySelectorAll('p').forEach(p => {
                    const text = p.textContent.trim();
                    if (text.length > 20) result.paragraphs.push(text);
                });
                
                main.querySelectorAll('ul, ol').forEach(list => {
                    const items = [];
                    list.querySelectorAll(':scope > li').forEach(li => {
                        const text = li.textContent.trim();
                        if (text.length > 0) items.push(text);
                    });
                    if (items.length > 0) result.lists.push(items);
                });
                
                main.querySelectorAll('a[href]').forEach(a => {
                    const href = a.getAttribute('href');
                    if (href && !href.startsWith('#')) {
                        result.links.push({
                            text: a.textContent.trim(),
                            href: href
                        });
                    }
                });
                
                return result;
            }
        """)
        
        return content
    
    async def scrape_page_with_retry(self, page, url: str, base_url: str = None, max_retries: int = 2) -> Optional[Dict]:
        """Scrapa página com retry se conteúdo for pequeno demais"""
        for attempt in range(max_retries):
            content = await self.scrape_page(page, url, base_url)
            
            if not content:
                continue
            
            # Se conteúdo é suficiente, retorna
            if content['total_chars'] >= 100:
                return content
            
            # Se não é suficiente e ainda temos tentativas, aguarda e tenta novamente
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Backoff exponencial: 1s, 2s, 4s
                print(f"    [AVISO] Conteúdo pequeno ({content['total_chars']} chars), aguardando {wait_time}s e retentando...")
                await asyncio.sleep(wait_time)
        
        # Retorna última tentativa mesmo que pequena
        return content
    
    async def extract_article_links(self, page, current_url: str) -> List[Dict]:
        """
        Extrai links de tabelas/funções dentro de um artigo.
        
        Exemplo: Em uma página de "Funções Gerais", extrai links como:
        - <a href="gerais/alfaparaint.htm">AlfaParaInt</a>
        - <a href="gerais/arqexiste.htm">ArqExiste</a>
        
        Retorna lista de dicts com:
        {
            'text': 'Nome da Função',
            'href': 'caminho/relativo.htm',
            'absolute_url': 'https://...',
            'type': 'article_link'
        }
        """
        try:
            article_links = await page.evaluate("""
                () => {
                    const result = [];
                    const seen = new Set();
                    
                    // Estratégia 1: Buscar links em tabelas (estrutura comum)
                    const tables = document.querySelectorAll('table');
                    tables.forEach(table => {
                        const rows = table.querySelectorAll('tbody tr');
                        rows.forEach(row => {
                            const link = row.querySelector('a[href]');
                            if (link) {
                                const href = link.getAttribute('href');
                                const text = link.textContent?.trim();
                                
                                // Filtrar links relativos (não começam com http, #, ou javascript)
                                if (href && text && 
                                    !href.startsWith('http') && 
                                    !href.startsWith('#') && 
                                    !href.startsWith('javascript:') &&
                                    !seen.has(href)) {
                                    
                                    result.push({
                                        text: text,
                                        href: href,
                                        type: 'table_link'
                                    });
                                    seen.add(href);
                                }
                            }
                        });
                    });
                    
                    // Estratégia 2: Buscar links em listas de definição
                    const defLists = document.querySelectorAll('dl, .function-list, [class*="list"]');
                    defLists.forEach(list => {
                        const links = list.querySelectorAll('a[href]');
                        links.forEach(link => {
                            const href = link.getAttribute('href');
                            const text = link.textContent?.trim();
                            
                            if (href && text &&
                                !href.startsWith('http') &&
                                !href.startsWith('#') &&
                                !href.startsWith('javascript:') &&
                                !seen.has(href)) {
                                
                                result.push({
                                    text: text,
                                    href: href,
                                    type: 'list_link'
                                });
                                seen.add(href);
                            }
                        });
                    });
                    
                    // Estratégia 3: Buscar links em divs específicas de conteúdo
                    const contentDivs = document.querySelectorAll('article, main, [role="main"], [data-role="main"]');
                    contentDivs.forEach(div => {
                        // Procurar links que parecem fazer referência a documentação técnica
                        const allLinks = div.querySelectorAll('a[href]');
                        allLinks.forEach(link => {
                            const href = link.getAttribute('href');
                            const text = link.textContent?.trim();
                            
                            // Links para .htm ou .html (arquivos de documentação)
                            if (href && text && 
                                (href.endsWith('.htm') || href.endsWith('.html')) &&
                                !href.startsWith('http') &&
                                !href.startsWith('#') &&
                                !href.startsWith('javascript:') &&
                                !seen.has(href) &&
                                text.length > 0 &&
                                text.length < 100) { // Evitar parágrafos inteiros
                                
                                result.push({
                                    text: text,
                                    href: href,
                                    type: 'content_link'
                                });
                                seen.add(href);
                            }
                        });
                    });
                    
                    return result;
                }
            """)
            
            # Converter hrefs relativos para URLs absolutas
            parsed_url = urlparse(current_url)
            base_for_relative = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/', 1)[0]}/"
            
            result = []
            for link in article_links:
                absolute_url = self.build_absolute_url(base_for_relative, link['href'])
                if absolute_url:
                    result.append({
                        'text': link['text'],
                        'href': link['href'],
                        'absolute_url': absolute_url,
                        'type': link['type']
                    })
            
            return result
            
        except Exception as e:
            print(f"    [AVISO] Erro ao extrair links do artigo: {e}")
            return []
    
    def sanitize_path(self, text: str) -> str:
        """Sanitiza texto para usar em caminho"""
        if not text:
            return "unnamed"
        
        # Converter para string
        text = str(text).strip()
        
        # Remover caracteres especiais (manter apenas alphanumério, espaço, hífen)
        text = re.sub(r'[^\w\s\-]', '', text, flags=re.UNICODE)
        
        # Substituir espaços por underscore
        text = re.sub(r'\s+', '_', text)
        
        # Limitar tamanho e remover underscores duplicados
        text = re.sub(r'_+', '_', text)
        text = text.strip('_')[:50]
        
        # Garantir que não fica vazio
        return text if text else "unnamed"
    
    async def flatten_menu(self, menu_items: List[Dict], breadcrumb: List[str] = None) -> List[Dict]:
        """Flatteia hierarquia em lista de URLs com breadcrumb"""
        if breadcrumb is None:
            breadcrumb = []
        
        all_links = []
        
        for item in menu_items:
            current_breadcrumb = breadcrumb + [item['text']]
            
            if item.get('href'):
                all_links.append({
                    'text': item['text'],
                    'url': item['href'],
                    'breadcrumb': current_breadcrumb,
                    'level': len(current_breadcrumb) - 1,
                    'folder_path': '/'.join([self.sanitize_path(b) for b in current_breadcrumb[:-1]])
                })
            
            # Processar filhos se existirem (pode ser 'children', 'items', etc)
            children = item.get('children') or item.get('items') or item.get('submenu') or []
            if children:
                children_links = await self.flatten_menu(children, current_breadcrumb)
                all_links.extend(children_links)
        
        return all_links
    
    async def save_document(self, doc: Dict, breadcrumb: List[str]):
        """Salva documento em hierarquia de pastas"""
        # Criar pasta com sanitização
        if not breadcrumb or len(breadcrumb) == 0:
            return None
            
        folder = self.output_dir
        for part in breadcrumb:
            sanitized = self.sanitize_path(part)
            if sanitized:  # Garantir que não é vazio
                folder = folder / sanitized
        
        folder.mkdir(parents=True, exist_ok=True)
        
        # Salvar conteúdo
        try:
            content_file = folder / 'content.txt'
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(f"# {doc['title']}\n\n")
                f.write(f"URL: {doc['url']}\n\n")
                f.write("---\n\n")
                f.write(doc['text_content'][:50000])  # Primeiros 50k chars (documentação técnica completa)
            
            # Salvar HTML original se solicitado
            if self.save_html and doc.get('html_content'):
                html_file = folder / 'page.html'
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(f"<!--\n")
                    f.write(f"Title: {doc['title']}\n")
                    f.write(f"URL: {doc['url']}\n")
                    f.write(f"Scraped: {datetime.now().isoformat()}\n")
                    f.write(f"-->\n\n")
                    f.write(doc['html_content'])
            
            # Salvar metadata
            meta_file = folder / 'metadata.json'
            metadata = {
                'title': doc['title'],
                'url': doc['url'],
                'breadcrumb': breadcrumb,
                'total_chars': doc['total_chars'],
                'headers_count': len(doc['headers']),
                'paragraphs_count': len(doc['paragraphs']),
                'lists_count': len(doc['lists']),
                'links_count': len(doc['links']),
                'has_html': self.save_html and bool(doc.get('html_content')),
                'scraped_at': datetime.now().isoformat()
            }
            
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return {
                'folder': str(folder),
                'metadata': metadata
            }
        except Exception as e:
            print(f"    [AVISO] Erro ao salvar {doc['title']}: {e}")
            return None
    
    def path_to_full_url(self, breadcrumb: List[str], url_hint: str = None) -> str:
        """
        Converte caminho de breadcrumb para URL completo.
        
        Suporta dois domínios:
        - documentacao.senior.com.br (padrão para documentação técnica)
        - suporte.senior.com.br (para suporte/Zendesk)
        
        Exemplos:
        ["BI", "Apresentação"] → "https://documentacao.senior.com.br/bi/apresentacao/"
        ["Help Center", "LSP"] → "https://suporte.senior.com.br/help-center/lsp/"
        """
        if not breadcrumb:
            return "https://documentacao.senior.com.br/"
        
        # Detectar domínio baseado no breadcrumb ou hint
        domain = "documentacao.senior.com.br"  # Padrão
        
        # Palavras-chave que indicam domínio suporte.senior.com.br
        suporte_keywords = ['help center', 'suporte', 'zendesk', 'faq', 'ticket', 'support']
        first_part_lower = breadcrumb[0].lower() if breadcrumb else ""
        
        if any(kw in first_part_lower for kw in suporte_keywords):
            domain = "suporte.senior.com.br"
        
        # Também verificar no hint se fornecido
        if url_hint:
            if 'suporte' in url_hint.lower():
                domain = "suporte.senior.com.br"
            elif 'documentacao' in url_hint.lower():
                domain = "documentacao.senior.com.br"
        
        # Converter para lowercase e substituir espaços/underscores por hífens
        path_parts = []
        for part in breadcrumb:
            # Remove caracteres especiais e normaliza
            normalized = part.lower()
            normalized = normalized.replace("_", "-")
            normalized = normalized.replace(" ", "-")
            # Remove múltiplos hífens
            normalized = re.sub(r'-+', '-', normalized)
            # Remove caracteres não alfanuméricos (exceto hífens)
            normalized = re.sub(r'[^a-z0-9-]', '', normalized)
            if normalized:
                path_parts.append(normalized)
        
        path = "/".join(path_parts)
        return f"https://{domain}/{path}/"
    
    def generate_jsonl(self):
        """Gera arquivo JSONL para indexação com URLs completos"""
        jsonl_file = Path("docs_indexacao.jsonl")
        
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for doc in self.documents:
                # Gerar URL completo a partir do breadcrumb
                # Se doc['url'] já é completo (começa com http), usar como está
                # Senão, construir a partir do breadcrumb
                url = doc['url']
                if not url.startswith('http'):
                    url = self.path_to_full_url(doc['breadcrumb'])
                
                # Documento para Meilisearch
                index_doc = {
                    'id': url,  # URL completa como ID único
                    'title': doc['title'],
                    'url': url,  # URL completo para o cliente acessar
                    'module': doc['breadcrumb'][0] if doc['breadcrumb'] else 'unknown',
                    'category': doc['breadcrumb'][1] if len(doc['breadcrumb']) > 1 else '',
                    'subcategory': doc['breadcrumb'][2] if len(doc['breadcrumb']) > 2 else '',
                    'breadcrumb': ' > '.join(doc['breadcrumb']),
                    'content': doc['text_content'][:50000],  # Primeiros 50k chars (documentação técnica com tabelas de funções)
                    'content_length': doc['total_chars'],
                    'headers': doc['headers'][:5],  # Primeiros 5 headers
                    'tags': doc['breadcrumb'][1:],  # Tags são as categorias
                    'language': 'pt-BR',
                    'indexed_at': datetime.now().isoformat()
                }
                
                f.write(json.dumps(index_doc, ensure_ascii=False) + '\n')
        
        return jsonl_file
    
    async def scrape_direct_link(self, direct_url: str, page):
        """
        Scrapa um link direto de documentação Senior.
        
        Exemplo:
        https://documentacao.senior.com.br/tecnologia/5.10.4/#lsp/funcoes/gerais.html%3FTocPath%3D...
        """
        print(f"\n{'='*90}")
        print(f"[LINK DIRETO] {direct_url}")
        print(f"{'='*90}\n")
        
        # Parse do link
        link_info = self.parse_senior_doc_link(direct_url)
        print(f"[1] Análise do link:")
        print(f"    Módulo: {link_info['module']}")
        print(f"    Versão: {link_info['version']}")
        print(f"    Arquivo: {link_info['file_path']}")
        if link_info['breadcrumb']:
            print(f"    Breadcrumb: {' > '.join(link_info['breadcrumb'])}\n")
        
        # Scraping
        print(f"[2] Scrapando página...")
        content = await self.scrape_page_with_retry(page, direct_url, link_info['base_url'], max_retries=3)
        
        if content and content['total_chars'] >= 100:
            # Construir breadcrumb completo
            if link_info['breadcrumb']:
                breadcrumb = link_info['breadcrumb']
            else:
                # Fallback: usar modulo e arquivo
                breadcrumb = [link_info['module'].title()] if link_info['module'] else ['Direct Link']
            
            print(f"[3] Salvando documento...")
            # Salvar documento
            save_result = await self.save_document(content, breadcrumb)
            
            # Adicionar aos documentos para JSONL
            if save_result:
                self.documents.append({
                    'title': content['title'],
                    'url': direct_url,
                    'breadcrumb': breadcrumb,
                    'text_content': content['text_content'],
                    'total_chars': content['total_chars'],
                    'headers': content['headers'],
                    'paragraphs': content['paragraphs'],
                    'lists': content['lists'],
                    'links': content['links']
                })
                
                print(f"[OK] Documento salvo com sucesso!")
                print(f"    Título: {content['title']}")
                print(f"    Caracteres: {content['total_chars']}")
                print(f"    Headers: {len(content['headers'])}")
                return True
            else:
                print(f"[ERRO] Falha ao salvar documento")
                return False
        else:
            chars = content['total_chars'] if content else 0
            print(f"[ERRO] Conteúdo insuficiente ({chars} caracteres)")
            return False
    
    async def scrape_module(self, module_name: str, base_url: str, page):
        """Scrapa um módulo completo"""
        print(f"\n{'='*90}")
        print(f"[MÓDULO] {module_name}")
        print(f"{'='*90}\n")
        
        # Detectar tipo
        await page.goto(base_url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        
        doc_type = await self.detect_doc_type(page)
        print(f"[1] Tipo de documentação: {doc_type.upper()}\n")
        
        self.metadata['statistics']['by_type'][doc_type] += 1
        self.metadata['statistics']['by_module'][module_name] = {
            'type': doc_type,
            'pages': 0,
            'total_chars': 0
        }
        
        # Extrair hierarquia
        print(f"[2] Extraindo hierarquia...")
        
        if doc_type == 'astro':
            menu = await self.extract_astro_menu(page)
        else:
            menu = await self.extract_madcap_seções(page)
        
        all_links = await self.flatten_menu(menu)
        print(f"    [OK] {len(all_links)} paginas encontradas\n")
        
        # Scraping
        print(f"[3] Scrapando paginas...")
        
        for i, link in enumerate(all_links, 1):
            if (i - 1) % 10 == 0:
                print(f"    [{i}/{len(all_links)}] {link['text'][:40]}")
            
            # Construir URL absoluta
            absolute_url = self.build_absolute_url(base_url, link['url'])
            
            if not absolute_url:
                self.metadata['statistics']['navigation_stats']['skipped'] += 1
                continue
            
            # Scraping com retry para iframes MadCap que demoram a carregar
            # Usar o doc_type da tentativa anterior (armazenado no metadata)
            doc_type = self.metadata['statistics']['by_module'][module_name]['type']
            max_retries = 3 if doc_type == 'madcap' else 1  # MadCap pode precisar de mais tentativas
            content = await self.scrape_page_with_retry(page, absolute_url, base_url, max_retries)
            
            # Validação melhorada: conteúdo mínimo de 100 caracteres
            # (aumentado de 50 para evitar conteúdo lixo ou placeholders)
            if content and content['total_chars'] >= 100:
                breadcrumb = [module_name] + link['breadcrumb']
                
                # Salvar documento
                save_result = await self.save_document(content, breadcrumb)
                
                # Adicionar aos documentos para JSONL
                if save_result:
                    self.documents.append({
                        'title': content['title'],
                        'url': absolute_url,
                        'breadcrumb': breadcrumb,
                        'text_content': content['text_content'],
                        'total_chars': content['total_chars'],
                        'headers': content['headers'],
                        'paragraphs': content['paragraphs'],
                        'lists': content['lists'],
                        'links': content['links']
                    })
                    
                    # Atualizar stats
                    self.metadata['statistics']['by_module'][module_name]['pages'] += 1
                    self.metadata['statistics']['by_module'][module_name]['total_chars'] += content['total_chars']
                    self.metadata['statistics']['navigation_stats']['successful'] += 1
                
                # NOVO: Extrair links de artigos (tabelas de funções, etc)
                print(f"    [LINKS] Extraindo links do artigo...")
                article_links = await self.extract_article_links(page, absolute_url)
                
                if article_links:
                    print(f"    [LINKS] Encontrados {len(article_links)} links internos")
                    for sub_link in article_links:
                        # Construir breadcrumb para subpágina
                        sub_breadcrumb = breadcrumb + [sub_link['text']]
                        
                        # Scraping da subpágina
                        sub_content = await self.scrape_page_with_retry(page, sub_link['absolute_url'], base_url, max_retries=2)
                        
                        if sub_content and sub_content['total_chars'] >= 50:  # Requisito menor para subpáginas
                            # Salvar subpágina
                            sub_save_result = await self.save_document(sub_content, sub_breadcrumb)
                            
                            if sub_save_result:
                                self.documents.append({
                                    'title': sub_content['title'],
                                    'url': sub_link['absolute_url'],
                                    'breadcrumb': sub_breadcrumb,
                                    'text_content': sub_content['text_content'],
                                    'total_chars': sub_content['total_chars'],
                                    'headers': sub_content['headers'],
                                    'paragraphs': sub_content['paragraphs'],
                                    'lists': sub_content['lists'],
                                    'links': sub_content['links']
                                })
                                
                                self.metadata['statistics']['by_module'][module_name]['pages'] += 1
                                self.metadata['statistics']['by_module'][module_name]['total_chars'] += sub_content['total_chars']
                                self.metadata['statistics']['navigation_stats']['successful'] += 1
            else:
                self.metadata['statistics']['navigation_stats']['failed'] += 1
        
        print(f"    [OK] Completo\n")
    
    async def run(self, modules: Optional[List[Tuple[str, str]]] = None):
        """Executa scraping para múltiplos módulos ou descobre automaticamente"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
            from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            
            print("\n" + "="*90)
            print("[SCRAPER UNIFICADO] Senior Documentation")
            print("="*90)
            
            for module_name, base_url in modules:
                if not base_url or base_url.strip() == '':
                    print(f"\n[AVISO] URL vazia para {module_name}, pulando...")
                    continue
                    
                await self.scrape_module(module_name, base_url, page)
            
            await browser.close()
        
        # Gerar JSONL
        print(f"\n[4] Gerando arquivo JSONL para indexação...")
        jsonl_file = self.generate_jsonl()
        print(f"    [OK] {jsonl_file}")
        print(f"    [OK] {len(self.documents)} documentos\n")
        
        # Atualizar stats
        self.metadata['statistics']['total_pages'] = len(self.documents)
        self.metadata['statistics']['total_chars'] = sum(d['total_chars'] for d in self.documents)
        self.metadata['output_jsonl'] = str(jsonl_file)
        
        # Salvar metadata
        meta_file = Path("docs_metadata.json")
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        
        # Resumo final
        print("="*90)
        print("[RESULTADO FINAL]")
        print("="*90)
        print(f"\n[INFO] Documentos salvos em: {self.output_dir}/")
        print(f"[INFO] Total de paginas: {self.metadata['statistics']['total_pages']}")
        print(f"[INFO] Total de conteudo: {self.metadata['statistics']['total_chars']:,} caracteres")
        print(f"[INFO] Arquivo JSONL: {jsonl_file}")
        print(f"[INFO] Metadados: {meta_file}\n")
        
        print("[NAVEGACAO]")
        nav_stats = self.metadata['statistics']['navigation_stats']
        print(f"  Bem-sucedidas: {nav_stats['successful']}")
        print(f"  Falhadas: {nav_stats['failed']}")
        print(f"  Puladas: {nav_stats['skipped']}\n")
        
        print("[MODULOS PROCESSADOS]")
        for mod_name, stats in self.metadata['statistics']['by_module'].items():
            print(f"  - {mod_name}: {stats['pages']} paginas | {stats['total_chars']:,} chars ({stats['type']})")
        
        print("\n" + "="*90 + "\n")


async def main():
    import sys
    save_html = "--save-html" in sys.argv or "--save_html" in sys.argv
    scraper = SeniorDocScraper(save_html=save_html)
    
    # Tentar carregar módulos descobertos
    modulos_file = Path("modulos_descobertos.json")
    if modulos_file.exists():
        with open(modulos_file, 'r', encoding='utf-8') as f:
            modulos_dict = json.load(f)
            modules = [(name, info['url']) for name, info in modulos_dict.items()]
    else:
        # Fallback se arquivo não existe
        modules = [
            ("Gestão de Relacionamento CRM", "https://documentacao.senior.com.br/gestao-de-relacionamento-crm/6.2.4/"),
            ("Tecnologia", "https://documentacao.senior.com.br/tecnologia/5.10.4/"),
        ]
    
    # Executar com os módulos carregados
    await scraper.run(modules=modules)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[AVISO] Interrompido")
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
