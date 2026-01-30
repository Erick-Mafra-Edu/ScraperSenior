import json

docs = []
with open('docs_indexacao_detailed.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 3:
            break
        docs.append(json.loads(line))

for i, doc in enumerate(docs):
    print(f"Doc {i+1}: {doc.get('title')}")
    print(f"  Content size: {len(doc.get('content',''))}")
    print(f"  Content_length: {doc.get('content_length')}")
    print()
