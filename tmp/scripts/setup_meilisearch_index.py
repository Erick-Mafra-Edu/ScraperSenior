#!/usr/bin/env python3
"""
Setup Meilisearch Index
Configura o índice 'documentation' com atributos filtráveis e outras configurações
"""

import meilisearch
import time
import sys

MEILISEARCH_URL = "http://localhost:7700"
MEILISEARCH_KEY = "meilisearch_master_key_change_me"

def setup_index():
    """Configura o índice com atributos filtráveis"""
    
    print("="*80)
    print("⚙️  SETUP MEILISEARCH INDEX")
    print("="*80)
    
    # Conecta
    print(f"\n📡 Conectando a {MEILISEARCH_URL}...")
    try:
        client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_KEY)
        health = client.health()
        print(f"   ✅ Conectado")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        sys.exit(1)
    
    # Obtém ou cria índice
    print(f"\n📑 Obtendo índice 'documentation'...")
    try:
        index = client.get_index("documentation")
        print(f"   ✅ Índice existe")
    except:
        print(f"   🆕 Criando índice...")
        task = client.create_index("documentation", {"primaryKey": "id"})
        time.sleep(2)
        index = client.get_index("documentation")
        print(f"   ✅ Índice criado")
    
    # Configura atributos filtráveis
    print(f"\n🔧 Configurando atributos filtráveis...")
    try:
        settings = {
            "filterableAttributes": ["source", "module", "type"],
            "searchableAttributes": ["title", "content", "module", "breadcrumb"],
            "sortableAttributes": ["title"],
            "distinctAttribute": None
        }
        
        task = index.update_settings(settings)
        print(f"   ✅ Configurações aplicadas (Task: {task.task_uid if hasattr(task, 'task_uid') else 'pending'})")
        
        # Aguarda processamento
        time.sleep(3)
        
        # Verifica configuração
        current_settings = index.get_settings()
        print(f"   ✅ Atributos filtráveis: {current_settings.get('filterableAttributes', [])}")
        print(f"   ✅ Atributos pesquisáveis: {current_settings.get('searchableAttributes', [])}")
        
    except Exception as e:
        print(f"   ❌ Erro ao configurar: {e}")
        return False
    
    # Verifica estatísticas
    print(f"\n📊 Estatísticas do índice:")
    try:
        stats = index.get_stats()
        print(f"   Documentos: {stats.number_of_documents}")
        print(f"   Indexando: {stats.is_indexing}")
        print(f"   Campos: {list(stats.field_distribution.keys()) if hasattr(stats, 'field_distribution') else 'N/A'}")
    except Exception as e:
        print(f"   ⚠️  Não foi possível obter estatísticas: {e}")
    
    print(f"\n✅ Setup concluído!\n")
    return True


if __name__ == "__main__":
    setup_index()
