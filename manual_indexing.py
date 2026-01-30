#!/usr/bin/env python3
"""
Manual Indexing Script
Indexes already-scraped documents into Meilisearch
"""

import json
import meilisearch
from pathlib import Path

# Configuration
MEILISEARCH_URL = "http://localhost:7700"
MEILISEARCH_KEY = "meilisearch_master_key_change_me"
JSONL_FILE = Path("docs_unified/unified_documentation.jsonl")

def main():
    print("=" * 80)
    print("MANUAL INDEXING - UNIFIED DOCUMENTS")
    print("=" * 80)
    
    # Connect to Meilisearch
    print(f"\n📡 Conectando ao Meilisearch ({MEILISEARCH_URL})...")
    try:
        client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_KEY)
        health = client.health()
        print(f"   ✅ Conectado com sucesso")
    except Exception as e:
        print(f"   ❌ Erro ao conectar: {e}")
        return False
    
    # Get or create index
    print(f"\n📑 Obtendo índice 'documentation'...")
    try:
        index = client.get_index("documentation")
        print(f"   ✅ Índice obtido")
    except:
        print(f"   🆕 Criando novo índice...")
        index = client.create_index("documentation", {"primaryKey": "id"})
        print(f"   ✅ Índice criado")
    
    # Load documents from JSONL
    print(f"\n📂 Carregando documentos de {JSONL_FILE}...")
    if not JSONL_FILE.exists():
        print(f"   ❌ Arquivo não encontrado: {JSONL_FILE}")
        return False
    
    documents = []
    with open(JSONL_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                doc = json.loads(line)
                documents.append(doc)
    
    print(f"   ✅ {len(documents)} documentos carregados")
    
    # Index documents in batches
    print(f"\n🔍 Indexando documentos no Meilisearch...")
    batch_size = 100
    indexed = 0
    
    try:
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            
            # Clean up batch data
            batch_data = [
                {
                    'id': doc['id'],
                    'type': doc.get('type', 'document'),
                    'url': doc.get('url', ''),
                    'title': doc.get('title', ''),
                    'content': doc.get('content', '')[:10000],  # Limita conteúdo
                    'module': doc.get('module', ''),
                    'breadcrumb': doc.get('breadcrumb', ''),
                    'source': doc.get('source', '')
                }
                for doc in batch
            ]
            
            task = index.add_documents(batch_data)
            indexed += len(batch_data)
            
            if (i + batch_size) % 500 == 0 or (i + batch_size) >= len(documents):
                task_uid = task.task_uid if hasattr(task, 'task_uid') else str(task)
                print(f"   📤 {indexed}/{len(documents)} documentos enviados... Task ID: {task_uid}")
        
        print(f"   ✅ Todos os {len(documents)} documentos foram enviados para indexação")
        
    except Exception as e:
        print(f"   ❌ Erro ao indexar: {e}")
        return False
    
    # Check index status
    print(f"\n📊 Status da indexação:")
    try:
        stats = index.get_stats()
        print(f"   Documentos no índice: {stats['numberOfDocuments']}")
        print(f"   Está indexando: {stats['isIndexing']}")
        if stats.get('fieldDistribution'):
            print(f"   Campos: {list(stats['fieldDistribution'].keys())}")
    except Exception as e:
        print(f"   ⚠️  Não foi possível obter estatísticas: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Indexação iniciada com sucesso!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
