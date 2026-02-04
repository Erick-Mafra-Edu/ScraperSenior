#!/usr/bin/env python3
"""
MCP Server Entrypoint with Auto-Indexing
==========================================
Iniciates MCP Server with automatic document indexing on startup
- Aguarda Meilisearch
- Indexa 855 documentos automaticamente
- Inicia MCP Server para servir dados
"""

import sys
import time
import json
import asyncio
import requests
from pathlib import Path
from datetime import datetime


def wait_for_meilisearch(max_retries=60, timeout=5):
    """Aguarda Meilisearch ficar disponível"""
    url = "http://meilisearch:7700/health"
    print(f"\n[*] Aguardando Meilisearch ({url})...")
    
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                print(f"[OK] Meilisearch disponível!")
                return True
        except:
            pass
        
        wait_time = min(2 ** attempt, 30)
        print(f"    Tentativa {attempt+1}/{max_retries}... (aguardando {wait_time}s)")
        time.sleep(wait_time)
    
    print(f"[ERROR] Timeout: Meilisearch não respondeu")
    return False


def load_documents():
    """Carrega documentos do arquivo JSONL"""
    documents = []
    
    # Procura pelos arquivos JSONL
    jsonl_files = [
        Path("/app/docs_indexacao_detailed.jsonl"),
        Path("/app/docs_indexacao.jsonl"),
        Path("./docs_indexacao_detailed.jsonl"),
        Path("./docs_indexacao.jsonl"),
    ]
    
    for jsonl_file in jsonl_files:
        if jsonl_file.exists():
            print(f"\n[*] Carregando documentos de {jsonl_file.name}...")
            
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        try:
                            doc = json.loads(line)
                            documents.append(doc)
                        except json.JSONDecodeError as e:
                            if line_num <= 3:
                                print(f"    [WARNING] Erro na linha {line_num}: {e}")
                
                print(f"    [OK] {len(documents)} documentos carregados de {jsonl_file.name}")
                break
            
            except Exception as e:
                print(f"    [ERROR] Erro ao ler {jsonl_file}: {e}")
    
    if not documents:
        print(f"\n[WARNING] Nenhum documento encontrado, criando dados de exemplo...")
        documents = [
            {
                "id": "doc-001",
                "title": "Guia de Instalacao",
                "content": "Este e um guia completo de instalacao do sistema Senior",
                "module": "general",
                "type": "guide",
                "url": "https://docs.senior.com.br/install"
            },
            {
                "id": "doc-002",
                "title": "API Reference",
                "content": "Documentacao completa da API REST para integracao",
                "module": "api",
                "type": "reference",
                "url": "https://docs.senior.com.br/api"
            },
            {
                "id": "doc-003",
                "title": "Release Notes",
                "content": "Notas de lancamento da versao 6.10.4 com melhorias e bugfixes",
                "module": "releases",
                "type": "release",
                "url": "https://docs.senior.com.br/releases"
            }
        ]
        print(f"    [OK] {len(documents)} documentos de exemplo criados")
    
    return documents


