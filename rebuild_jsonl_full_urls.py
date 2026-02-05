#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reconstruir o JSONL com URLs completos
Suporta dois domínios:
- documentacao.senior.com.br (documentação técnica)
- suporte.senior.com.br (suporte/Zendesk)

Transforma: /BI/Apresentação/ 
Em: https://documentacao.senior.com.br/bi/apresentacao/
"""

import json
import re
from pathlib import Path

def convert_path_to_full_url(path: str, module: str = None) -> str:
    """
    Converte path relativo para URL completo.
    
    Suporta dois domínios baseado no módulo:
    - Help Center, Suporte, Zendesk → suporte.senior.com.br
    - Outros → documentacao.senior.com.br
    
    Exemplos:
    /BI/Apresentação/ → https://documentacao.senior.com.br/bi/apresentacao/
    /Help Center/LSP/ → https://suporte.senior.com.br/help-center/lsp/
    """
    if not path:
        return "https://documentacao.senior.com.br/"
    
    # Detectar domínio baseado no módulo
    domain = "documentacao.senior.com.br"  # Padrão
    
    suporte_keywords = ['help center', 'suporte', 'zendesk', 'faq', 'ticket', 'support']
    if module:
        module_lower = module.lower()
        if any(kw in module_lower for kw in suporte_keywords):
            domain = "suporte.senior.com.br"
    
    # Remove barras finais/iniciais
    path = path.strip("/")
    
    # Converter para lowercase e substituir espaços/underscores por hífens
    path = path.lower()
    path = path.replace("_", "-")
    path = path.replace(" ", "-")
    
    # Normalizar múltiplos hífens
    path = re.sub(r'-+', '-', path)
    
    # Remove caracteres especiais (exceto hífens)
    path = re.sub(r'[^a-z0-9\-/]', '', path)
    
    return f"https://{domain}/{path}/"


def process_jsonl(input_file: str, output_file: str):
    """Processa JSONL e reconstrói com URLs completos"""
    
    count = 0
    processed = 0
    errors = 0
    
    print(f"🔄 Processando {input_file}...")
    print()
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                count += 1
                
                try:
                    if not line.strip():
                        continue
                    
                    doc = json.loads(line)
                    
                    # Verificar se tem URL relativo
                    url = doc.get('url', '')
                    module = doc.get('module', '')
                    
                    if url and url.startswith('/'):
                        # Converter para URL completo
                        full_url = convert_path_to_full_url(url, module)
                        doc['url'] = full_url
                        
                        # Log para primeiros 5 documentos
                        if processed < 5:
                            print(f"  ✓ {doc.get('title', 'N/A')}")
                            print(f"    Módulo: {module}")
                            print(f"    Antes: {url}")
                            print(f"    Depois: {full_url}")
                            print()
                    
                    # Escrever documento processado
                    outfile.write(json.dumps(doc, ensure_ascii=False) + '\n')
                    processed += 1
                    
                except json.JSONDecodeError as e:
                    print(f"  ❌ Erro na linha {count}: {e}")
                    errors += 1
                    continue
        
        print(f"✅ Processamento concluído!")
        print(f"  📄 Linhas processadas: {processed}")
        print(f"  ⚠️  Erros: {errors}")
        print(f"  💾 Salvo em: {output_file}")
        print()
        print("Domínios suportados:")
        print("  - documentacao.senior.com.br (documentação técnica)")
        print("  - suporte.senior.com.br (suporte/Zendesk)")
        
        return processed, errors
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        return 0, count


if __name__ == "__main__":
    input_file = "docs_indexacao_detailed.jsonl"
    output_file = "docs_indexacao_detailed_full_urls.jsonl"
    
    print("=" * 70)
    print("RECONSTITUINDO JSONL COM URLs COMPLETOS")
    print("Suporta: documentacao.senior.com.br e suporte.senior.com.br")
    print("=" * 70)
    print()
    
    # Verificar se arquivo existe
    if not Path(input_file).exists():
        print(f"❌ Arquivo não encontrado: {input_file}")
        exit(1)
    
    # Processar
    processed, errors = process_jsonl(input_file, output_file)
    
    if errors == 0:
        print(f"✨ Sucesso! Nenhum erro encontrado.")
        print(f"\n💡 Próximo passo:")
        print(f"   1. Substituir arquivo original:")
        print(f"      mv {output_file} {input_file}")
        print(f"   2. Reiniciar servidor MCP")
    else:
        print(f"\n⚠️  {errors} erro(s) encontrado(s). Verifique o arquivo original.")

