"""
Script de teste prático dos adapters criados.

Testa os adapters SeniorDocAdapter e ZendeskAdapter em um cenário real.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from libs.scrapers.adapters import (
    SeniorDocAdapter,
    ZendeskAdapter,
    PlaywrightExtractor,
    UrlResolver,
    FileSystemRepository,
)


async def test_senior_doc_adapter():
    """Testa SeniorDocAdapter com URL real"""
    print("\n" + "="*70)
    print(" TESTANDO SENIOR DOC ADAPTER")
    print("="*70)
    
    # Setup
    extractor = PlaywrightExtractor()
    resolver = UrlResolver()
    adapter = SeniorDocAdapter(extractor=extractor, url_resolver=resolver)
    
    # Test URL
    test_url = "https://documentacao.senior.com.br/gestao-pessoal/6.10.4/index.html"
    
    try:
        print(f"\n URL: {test_url}")
        print(" Iniciando scraping...")
        
        # Validate URL
        is_valid = await adapter.validate_url(test_url)
        print(f"✓ URL válida: {is_valid}")
        
        if not is_valid:
            print(" URL não é válida")
            return
        
        # Scrape single page
        doc = await adapter.scrape(test_url)
        
        print(f"\n DOCUMENTO EXTRAÍDO:")
        print(f"  • ID: {doc.id}")
        print(f"  • Título: {doc.title}")
        print(f"  • Módulo: {doc.module}")
        print(f"  • Tipo: {doc.doc_type.value}")
        print(f"  • Fonte: {doc.source.value}")
        print(f"  • Palavras: {doc.word_count()}")
        print(f"  • Caracteres: {doc.char_count()}")
        print(f"  • Breadcrumb: {doc.metadata.get('breadcrumb', 'N/A')}")
        print(f"  • Formato: {doc.metadata.get('format', 'N/A')}")
        
        # Test supports_url
        print(f"\n✓ Suporta URL: {adapter.supports_url(test_url)}")
        print(f"✓ Nome da fonte: {adapter.get_source_name()}")
        
    except Exception as e:
        print(f"\n ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await extractor.close()
        await adapter.close()


async def test_zendesk_adapter():
    """Testa ZendeskAdapter com API real"""
    print("\n" + "="*70)
    print(" TESTANDO ZENDESK ADAPTER")
    print("="*70)
    
    adapter = ZendeskAdapter()
    
    try:
        # Test URL
        test_url = "https://suporte.senior.com.br/hc/pt-br/articles/1234567"
        
        print(f"\n Testando suporte a URL...")
        supports = adapter.supports_url(test_url)
        print(f"✓ Suporta URL: {supports}")
        print(f"✓ Nome da fonte: {adapter.get_source_name()}")
        
        # Estimate documents
        print(f"\n Estimando número de artigos...")
        estimate = await adapter.estimate_documents("https://suporte.senior.com.br")
        print(f"✓ Estimativa: ~{estimate} artigos")
        
    except Exception as e:
        print(f"\n ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await adapter.close()


async def test_filesystem_repository():
    """Testa FileSystemRepository"""
    print("\n" + "="*70)
    print(" TESTANDO FILESYSTEM REPOSITORY")
    print("="*70)
    
    from datetime import datetime
    from libs.scrapers.domain import Document, DocumentType, DocumentSource
    import tempfile
    
    # Create temp dir
    temp_dir = tempfile.mkdtemp(prefix="test_repo_")
    print(f"\n Diretório temporário: {temp_dir}")
    
    repository = FileSystemRepository(base_dir=temp_dir)
    
    try:
        # Create test document
        doc = Document(
            id="test-123",
            url="https://example.com/test",
            title="Documento de Teste",
            content="Este é um conteúdo de teste para validar o repository.",
            module="modulo-teste",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.SENIOR_MADCAP,
            scraped_at=datetime.now(),
            metadata={"version": "1.0.0"}
        )
        
        print(f"\n Salvando documento...")
        saved_path = await repository.save(doc)
        print(f"✓ Salvo em: {saved_path}")
        
        print(f"\n Carregando documento...")
        loaded = await repository.load(doc.id)
        print(f"✓ Carregado: {loaded.title}")
        print(f"✓ Módulo: {loaded.module}")
        print(f"✓ Palavras: {loaded.word_count()}")
        
        print(f"\n Contando documentos...")
        count = await repository.count()
        print(f"✓ Total: {count} documento(s)")
        
        print(f"\n Listando por módulo...")
        by_module = await repository.list_by_module("modulo-teste")
        print(f"✓ Encontrados: {len(by_module)} documento(s)")
        
        print(f"\n Deletando documento...")
        deleted = await repository.delete(doc.id)
        print(f"✓ Deletado: {deleted}")
        
    except Exception as e:
        print(f"\n ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


async def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print(" TESTE PRÁTICO DOS ADAPTERS - HEXAGONAL ARCHITECTURE")
    print("="*70)
    
    # Test 1: FileSystemRepository (não precisa de network)
    await test_filesystem_repository()
    
    # Test 2: ZendeskAdapter (API simples)
    await test_zendesk_adapter()
    
    # Test 3: SeniorDocAdapter (requer browser)
    print("\n  ATENÇÃO: Teste do Senior Doc requer Playwright instalado")
    print("  Para executar: playwright install chromium")
    
    try:
        await test_senior_doc_adapter()
    except Exception as e:
        print(f"\n Pulando teste Senior Doc: {str(e)}")
    
    print("\n" + "="*70)
    print(" TESTES CONCLUÍDOS!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

