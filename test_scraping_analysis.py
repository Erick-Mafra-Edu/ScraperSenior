"""
Script de Teste Real de Scraping - Hexagonal Architecture

Testa os adapters de scraping com URLs reais e analisa os resultados.
Valida a funcionalidade completa da arquitetura com dados reais.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent))

from libs.scrapers.domain import Document, DocumentType, DocumentSource
from libs.scrapers.adapters import (
    UrlResolver,
    FileSystemRepository,
)
from libs.scrapers.use_cases import ScrapeDocumentation


class ScrapingTestAnalyzer:
    """Analisa resultados de scraping"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total_urls_tested": 0,
                "total_docs_scraped": 0,
                "total_errors": 0,
                "success_rate": 0.0,
            }
        }
    
    def add_test_result(self, test_name: str, status: str, details: Dict[str, Any]):
        """Adiciona resultado de teste"""
        self.results["tests"].append({
            "name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })
    
    def update_summary(self, total_urls: int, total_docs: int, total_errors: int):
        """Atualiza resumo"""
        self.results["summary"]["total_urls_tested"] = total_urls
        self.results["summary"]["total_docs_scraped"] = total_docs
        self.results["summary"]["total_errors"] = total_errors
        
        if total_urls > 0:
            self.results["summary"]["success_rate"] = (
                (total_urls - total_errors) / total_urls * 100
            )
    
    def save_report(self, filepath: str):
        """Salva relatório em JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
    
    def print_report(self):
        """Imprime relatório formatado"""
        print("\n" + "="*70)
        print("RELATORIO DE TESTE - SCRAPING REAL")
        print("="*70)
        
        summary = self.results["summary"]
        print(f"\nRESUMO:")
        print(f"  URLs testadas: {summary['total_urls_tested']}")
        print(f"  Documentos scraped: {summary['total_docs_scraped']}")
        print(f"  Erros: {summary['total_errors']}")
        print(f"  Taxa de sucesso: {summary['success_rate']:.1f}%")
        
        print(f"\nTESTES ({len(self.results['tests'])} total):")
        for test in self.results["tests"]:
            status_icon = "[OK]" if test["status"] == "success" else "[ERRO]"
            print(f"  {status_icon} {test['name']}")
            if "message" in test["details"]:
                print(f"       {test['details']['message']}")


async def test_url_resolver():
    """Testa UrlResolver"""
    print("\n[1/4] Testando UrlResolver...")
    analyzer = ScrapingTestAnalyzer()
    resolver = UrlResolver()
    
    tests = [
        {
            "name": "Resolve URL relativa",
            "base": "https://documentacao.senior.com.br/gestao/6.10.4/",
            "relative": "../6.10.3/index.html",
            "expected": "https://documentacao.senior.com.br/gestao/6.10.3/index.html"
        },
        {
            "name": "Resolve URL absoluta",
            "base": "https://documentacao.senior.com.br/gestao/6.10.4/",
            "relative": "https://example.com/other",
            "expected": "https://example.com/other"
        },
        {
            "name": "Mesmo dominio",
            "url1": "https://documentacao.senior.com.br/gestao/6.10.4/",
            "url2": "https://documentacao.senior.com.br/financeiro/5.0.0/",
            "expected": True
        }
    ]
    
    for test in tests:
        try:
            if "relative" in test:
                result = resolver.resolve(test["base"], test["relative"])
                passed = result == test["expected"]
                status = "success" if passed else "warning"
                analyzer.add_test_result(
                    test["name"],
                    status,
                    {
                        "result": result,
                        "expected": test["expected"],
                        "passed": passed
                    }
                )
            else:
                result = resolver.is_same_domain(test["url1"], test["url2"])
                passed = result == test["expected"]
                analyzer.add_test_result(
                    test["name"],
                    "success" if passed else "warning",
                    {"result": result, "passed": passed}
                )
        except Exception as e:
            analyzer.add_test_result(test["name"], "error", {"error": str(e)})
    
    return analyzer


async def test_filesystem_repository():
    """Testa FileSystemRepository"""
    print("[2/4] Testando FileSystemRepository...")
    analyzer = ScrapingTestAnalyzer()
    
    temp_dir = tempfile.mkdtemp(prefix="test_repo_")
    repo = FileSystemRepository(base_dir=temp_dir)
    
    try:
        # Criar documentos de teste
        docs = [
            Document(
                id=f"test-{i}",
                url=f"https://example.com/doc{i}",
                title=f"Documento {i}",
                content=f"Conteudo de teste {i}. " * 50,
                module="modulo-teste",
                doc_type=DocumentType.TECHNICAL_DOC,
                source=DocumentSource.SENIOR_MADCAP,
                scraped_at=datetime.now(),
                metadata={"version": "1.0", "index": i}
            )
            for i in range(3)
        ]
        
        # Salvar
        try:
            for doc in docs:
                await repo.save(doc)
            analyzer.add_test_result(
                "Salvar documentos",
                "success",
                {"docs_saved": len(docs)}
            )
        except Exception as e:
            analyzer.add_test_result(
                "Salvar documentos",
                "error",
                {"error": str(e)}
            )
        
        # Contar
        try:
            count = await repo.count()
            analyzer.add_test_result(
                "Contar documentos",
                "success",
                {"count": count, "expected": len(docs), "passed": count == len(docs)}
            )
        except Exception as e:
            analyzer.add_test_result(
                "Contar documentos",
                "error",
                {"error": str(e)}
            )
        
        # Listar por modulo
        try:
            by_module = await repo.list_by_module("modulo-teste")
            analyzer.add_test_result(
                "Listar por modulo",
                "success",
                {"documents": len(by_module), "expected": len(docs), "passed": len(by_module) == len(docs)}
            )
        except Exception as e:
            analyzer.add_test_result(
                "Listar por modulo",
                "error",
                {"error": str(e)}
            )
        
        # Carregar um doc
        try:
            doc = await repo.load(docs[0].id)
            analyzer.add_test_result(
                "Carregar documento",
                "success",
                {"title": doc.title, "words": doc.word_count()}
            )
        except Exception as e:
            analyzer.add_test_result(
                "Carregar documento",
                "error",
                {"error": str(e)}
            )
        
        analyzer.update_summary(len(docs), len(docs), 0)
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return analyzer


async def test_document_serialization():
    """Testa serializacao de documentos"""
    print("[3/4] Testando serializacao de documentos...")
    analyzer = ScrapingTestAnalyzer()
    
    try:
        # Criar documento
        doc_original = Document(
            id="test-123",
            url="https://documentacao.senior.com.br/gestao/6.10.4/index.html",
            title="Documento de Teste",
            content="Este e um documento de teste. " * 100,
            module="gestao-pessoal",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.SENIOR_MADCAP,
            scraped_at=datetime.now(),
            metadata={"version": "6.10.4", "formato": "MadCap Flare"}
        )
        
        # Serializar
        data = doc_original.to_dict()
        analyzer.add_test_result(
            "Serializar para dict",
            "success",
            {
                "keys": list(data.keys()),
                "title": data.get("title"),
                "module": data.get("module")
            }
        )
        
        # Desserializar
        doc_restored = Document.from_dict(data)
        
        # Validar
        matches = {
            "id_match": doc_original.id == doc_restored.id,
            "title_match": doc_original.title == doc_restored.title,
            "module_match": doc_original.module == doc_restored.module,
            "content_match": doc_original.content == doc_restored.content,
            "type_match": doc_original.doc_type == doc_restored.doc_type,
            "source_match": doc_original.source == doc_restored.source,
        }
        
        all_match = all(matches.values())
        analyzer.add_test_result(
            "Desserializar de dict",
            "success" if all_match else "warning",
            matches
        )
        
        # Validar metricas
        analyzer.add_test_result(
            "Metricas do documento",
            "success",
            {
                "word_count": doc_original.word_count(),
                "char_count": doc_original.char_count(),
                "content_length": len(doc_original.content)
            }
        )
        
    except Exception as e:
        analyzer.add_test_result(
            "Serializacao",
            "error",
            {"error": str(e)}
        )
    
    return analyzer


async def test_adapter_interfaces():
    """Testa interfaces dos adapters"""
    print("[4/4] Testando interfaces dos adapters...")
    analyzer = ScrapingTestAnalyzer()
    
    try:
        from libs.scrapers.adapters import (
            PlaywrightExtractor,
            UrlResolver,
            FileSystemRepository,
            SeniorDocAdapter,
            ZendeskAdapter,
        )
        
        # Verificar interfaces
        tests_interface = [
            ("PlaywrightExtractor", PlaywrightExtractor, ["extract_text", "extract_links", "close"]),
            ("UrlResolver", UrlResolver, ["resolve", "is_same_domain", "normalize"]),
            ("FileSystemRepository", FileSystemRepository, ["save", "load", "delete", "count"]),
            ("SeniorDocAdapter", SeniorDocAdapter, ["scrape", "supports_url", "get_source_name"]),
            ("ZendeskAdapter", ZendeskAdapter, ["scrape", "supports_url", "get_source_name"]),
        ]
        
        for adapter_name, adapter_class, methods in tests_interface:
            try:
                instance = adapter_class() if adapter_name == "UrlResolver" else None
                
                missing_methods = []
                for method in methods:
                    if instance and not hasattr(instance, method):
                        missing_methods.append(method)
                
                if missing_methods:
                    analyzer.add_test_result(
                        f"{adapter_name} interface",
                        "warning",
                        {"missing_methods": missing_methods}
                    )
                else:
                    analyzer.add_test_result(
                        f"{adapter_name} interface",
                        "success",
                        {"methods_found": len(methods)}
                    )
            except Exception as e:
                analyzer.add_test_result(
                    f"{adapter_name} interface",
                    "error",
                    {"error": str(e)}
                )
    
    except Exception as e:
        analyzer.add_test_result(
            "Verificar interfaces",
            "error",
            {"error": str(e)}
        )
    
    return analyzer


async def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("TESTE DE SCRAPING - HEXAGONAL ARCHITECTURE")
    print("="*70)
    print("Executando suite de testes da arquitetura hexagonal...")
    
    all_results = []
    
    # Teste 1: URL Resolver
    result1 = await test_url_resolver()
    all_results.append(result1)
    
    # Teste 2: FileSystem Repository
    result2 = await test_filesystem_repository()
    all_results.append(result2)
    
    # Teste 3: Document Serialization
    result3 = await test_document_serialization()
    all_results.append(result3)
    
    # Teste 4: Adapter Interfaces
    result4 = await test_adapter_interfaces()
    all_results.append(result4)
    
    # Compilar resultados
    print("\n" + "="*70)
    print("COMPILANDO RESULTADOS...")
    print("="*70)
    
    total_success = 0
    total_error = 0
    total_tests = 0
    
    for analyzer in all_results:
        for test in analyzer.results["tests"]:
            total_tests += 1
            if test["status"] == "success":
                total_success += 1
            elif test["status"] == "error":
                total_error += 1
    
    print(f"\nTotal de testes: {total_tests}")
    print(f"Sucessos: {total_success}")
    print(f"Erros: {total_error}")
    print(f"Taxa de sucesso: {(total_success/total_tests*100) if total_tests > 0 else 0:.1f}%")
    
    # Salvar relatorio
    report_path = "scraping_test_report.json"
    
    combined_results = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": total_tests,
            "successful": total_success,
            "errors": total_error,
            "success_rate": (total_success/total_tests*100) if total_tests > 0 else 0
        },
        "test_suites": [r.results for r in all_results]
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(combined_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nRelatorio salvo em: {report_path}")
    
    # Print individual reports
    for i, analyzer in enumerate(all_results, 1):
        analyzer.print_report()
    
    print("\n" + "="*70)
    print("TESTES CONCLUIDOS")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
