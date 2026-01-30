#!/usr/bin/env python3
"""
Post-Scraping Indexation Script
Indexa documentos que foram scraped para o Meilisearch
"""

import json
import meilisearch
from pathlib import Path
import time
import sys

def main():
    MEILISEARCH_URL = "http://meilisearch:7700"
    MEILISEARCH_KEY = "meilisearch_master_key_change_me"
    JSONL_FILE = Path("/app/docs_unified/unified_documentation.jsonl")
    
    print("=" * 80)
    print("POST-SCRAPING INDEXATION")
    print("=" * 80)
    
    # Check if JSONL file exists
    if not JSONL_FILE.exists():
        print(f"\n❌ ERRO: Arquivo não encontrado: {JSONL_FILE}")
        return False
    
    # Aguarda conexão ao Meilisearch
    print(f"\n⏳ Aguardando Meilisearch ({MEILISEARCH_URL})...")
    client = None
    for attempt in range(10):
        try:
            client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_KEY)
            health = client.health()
            print(f"✅ Meilisearch disponível")
            break
        except Exception as e:
            print(f"⚠️  Tentativa {attempt + 1}/10: {str(e)[:50]}...")
            time.sleep(3)
    
    if not client:
        print(f"\n❌ Não foi possível conectar ao Meilisearch")
        return False
    
    # Get or create index
    print(f"\n📑 Obtendo/criando índice 'documentation'...")
    try:
        index = client.get_index("documentation")
        print(f"✅ Índice obtido")
    except:
        try:
            task = client.create_index("documentation", {"primaryKey": "id"})
            print(f"✅ Índice criado (Task: {task.task_uid if hasattr(task, 'task_uid') else task})")
            time.sleep(3)
            index = client.get_index("documentation")
        except Exception as e:
            print(f"❌ Erro ao criar índice: {e}")
            return False
    
    # Load and index documents
    print(f"\n📂 Carregando documentos de {JSONL_FILE}...")
    documents = []
    with open(JSONL_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                documents.append(json.loads(line))
    
    print(f"✅ {len(documents)} documentos carregados")
    
    # Index in batches
    print(f"\n🔍 Indexando documentos...")
    batch_size = 100
    total_indexed = 0
    
    try:
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            
            batch_data = [
                {
                    'id': str(doc.get('id', f'doc_{i}')),
                    'type': doc.get('type', 'document'),
                    'url': doc.get('url', '')[:2000],
                    'title': doc.get('title', '')[:500],
                    'content': doc.get('content', '')[:10000],
                    'module': doc.get('module', '')[:200],
                    'breadcrumb': doc.get('breadcrumb', '')[:500],
                    'source': doc.get('source', '')[:100]
                }
                for doc in batch
            ]
            
            task = index.add_documents(batch_data)
            total_indexed += len(batch_data)
            
            if (total_indexed % 500 == 0) or (total_indexed >= len(documents)):
                print(f"   📤 {total_indexed}/{len(documents)} enviados...")
        
        print(f"\n✅ {total_indexed} documentos enviados para indexação")
        
        # Aguarda conclusão
        print(f"\n⏳ Aguardando indexação ser processada...")
        time.sleep(5)
        
        stats = index.get_stats()
        print(f"\n📊 Status da indexação:")
        print(f"   Documentos indexados: {stats.number_of_documents}")
        print(f"   Está indexando: {stats.is_indexing}")
        
        print(f"\n{'='*80}")
        print(f"✅ INDEXAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"{'='*80}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante indexação: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
