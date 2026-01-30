#!/usr/bin/env python3
"""
Index all 855 documents into Meilisearch
"""

import requests
import time
import json

headers = {'Authorization': 'Bearer meilisearch_master_key_change_me'}
url = 'http://localhost:7700'

print("="*70)
print("FULL DOCUMENT INDEXING - 855 DOCUMENTS")
print("="*70)

# First delete the old index
print("\n[1] Deleting old index...")
resp = requests.delete(
    f'{url}/indexes/documentation',
    headers=headers,
    timeout=5
)
print(f"    Delete task: {resp.status_code}")
time.sleep(2)

# Load ALL documents
print("\n[2] Loading documents from docs_indexacao_detailed.jsonl...")
docs = []
with open('docs_indexacao_detailed.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            doc = json.loads(line)
            docs.append(doc)
        except Exception as e:
            print(f"    Error loading: {e}")

print(f"    Loaded {len(docs)} documents")

# Create new index
print("\n[3] Creating new index...")
resp = requests.post(
    f'{url}/indexes',
    json={"uid": "documentation", "primaryKey": "id"},
    headers=headers,
    timeout=5
)
print(f"    Create response: {resp.status_code}")
time.sleep(1)

# Index documents in batches
print("\n[4] Indexing documents in batches...")
batch_size = 100
total_indexed = 0

for i in range(0, len(docs), batch_size):
    batch = docs[i:i+batch_size]
    
    resp = requests.post(
        f'{url}/indexes/documentation/documents',
        json=batch,
        headers=headers,
        timeout=10
    )
    
    print(f"    Batch {i//batch_size + 1}: {len(batch)} docs -> Status {resp.status_code}")
    total_indexed += len(batch)

print(f"    Total sent: {total_indexed} documents")

# Wait for processing
print("\n[5] Waiting for indexing to complete (max 30s)...")
for attempt in range(30):
    resp = requests.get(
        f'{url}/indexes/documentation',
        headers=headers,
        timeout=5
    )
    
    data = resp.json()
    count = data.get('numberOfDocuments', 0)
    
    if count > 0:
        print(f"    ✓ {count} documents indexed after {attempt+1}s")
        break
    
    if attempt % 5 == 0:
        print(f"    Attempt {attempt+1}/30...")
    
    time.sleep(1)

# Final verification
print("\n[6] Final verification...")
resp = requests.get(
    f'{url}/indexes/documentation',
    headers=headers,
    timeout=5
)

data = resp.json()
print(f"    Index: {data.get('uid')}")
print(f"    Documents: {data.get('numberOfDocuments', 0)}")

# Test search
print("\n[7] Test search...")
resp = requests.post(
    f'{url}/indexes/documentation/search',
    json={'q': ''},
    headers=headers,
    timeout=5
)

if resp.status_code == 200:
    results = resp.json()
    print(f"    Results: {len(results.get('hits', []))} hits")

print("\n" + "="*70)
print("INDEXING COMPLETE")
print("="*70 + "\n")
