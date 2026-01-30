#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Indexar documentos no Meilisearch
Carrega docs_para_mcp.jsonl e indexa no Meilisearch rodando em Docker
"""

import json
import time
import requests
from pathlib import Path


def index_documents():
    """Indexa documentos no Meilisearch"""
    
    print("\n" + "="*80)
    print("📊 INDEXAÇÃO NO MEILISEARCH")
    print("="*80 + "\n")
    
    # URL do Meilisearch
    meilisearch_url = "http://localhost:7700"
    master_key = "meilisearch_master_key_change_me"
    
    # Verificar conexão
    print("1️⃣  Verificando conexão com Meilisearch\n")
    
    try:
        response = requests.get(f"{meilisearch_url}/health")
        if response.status_code == 200:
            print(f"   ✓ Meilisearch está ONLINE\n")
        else:
            print(f"   ✗ Meilisearch retornou status {response.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Erro ao conectar: {e}")
        print(f"   Verifique se docker-compose está rodando\n")
        return
    
    # Carregar documentos
    print("2️⃣  Carregando documentos scrapados\n")
    
    docs_file = Path("docs_para_mcp.jsonl")
    if not docs_file.exists():
        print(f"   ✗ Arquivo não encontrado: {docs_file}")
        print(f"   Execute primeiro: python test_mcp_titles.py\n")
        return
    
    docs = []
    with open(docs_file) as f:
        for idx, line in enumerate(f, 1):
            if line.strip():
                doc = json.loads(line)
                # Adicionar ID válido (apenas alphanuméricos, - e _)
                doc['id'] = f"doc_{idx}"
                docs.append(doc)
    
    print(f"   ✓ {len(docs)} documentos carregados\n")
    
    # Criar índice
    print("3️⃣  Criando/Verificando índice 'senior_docs'\n")
    
    index_name = "senior_docs"
    headers = {"Authorization": f"Bearer {master_key}"}
    
    # Criar índice se não existir
    try:
        response = requests.post(
            f"{meilisearch_url}/indexes",
            json={"uid": index_name, "primaryKey": "id"},
            headers=headers
        )
        if response.status_code in [201, 202, 409]:  # 201/202=criado, 409=já existe
            print(f"   ✓ Índice '{index_name}' está pronto\n")
        else:
            print(f"   ✗ Erro: {response.status_code}")
            print(f"   {response.text}\n")
            return
    except Exception as e:
        print(f"   ✗ Erro: {e}\n")
        return
    
    # Indexar documentos
    print("4️⃣  Adicionando documentos ao índice\n")
    
    try:
        response = requests.post(
            f"{meilisearch_url}/indexes/{index_name}/documents",
            json=docs,
            headers=headers
        )
        
        if response.status_code == 202:
            task_info = response.json()
            task_id = task_info.get("taskUid")
            print(f"   ✓ Tarefa iniciada (ID: {task_id})")
            print(f"   ✓ Indexando {len(docs)} documentos...")
            
            # Aguardar conclusão
            print(f"\n5️⃣  Aguardando conclusão da indexação\n")
            
            for attempt in range(30):
                time.sleep(1)
                task_response = requests.get(
                    f"{meilisearch_url}/tasks/{task_id}",
                    headers=headers
                )
                
                if task_response.status_code == 200:
                    task_data = task_response.json()
                    status = task_data.get("status")
                    
                    if status == "succeeded":
                        print(f"   ✓ Indexação concluída com SUCESSO!")
                        print(f"   ✓ {len(docs)} documentos indexados\n")
                        
                        # Mostrar estatísticas
                        stats_response = requests.get(
                            f"{meilisearch_url}/indexes/{index_name}/stats",
                            headers=headers
                        )
                        
                        if stats_response.status_code == 200:
                            stats = stats_response.json()
                            print(f"   📊 Estatísticas do índice:")
                            print(f"      • Total de documentos: {stats.get('numberOfDocuments', 0)}")
                            print(f"      • Tamanho: {stats.get('indexedSize', 0)} bytes\n")
                        
                        break
                    elif status == "failed":
                        print(f"   ✗ Indexação FALHOU")
                        print(f"   Erro: {task_data.get('error', 'N/A')}\n")
                        break
                    else:
                        print(f"   ⏳ Status: {status}...", end="\r")
        else:
            print(f"   ✗ Erro ao indexar: {response.status_code}")
            print(f"   {response.text}\n")
    
    except Exception as e:
        print(f"   ✗ Erro: {e}\n")
        return
    
    # Teste de busca
    print("6️⃣  Testando busca\n")
    
    search_queries = [
        "notas de versão",
        "versão",
        "Gestão de Pessoas"
    ]
    
    for query in search_queries:
        try:
            response = requests.get(
                f"{meilisearch_url}/indexes/{index_name}/search",
                params={"q": query},
                headers=headers
            )
            
            if response.status_code == 200:
                results = response.json()
                hits = results.get("hits", [])
                print(f"   🔍 Busca por '{query}': {len(hits)} resultado(s)")
                if hits:
                    print(f"      • {hits[0].get('title', 'N/A')}")
        except:
            pass
    
    print("\n" + "="*80)
    print("✅ INDEXAÇÃO CONCLUÍDA")
    print("="*80 + "\n")
    
    print("📝 Próximas ações:")
    print("   1. Testar MCP: python test_mcp_search.py")
    print("   2. Verificar notas de versão: curl http://localhost:8000/search?q=versao")


if __name__ == "__main__":
    index_documents()
