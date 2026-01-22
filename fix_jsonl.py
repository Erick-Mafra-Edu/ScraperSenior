import json

# Ler docs_para_mcp.jsonl
docs = []
with open('docs_para_mcp.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            doc = json.loads(line)
            doc['module'] = 'GESTAO DE PESSOAS HCM'
            docs.append(doc)

# Escrever para docs_indexacao_detailed.jsonl
with open('docs_indexacao_detailed.jsonl', 'w', encoding='utf-8') as f:
    for doc in docs:
        json.dump(doc, f, ensure_ascii=False)
        f.write('\n')

print(f'✓ Criado docs_indexacao_detailed.jsonl com {len(docs)} documentos')
print(f'✓ Verificando primeira linha...')
with open('docs_indexacao_detailed.jsonl', 'r', encoding='utf-8') as f:
    first_line = f.readline()
    first_doc = json.loads(first_line)
    print(f'  Title: {first_doc.get("title")}')
    print(f'  Module: {first_doc.get("module")}')