def index_documents(documents):
    """Indexa documentos no Meilisearch com batching"""
    
    meilisearch_url = "http://meilisearch:7700"
    meilisearch_key = "5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"
    headers = {"Authorization": f"Bearer {meilisearch_key}"}
    
    print(f"\n{'='*70}")
    print("INDEXACAO DE DOCUMENTOS - MEILISEARCH")
    print(f"{'='*70}")
    
    # Remover índice antigo
    print(f"\n[0] Removendo índice antigo (se existir)...")
    try:
        response = requests.delete(
            f"{meilisearch_url}/indexes/documentation",
            headers=headers,
            timeout=10
        )
        if response.status_code in [200, 202, 404]:
            print(f"    [OK] Índice antigo removido ou não existia")
            time.sleep(1)
    except:
        pass
    
    # Criar novo índice
    print(f"\n[1] Criando indice 'documentation'...")
    
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
        
        if response.status_code in [200, 201, 202]:
            print(f"    [OK] Indice criado")
        else:
            print(f"    [WARNING] Status: {response.status_code}")
        
        time.sleep(1)
    
    except Exception as e:
        print(f"    [ERROR] Erro ao criar indice: {e}")
        return False
    
    # Adicionar documentos em batches
    print(f"\n[2] Adicionando {len(documents)} documentos em lotes...")
    
    batch_size = 100
    total_sent = 0
    
    try:
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            
            response = requests.post(
                f"{meilisearch_url}/indexes/documentation/documents",
                json=batch,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 202]:
                total_sent += len(batch)
                batch_num = (i // batch_size) + 1
                print(f"    Lote {batch_num}: {len(batch)} docs -> OK")
            else:
                print(f"    [ERROR] Lote {i//batch_size + 1}: Status {response.status_code}")
                return False
        
        print(f"    [OK] Total enviado: {total_sent} documentos")
    
    except Exception as e:
        print(f"    [ERROR] Erro ao adicionar documentos: {e}")
        return False
    
    # Aguardar indexação com busca para validar
    print(f"\n[3] Aguardando conclusao da indexacao...")
    
    max_attempts = 60
    for attempt in range(max_attempts):
        try:
            # Tentar busca vazia para ver se há documentos
            response = requests.post(
                f"{meilisearch_url}/indexes/documentation/search",
                json={"q": "", "limit": 1},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                doc_count = len(data.get("hits", []))
                
                if doc_count > 0:
                    print(f"    [OK] Documentos indexados com sucesso!")
                    return True
                
                if attempt % 10 == 0:
                    print(f"    Tentativa {attempt+1}/{max_attempts}...")
        
        except:
            pass
        
        time.sleep(1)
    
    print(f"    [WARNING] Timeout na indexacao (mas continuando...)")
    return True


def verify_index():
    """Verifica o status do índice"""
    
    meilisearch_url = "http://meilisearch:7700"
    meilisearch_key = "5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"
    headers = {"Authorization": f"Bearer {meilisearch_key}"}
    
    print(f"\n[4] Verificando estado do indice...")
    
    try:
        response = requests.get(
            f"{meilisearch_url}/indexes/documentation",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n    Indice: {data.get('uid', 'N/A')}")
            print(f"    Documentos: {data.get('numberOfDocuments', 0)}")
            
            fields = data.get('fieldsDistribution', {})
            if fields:
                print(f"    Campos: {', '.join(list(fields.keys())[:5])}...")
            
            # Teste de busca
            print(f"\n[5] Teste de busca...")
            
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
                
                print(f"    Query: 'documentation'")
                print(f"    Resultados: {len(hits)}")
                
                if hits:
                    print(f"    Primeiro resultado: {hits[0].get('title', 'N/A')}")
            
            print(f"\n{'='*70}")
            print("INDEXACAO CONCLUIDA COM SUCESSO")
            print(f"{'='*70}\n")
            
            return True
    
    except Exception as e:
        print(f"    [ERROR] {str(e)}")
    
    return False


def start_mcp_server():
    """Inicia o servidor MCP"""
    
    print(f"\n{'='*70}")
    print("INICIANDO MCP SERVER")
    print(f"{'='*70}\n")
    
    try:
        # Importa e executa o servidor MCP
        import subprocess
        
        result = subprocess.run(
            [sys.executable, "-u", "src/mcp_server_docker.py"],
            cwd="/app"
        )
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"[ERROR] Erro ao iniciar MCP Server: {e}")
        return False


def main():
    """Função principal do entrypoint"""
    
    print(f"\n{'='*70}")
    print("MCP SERVER ENTRYPOINT COM AUTO-INDEXING")
    print(f"{'='*70}")
    
    # 1. Aguarda Meilisearch
    if not wait_for_meilisearch():
        print(f"\n[ERROR] Nao conseguiu conectar ao Meilisearch")
        sys.exit(1)
    
    # 2. Carrega documentos
    documents = load_documents()
    
    if not documents:
        print(f"\n[ERROR] Nenhum documento disponível")
        sys.exit(1)
    
    # 3. Indexa documentos
    if not index_documents(documents):
        print(f"\n[WARNING] Indexacao teve problemas, continuando mesmo assim...")
    
    # 4. Verifica índice
    verify_index()
    
    # 5. Inicia MCP Server
    print(f"\n[*] Iniciando MCP Server para servir dados...")
    start_mcp_server()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[*] MCP Server finalizado")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Erro não esperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
