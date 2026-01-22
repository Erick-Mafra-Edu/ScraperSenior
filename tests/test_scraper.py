#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite para Scraper de Documentação Senior
Valida: Titles, Content, URLs, Metadata
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_jsonl_structure():
    """Testa se JSONL tem estrutura correta"""
    print("\n" + "="*80)
    print("🧪 TEST: JSONL Structure")
    print("="*80)
    
    required_fields = ['id', 'title', 'url', 'module', 'breadcrumb', 'text_content']
    jsonl_file = Path(__file__).parent.parent / 'docs_indexacao_detailed.jsonl'
    
    if not jsonl_file.exists():
        print(f"❌ FAIL: Arquivo não encontrado: {jsonl_file}")
        return False
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                    
                try:
                    doc = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"❌ FAIL: Documento {i} - JSON inválido: {e}")
                    return False
                
                # Check required fields
                missing = [f for f in required_fields if f not in doc]
                if missing:
                    print(f"❌ FAIL: Documento {i} - Campos ausentes: {missing}")
                    return False
                
                # Validate field types
                if not isinstance(doc.get('id'), str) or not doc['id']:
                    print(f"❌ FAIL: Documento {i} - 'id' deve ser string não vazia")
                    return False
                
                if not isinstance(doc.get('title'), str):
                    print(f"❌ FAIL: Documento {i} - 'title' deve ser string")
                    return False
                
                if not isinstance(doc.get('url'), str) or not doc['url'].startswith('http'):
                    print(f"❌ FAIL: Documento {i} - 'url' deve ser URL válida")
                    return False
                
                if not isinstance(doc.get('module'), str) or not doc['module']:
                    print(f"❌ FAIL: Documento {i} - 'module' deve ser string não vazia")
                    return False
        
        print(f"✅ PASS: {i} documentos validados com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Erro ao validar JSONL: {e}")
        return False


def test_document_titles():
    """Testa se títulos foram capturados corretamente"""
    print("\n" + "="*80)
    print("🧪 TEST: Document Titles")
    print("="*80)
    
    jsonl_file = Path(__file__).parent.parent / 'docs_indexacao_detailed.jsonl'
    
    if not jsonl_file.exists():
        print(f"❌ FAIL: Arquivo não encontrado: {jsonl_file}")
        return False
    
    empty_titles = 0
    sem_titulo = 0
    valid_titles = 0
    server_errors = 0
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                doc = json.loads(line)
                title = doc.get('title', '').strip()
                
                if not title or title == '':
                    empty_titles += 1
                elif title == 'Sem título':
                    sem_titulo += 1
                elif 'Server Error' in title or 'Error' in title:
                    server_errors += 1
                else:
                    valid_titles += 1
        
        total = empty_titles + sem_titulo + valid_titles + server_errors
        success_rate = (valid_titles / total * 100) if total > 0 else 0
        
        print(f"✓ Títulos válidos: {valid_titles}/{total} ({success_rate:.1f}%)")
        print(f"⚠ Sem título: {sem_titulo}")
        print(f"⚠ Vazios: {empty_titles}")
        print(f"⚠ Erros: {server_errors}")
        
        if success_rate >= 90:
            print(f"✅ PASS: Taxa de sucesso >= 90%")
            return True
        else:
            print(f"❌ FAIL: Taxa de sucesso < 90% ({success_rate:.1f}%)")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Erro ao validar títulos: {e}")
        return False


def test_url_validity():
    """Testa se URLs são válidas"""
    print("\n" + "="*80)
    print("🧪 TEST: URL Validity")
    print("="*80)
    
    jsonl_file = Path(__file__).parent.parent / 'docs_indexacao_detailed.jsonl'
    
    if not jsonl_file.exists():
        print(f"❌ FAIL: Arquivo não encontrado: {jsonl_file}")
        return False
    
    invalid_urls = 0
    valid_urls = 0
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                doc = json.loads(line)
                url = doc.get('url', '')
                
                if not url or not url.startswith('http'):
                    invalid_urls += 1
                    print(f"⚠ Documento {i}: URL inválida")
                else:
                    valid_urls += 1
        
        total = valid_urls + invalid_urls
        print(f"✓ URLs válidas: {valid_urls}/{total}")
        
        if invalid_urls == 0:
            print(f"✅ PASS: Todas as URLs são válidas")
            return True
        else:
            print(f"❌ FAIL: {invalid_urls} URLs inválidas")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Erro ao validar URLs: {e}")
        return False


