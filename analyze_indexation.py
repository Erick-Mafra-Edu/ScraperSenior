#!/usr/bin/env python3
"""
Analise de Indexacao - Meilisearch
Verifica se documentos estao sendo indexados, especialmente da API Zendesk
"""

import sys
import os
import json
from datetime import datetime

try:
    import requests
    import meilisearch
except ImportError:
    print("[ERROR] Instale: pip install requests meilisearch")
    sys.exit(1)


class MeilisearchAnalyzer:
    """Analisa status de indexacao"""
    
    def __init__(self, url="http://localhost:7700", api_key=None):
        self.url = url
        self.api_key = api_key or os.getenv("MEILISEARCH_KEY", "5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa")
        self.client = None
        self.index = None
        
    def connect(self):
        """Conecta ao Meilisearch"""
        print(f"\n[*] Conectando a Meilisearch ({self.url})...")
        
        try:
            self.client = meilisearch.Client(self.url, self.api_key)
            health = self.client.health()
            print(f"[OK] Conectado com sucesso")
            
            # Tenta obter indice
            try:
                self.index = self.client.get_index("documentation")
                print(f"[OK] Indice 'documentation' encontrado")
                return True
            except:
                print(f"[!] Indice 'documentation' nao existe")
                return False
        
        except Exception as e:
            print(f"[ERROR] Nao conseguiu conectar: {e}")
            print(f"[!] Meilisearch nao esta rodando em {self.url}")
            print(f"    Inicie com: docker-compose up -d")
            return False
    
    def get_stats(self):
        """Obtem estatisticas do indice"""
        if not self.index:
            return None
        
        try:
            stats = self.index.get_stats()
            return stats
        except Exception as e:
            print(f"[ERROR] Erro ao obter stats: {e}")
            return None
    
    def count_by_source(self):
        """Conta documentos por fonte"""
        if not self.index:
            return {}
        
        print(f"\n[*] Contando documentos por fonte...")
        
        try:
            # Website
            website_count = 0
            try:
                result = self.index.search("", {"filter": "source = 'website'"})
                website_count = result.get('estimatedTotalHits', 0)
            except:
                pass
            
            # Zendesk
            zendesk_count = 0
            try:
                result = self.index.search("", {"filter": "source = 'zendesk_api'"})
                zendesk_count = result.get('estimatedTotalHits', 0)
            except:
                pass
            
            return {
                'website': website_count,
                'zendesk': zendesk_count,
                'total': website_count + zendesk_count
            }
        
        except Exception as e:
            print(f"[ERROR] Erro ao contar por fonte: {e}")
            return {}
    
    def get_sample_documents(self, source=None, limit=5):
        """Obtem amostra de documentos"""
        if not self.index:
            return []
        
        try:
            filter_str = None
            if source:
                filter_str = f"source = '{source}'"
            
            result = self.index.search(
                "",
                {
                    "filter": filter_str,
                    "limit": limit,
                    "sort": ["id:desc"]
                }
            )
            
            return result.get('hits', [])
        
        except Exception as e:
            print(f"[ERROR] Erro ao obter amostra: {e}")
            return []
    
    def analyze_zendesk_documents(self):
        """Analisa documentos Zendesk em detalhe"""
        print(f"\n{'='*80}")
        print("ANALISE DETALHADA - ZENDESK HELP CENTER")
        print(f"{'='*80}\n")
        
        # Obtem amostra
        docs = self.get_sample_documents(source='zendesk_api', limit=10)
        
        if not docs:
            print("[!] Nenhum documento Zendesk encontrado")
            return False
        
        print(f"[OK] {len(docs)} documentos Zendesk encontrados\n")
        
        for i, doc in enumerate(docs, 1):
            print(f"Documento {i}:")
            print(f"  ID: {doc.get('id', 'N/A')}")
            print(f"  Titulo: {doc.get('title', 'N/A')[:60]}...")
            print(f"  URL: {doc.get('url', 'N/A')[:60]}...")
            print(f"  Fonte: {doc.get('source', 'N/A')}")
            print(f"  Modulo: {doc.get('module', 'N/A')}")
            print(f"  Conteudo: {len(doc.get('content', ''))} caracteres")
            print()
        
        return True
    
    def analyze_website_documents(self):
        """Analisa documentos Website em detalhe"""
        print(f"\n{'='*80}")
        print("ANALISE DETALHADA - WEBSITE DOCUMENTATION")
        print(f"{'='*80}\n")
        
        # Obtem amostra
        docs = self.get_sample_documents(source='website', limit=10)
        
        if not docs:
            print("[!] Nenhum documento Website encontrado")
            return False
        
        print(f"[OK] {len(docs)} documentos Website encontrados\n")
        
        for i, doc in enumerate(docs, 1):
            print(f"Documento {i}:")
            print(f"  ID: {doc.get('id', 'N/A')}")
            print(f"  Titulo: {doc.get('title', 'N/A')[:60]}...")
            print(f"  Fonte: {doc.get('source', 'N/A')}")
            print(f"  Modulo: {doc.get('module', 'N/A')}")
            print(f"  Breadcrumb: {doc.get('breadcrumb', 'N/A')[:60]}...")
            print(f"  Conteudo: {len(doc.get('content', ''))} caracteres")
            print()
        
        return True
    
    def test_search(self):
        """Testa funcao de busca"""
        print(f"\n{'='*80}")
        print("TESTE DE BUSCA")
        print(f"{'='*80}\n")
        
        test_queries = [
            ("CRM", None),
            ("Help Center", "zendesk_api"),
            ("Portal", "website"),
        ]
        
        for query, source in test_queries:
            try:
                filter_str = None
                if source:
                    filter_str = f"source = '{source}'"
                
                result = self.index.search(
                    query,
                    {
                        "filter": filter_str,
                        "limit": 3
                    }
                )
                
                hits = result.get('hits', [])
                print(f"Query: '{query}' (fonte: {source or 'todas'})")
                print(f"  Resultados: {len(hits)}")
                
                if hits:
                    for hit in hits[:2]:
                        print(f"    - {hit.get('title', 'N/A')[:50]}... ({hit.get('source')})")
                
                print()
            
            except Exception as e:
                print(f"[ERROR] Erro na busca '{query}': {e}\n")
    
    def print_summary(self):
        """Imprime resumo final"""
        stats = self.get_stats()
        counts = self.count_by_source()
        
        print(f"\n{'='*80}")
        print("RESUMO DA INDEXACAO")
        print(f"{'='*80}\n")
        
        if stats:
            print(f"Total de documentos indexados: {stats.get('numberOfDocuments', 0):,}")
            print(f"Tamanho do indice: {stats.get('databaseSize', 0):,} bytes")
            print(f"Tamanho do indice (legivel): {stats.get('databaseSize', 0) / 1024 / 1024:.2f} MB")
        
        print(f"\nBreakdown por fonte:")
        print(f"  Website: {counts.get('website', 0)} documentos")
        print(f"  Zendesk API: {counts.get('zendesk', 0)} documentos")
        print(f"  Total: {counts.get('total', 0)} documentos")
        
        if counts.get('zendesk', 0) > 0:
            pct = (counts.get('zendesk', 0) / counts.get('total', 1)) * 100
            print(f"\n[OK] Zendesk representa {pct:.1f}% do indice")
        else:
            print(f"\n[!] AVISO: Nenhum documento Zendesk indexado!")
        
        print(f"\nTimestamp: {datetime.now().isoformat()}")
        print(f"{'='*80}\n")
    
    def run_analysis(self):
        """Executa analise completa"""
        print(f"\n{'='*80}")
        print("ANALISE DE INDEXACAO - MEILISEARCH")
        print(f"{'='*80}")
        
        # Conecta
        if not self.connect():
            return False
        
        # Imprime resumo
        self.print_summary()
        
        # Analisa Website
        self.analyze_website_documents()
        
        # Analisa Zendesk
        self.analyze_zendesk_documents()
        
        # Testa busca
        self.test_search()
        
        return True


def main():
    """Funcao principal"""
    analyzer = MeilisearchAnalyzer()
    success = analyzer.run_analysis()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
