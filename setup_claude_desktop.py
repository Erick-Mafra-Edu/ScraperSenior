#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Configurar e Validar Claude Desktop com MCP Server
==============================================================

Configura o arquivo claude_desktop_config.json para usar o MCP Server customizado.
"""

import json
import os
from pathlib import Path
import shutil
import sys

def get_claude_config_path():
    """Localiza o arquivo de configuração do Claude Desktop"""
    # Windows: AppData\Claude
    windows_path = Path(os.getenv('APPDATA')) / 'Claude' / 'claude_desktop_config.json'
    
    # macOS: ~/.config/Claude
    macos_path = Path.home() / '.config' / 'Claude' / 'claude_desktop_config.json'
    
    # Linux: ~/.config/Claude
    linux_path = Path.home() / '.config' / 'Claude' / 'claude_desktop_config.json'
    
    # Verificar qual existe
    if windows_path.exists():
        return windows_path
    elif macos_path.exists():
        return macos_path
    elif linux_path.exists():
        return linux_path
    else:
        # Retornar path padrão (Windows)
        return windows_path

def get_mcp_server_config():
    """Retorna a configuração do MCP Server para Claude"""
    return {
        "senior-docs": {
            "command": "python",
            "args": [
                "C:\\Users\\Digisys\\scrapyTest\\src\\mcp_server.py"
            ],
            "cwd": "C:\\Users\\Digisys\\scrapyTest"
        }
    }

def load_or_create_config(config_path):
    """Carrega ou cria o arquivo de configuração do Claude"""
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"mcpServers": {}}

def save_config(config_path, config):
    """Salva a configuração do Claude"""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def validate_mcp_connection():
    """Valida se o MCP Server está acessível"""
    try:
        from mcp_server import load_config, SeniorDocumentationMCP
        
        print("\n" + "=" * 70)
        print("VALIDAÇÃO DO MCP SERVER")
        print("=" * 70)
        
        # Carregar configuração
        config = load_config()
        print("✅ Configuração do MCP carregada")
        
        # Inicializar servidor
        mcp = SeniorDocumentationMCP()
        print(f"✅ MCP Server inicializado")
        print(f"   - URL: {mcp.meilisearch_url}")
        print(f"   - Modo: {'Local (JSONL)' if mcp.use_local else 'Meilisearch'}")
        print(f"   - Documentos: {len(mcp.local_documents)}")
        
        # Testar busca
        results = mcp.search("teste", limit=1)
        print(f"✅ Busca funcional ({len(results)} resultados)")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao validar MCP Server: {e}")
        return False

def setup_claude_config():
    """Configura o arquivo claude_desktop_config.json"""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " CONFIGURAR CLAUDE DESKTOP COM MCP SERVER ".center(68) + "║")
    print("╚" + "=" * 68 + "╝\n")
    
    # 1. Localizar arquivo de configuração
    config_path = get_claude_config_path()
    print(f"📁 Arquivo de Configuração do Claude:")
    print(f"   {config_path}\n")
    
    # 2. Verificar se existe
    if config_path.exists():
        print(f"✅ Arquivo encontrado\n")
    else:
        print(f"⚠️  Arquivo NÃO encontrado. Será criado.\n")
    
    # 3. Carregar ou criar configuração
    print("📝 Carregando configuração...")
    config = load_or_create_config(config_path)
    
    # 4. Atualizar com MCP Server
    print("🔧 Adicionando configuração do MCP Server...")
    mcp_config = get_mcp_server_config()
    
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"].update(mcp_config)
    
    # 5. Fazer backup
    if config_path.exists():
        backup_path = config_path.with_suffix('.json.backup')
        shutil.copy2(config_path, backup_path)
        print(f"💾 Backup criado: {backup_path}\n")
    
    # 6. Salvar configuração
    print("💾 Salvando configuração...")
    save_config(config_path, config)
    print(f"✅ Configuração salva em: {config_path}\n")
    
    # 7. Mostrar configuração
    print("=" * 70)
    print("CONFIGURAÇÃO SALVA NO CLAUDE DESKTOP:")
    print("=" * 70)
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print("=" * 70)
    
    # 8. Validar MCP
    print()
    mcp_ok = validate_mcp_connection()
    
    # 9. Instruções finais
    print("\n" + "=" * 70)
    print("✅ PRÓXIMOS PASSOS:")
    print("=" * 70)
    print("""
1. ✅ Configuração salva com sucesso!

2. Reinicie o Claude Desktop:
   - Feche completamente o aplicativo
   - Abra novamente

3. Teste a conexão:
   - Use @senior-docs no chat
   - Exemplo: "@senior-docs: Como configurar CRM?"

4. Verificar logs (se houver problema):
   - Windows: Abra o Developer Console
   - Menu > Help > Toggle Developer Tools

5. Se precisar remover a configuração:
   - Edite o arquivo manualmente
   - Ou execute: python setup_claude_desktop.py --remove
""")
    print("=" * 70)
    
    return True

def remove_claude_config():
    """Remove a configuração do MCP do Claude"""
    config_path = get_claude_config_path()
    
    print("\n" + "=" * 70)
    print("⚠️  REMOVER CONFIGURAÇÃO DO CLAUDE DESKTOP")
    print("=" * 70)
    
    if not config_path.exists():
        print("❌ Arquivo de configuração não encontrado")
        return False
    
    config = load_or_create_config(config_path)
    
    if "mcpServers" in config and "senior-docs" in config["mcpServers"]:
        del config["mcpServers"]["senior-docs"]
        save_config(config_path, config)
        print(f"✅ Configuração do 'senior-docs' removida")
        print(f"   Arquivo: {config_path}")
        return True
    else:
        print("ℹ️  Configuração do 'senior-docs' não encontrada")
        return False

def show_config():
    """Mostra a configuração atual"""
    config_path = get_claude_config_path()
    
    print("\n" + "=" * 70)
    print("📋 CONFIGURAÇÃO ATUAL DO CLAUDE DESKTOP")
    print("=" * 70)
    
    if not config_path.exists():
        print(f"❌ Arquivo não encontrado: {config_path}")
        return False
    
    config = load_or_create_config(config_path)
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print("=" * 70)
    return True

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--remove":
            remove_claude_config()
        elif sys.argv[1] == "--show":
            show_config()
        elif sys.argv[1] == "--validate":
            validate_mcp_connection()
        else:
            print(f"Comando desconhecido: {sys.argv[1]}")
            print("\nUso:")
            print("  python setup_claude_desktop.py          - Configurar Claude Desktop")
            print("  python setup_claude_desktop.py --show   - Mostrar configuração atual")
            print("  python setup_claude_desktop.py --remove - Remover configuração")
            print("  python setup_claude_desktop.py --validate - Validar MCP Server")
    else:
        setup_claude_config()

if __name__ == "__main__":
    main()
