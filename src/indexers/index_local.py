#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Indexador Local para Documentação Senior
========================================

Indexa documentos localmente em JSON, pronto para Meilisearch.
Sem dependência de servidor externo para desenvolvimento/debug.

Uso:
    python src/indexers/index_local.py [--debug] [--search "query"]
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import sys


class LocalIndexer:
    """Indexador local para desenvolvimento"""
    
    def __init__(self):
        self.index_file = Path("docs_indexacao_detailed.jsonl")
        self.documents = []
        self.stats = {
            'processed': 0,
            'indexed': 0,
            'failed': 0,
            'by_module': {}
        }
    
    def process_documents(self, docs_dir: Path = None) -> List[Dict]:
        """
        Processa documentos da estrutura docs_estruturado/
        e extrai metadados para indexação
        """
        if docs_dir is None:
            docs_dir = Path("docs_estruturado")
        
        if not docs_dir.exists():
            print(f"[✗] Diretório não encontrado: {docs_dir}")
            return []
        
        print(f"\n[→] Processando documentos de {docs_dir}...\n")
        
        # Iterar por módulos
        for module_dir in sorted(docs_dir.iterdir()):
            if not module_dir.is_dir():
                continue
            
            module_name = module_dir.name
            module_docs = 0
            
            print(f"  Módulo: {module_name}")
            
            # Iterar por documentos do módulo
            for doc_path in sorted(module_dir.rglob("metadata.json")):
                try:
                    # Ler metadados
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Ler conteúdo
                    content_file = doc_path.parent / "content.txt"
                    content = ""
                    if content_file.exists():
                        with open(content_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    # Verificar se tem HTML
                    html_file = doc_path.parent / "page.html"
                    has_html = html_file.exists()
                    
                    # Extrair texto sem headers
                    content_clean = content.split("---\n\n", 1)[-1] if "---" in content else content
                    
                    # Extrair breadcrumb
                    breadcrumb_parts = [module_name]
                    rel_path = doc_path.parent.relative_to(module_dir)
                    breadcrumb_parts.extend(p.replace("_", " ") for p in rel_path.parts[:-1])
                    breadcrumb = " > ".join(breadcrumb_parts)
                    
                    # Extrair headers do conteúdo
                    headers = []
                    for line in content.split("\n"):
                        if line.startswith("#"):
                            header_text = line.replace("#", "").strip()
                            if header_text:
                                headers.append(header_text)
                    
                    # Criar documento para indexação
                    doc_id = f"{module_name}_{doc_path.parent.name}".replace(" ", "_")
                    
                    doc = {
                        "id": doc_id,
                        "title": metadata.get('title', 'Sem título'),
                        "url": metadata.get('url', ''),
                        "module": module_name,
                        "breadcrumb": breadcrumb,
                        "content": content_clean[:5000],  # Primeiros 5k caracteres
                        "content_length": len(content_clean),
                        "headers": headers,
                        "type": "documentation",
                        "has_html": has_html,
                        "headers_count": metadata.get('headers_count', 0),
                        "paragraphs_count": metadata.get('paragraphs_count', 0),
                        "scraped_at": metadata.get('scraped_at', '')
                    }
                    
                    self.documents.append(doc)
                    module_docs += 1
                    self.stats['processed'] += 1
                    
                except Exception as e:
                    print(f"    [✗] Erro ao processar {doc_path}: {e}")
                    self.stats['failed'] += 1
                    continue
            
            # Registrar estatísticas por módulo
            self.stats['by_module'][module_name] = module_docs
            print(f"    → {module_docs} documentos processados")
        
        print(f"\n[✓] Total de documentos processados: {self.stats['processed']}")
        return self.documents
    
    def save_index(self) -> bool:
        """
        Salva índice como JSONL (formato Meilisearch)
        """
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                for doc in self.documents:
                    f.write(json.dumps(doc, ensure_ascii=False) + '\n')
            
            self.stats['indexed'] = len(self.documents)
            print(f"[✓] Índice salvo em: {self.index_file}")
            print(f"[✓] Total de documentos indexados: {self.stats['indexed']}")
            return True
        except Exception as e:
            print(f"[✗] Erro ao salvar índice: {e}")
            return False
    
    def debug_sample(self, module_name: str = "TECNOLOGIA", limit: int = 3):
        """
        Exibe amostra de documentos para debug
        """
        print(f"\n[DEBUG] Amostra de documentos do módulo '{module_name}':\n")
        
        matching = [d for d in self.documents if d['module'] == module_name][:limit]
        
        if matching:
            for i, doc in enumerate(matching, 1):
                print(f"  {i}. {doc['title']}")
                print(f"     URL: {doc['url']}")
                print(f"     ID: {doc['id']}")
                print(f"     Breadcrumb: {doc['breadcrumb']}")
                print(f"     Headers: {doc.get('headers_count', 0)} | Content: {doc.get('content_length', 0)} chars")
                print(f"     Has HTML: {doc['has_html']}")
                if doc['headers']:
                    print(f"     Headers encontrados: {', '.join(doc['headers'][:3])}")
                print()
        else:
            print(f"  Nenhum documento encontrado para '{module_name}'")
    
    def search_example(self, query: str = "CRM"):
        """
        Faz uma busca de exemplo (busca simples em texto)
        """
        print(f"\n[SEARCH] Buscando por: '{query}'\n")
        
        query_lower = query.lower()
        results = []
        
        for doc in self.documents:
            score = 0
            # Buscar em título (peso maior)
            if query_lower in doc['title'].lower():
                score += 3
            # Buscar em módulo
            if query_lower in doc['module'].lower():
                score += 2
            # Buscar em breadcrumb
            if query_lower in doc['breadcrumb'].lower():
                score += 1
            # Buscar em conteúdo
            if query_lower in doc['content'].lower():
                score += 1
            
            if score > 0:
                results.append((score, doc))
        
        # Ordenar por score
        results.sort(key=lambda x: x[0], reverse=True)
        
        if results:
            for i, (score, doc) in enumerate(results[:5], 1):
                print(f"  {i}. {doc['title']}")
                print(f"     Módulo: {doc['module']} | Breadcrumb: {doc['breadcrumb']}")
                print(f"     URL: {doc['url']}")
                print(f"     Score: {score}")
                print()
        else:
            print(f"  Nenhum resultado encontrado")
    
    def print_stats(self):
        """Imprime estatísticas finais"""
        print(f"\n{'='*80}")
        print(f"[ESTATÍSTICAS DE INDEXAÇÃO]")
        print(f"{'='*80}\n")
        print(f"  Processados: {self.stats['processed']}")
        print(f"  Indexados: {self.stats['indexed']}")
        print(f"  Falhados: {self.stats['failed']}")
        print(f"\n[POR MÓDULO]")
        for module, count in sorted(self.stats['by_module'].items()):
            print(f"  - {module}: {count}")
        print(f"\n{'='*80}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Indexador Local para Documentação Senior")
    parser.add_argument("--docs-dir", default="docs_estruturado", help="Diretório de documentos")
    parser.add_argument("--debug", action="store_true", help="Exibir amostra para debug")
    parser.add_argument("--search", type=str, help="Fazer busca de exemplo")
    
    args = parser.parse_args()
    
    # Criar indexador
    indexer = LocalIndexer()
    
    # Processar documentos
    docs = indexer.process_documents(Path(args.docs_dir))
    
    if not docs:
        print("[✗] Nenhum documento foi processado")
        sys.exit(1)
    
    # Salvar índice
    if not indexer.save_index():
        sys.exit(1)
    
    # Debug
    if args.debug:
        indexer.debug_sample("TECNOLOGIA", limit=3)
    
    # Busca de exemplo
    if args.search:
        indexer.search_example(args.search)
    else:
        indexer.search_example("CRM")
    
    # Estatísticas
    indexer.print_stats()


if __name__ == "__main__":
    main()
