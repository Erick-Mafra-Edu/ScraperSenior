#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guia para Configurar MCP Server com Docker
============================================

Este script ajuda a configurar e gerenciar o MCP Server usando Docker.
"""

import json
from pathlib import Path

def get_mcp_docker_config():
    """Retorna a configuração para usar MCP via Docker"""
    
    configs = {
        "option1_local_docker": {
            "descricao": "Conecta ao MCP Server rodando em Docker (porta 8000)",
            "tipo": "HTTP",
            "config": {
                "type": "http",
                "url": "http://localhost:8000",
                "name": "senior-docs-docker"
            }
        },
        
        "option2_docker_cli": {
            "descricao": "Executa MCP via Docker diretamente do VS Code",
            "tipo": "Docker Image",
            "config": {
                "type": "docker",
                "image": "senior-docs-mcp:latest",
                "name": "senior-docs-docker"
            }
        },
        
        "option3_docker_compose": {
            "descricao": "Usa docker-compose para orquestração completa",
            "tipo": "Docker Compose",
            "config": {
                "type": "docker-compose",
                "compose_file": "docker-compose.yml",
                "service": "mcp-server",
                "name": "senior-docs-docker"
            }
        }
    }
    
    return configs

def print_setup_guide():
    """Imprime o guia de configuração do Docker"""
    
    print("\n" + "="*80)
    print("CONFIGURAR MCP SERVER COM DOCKER".center(80))
    print("="*80 + "\n")
    
    print("📋 OPÇÕES DE CONFIGURAÇÃO:\n")
    
    configs = get_mcp_docker_config()
    
    print("1️⃣  OPÇÃO 1: Conectar ao Container Rodando (RECOMENDADO)")
    print("   " + "-"*76)
    print("""   
   ✓ Melhor para: Desenvolvimento com Docker já rodando
   ✓ Comando: docker-compose up -d
   ✓ Conecta via HTTP na porta 8000
   
   Configuração mcp.json:
   {
       "senior-docs": {
           "type": "http",
           "url": "http://localhost:8000"
       }
   }
   """)
    
    print("\n2️⃣  OPÇÃO 2: Executar Docker Container Direto")
    print("   " + "-"*76)
    print("""   
   ✓ Melhor para: Ambiente isolado
   ✓ Build: docker build -f Dockerfile.mcp -t senior-docs-mcp:latest .
   ✓ Executa container diretamente
   
   Configuração mcp.json:
   {
       "senior-docs": {
           "type": "docker",
           "image": "senior-docs-mcp:latest",
           "command": "python src/mcp_server.py"
       }
   }
   """)
    
    print("\n3️⃣  OPÇÃO 3: Docker Compose Orquestrado (MAIS COMPLETO)")
    print("   " + "-"*76)
    print("""   
   ✓ Melhor para: Produção com Meilisearch + MCP Server
   ✓ Inclui: Meilisearch + MCP Server + Networking
   ✓ Comando: docker-compose up -d
   
   Já configurado em docker-compose.yml!
   """)

def print_step_by_step():
    """Imprime passo a passo para cada opção"""
    
    print("\n\n" + "="*80)
    print("PASSO A PASSO: OPÇÃO 1 (RECOMENDADA)".center(80))
    print("="*80 + "\n")
    
    steps = [
        ("1. Construir a imagem Docker", """
   cd c:\\Users\\Digisys\\scrapyTest
   docker-compose build
        """),
        
        ("2. Iniciar os containers", """
   docker-compose up -d
   
   Isso iniciará:
   • Meilisearch na porta 7700
   • MCP Server na porta 8000
        """),
        
        ("3. Verificar status", """
   docker-compose ps
   docker-compose logs mcp-server
        """),
        
        ("4. Configurar VS Code (mcp.json)", """
   Atualize: C:\\Users\\Digisys\\AppData\\Roaming\\Code\\User\\mcp.json
   
   Adicione:
   {
       "servers": {
           "senior-docs-docker": {
               "type": "http",
               "url": "http://localhost:8000"
           }
       }
   }
        """),
        
        ("5. Testar conexão", """
   curl http://localhost:8000/health
   
   Resposta esperada: HTTP 200 OK
        """),
        
        ("6. Usar no VS Code", """
   @senior-docs-docker: Como configurar CRM?
        """)
    ]
    
    for title, content in steps:
        print(f"📌 {title}")
        print(content)
        print()

def print_dockerfile_mcp_info():
    """Informações sobre o Dockerfile.mcp"""
    
    print("\n" + "="*80)
    print("INFORMAÇÕES DO DOCKERFILE.MCP".center(80))
    print("="*80 + "\n")
    
    print("""
