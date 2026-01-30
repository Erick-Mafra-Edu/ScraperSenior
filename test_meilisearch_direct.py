#!/usr/bin/env python3
import requests
import time
import json

headers = {'Authorization': 'Bearer meilisearch_master_key_change_me'}
url = 'http://localhost:7700'

print("[1] Testing document indexing...")

# Load actual documents
docs = []
with open('docs_indexacao_detailed.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 10:  # Just first 10 for testing
            break
        try:
            doc = json.loads(line)
            docs.append(doc)
        except:
            pass

print(f"    Loaded {len(docs)} documents")

# Try to index them
resp = requests.post(
    f'{url}/indexes/documentation/documents',
    json=docs,
    headers=headers,
    timeout=10
)

print(f"    POST response: {resp.status_code}")
print(f"    Response body: {resp.json()}")

# Wait and check
print("[2] Waiting for indexing...")
time.sleep(3)

resp = requests.get(
    f'{url}/indexes/documentation',
    headers=headers,
    timeout=5
)

data = resp.json()
print(f"    Documents in index: {data.get('numberOfDocuments', 0)}")

# Try a search
print("[3] Testing search...")
resp = requests.post(
    f'{url}/indexes/documentation/search',
    json={'q': ''},
    headers=headers,
    timeout=5
)

if resp.status_code == 200:
    results = resp.json()
    print(f"    Search results: {len(results.get('hits', []))} hits")
    if results.get('hits'):
        print(f"    First hit: {results['hits'][0].get('id', 'N/A')}")
else:
    print(f"    Search failed: {resp.status_code}")

print("\n[DONE]")
