#!/usr/bin/env python3
"""
Index Scraped Documents to Meilisearch
Indexes documents from docs_estruturado/ folder
"""

import json
import meilisearch
from pathlib import Path
import sys
import time

def main():
    MEILISEARCH_URL = "http://localhost:7700"
    MEILISEARCH_KEY = "5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"
    SCRAPED_DIR = Path("./docs_estruturado")
    
    print("=" * 80)
    print("INDEXING SCRAPED DOCUMENTS")
    print("=" * 80)
    
    # Connect to Meilisearch
    print(f"\n🔗 Connecting to {MEILISEARCH_URL}...")
    try:
        client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_KEY)
        health = client.health()
        print("✅ Connected to Meilisearch")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Get or create index
    print(f"\n📑 Getting/creating index 'documentation'...")
    try:
        index = client.get_index("documentation")
        print("✅ Index obtained")
    except:
        print("📝 Creating index...")
        try:
            response = client.create_index("documentation", {"primaryKey": "id"})
            time.sleep(1)
            index = client.get_index("documentation")
            print("✅ Index created")
        except Exception as e:
            print(f"❌ Could not create index: {e}")
            return False
    
    # Collect all documents from metadata.json files
    print(f"\n🔍 Scanning {SCRAPED_DIR} for documents...")
    docs = []
    doc_count = 0
    
    for metadata_file in SCRAPED_DIR.rglob("metadata.json"):
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                doc = json.load(f)
                
                # Add ID based on file path
                doc['id'] = str(metadata_file.parent.relative_to(SCRAPED_DIR))
                
                # Add content from content.txt if exists
                content_file = metadata_file.parent / "content.txt"
                if content_file.exists():
                    with open(content_file, 'r', encoding='utf-8') as cf:
                        doc['content'] = cf.read()[:10000]  # Limit to 10k chars
                
                docs.append(doc)
                doc_count += 1
                
                if doc_count % 50 == 0:
                    print(f"   📄 Found {doc_count} documents...")
        except Exception as e:
            print(f"⚠️  Skipped {metadata_file}: {str(e)[:60]}")
    
    print(f"\n📊 Total documents to index: {doc_count}")
    
    if doc_count == 0:
        print("⚠️  No documents found to index")
        return False
    
    # Batch indexing (Meilisearch has limits)
    print(f"\n⏳ Indexing {doc_count} documents...")
    batch_size = 100
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i+batch_size]
        try:
            result = index.add_documents(batch)
            print(f"   ✅ Batch {i//batch_size + 1}: {len(batch)} documents queued")
        except Exception as e:
            print(f"   ❌ Batch {i//batch_size + 1} failed: {e}")
    
    # Wait and check status
    print(f"\n⏳ Waiting for indexation to complete...")
    time.sleep(3)
    
    try:
        stats = index.get_stats()
        print(f"\n📊 Index Statistics:")
        print(f"   - Documents in index: {stats['numberOfDocuments']}")
        print(f"   - Still indexing: {stats['isIndexing']}")
        print(f"   - Field distribution: {stats.get('fieldDistribution', {})}")
    except Exception as e:
        print(f"⚠️  Could not get stats: {e}")
    
    print("\n✅ Indexation complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