🐳 O arquivo Dockerfile.mcp está configurado com:

✓ Imagem base: python:3.14-slim
✓ Diretório de trabalho: /app
✓ Variáveis de ambiente:
  - MEILISEARCH_URL: http://meilisearch:7700 (inside Docker network)
  - MEILISEARCH_KEY: Da variável de ambiente
  - PYTHONUNBUFFERED: 1 (para logs em tempo real)

✓ Dependências:
  - requirements.txt instalado
  - Playwright chromium instalado
  - Usuário não-root (appuser)

✓ Volumes:
  - docs_indexacao_detailed.jsonl (read-only)

✓ Porta exposta: 8000
✓ Health check: curl http://localhost:7700/health
✓ Restart policy: unless-stopped
    """)

def print_troubleshooting():
    """Dicas de troubleshooting"""
    
    print("\n" + "="*80)
    print("🆘 TROUBLESHOOTING".center(80))
    print("="*80 + "\n")
    
    issues = {
        "Porta 8000 já está em uso": """
   1. Verificar qual processo usa a porta:
      netstat -ano | findstr :8000
   
   2. Ou mudar a porta no docker-compose.yml:
      ports:
        - "8001:8000"  # Mudar para 8001
   
   3. Atualizar mcp.json:
      "url": "http://localhost:8001"
        """,
        
        "Container não inicia": """
   1. Verificar logs:
      docker-compose logs mcp-server
   
   2. Verificar se a imagem foi buildada:
      docker images | grep senior-docs
   
   3. Rebuildar:
      docker-compose build --no-cache
        """,
        
        "VS Code não consegue conectar": """
   1. Testar conexão manual:
      curl http://localhost:8000/health
   
   2. Se falhar, verificar:
      docker-compose ps
      docker-compose logs
   
   3. Restartar:
      docker-compose restart mcp-server
        """,
        
        "Meilisearch não conecta": """
   1. Verificar se Meilisearch está rodando:
      docker-compose logs meilisearch
   
   2. Testar health:
      curl http://localhost:7700/health
   
   3. Se falhar, reiniciar:
      docker-compose restart meilisearch
        """
    }
    
    for issue, solution in issues.items():
        print(f"❌ {issue}")
        print(solution)
        print()

def print_commands():
    """Comandos úteis"""
    
    print("\n" + "="*80)
    print("📝 COMANDOS ÚTEIS".center(80))
    print("="*80 + "\n")
    
    commands = {
        "Iniciar": "docker-compose up -d",
        "Parar": "docker-compose down",
        "Logs MCP": "docker-compose logs -f mcp-server",
        "Logs Meilisearch": "docker-compose logs -f meilisearch",
        "Status": "docker-compose ps",
        "Reiniciar": "docker-compose restart",
        "Build": "docker-compose build",
        "Build sem cache": "docker-compose build --no-cache",
        "Testar saúde MCP": "curl http://localhost:8000/health",
        "Testar saúde Meilisearch": "curl http://localhost:7700/health",
        "Conectar ao container": "docker exec -it senior-docs-mcp-server bash",
        "Ver variáveis de ambiente": "docker exec senior-docs-mcp-server env",
    }
    
    for desc, cmd in commands.items():
        print(f"  {desc:.<40} {cmd}")
    
    print()

def main():
    """Função principal"""
    print_setup_guide()
    print_step_by_step()
    print_dockerfile_mcp_info()
    print_commands()
    print_troubleshooting()
    
    print("\n" + "="*80)
    print("✨ PRÓXIMOS PASSOS".center(80))
    print("="*80 + "\n")
    print("""
1. Execute: docker-compose build
2. Execute: docker-compose up -d
3. Aguarde ~10 segundos para inicialização
4. Verifique: curl http://localhost:8000/health
5. Atualize mcp.json com a configuração HTTP
6. Reinicie VS Code
7. Use @senior-docs-docker no chat

🎉 Pronto! Seu MCP Server está rodando em Docker!
    """)

if __name__ == "__main__":
    main()