def test_module_consistency():
    """Testa se módulos são consistentes"""
    print("\n" + "="*80)
    print("🧪 TEST: Module Consistency")
    print("="*80)
    
    jsonl_file = Path(__file__).parent.parent / 'docs_indexacao_detailed.jsonl'
    
    if not jsonl_file.exists():
        print(f"❌ FAIL: Arquivo não encontrado: {jsonl_file}")
        return False
    
    modules = {}
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                doc = json.loads(line)
                module = doc.get('module', 'UNKNOWN')
                
                if module not in modules:
                    modules[module] = 0
                modules[module] += 1
        
        print("Módulos encontrados:")
        for module, count in sorted(modules.items()):
            print(f"  • {module}: {count} documentos")
        
        if len(modules) > 0:
            print(f"✅ PASS: {len(modules)} módulo(s) encontrado(s)")
            return True
        else:
            print(f"❌ FAIL: Nenhum módulo encontrado")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Erro ao validar módulos: {e}")
        return False


def test_breadcrumb_structure():
    """Testa se breadcrumbs estão bem estruturados"""
    print("\n" + "="*80)
    print("🧪 TEST: Breadcrumb Structure")
    print("="*80)
    
    jsonl_file = Path(__file__).parent.parent / 'docs_indexacao_detailed.jsonl'
    
    if not jsonl_file.exists():
        print(f"❌ FAIL: Arquivo não encontrado: {jsonl_file}")
        return False
    
    invalid_breadcrumbs = 0
    valid_breadcrumbs = 0
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                doc = json.loads(line)
                breadcrumb = doc.get('breadcrumb', [])
                
                if not isinstance(breadcrumb, list):
                    invalid_breadcrumbs += 1
                    print(f"⚠ Documento {i}: breadcrumb não é lista")
                elif len(breadcrumb) == 0:
                    invalid_breadcrumbs += 1
                else:
                    valid_breadcrumbs += 1
        
        total = valid_breadcrumbs + invalid_breadcrumbs
        print(f"✓ Breadcrumbs válidos: {valid_breadcrumbs}/{total}")
        
        if invalid_breadcrumbs == 0:
            print(f"✅ PASS: Todos os breadcrumbs são válidos")
            return True
        else:
            print(f"⚠️ WARNING: {invalid_breadcrumbs} breadcrumbs inválidos")
            return True  # Não é crítico
            
    except Exception as e:
        print(f"❌ FAIL: Erro ao validar breadcrumbs: {e}")
        return False


def test_encoding():
    """Testa se encoding UTF-8 está correto"""
    print("\n" + "="*80)
    print("🧪 TEST: UTF-8 Encoding")
    print("="*80)
    
    jsonl_file = Path(__file__).parent.parent / 'docs_indexacao_detailed.jsonl'
    
    if not jsonl_file.exists():
        print(f"❌ FAIL: Arquivo não encontrado: {jsonl_file}")
        return False
    
    encoding_errors = 0
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    doc = json.loads(line)
                    # Tentar acessar strings com acentos
                    _ = doc.get('title', '')
                    _ = doc.get('breadcrumb', [])
                except UnicodeDecodeError:
                    encoding_errors += 1
                    print(f"⚠ Documento {i}: Erro de encoding")
        
        if encoding_errors == 0:
            print(f"✅ PASS: Encoding UTF-8 correto em todos os documentos")
            return True
        else:
            print(f"❌ FAIL: {encoding_errors} documentos com erro de encoding")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Erro ao validar encoding: {e}")
        return False


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "="*80)
    print("🚀 INICIANDO SUITE DE TESTES - SCRAPER DE DOCUMENTAÇÃO")
    print("="*80)
    
    tests = [
        ("JSONL Structure", test_jsonl_structure),
        ("Document Titles", test_document_titles),
        ("URL Validity", test_url_validity),
        ("Module Consistency", test_module_consistency),
        ("Breadcrumb Structure", test_breadcrumb_structure),
        ("UTF-8 Encoding", test_encoding),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ ERRO ao executar {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*80)
    print(f"Total: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    print("="*80 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
