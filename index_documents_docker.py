"""
Script para indexar documentos no Meilisearch

Processa os arquivos JSONL e JSONL nos dados e adiciona ao índice
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
import requests
from typing import List, Dict, Any


async def index_documents():
    """Indexa documentos no Meilisearch"""
    
    meilisearch_url = "http://localhost:7700"
    meilisearch_key = "meilisearch_master_key_change_me"
    headers = {"Authorization": f"Bearer {meilisearch_key}"}
    
    print("\n" + "="*70)
    print("INDEXACAO DE DOCUMENTOS - MEILISEARCH")
    print("="*70)
    
    # Criar índice
    print("\n[1] Criando índice 'documentation'...")
    
    index_data = {
        "uid": "documentation",
        "primaryKey": "id"
    }
    
    try:
        response = requests.post(
            f"{meilisearch_url}/indexes",
            json=index_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print("  [OK] Indice criado ou já existe")
        else:
            print(f"  [INFO] Status: {response.status_code}")
    
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return
    
    # Carregar documentos do JSONL
    print("\n[2] Carregando documentos...")
    
    documents = []
    
    # Tentar diferentes caminhos
    jsonl_files = [
        "docs_indexacao_detailed.jsonl",
        "docs_indexacao.jsonl",
    ]
    
    for jsonl_file in jsonl_files:
        path = Path(jsonl_file)
        
        if path.exists():
            print(f"  Processando {jsonl_file}...")
            
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        doc = json.loads(line)
                        documents.append(doc)
                    except:
                        pass
    
    if not documents:
        print("  [WARNING] Nenhum documento encontrado nos arquivos JSONL")
        
        # Criar documentos de exemplo para teste
        print("  Criando documentos de exemplo para teste...")
        documents = [
            {
                "id": "doc-001",
                "title": "Guia de Instalacao",
                "content": "Este e um guia completo de instalacao do sistema Senior",
                "module": "general",
                "type": "guide"
            },
            {
                "id": "doc-002",
                "title": "API Reference",
                "content": "Documentacao completa da API REST",
                "module": "api",
                "type": "reference"
            },
            {
                "id": "doc-003",
                "title": "Release Notes",
                "content": "Notas de lancamento da versao 6.10.4",
                "module": "releases",
                "type": "release"
            }
        ]
    
    print(f"  Total de documentos: {len(documents)}")
    
    # Adicionar documentos
    print("\n[3] Adicionando documentos ao Meilisearch...")
    
    try:
        response = requests.post(
            f"{meilisearch_url}/indexes/documentation/documents",
            json=documents,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 202]:
            data = response.json()
            print(f"  [OK] Documentos adicionados")
            print(f"    Task ID: {data.get('taskId', 'N/A')}")
            print(f"    Status: {data.get('status', 'pending')}")
        else:
            print(f"  [ERROR] Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return
    
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return
    
    # Aguardar indexacao
    print("\n[4] Aguardando conclusao da indexacao...")
    
    for i in range(10):
        try:
            response = requests.get(
                f"{meilisearch_url}/indexes/documentation",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                doc_count = data.get("numberOfDocuments", 0)
                
                print(f"  Documentos indexados: {doc_count}")
                
                if doc_count > 0:
                    print("  [OK] Indexacao completa!")
                    break
        
        except:
            pass
        
        await asyncio.sleep(1)
    
    # Verificar resultado
    print("\n[5] Verificando resultado...")
    
    try:
        response = requests.get(
            f"{meilisearch_url}/indexes/documentation",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"  Indice: {data.get('uid', 'N/A')}")
            print(f"  Documentos: {data.get('numberOfDocuments', 0)}")
            print(f"  Campos: {list(data.get('fieldsDistribution', {}).keys())}")
            
            # Teste de busca
            print("\n[6] Teste de busca...")
            
            search_query = {"q": "documentation"}
            response = requests.post(
                f"{meilisearch_url}/indexes/documentation/search",
                json=search_query,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                search_data = response.json()
                hits = search_data.get("hits", [])
                
                print(f"  Query: 'documentation'")
                print(f"  Resultados: {len(hits)}")
                
                if hits:
                    print(f"  Primeiro resultado: {hits[0].get('title', 'N/A')}")
    
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    print("\n" + "="*70)
    print("INDEXACAO CONCLUIDA")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(index_documents())
