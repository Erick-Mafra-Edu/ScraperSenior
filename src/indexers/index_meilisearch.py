#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Indexador Meilisearch para Documentação Senior
==============================================

Processa documentos da estrutura docs_estruturado/ e indexa no Meilisearch.
Extrai metadados e cria índice de busca vetorial.

Uso:
    python src/indexers/index_meilisearch.py [--url http://localhost:7700] [--api-key meilisearch_master_key]

Features:
- Índexação automática de documentos
- Extração de metadados
- Suporte a HTML original
- Debug com exemplos
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import sys
from urllib.parse import urljoin
import meilisearch


class MeilisearchIndexer:
    """Indexador para Meilisearch"""
    
    def __init__(self, url: str = "http://localhost:7700", api_key: str = "meilisearch_master_key"):
        self.url = url
        self.api_key = api_key
        self.client = meilisearch.Client(url, api_key)
        self.index_name = "senior_docs"
        self.documents = []
        self.stats = {
            'processed': 0,
            'indexed': 0,
            'failed': 0,
            'by_module': {}
        }
    
    def connect(self) -> bool:
        """Testa conexão com Meilisearch"""
        try:
            health = self.client.health()
            print(f"[✓] Conectado ao Meilisearch: {self.url}")
            return True
        except Exception as e:
            print(f"[✗] Erro ao conectar ao Meilisearch: {e}")
            return False
    
    def create_index(self) -> bool:
        """Cria índice no Meilisearch com configurações otimizadas"""
        try:
            # Deletar índice anterior se existir
            try:
                self.client.index(self.index_name).delete()
                print(f"[✓] Índice anterior '{self.index_name}' removido")
            except:
                pass
            
            # Criar novo índice
            index = self.client.create_index(self.index_name, {"primaryKey": "id"})
            
            # Configurar atributos para busca
            index.update_searchable_attributes([
                "title",
                "content",
                "breadcrumb",
                "module",
                "headers"
            ])
            
            # Configurar atributos para filtragem
            index.update_filterable_attributes([
                "module",
                "type",
                "has_html"
            ])
            
            # Configurar atributos para ordenação
            index.update_sortable_attributes([
                "module",
                "title"
            ])
            
            # Configurar ranking
            index.update_ranking_rules([
                "words",
                "typo",
                "proximity",
                "attribute",
                "sort",
                "exactness"
            ])
            
            print(f"[✓] Índice '{self.index_name}' criado com sucesso")
            return True
        except Exception as e:
            print(f"[✗] Erro ao criar índice: {e}")
            return False
    
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
    
    def index_documents(self, batch_size: int = 100) -> bool:
        """
        Indexa documentos no Meilisearch em lotes
        """
        if not self.documents:
            print("[✗] Nenhum documento para indexar")
            return False
        
        try:
            index = self.client.index(self.index_name)
            
            # Indexar em lotes
            for i in range(0, len(self.documents), batch_size):
                batch = self.documents[i:i+batch_size]
                response = index.add_documents(batch)
                self.stats['indexed'] += len(batch)
                
                progress = min(i + batch_size, len(self.documents))
                print(f"  [{progress}/{len(self.documents)}] Documentos indexados...")
            
            print(f"\n[✓] Total indexado: {self.stats['indexed']} documentos")
            return True
        except Exception as e:
            print(f"[✗] Erro ao indexar documentos: {e}")
            return False
    
    def debug_sample(self, module_name: str = "TECNOLOGIA", limit: int = 3):
        """
        Exibe amostra de documentos indexados para debug
        """
        try:
            index = self.client.index(self.index_name)
            
            print(f"\n[DEBUG] Amostra de documentos do módulo '{module_name}':\n")
            
            # Buscar documentos do módulo
            results = index.search(
                "",
                {
                    "filter": f'module = "{module_name}"',
                    "limit": limit,
                    "attributesToRetrieve": ["id", "title", "url", "module", "headers_count", "content_length"]
                }
            )
            
            if results['hits']:
                for i, doc in enumerate(results['hits'], 1):
                    print(f"  {i}. {doc['title']}")
                    print(f"     URL: {doc['url']}")
                    print(f"     ID: {doc['id']}")
                    print(f"     Headers: {doc.get('headers_count', 0)} | Content: {doc.get('content_length', 0)} chars")
                    print()
            else:
                print(f"  Nenhum documento encontrado para '{module_name}'")
            
            # Estatísticas gerais
            print(f"\n[STATS] Estatísticas do índice:")
            stats = index.get_stats()
            print(f"  Total de documentos: {stats['numberOfDocuments']}")
            print(f"  Documentos em processamento: {stats['isIndexing']}")
            
        except Exception as e:
            print(f"[✗] Erro ao exibir amostra: {e}")
    
    def search_example(self, query: str = "CRM"):
        """
        Faz uma busca de exemplo
        """
        try:
            index = self.client.index(self.index_name)
            
            print(f"\n[SEARCH] Buscando por: '{query}'\n")
            
            results = index.search(
                query,
                {
                    "limit": 5,
                    "attributesToRetrieve": ["id", "title", "url", "module", "breadcrumb"]
                }
            )
            
            if results['hits']:
                for i, doc in enumerate(results['hits'], 1):
                    print(f"  {i}. {doc['title']}")
                    print(f"     Módulo: {doc['module']} | Breadcrumb: {doc['breadcrumb']}")
                    print(f"     URL: {doc['url']}")
                    print()
            else:
                print(f"  Nenhum resultado encontrado")
            
        except Exception as e:
            print(f"[✗] Erro ao buscar: {e}")
    
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


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Indexador Meilisearch para Documentação Senior")
    parser.add_argument("--url", default="http://localhost:7700", help="URL do Meilisearch")
    parser.add_argument("--api-key", default="meilisearch_master_key", help="Chave de API")
    parser.add_argument("--docs-dir", default="docs_estruturado", help="Diretório de documentos")
    parser.add_argument("--debug", action="store_true", help="Exibir amostra para debug")
    parser.add_argument("--search", type=str, help="Fazer busca de exemplo")
    
    args = parser.parse_args()
    
    # Criar indexador
    indexer = MeilisearchIndexer(url=args.url, api_key=args.api_key)
    
    # Testar conexão
    if not indexer.connect():
        print("\n[!] Configure o Meilisearch:")
        print("   docker-compose up -d meilisearch")
        print("   # Aguarde alguns segundos para iniciar")
        sys.exit(1)
    
    # Criar índice
    if not indexer.create_index():
        sys.exit(1)
    
    # Processar documentos
    docs = indexer.process_documents(Path(args.docs_dir))
    
    if not docs:
        print("[✗] Nenhum documento foi processado")
        sys.exit(1)
    
    # Indexar
    if not indexer.index_documents():
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
    asyncio.run(main())
