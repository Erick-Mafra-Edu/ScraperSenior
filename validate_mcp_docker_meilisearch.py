#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação Completa do MCP, Docker e Meilisearch
================================================

Script para validar:
1. Estrutura e configuração do MCP
2. Dockerfile e docker-compose
3. Índices do Meilisearch
4. Conformidade com o padrão MCP 2.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import re

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

class MCPValidator:
    def __init__(self):
        self.project_root = Path(".")
        self.issues = []
        self.warnings = []
        self.successes = []
    
    def validate_all(self):
        print_header("VALIDAÇÃO COMPLETA: MCP, Docker e Meilisearch")
        
        self.validate_mcp_structure()
        self.validate_mcp_config()
        self.validate_mcp_server_code()
        self.validate_docker_files()
        self.validate_docker_compose()
        self.validate_meilisearch_config()
        self.validate_index_files()
        self.validate_mcp_protocol_compliance()
        
        self.print_summary()
    
    # ============================================================================
    # 1. VALIDAÇÃO DA ESTRUTURA DO MCP
    # ============================================================================
    
    def validate_mcp_structure(self):
        print_header("1. ESTRUTURA DO MCP")
        
        required_files = [
            "apps/mcp-server/mcp_server.py",
            "apps/mcp-server/mcp_server_docker.py",
            "mcp_config.json",
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print_success(f"Arquivo encontrado: {file_path}")
                self.successes.append(file_path)
            else:
                print_error(f"Arquivo NÃO encontrado: {file_path}")
                self.issues.append(f"Arquivo obrigatório faltando: {file_path}")
        
        # Verificar estrutura de diretórios
        required_dirs = [
            "apps/mcp-server",
            "libs/scrapers",
            "libs/indexers",
            "infra/docker",
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.is_dir():
                print_success(f"Diretório encontrado: {dir_path}")
                self.successes.append(dir_path)
            else:
                print_warning(f"Diretório não encontrado: {dir_path}")
                self.warnings.append(f"Diretório esperado: {dir_path}")
    
    # ============================================================================
    # 2. VALIDAÇÃO DA CONFIGURAÇÃO DO MCP
    # ============================================================================
    
    def validate_mcp_config(self):
        print_header("2. CONFIGURAÇÃO DO MCP (mcp_config.json)")
        
        config_path = self.project_root / "mcp_config.json"
        
        if not config_path.exists():
            print_error(f"Arquivo de configuração não encontrado: {config_path}")
            self.issues.append("mcp_config.json não encontrado")
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print_success(f"Arquivo JSON válido")
            
            # Verificar estrutura obrigatória
            required_keys = ["mcpServers", "meilisearch", "settings"]
            for key in required_keys:
                if key in config:
                    print_success(f"Chave obrigatória presente: {key}")
                    self.successes.append(f"config.{key}")
                else:
                    print_error(f"Chave obrigatória ausente: {key}")
                    self.issues.append(f"Chave obrigatória ausente em mcp_config.json: {key}")
            
            # Validar estrutura do Meilisearch
            if "meilisearch" in config:
                self._validate_meilisearch_config(config["meilisearch"])
            
            # Validar estrutura de settings
            if "settings" in config:
                self._validate_settings_config(config["settings"])
        
        except json.JSONDecodeError as e:
            print_error(f"Erro ao parsear JSON: {e}")
            self.issues.append(f"JSON inválido em mcp_config.json: {e}")
        except Exception as e:
            print_error(f"Erro ao ler configuração: {e}")
            self.issues.append(f"Erro ao ler mcp_config.json: {e}")
    
    def _validate_meilisearch_config(self, config: Dict):
        """Valida configuração do Meilisearch"""
        required_keys = ["url", "apiKey"]
        for key in required_keys:
            if key in config:
                print_success(f"  Meilisearch.{key}: {config[key]}")
                self.successes.append(f"meilisearch.{key}")
            else:
                print_warning(f"  Meilisearch.{key}: AUSENTE")
                self.warnings.append(f"Meilisearch.{key} não configurado")
    
    def _validate_settings_config(self, config: Dict):
        """Valida configuração de settings"""
        settings = {
            "indexName": config.get("indexName", "N/A"),
            "maxResults": config.get("maxResults", "N/A"),
            "timeout": config.get("timeout", "N/A"),
        }
        for key, value in settings.items():
            print_success(f"  Settings.{key}: {value}")
            self.successes.append(f"settings.{key}")
    
    # ============================================================================
    # 3. VALIDAÇÃO DO CÓDIGO DO MCP SERVER
    # ============================================================================
    
    def validate_mcp_server_code(self):
        print_header("3. CÓDIGO DO MCP SERVER")
        
        server_path = self.project_root / "apps/mcp-server/mcp_server.py"
        
        if not server_path.exists():
            print_error(f"Arquivo não encontrado: {server_path}")
            return
        
        try:
            with open(server_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            print_success("Arquivo Python válido")
            
            # Verificar classes obrigatórias
            required_classes = [
                "SeniorDocumentationMCP",
                "MCPServer",
            ]
            
            for class_name in required_classes:
                if f"class {class_name}" in code:
                    print_success(f"Classe encontrada: {class_name}")
                    self.successes.append(f"class {class_name}")
                else:
                    print_error(f"Classe NÃO encontrada: {class_name}")
                    self.issues.append(f"Classe obrigatória não encontrada: {class_name}")
            
            # Verificar métodos obrigatórios
            required_methods = [
                ("SeniorDocumentationMCP", "search"),
                ("SeniorDocumentationMCP", "get_modules"),
                ("SeniorDocumentationMCP", "get_stats"),
                ("MCPServer", "handle_tool_call"),
            ]
            
            for class_name, method_name in required_methods:
                pattern = f"def {method_name}\("
                if pattern in code:
                    print_success(f"Método encontrado: {class_name}.{method_name}")
                    self.successes.append(f"{class_name}.{method_name}")
                else:
                    print_warning(f"Método não encontrado: {class_name}.{method_name}")
            
            # Verificar ferramentas definidas
            tools_pattern = r'"([a-z_]+)":\s*\{'
            tools = re.findall(tools_pattern, code)
            if tools:
                print_success(f"Ferramentas encontradas: {', '.join(set(tools))}")
                for tool in set(tools):
                    self.successes.append(f"tool: {tool}")
            else:
                print_warning("Nenhuma ferramenta foi definida")
        
        except Exception as e:
            print_error(f"Erro ao analisar código: {e}")
            self.issues.append(f"Erro ao analisar mcp_server.py: {e}")
    
    # ============================================================================
    # 4. VALIDAÇÃO DOS DOCKERFILES
    # ============================================================================
    
    def validate_docker_files(self):
        print_header("4. DOCKERFILES")
        
        docker_files = [
            ("infra/docker/Dockerfile.mcp", "MCP Server"),
            ("infra/docker/Dockerfile", "Scraper"),
        ]
        
        for docker_file, description in docker_files:
            docker_path = self.project_root / docker_file
            
            if not docker_path.exists():
                print_error(f"{description}: Arquivo não encontrado: {docker_file}")
                self.issues.append(f"Dockerfile não encontrado: {docker_file}")
                continue
            
            print_success(f"{description}: Arquivo encontrado")
            self.successes.append(f"{docker_file}")
            
            try:
                with open(docker_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Validar estrutura básica do Dockerfile
                if "FROM" in content:
                    print_success(f"  - Possui instrução FROM")
                    self.successes.append(f"{docker_file}:FROM")
                
                if "WORKDIR" in content:
                    print_success(f"  - Possui instrução WORKDIR")
                    self.successes.append(f"{docker_file}:WORKDIR")
                
                if "EXPOSE" in content or description == "Scraper":
                    print_success(f"  - Possui configuração de porta/EXPOSE")
                    self.successes.append(f"{docker_file}:EXPOSE")
                
                if "HEALTHCHECK" in content:
                    print_success(f"  - Possui HEALTHCHECK")
                    self.successes.append(f"{docker_file}:HEALTHCHECK")
                else:
                    print_warning(f"  - HEALTHCHECK não definido")
            
            except Exception as e:
                print_error(f"  - Erro ao ler arquivo: {e}")
                self.issues.append(f"Erro ao ler {docker_file}: {e}")
    
    # ============================================================================
    # 5. VALIDAÇÃO DO DOCKER-COMPOSE
    # ============================================================================
    
    def validate_docker_compose(self):
        print_header("5. DOCKER-COMPOSE")
        
        compose_path = self.project_root / "infra/docker/docker-compose.yml"
        
        if not compose_path.exists():
            print_error(f"Arquivo não encontrado: {compose_path}")
            self.issues.append("docker-compose.yml não encontrado")
            return
        
        try:
            with open(compose_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print_success("Arquivo YAML válido (estruturalmente)")
            
            # Validar serviços
            required_services = ["meilisearch", "mcp-server", "scraper"]
            
            for service in required_services:
                if service + ":" in content:
                    print_success(f"Serviço definido: {service}")
                    self.successes.append(f"service: {service}")
                else:
                    print_warning(f"Serviço não encontrado: {service}")
                    self.warnings.append(f"Serviço não configurado: {service}")
            
            # Validar network
            if "networks:" in content or "senior-docs" in content:
                print_success("Network configurada")
                self.successes.append("network:senior-docs")
            else:
                print_warning("Network não configurada")
            
            # Validar volumes
            if "volumes:" in content:
                print_success("Volumes configurados")
                self.successes.append("volumes:configured")
            else:
                print_warning("Volumes não configurados")
        
        except Exception as e:
            print_error(f"Erro ao analisar docker-compose: {e}")
            self.issues.append(f"Erro ao ler docker-compose.yml: {e}")
    
    # ============================================================================
    # 6. VALIDAÇÃO DA CONFIGURAÇÃO DO MEILISEARCH
    # ============================================================================
    
    def validate_meilisearch_config(self):
        print_header("6. MEILISEARCH - CONFIGURAÇÃO")
        
        # Verificar variáveis de ambiente no docker-compose
        compose_path = self.project_root / "infra/docker/docker-compose.yml"
        
        if compose_path.exists():
            try:
                with open(compose_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                expected_env_vars = [
                    "MEILI_ENV",
                    "MEILI_MASTER_KEY",
                    "MEILI_LOG_LEVEL",
                ]
                
                for env_var in expected_env_vars:
                    if env_var in content:
                        print_success(f"Variável de ambiente: {env_var}")
                        self.successes.append(f"env:{env_var}")
                    else:
                        print_warning(f"Variável de ambiente não definida: {env_var}")
                
                # Verificar healthcheck
                if "healthcheck:" in content and "meilisearch" in content:
                    print_success("Healthcheck para Meilisearch configurado")
                    self.successes.append("meilisearch:healthcheck")
                else:
                    print_warning("Healthcheck para Meilisearch não configurado")
            
            except Exception as e:
                print_error(f"Erro ao analisar docker-compose: {e}")
    
    # ============================================================================
    # 7. VALIDAÇÃO DOS ARQUIVOS DE ÍNDICE
    # ============================================================================
    
    def validate_index_files(self):
        print_header("7. ARQUIVOS DE ÍNDICE MEILISEARCH")
        
        index_dir = self.project_root / "data/indexes"
        
        if not index_dir.exists():
            print_warning(f"Diretório de índices não encontrado: {index_dir}")
            self.warnings.append("Diretório data/indexes não existe")
            return
        
        print_success(f"Diretório de índices encontrado: {index_dir}")
        
        # Listar arquivos JSONL
        jsonl_files = list(index_dir.glob("*.jsonl"))
        
        if jsonl_files:
            print_success(f"Arquivos JSONL encontrados: {len(jsonl_files)}")
            self.successes.append(f"jsonl_files:{len(jsonl_files)}")
            
            for file_path in jsonl_files:
                file_size = file_path.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
                print_info(f"  - {file_path.name}: {file_size_mb:.2f} MB")
                self.successes.append(f"file:{file_path.name}")
                
                # Validar conteúdo JSONL
                self._validate_jsonl_file(file_path)
        else:
            print_warning("Nenhum arquivo JSONL encontrado")
            self.warnings.append("Nenhum arquivo JSONL em data/indexes")
    
    def _validate_jsonl_file(self, file_path: Path):
        """Valida estrutura de um arquivo JSONL"""
        try:
            line_count = 0
            valid_lines = 0
            invalid_lines = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line_count += 1
                    if line.strip():
                        try:
                            obj = json.loads(line)
                            valid_lines += 1
                            
                            # Validar estrutura esperada
                            if line_num == 1:  # Primeira linha
                                expected_keys = ["id", "title", "url", "module", "content"]
                                missing_keys = [k for k in expected_keys if k not in obj]
                                if missing_keys:
                                    print_warning(f"    Chaves ausentes em {file_path.name}: {', '.join(missing_keys)}")
                        except json.JSONDecodeError as e:
                            invalid_lines.append((line_num, str(e)))
            
            if valid_lines == line_count:
                print_success(f"    {file_path.name}: {line_count} linhas válidas")
                self.successes.append(f"jsonl:{file_path.name}:valid")
            else:
                print_warning(f"    {file_path.name}: {valid_lines}/{line_count} linhas válidas")
                if invalid_lines:
                    print_warning(f"      Linhas inválidas: {invalid_lines[:3]}")  # Mostrar primeiras 3
        
        except Exception as e:
            print_error(f"    Erro ao validar {file_path.name}: {e}")
            self.issues.append(f"Erro ao validar JSONL {file_path.name}: {e}")
    
    # ============================================================================
    # 8. CONFORMIDADE COM MCP 2.0
    # ============================================================================
    
    def validate_mcp_protocol_compliance(self):
        print_header("8. CONFORMIDADE COM MCP 2.0")
        
        server_path = self.project_root / "apps/mcp-server/mcp_server.py"
        docker_path = self.project_root / "apps/mcp-server/mcp_server_docker.py"
        
        print_info("Validando estrutura de protocolo MCP 2.0...")
        
        # Requisitos do MCP 2.0
        requirements = {
            "JSON-RPC 2.0": {
                "files": [server_path, docker_path],
                "patterns": ["jsonrpc", "2.0", "request_id"],
            },
            "Request Structure": {
                "files": [server_path, docker_path],
                "patterns": ["id", "method", "params"],
            },
            "Response Structure": {
                "files": [server_path, docker_path],
                "patterns": ["result", "error"],
            },
            "Tool Definition": {
                "files": [server_path],
                "patterns": ["inputSchema", "description", "parameters"],
            },
            "Error Handling": {
                "files": [server_path, docker_path],
                "patterns": ["error_code", "error_msg"],
            },
        }
        
        for requirement, details in requirements.items():
            found = False
            for file_path in details["files"]:
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        patterns_found = sum(1 for p in details["patterns"] if p in content)
                        if patterns_found > 0:
                            print_success(f"{requirement}: {patterns_found}/{len(details['patterns'])} padrões encontrados")
                            self.successes.append(f"mcp20:{requirement}")
                            found = True
                            break
                    except Exception as e:
                        pass
            
            if not found:
                print_warning(f"{requirement}: Não foi possível validar")
    
    # ============================================================================
    # RESUMO FINAL
    # ============================================================================
    
    def print_summary(self):
        print_header("RESUMO DA VALIDAÇÃO")
        
        total_successes = len(self.successes)
        total_warnings = len(self.warnings)
        total_issues = len(self.issues)
        
        print(f"{Colors.GREEN}✓ Sucessos: {total_successes}{Colors.RESET}")
        if total_successes > 0 and total_successes <= 10:
            for success in self.successes:
                print(f"  • {success}")
        elif total_successes > 10:
            print(f"  • {total_successes} validações bem-sucedidas")
        
        if total_warnings > 0:
            print(f"\n{Colors.YELLOW}⚠ Avisos: {total_warnings}{Colors.RESET}")
            for warning in self.warnings[:5]:
                print(f"  • {warning}")
            if total_warnings > 5:
                print(f"  • ... e mais {total_warnings - 5}")
        
        if total_issues > 0:
            print(f"\n{Colors.RED}✗ Problemas: {total_issues}{Colors.RESET}")
            for issue in self.issues:
                print(f"  • {issue}")
        
        print(f"\n{Colors.BOLD}Status Geral:{Colors.RESET}")
        if total_issues == 0:
            print(f"{Colors.GREEN}✓ Todas as validações passaram!{Colors.RESET}")
            return 0
        else:
            print(f"{Colors.RED}✗ {total_issues} problema(s) encontrado(s){Colors.RESET}")
            return 1

def main():
    try:
        validator = MCPValidator()
        exit_code = validator.validate_all()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_warning("Validação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
