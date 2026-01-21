#!/usr/bin/env python3
"""
Orchestrator: Scrape → Index → Export
Complete workflow for scraping Senior documentation and indexing with Meilisearch.
"""

import subprocess
import time
import requests
import json
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command."""
    print(f"\n{'='*70}")
    print(f"▶️  {description}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\n❌ Error: {description} failed")
        return False
    
    return True


def wait_for_api(max_retries=10):
    """Wait for API to be ready."""
    print("\n⏳ Waiting for API to be ready...")
    
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is ready\n")
                return True
        except:
            print(f"  Retry {i+1}/{max_retries}...")
            time.sleep(2)
    
    return False


def check_api():
    """Check if API is running."""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def scrape_documentation(url, max_pages):
    """Scrape documentation."""
    print(f"\n{'='*70}")
    print(f"🕷️  SCRAPING DOCUMENTATION")
    print(f"{'='*70}")
    print(f"URL: {url}")
    print(f"Max Pages: {max_pages}\n")
    
    cmd = f"python scraper_senior.py '{url}' {max_pages}"
    
    if not run_command(cmd, f"Scraping {url} (max {max_pages} pages)"):
        return False
    
    # Check if any files were created
    doc_dir = Path("documentacao")
    if doc_dir.exists():
        pages = list(doc_dir.glob("*/metadata.json"))
        print(f"\n✅ Found {len(pages)} pages to index")
        return True
    
    return False


def index_documents():
    """Index documents via API."""
    print(f"\n{'='*70}")
    print(f"📑 INDEXING DOCUMENTS")
    print(f"{'='*70}\n")
    
    try:
        response = requests.post("http://localhost:5000/index", timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            indexed = data.get("documents_indexed", 0)
            print(f"✅ Successfully indexed {indexed} documents\n")
            return True
        else:
            print(f"❌ Indexing failed: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"❌ Error indexing: {e}")
        return False


def get_stats():
    """Get index statistics."""
    try:
        response = requests.get("http://localhost:5000/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data
    
    except Exception as e:
        print(f"Error getting stats: {e}")
    
    return None


def verify_indexing():
    """Verify that documents were indexed."""
    print(f"\n{'='*70}")
    print(f"✅ VERIFYING INDEX")
    print(f"{'='*70}\n")
    
    stats = get_stats()
    
    if not stats:
        print("❌ Could not retrieve stats")
        return False
    
    doc_count = stats.get("documents_count", 0)
    
    print(f"📊 Index Statistics:")
    print(f"   • Total Documents: {doc_count}")
    print(f"   • Fields: {len(stats.get('field_distribution', {}))}")
    
    if doc_count > 0:
        print(f"\n✅ Index contains {doc_count} documents")
        return True
    else:
        print("\n⚠️  No documents indexed")
        return False


def test_search():
    """Test search functionality."""
    print(f"\n{'='*70}")
    print(f"🔍 TESTING SEARCH")
    print(f"{'='*70}\n")
    
    test_queries = ["python", "api", "tecnologia"]
    
    for query in test_queries:
        try:
            response = requests.get(
                "http://localhost:5000/search",
                params={"q": query, "limit": 3},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get("total_hits", 0)
                print(f"  🔍 '{query}': {hits} results")
            else:
                print(f"  ❌ Search failed for '{query}'")
        
        except Exception as e:
            print(f"  ❌ Error searching '{query}': {e}")


def export_data():
    """Export indexed data."""
    print(f"\n{'='*70}")
    print(f"💾 EXPORTING DATA FOR AI")
    print(f"{'='*70}\n")
    
    formats = ["jsonl", "csv"]
    
    for fmt in formats:
        try:
            response = requests.get(
                "http://localhost:5000/export",
                params={"format": fmt},
                timeout=60
            )
            
            if response.status_code == 200:
                filename = f"export_data.{fmt}"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(response.text)
                
                size = Path(filename).stat().st_size
                print(f"✅ Exported {fmt.upper()}: {filename} ({size/1024:.1f} KB)")
            else:
                print(f"❌ Export failed for {fmt}")
        
        except Exception as e:
            print(f"❌ Error exporting {fmt}: {e}")


def main():
    """Main workflow."""
    print("\n" + "="*70)
    print("🚀 SENIOR DOCUMENTATION PIPELINE")
    print("="*70)
    print("Workflow: Scrape → Index → Verify → Export")
    print("="*70)
    
    # Parse arguments
    url = sys.argv[1] if len(sys.argv) > 1 else "https://documentacao.senior.com.br"
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    # Check if API is running
    print("\n1️⃣  Checking API status...")
    if not check_api():
        print("❌ API is not running!")
        print("Start it with: docker-compose up -d")
        return
    print("✅ API is running\n")
    
    # Step 1: Scrape
    print("\n2️⃣  Starting scraper...")
    if not scrape_documentation(url, max_pages):
        print("❌ Scraping failed")
        return
    
    # Wait a moment
    time.sleep(2)
    
    # Step 2: Index
    print("\n3️⃣  Indexing documents...")
    if not index_documents():
        print("❌ Indexing failed")
        return
    
    # Wait for indexing to complete
    time.sleep(3)
    
    # Step 3: Verify
    print("\n4️⃣  Verifying index...")
    if not verify_indexing():
        print("⚠️  Verification showed no documents")
    
    # Step 4: Test Search
    print("\n5️⃣  Testing search...")
    test_search()
    
    # Step 5: Export
    print("\n6️⃣  Exporting data...")
    export_data()
    
    # Summary
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETE!")
    print("="*70)
    print("\nWhat's next:")
    print("  • View Meilisearch UI: http://localhost:7700")
    print("  • Search API: http://localhost:5000/search?q=<query>")
    print("  • Export more formats: curl 'http://localhost:5000/export?format=json'")
    print("  • Use export files for AI training")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
