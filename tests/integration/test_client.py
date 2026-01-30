#!/usr/bin/env python3
import meilisearch
import os

url = os.getenv('MEILISEARCH_URL')
key = os.getenv('MEILISEARCH_KEY')

print(f'URL: {url}')
print(f'Key: {key}')
print(f'Key length: {len(key)}')

try:
    client = meilisearch.Client(url, key)
    print('✅ Client created')
    
    # Try health
    h = client.health()
    print(f'✅ Health: {h}')
    
    # Try list indexes
    indexes = client.get_indexes()
    print(f'✅ Indexes count: {len(indexes.get("results", []))}')
    
    # Try to create index
    try:
        task = client.create_index("test_index_123", {"primaryKey": "id"})
        print(f'✅ Index creation task: {task}')
    except Exception as e:
        print(f'❌ Index creation error: {e}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
