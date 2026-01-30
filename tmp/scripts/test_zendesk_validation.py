#!/usr/bin/env python3
"""
Teste de Validação - Documentos Zendesk
Verifica se os artigos do Zendesk foram indexados e categorizados corretamente
"""

import meilisearch
import json
from pathlib import Path

def test_zendesk_indexation():
    """Testa a indexação de documentos do Zendesk"""
    
    client = meilisearch.Client('http://localhost:7700', 'meilisearch_master_key_change_me')
    index = client.get_index('documentation')
    
    print("\n" + "="*80)
    print("🧪 TESTE DE VALIDAÇÃO - DOCUMENTOS ZENDESK")
    print("="*80)
    
    # 1. Verificar total de documentos
    print("\n📊 1. ESTATÍSTICAS GERAIS")
    print("-" * 80)
    stats = index.get_stats()
    total_docs = stats.number_of_documents
    print(f"   ✅ Total de documentos no índice: {total_docs}")
    print(f"   ✅ Status: {'Indexando' if stats.is_indexing else 'Completo'}")
    
    # 2. Buscar documentos Zendesk
    print("\n🔍 2. DOCUMENTOS POR FONTE")
    print("-" * 80)
    
    # Busca por documentos com fonte 'zendesk_api'
    try:
        results_zendesk = index.search("", {"filter": "source = 'zendesk_api'", "limit": 1})
        zendesk_count = results_zendesk.get('estimatedTotalHits', 0)
        print(f"   ✅ Documentos Zendesk: {zendesk_count}")
    except Exception as e:
        print(f"   ⚠️  Erro ao filtrar Zendesk: {e}")
        zendesk_count = 0
    
    # Busca por documentos com fonte 'website'
    try:
        results_website = index.search("", {"filter": "source = 'website'", "limit": 1})
        website_count = results_website.get('estimatedTotalHits', 0)
        print(f"   ✅ Documentos Website: {website_count}")
    except Exception as e:
        print(f"   ⚠️  Erro ao filtrar Website: {e}")
        website_count = 0
    
    # 3. Verificar categorização
    print("\n📁 3. CATEGORIZAÇÃO DOS DOCUMENTOS")
    print("-" * 80)
    
    # Busca alguns documentos Zendesk para analisar
    try:
        results = index.search("", {
            "filter": "source = 'zendesk_api'",
            "limit": 10
        })
        
        if results.get('hits'):
            print(f"\n   Analisando {len(results['hits'])} documentos Zendesk...")
            
            modules = set()
            sources = set()
            types = set()
            
            for i, doc in enumerate(results['hits'], 1):
                modules.add(doc.get('module', 'N/A'))
                sources.add(doc.get('source', 'N/A'))
                types.add(doc.get('type', 'N/A'))
                
                if i <= 3:
                    print(f"\n   Documento {i}:")
                    print(f"      ID: {doc.get('id', 'N/A')}")
                    print(f"      Título: {doc.get('title', 'N/A')[:70]}...")
                    print(f"      Módulo: {doc.get('module', 'N/A')}")
                    print(f"      Breadcrumb: {doc.get('breadcrumb', 'N/A')[:60]}...")
                    print(f"      Source: {doc.get('source', 'N/A')}")
            
            print(f"\n   📋 Módulos encontrados: {modules}")
            print(f"   🏷️  Tipos encontrados: {types}")
            print(f"   🔗 Fontes encontradas: {sources}")
        else:
            print("   ⚠️  Nenhum documento Zendesk encontrado para análise")
    except Exception as e:
        print(f"   ❌ Erro ao buscar documentos: {e}")
    
    # 4. Testes de busca por conteúdo
    print("\n🔎 4. TESTES DE BUSCA POR CONTEÚDO")
    print("-" * 80)
    
    test_queries = [
        ("Help Center", "termo geral"),
        ("ERP", "produto específico"),
        ("Zendesk", "menção da plataforma"),
        ("API", "termo técnico"),
        ("Impostos", "tema específico"),
    ]
    
    for query, description in test_queries:
        try:
            results = index.search(query, {"limit": 5})
            total_hits = results.get('estimatedTotalHits', 0)
            
            # Conta quantos são do Zendesk
            zendesk_results = [hit for hit in results.get('hits', []) if hit.get('source') == 'zendesk_api']
            
            print(f"\n   📌 Busca: '{query}' ({description})")
            print(f"      Total encontrado: {total_hits}")
            print(f"      Do Zendesk: {len(zendesk_results)}/{len(results.get('hits', []))}")
            
            if zendesk_results:
                print(f"      Exemplos Zendesk:")
                for hit in zendesk_results[:2]:
                    print(f"        • {hit.get('title', 'N/A')[:60]}...")
        except Exception as e:
            print(f"   ⚠️  Erro na busca '{query}': {e}")
    
    # 5. Verificar estrutura de um documento
    print("\n📋 5. ESTRUTURA DE DOCUMENTOS ZENDESK")
    print("-" * 80)
    
    try:
        results = index.search("", {
            "filter": "source = 'zendesk_api'",
            "limit": 1
        })
        
        if results.get('hits'):
            doc = results['hits'][0]
            print(f"\n   Campos presentes em um documento Zendesk:")
            for key in sorted(doc.keys()):
                value = doc[key]
                if isinstance(value, str):
                    value_preview = value[:50] + "..." if len(value) > 50 else value
                    print(f"      ✅ {key}: {value_preview}")
                else:
                    print(f"      ✅ {key}: {value}")
    except Exception as e:
        print(f"   ❌ Erro ao analisar estrutura: {e}")
    
    # 6. Teste de arquivo JSONL
    print("\n📄 6. VALIDAÇÃO DO ARQUIVO JSONL")
    print("-" * 80)
    
    jsonl_file = Path("docs_unified/unified_documentation.jsonl")
    if jsonl_file.exists():
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        print(f"   ✅ Arquivo encontrado: {jsonl_file}")
        print(f"   ✅ Total de linhas: {len(lines)}")
        
        # Analisa primeiros documentos
        zendesk_count_jsonl = 0
        website_count_jsonl = 0
        
        for line in lines:
            try:
                doc = json.loads(line)
                if doc.get('source') == 'zendesk_api':
                    zendesk_count_jsonl += 1
                elif doc.get('source') == 'website':
                    website_count_jsonl += 1
            except:
                pass
        
        print(f"   ✅ Documentos Zendesk no JSONL: {zendesk_count_jsonl}")
        print(f"   ✅ Documentos Website no JSONL: {website_count_jsonl}")
        print(f"   ✅ Total: {zendesk_count_jsonl + website_count_jsonl}")
    else:
        print(f"   ❌ Arquivo não encontrado: {jsonl_file}")
    
    # 7. Resumo Final
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    
    print(f"\n✅ ÍNDICE MEILISEARCH:")
    print(f"   • Total de documentos: {total_docs}")
    print(f"   • Documentos Zendesk: {zendesk_count}")
    print(f"   • Documentos Website: {website_count}")
    print(f"   • Proporção: {(zendesk_count/total_docs*100):.1f}% Zendesk, {(website_count/total_docs*100):.1f}% Website")
    
    print(f"\n✅ ARQUIVO JSONL:")
    print(f"   • Total de documentos: {zendesk_count_jsonl + website_count_jsonl}")
    print(f"   • Documentos Zendesk: {zendesk_count_jsonl}")
    print(f"   • Documentos Website: {website_count_jsonl}")
    
    # Validação final
    print(f"\n{'='*80}")
    if zendesk_count > 0 and website_count > 0:
        print("✅ TESTE PASSOU - Ambas as fontes estão indexadas corretamente!")
    elif zendesk_count > 0:
        print("⚠️  AVISO - Apenas Zendesk está indexado")
    elif website_count > 0:
        print("⚠️  AVISO - Apenas Website está indexado")
    else:
        print("❌ TESTE FALHOU - Nenhum documento foi indexado!")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    test_zendesk_indexation()
