#!/usr/bin/env python3
"""
Teste prático da API Zendesk Help Center
Valida conectividade com o endpoint real e extração de dados
"""

import asyncio
import json
from pathlib import Path
from src.api_zendesk import ZendeskScraper
from src.zendesk_modular_adapter import ZendeskToModularAdapter


async def test_zendesk_connectivity():
    """Testa conectividade com API Zendesk"""
    print("\n" + "="*80)
    print("TESTE - CONECTIVIDADE COM ZENDESK HELP CENTER API")
    print("="*80 + "\n")
    
    # Teste 1: Verificar categorias
    print("1️⃣ Testando obtenção de categorias...")
    try:
        scraper = ZendeskScraper(output_dir="test_zendesk_output")
        
        # Tenta obter categorias
        categories = await scraper.fetch_categories()
        print(f"   ✅ Categorias obtidas: {len(categories)}")
        
        if categories:
            print(f"   📌 Primeira categoria: {categories[0].name}")
        
    except Exception as e:
        print(f"   ❌ Erro ao obter categorias: {e}")
        print(f"   💡 Possível causa: API indisponível ou URL incorreta")
        return False
    
    # Teste 2: Verificar seções
    print("\n2️⃣ Testando obtenção de seções...")
    try:
        sections = await scraper.fetch_sections()
        print(f"   ✅ Seções obtidas: {len(sections)}")
        
        if sections:
            print(f"   📌 Primeira seção: {sections[0].name}")
        
    except Exception as e:
        print(f"   ❌ Erro ao obter seções: {e}")
        return False
    
    # Teste 3: Verificar artigos (primeiros 5)
    print("\n3️⃣ Testando obtenção de artigos...")
    try:
        scraper.limit_articles = 5  # Limita para teste rápido
        articles_count = 0
        
        async for article in scraper.fetch_articles_streaming():
            articles_count += 1
            print(f"   📄 Artigo {articles_count}: {article.title[:50]}...")
        
        print(f"   ✅ Artigos obtidos: {articles_count}")
        
    except Exception as e:
        print(f"   ❌ Erro ao obter artigos: {e}")
        return False
    
    # Teste 4: Verificar conversão de formato
    print("\n4️⃣ Testando conversão para formato modular...")
    try:
        if articles_count > 0:
            # Reconstrói documentos para teste
            scraper.limit_articles = 3
            scraper.documents = []
            
            async for article in scraper.fetch_articles_streaming():
                doc = {
                    'id': f'zendesk_{article.id}',
                    'url': article.url,
                    'title': article.title,
                    'content': article.body[:500],  # Primeiros 500 caracteres
                    'category_id': article.category_id,
                    'section_id': article.section_id,
                    'locale': article.locale,
                    'metadata': {
                        'source': 'zendesk',
                        'created_at': article.created_at,
                        'updated_at': article.updated_at
                    }
                }
                scraper.documents.append(doc)
            
            # Testa conversão
            converted_docs = []
            for doc in scraper.documents:
                converted = ZendeskToModularAdapter.convert_article(doc)
                converted_docs.append(converted)
            
            print(f"   ✅ Documentos convertidos: {len(converted_docs)}")
            
            if converted_docs:
                converted_json = json.dumps(converted_docs[0], indent=2, ensure_ascii=False)
                print(f"   📋 Exemplo de documento convertido:\n{converted_json}")
        
    except Exception as e:
        print(f"   ❌ Erro na conversão: {e}")
        return False
    
    # Teste 5: Salvar em arquivo
    print("\n5️⃣ Testando salvamento em arquivo...")
    try:
        output_dir = Path("test_zendesk_output")
        output_dir.mkdir(exist_ok=True)
        
        # Salva documentos convertidos
        output_file = output_dir / "zendesk_modular.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for doc in converted_docs:
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')
        
        print(f"   ✅ Arquivo salvo: {output_file}")
        print(f"   📁 Documentos armazenados: {len(converted_docs)}")
        
        # Salva metadados
        metadata = {
            'source': 'zendesk_help_center',
            'base_url': 'https://suporte.senior.com.br/api/v2/help_center',
            'locale': 'pt-BR',
            'documents_count': len(converted_docs),
            'documents': [
                {
                    'id': doc['id'],
                    'title': doc['title'],
                    'url': doc['url']
                } for doc in converted_docs
            ]
        }
        
        metadata_file = output_dir / "zendesk_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Metadados salvos: {metadata_file}")
        
    except Exception as e:
        print(f"   ❌ Erro ao salvar arquivos: {e}")
        return False
    
    return True


async def main():
    """Executa testes"""
    try:
        success = await test_zendesk_connectivity()
        
        print("\n" + "="*80)
        if success:
            print("✅ TODOS OS TESTES PASSARAM")
            print("="*80)
            print("\n📊 Próximos passos:")
            print("   1. Revisar documentos em test_zendesk_output/")
            print("   2. Indexar documentos em Meilisearch")
            print("   3. Testar busca integrada (website + API)")
            print("   4. Configurar Docker para usar ambas as fontes")
            print("="*80 + "\n")
        else:
            print("❌ ALGUNS TESTES FALHARAM")
            print("="*80)
            print("\n🔧 Troubleshooting:")
            print("   1. Verifique a URL da API: https://suporte.senior.com.br/api/v2/help_center")
            print("   2. Verifique conexão de internet")
            print("   3. Verifique se a API está disponível")
            print("   4. Revise logs de erro acima")
            print("="*80 + "\n")
            
    except Exception as e:
        print(f"\n❌ Erro durante testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
