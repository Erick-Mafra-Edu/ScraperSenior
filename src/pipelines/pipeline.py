#!/usr/bin/env python3
"""
Pipeline completo: Scraper → Index → Search → Export
Integra simple_scraper com meilisearch_client
"""

import sys
import json
import subprocess
from pathlib import Path
import time
import requests


def wait_for_api(max_tries=10):
    """Aguarda API estar pronta."""
    for i in range(max_tries):
        try:
            resp = requests.get("http://localhost:5000/health", timeout=2)
            if resp.status_code == 200:
                print("✅ API ready!")
                return True
        except:
            pass
        print(f"⏳ Waiting for API... ({i+1}/{max_tries})")
        time.sleep(1)
    
    print("❌ API not responding")
    return False


def run_scraper(url, max_pages=20):
    """Executa o scraper."""
    print(f"\n{'='*70}")
    print("📥 STEP 1: Scraping")
    print(f"{'='*70}\n")
    
    cmd = [sys.executable, "simple_scraper.py", url, str(max_pages)]
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def index_documents():
    """Indexa documentos scraped."""
    print(f"\n{'='*70}")
    print("📤 STEP 2: Indexing")
    print(f"{'='*70}\n")
    
    doc_dir = Path("documentacao")
    if not doc_dir.exists():
        print("❌ documentacao/ not found!")
        return False
    
    docs = []
    for page_dir in doc_dir.iterdir():
        if page_dir.is_dir():
            metadata_file = page_dir / "metadata.json"
            content_file = page_dir / "content.txt"
            
            if metadata_file.exists() and content_file.exists():
                try:
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    with open(content_file) as f:
                        content = f.read()
                    
                    doc = {
                        **metadata,
                        "content": content,
                        "id": page_dir.name
                    }
                    docs.append(doc)
                except Exception as e:
                    print(f"⚠️  Error reading {page_dir.name}: {e}")
    
    if not docs:
        print("❌ No documents found!")
        return False
    
    print(f"Found {len(docs)} documents. Indexing...")
    
    try:
        resp = requests.post(
            "http://localhost:5000/index",
            json={"documents": docs},
            timeout=30
        )
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ Indexed {result.get('indexed', len(docs))} documents")
            return True
        else:
            print(f"❌ Error: {resp.status_code} - {resp.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_search():
    """Testa busca nos documentos indexados."""
    print(f"\n{'='*70}")
    print("🔍 STEP 3: Testing Search")
    print(f"{'='*70}\n")
    
    test_queries = ["documentação", "sistema", "help", "guide"]
    
    for query in test_queries:
        try:
            resp = requests.get(
                "http://localhost:5000/search",
                params={"q": query, "limit": 3},
                timeout=5
            )
            
            if resp.status_code == 200:
                results = resp.json()
                count = len(results.get("results", []))
                print(f"📍 Query '{query}': {count} results")
        except Exception as e:
            print(f"⚠️  Error searching '{query}': {e}")


def export_data():
    """Exporta dados para AI."""
    print(f"\n{'='*70}")
    print("💾 STEP 4: Exporting")
    print(f"{'='*70}\n")
    
    try:
        resp = requests.get("http://localhost:5000/export?format=jsonl", timeout=30)
        
        if resp.status_code == 200:
            with open("export.jsonl", "w") as f:
                f.write(resp.text)
            print("✅ Exported to export.jsonl")
            return True
        else:
            print(f"❌ Error: {resp.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main pipeline."""
    url = sys.argv[1] if len(sys.argv) > 1 else "https://documentacao.senior.com.br"
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    print(f"""
    
╔═══════════════════════════════════════════════════════════════════╗
║         PIPELINE: Scraper → Index → Search → Export              ║
╚═══════════════════════════════════════════════════════════════════╝

Target: {url}
Max Pages: {max_pages}

    """)
    
    # Check API
    if not wait_for_api():
        print("\n❌ Cannot reach API. Make sure services are running:")
        print("   docker-compose up")
        return
    
    # Run pipeline
    steps = [
        ("Scraping", lambda: run_scraper(url, max_pages)),
        ("Indexing", index_documents),
        ("Testing", test_search),
        ("Exporting", export_data),
    ]
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                print(f"\n❌ {step_name} failed!")
                break
        except Exception as e:
            print(f"\n❌ {step_name} error: {e}")
            break
    
    print(f"\n{'='*70}")
    print("✅ Pipeline complete!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
