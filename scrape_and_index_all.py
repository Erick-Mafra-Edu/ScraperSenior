#!/usr/bin/env python3
"""
Scraper Unificado + Indexador Meilisearch
==========================================

Executa scraper de documentação local + API Zendesk Help Center
Converte ambos para formato unificado
Indexa tudo no Meilisearch em um único índice

Uso:
    python scrape_and_index_all.py [--url http://localhost:7700] [--api-key key]
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import sys
import time
import os
from datetime import datetime

# Tenta importar meilisearch
try:
    import meilisearch
except ImportError:
    print("[!] meilisearch nao instalado. Instalando...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "meilisearch"])
    import meilisearch

from src.scraper_modular import ModularScraper
from src.api_zendesk import ZendeskScraper
from src.zendesk_modular_adapter import ZendeskToModularAdapter


class UnifiedIndexer:
    """Indexador unificado para múltiplas fontes"""
    
    def __init__(self, 
                 meilisearch_url: str = None,
                 meilisearch_key: str = None,
                 output_dir: str = "docs_unified"):
        
        # Lê variáveis de ambiente, com fallback para valores padrão
        self.meilisearch_url = meilisearch_url or os.getenv('MEILISEARCH_URL', 'http://meilisearch:7700')
        self.meilisearch_key = meilisearch_key or os.getenv('MEILISEARCH_KEY', 'meilisearch_master_key_change_me')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Tenta conectar
        self.client = None
        self.index = None
        
        # Estatísticas
        self.stats = {
            'start_time': datetime.now(),
            'website_docs': 0,
            'zendesk_docs': 0,
            'total_docs': 0,
            'indexed_docs': 0,
            'errors': []
        }
    
    def connect_meilisearch(self) -> bool:
        """Conecta ao Meilisearch com retry e inicialização robusta"""
        import time
        max_retries = 10  # Aumentado para 10 tentativas
        retry_delay = 2
        
        print(f"\n📡 Conectando ao Meilisearch ({self.meilisearch_url})...")
        
        for attempt in range(max_retries):
            try:
                # Cria cliente
                self.client = meilisearch.Client(self.meilisearch_url, self.meilisearch_key)
                print(f"   ✅ Cliente Meilisearch criado (tentativa {attempt + 1})")
                
                # Testa saúde - isso é crítico
                health = self.client.health()
                print(f"   ✅ Meilisearch saudável")
                
                # Aguarda para garantir que Meilisearch está pronto
                time.sleep(2)
                
                # Tenta obter índice existente
                try:
                    self.index = self.client.get_index("documentation")
                    print(f"   📑 Índice 'documentation' encontrado (existente)")
                    
                    # Verifica se está pronto
                    stats = self.index.get_stats()
                    print(f"   ✅ Índice pronto: {stats.number_of_documents} documentos")
                    return True
                    
                except Exception as get_error:
                    # Índice não existe, cria novo
                    print(f"   ℹ️  Índice não existe, criando novo...")
                    try:
                        # Cria índice
                        task = self.client.create_index(
                            "documentation",
                            {"primaryKey": "id"}
                        )
                        print(f"   ✅ Índice criado (Task: {task.task_uid if hasattr(task, 'task_uid') else 'pending'})")
                        
                        # Aguarda criação completa
                        time.sleep(4)
                        
                        # Obtém referência ao índice
                        self.index = self.client.get_index("documentation")
                        print(f"   ✅ Índice 'documentation' pronto para indexação")
                        
                        return True
                        
                    except Exception as create_error:
                        print(f"   ❌ Erro ao criar índice: {create_error}")
                        raise
                        
            except Exception as e:
                print(f"   ⚠️  Tentativa {attempt + 1}/{max_retries} falhou: {type(e).__name__}")
                
                if attempt < max_retries - 1:
                    print(f"   ⏳ Aguardando {retry_delay}s antes de retry...")
                    time.sleep(retry_delay)
                else:
                    print(f"   ❌ Todas as {max_retries} tentativas falharam!")
        
        print(f"\n❌ FALHA CRÍTICA: Meilisearch não acessível")
        print(f"   URL: {self.meilisearch_url}")
        print(f"   Verifique se: docker-compose up está rodando")
        
        return False
    
    async def scrape_website_docs(self) -> List[Dict]:
        """Scrapa documentação do site usando scraper_modular"""
        print(f"\n🕷️  Scrapando documentação do site...")
        
        try:
            docs = []
            
            # Carrega estrutura de docs_estruturado/
            docs_dir = Path("docs_estruturado")
            if not docs_dir.exists():
                print(f"   ⚠️  Diretório docs_estruturado não encontrado")
                return docs
            
            count = 0
            for content_file in docs_dir.rglob("content.txt"):
                try:
                    # Obtém metadata correspondente
                    metadata_file = content_file.parent / "metadata.json"
                    
                    with open(content_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    metadata = {}
                    if metadata_file.exists():
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    
                    # Calcula caminho relativo como breadcrumb
                    rel_path = content_file.parent.relative_to(docs_dir)
                    breadcrumb = " > ".join(str(rel_path).split("\\")[:-1]).replace("\\", " > ")
                    
                    doc = {
                        'id': f"website_{count}",
                        'type': 'website_documentation',
                        'url': f"docs:///{rel_path.parent}",
                        'title': metadata.get('title', str(rel_path.parent)),
                        'content': content[:5000],  # Limita a 5000 caracteres
                        'module': metadata.get('module', 'Documentation'),
                        'breadcrumb': breadcrumb or 'Root',
                        'source': 'website',
                        'metadata': {
                            'source': 'website_scraper',
                            'scraped_at': datetime.now().isoformat(),
                            'path': str(rel_path)
                        }
                    }
                    docs.append(doc)
                    count += 1
                    
                except Exception as e:
                    self.stats['errors'].append(f"Website doc error: {e}")
            
            print(f"   ✅ {count} documentos do site coletados")
            self.stats['website_docs'] = count
            return docs
        
        except Exception as e:
            self.stats['errors'].append(f"Website scraping error: {e}")
            print(f"   ❌ Erro ao scrape website: {e}")
            return []
    
    async def scrape_zendesk_docs(self) -> List[Dict]:
        """Scrapa documentação da API Zendesk"""
        print(f"\n[*] Scrapando Zendesk Help Center API...")
        
        try:
            docs = []
            
            # Inicializa scraper Zendesk
            scraper = ZendeskScraper()
            
            # Executa o scraper
            result = await scraper.scrape_all()
            
            # Obtém documentos coletados pelo scraper
            count = 0
            for article in scraper.documents:
                try:
                    doc = {
                        'id': f"zendesk_{article.get('id', 'unknown')}",
                        'type': 'zendesk_article',
                        'url': article.get('url', ''),
                        'title': article.get('title', ''),
                        'content': article.get('content', '')[:5000],  # Limita a 5000 caracteres
                        'module': 'Help Center',
                        'breadcrumb': f"Help Center > {article.get('locale', 'pt-BR')}",
                        'source': 'zendesk_api',
                        'metadata': {
                            'source': 'zendesk_help_center',
                            'scraped_at': datetime.now().isoformat(),
                            'category_id': article.get('category_id'),
                            'section_id': article.get('section_id'),
                            'created_at': article.get('created_at'),
                            'updated_at': article.get('updated_at')
                        }
                    }
                    docs.append(doc)
                    count += 1
                    
                    if count % 50 == 0:
                        print(f"   📄 {count} artigos processados...")
                
                except Exception as e:
                    self.stats['errors'].append(f"Zendesk article error: {e}")
            
            print(f"   ✅ {count} artigos Zendesk coletados")
            self.stats['zendesk_docs'] = count
            return docs
        
        except Exception as e:
            self.stats['errors'].append(f"Zendesk scraping error: {e}")
            print(f"   ❌ Erro ao scrape Zendesk: {e}")
            print(f"   💡 Verifica se a API está acessível")
            return []
    
    def save_unified_jsonl(self, documents: List[Dict]) -> Path:
        """Salva documentos em formato JSONL unificado"""
        print(f"\n💾 Salvando documentos em formato unificado...")
        
        try:
            output_file = self.output_dir / "unified_documentation.jsonl"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for doc in documents:
                    f.write(json.dumps(doc, ensure_ascii=False) + '\n')
            
            print(f"   ✅ {len(documents)} documentos salvos em {output_file}")
            return output_file
        
        except Exception as e:
            self.stats['errors'].append(f"Save JSONL error: {e}")
            print(f"   ❌ Erro ao salvar: {e}")
            return None
    
    def save_metadata(self, documents: List[Dict]) -> Path:
        """Salva metadados dos documentos"""
        try:
            metadata_file = self.output_dir / "unified_metadata.json"
            
            metadata = {
                'total_documents': len(documents),
                'sources': {
                    'website': self.stats['website_docs'],
                    'zendesk': self.stats['zendesk_docs']
                },
                'timestamp': datetime.now().isoformat(),
                'documents': [
                    {
                        'id': doc['id'],
                        'title': doc['title'],
                        'source': doc['source'],
                        'module': doc.get('module', 'Unknown')
                    } for doc in documents
                ]
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Metadados salvos em {metadata_file}")
            return metadata_file
        
        except Exception as e:
            self.stats['errors'].append(f"Save metadata error: {e}")
            print(f"   ❌ Erro ao salvar metadados: {e}")
            return None
    
    def index_documents(self, documents: List[Dict]) -> bool:
        """Indexa documentos no Meilisearch com retry e tratamento de erro robusto"""
        if self.index is None:
            print(f"\n❌ ERRO CRÍTICO: Índice não inicializado")
            print(f"   Meilisearch não foi conectado com sucesso")
            print(f"   Documentos foram salvos em JSONL mas NÃO indexados!")
            self.stats['errors'].append("Index not initialized - documents saved but not indexed")
            return False
        
        if not documents:
            print(f"   ⚠️  Nenhum documento para indexar")
            return False
        
        print(f"\n🔍 Indexando {len(documents)} documentos no Meilisearch...")
        
        try:
            # Indexa em lotes para melhor controle
            batch_size = 100
            total_indexed = 0
            failed_batches = 0
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                
                try:
                    # Converte para dicionários simples e limpa dados
                    batch_data = []
                    for doc in batch:
                        clean_doc = {
                            'id': str(doc.get('id', f'doc_{i}')),
                            'type': doc.get('type', 'document'),
                            'url': str(doc.get('url', ''))[:2000],
                            'title': str(doc.get('title', ''))[:500],
                            'content': str(doc.get('content', ''))[:10000],
                            'module': str(doc.get('module', ''))[:200],
                            'breadcrumb': str(doc.get('breadcrumb', ''))[:500],
                            'source': str(doc.get('source', ''))[:100]
                        }
                        batch_data.append(clean_doc)
                    
                    # Envia o lote
                    task = self.index.add_documents(batch_data)
                    total_indexed += len(batch_data)
                    
                    if (total_indexed % 500 == 0) or (total_indexed >= len(documents)):
                        task_uid = task.task_uid if hasattr(task, 'task_uid') else str(task)
                        print(f"   📤 {total_indexed}/{len(documents)} documentos enviados (Task: {task_uid})")
                
                except Exception as batch_error:
                    failed_batches += 1
                    print(f"   ⚠️  Erro ao indexar lote {i//batch_size + 1}: {batch_error}")
                    self.stats['errors'].append(f"Batch {i//batch_size + 1} error: {batch_error}")
                    # Continua com o próximo lote
            
            if total_indexed > 0:
                print(f"   ✅ {total_indexed} documentos foram enviados para indexação")
                print(f"   💾 Meilisearch processará em background")
                self.stats['indexed_docs'] = total_indexed
                
                if failed_batches > 0:
                    print(f"   ⚠️  {failed_batches} lotes falharam")
                
                return True
            else:
                print(f"   ❌ Nenhum documento foi indexado!")
                return False
        
        except Exception as e:
            self.stats['errors'].append(f"Indexing error: {e}")
            print(f"   ❌ Erro crítico ao indexar: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_stats(self):
        """Imprime estatísticas finais"""
        elapsed = datetime.now() - self.stats['start_time']
        
        print(f"\n{'='*80}")
        print("📊 ESTATÍSTICAS FINAIS")
        print(f"{'='*80}")
        print(f"Website documentos:     {self.stats['website_docs']}")
        print(f"Zendesk artigos:        {self.stats['zendesk_docs']}")
        print(f"Total de documentos:    {self.stats['website_docs'] + self.stats['zendesk_docs']}")
        print(f"Documentos indexados:   {self.stats['indexed_docs']}")
        print(f"Tempo total:            {elapsed.total_seconds():.2f}s")
        
        if self.stats['errors']:
            print(f"\n⚠️  Erros encontrados ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:5]:
                print(f"   - {error}")
        
        print(f"{'='*80}\n")
    
    async def run(self):
        """Executa pipeline completo"""
        print(f"\n{'='*80}")
        print("🚀 SCRAPER + INDEXADOR UNIFICADO")
        print(f"{'='*80}")
        
        # Conecta ao Meilisearch
        self.connect_meilisearch()
        
        # Scrapa documentação
        website_docs = await self.scrape_website_docs()
        
        # Scrapa Zendesk
        zendesk_docs = await self.scrape_zendesk_docs()
        
        # Combina documentos
        all_docs = website_docs + zendesk_docs
        self.stats['total_docs'] = len(all_docs)
        
        if not all_docs:
            print(f"\n❌ Nenhum documento foi coletado!")
            return False
        
        print(f"\n✅ Total de documentos coletados: {len(all_docs)}")
        
        # Salva em JSONL
        self.save_unified_jsonl(all_docs)
        
        # Salva metadados
        self.save_metadata(all_docs)
        
        # Indexa no Meilisearch
        self.index_documents(all_docs)
        
        # Imprime estatísticas
        self.print_stats()
        
        return True


async def main():
    """Função principal"""
    # Parse argumentos
    meilisearch_url = "http://localhost:7700"
    meilisearch_key = "meilisearch_master_key"
    
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--url" and i+1 < len(sys.argv)-1:
            meilisearch_url = sys.argv[i+2]
        elif arg == "--api-key" and i+1 < len(sys.argv)-1:
            meilisearch_key = sys.argv[i+2]
    
    # Executa indexador
    indexer = UnifiedIndexer(
        meilisearch_url=meilisearch_url,
        meilisearch_key=meilisearch_key
    )
    
    success = await indexer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
