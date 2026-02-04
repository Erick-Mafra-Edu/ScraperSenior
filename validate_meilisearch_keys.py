#!/usr/bin/env python3
"""
Validação de Configuração de Chaves Meilisearch
Verifica se todas as chaves estão configuradas corretamente
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Chave padrão correta
CORRECT_KEY = "5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"
OLD_KEY = "meilisearch_master_key_change_me"

class MeilisearchKeyValidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        self.successes = []
        
    def check_file(self, filepath: Path) -> Tuple[bool, List[str]]:
        """Verifica um arquivo quanto a chaves hardcoded"""
        issues = []
        
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            
            # Procura pela chave antiga
            if OLD_KEY in content:
                issues.append(f"❌ Chave ANTIGA encontrada: {OLD_KEY}")
            
            # Procura por padrões de chaves hardcoded em Bearer tokens
            bearer_pattern = r"Bearer\s+[a-f0-9]{64}"
            for match in re.finditer(bearer_pattern, content):
                key = match.group(0).replace("Bearer ", "")
                if key != CORRECT_KEY:
                    issues.append(f"⚠️  Chave diferente em Bearer token: {key[:20]}...")
            
            # Procura por chaves hardcoded em Client()
            client_pattern = r"Client\([^,]+,\s*['\"]([a-f0-9]{64})['\"]"
            for match in re.finditer(client_pattern, content):
                key = match.group(1)
                if key != CORRECT_KEY:
                    issues.append(f"⚠️  Chave diferente em Client(): {key[:20]}...")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Erro ao ler arquivo: {e}"]
    
    def validate_docker_compose(self) -> bool:
        """Valida docker-compose.yml"""
        print("\n📦 Validando docker-compose.yml...")
        docker_compose_file = self.project_root / "docker-compose.yml"
        
        if not docker_compose_file.exists():
            self.issues.append("❌ docker-compose.yml não encontrado")
            return False
        
        content = docker_compose_file.read_text()
        
        # Verificar se usa variáveis de ambiente
        if "${MEILISEARCH_KEY:-" not in content:
            self.issues.append("❌ docker-compose.yml não usa ${MEILISEARCH_KEY:-}")
            return False
        
        # Contar quantas vezes a variável aparece
        count = content.count("${MEILISEARCH_KEY:-")
        print(f"   ✅ Found {count} references to MEILISEARCH_KEY variable")
        
        self.successes.append(f"✅ docker-compose.yml usa variáveis de ambiente")
        return True
    
    def validate_python_files(self) -> None:
        """Valida arquivos Python"""
        print("\n🐍 Validando arquivos Python...")
        
        critical_files = [
            "post_scraping_indexation.py",
            "scripts/indexing/post_scraping_indexation.py",
            "docker_entrypoint.py",
            "apps/mcp-server/openapi_adapter.py",
            "scrape_and_index_all.py",
        ]
        
        for file_path_str in critical_files:
            file_path = self.project_root / file_path_str
            
            if not file_path.exists():
                print(f"   ⚠️  {file_path_str} não encontrado (pode estar OK)")
                continue
            
            is_ok, issues = self.check_file(file_path)
            
            if is_ok:
                print(f"   ✅ {file_path_str}")
                self.successes.append(f"✅ {file_path_str} está correto")
            else:
                print(f"   ❌ {file_path_str}")
                for issue in issues:
                    print(f"      {issue}")
                    self.issues.append(f"{file_path_str}: {issue}")
    
    def validate_environment_usage(self) -> None:
        """Verifica se os arquivos usam os.getenv() corretamente"""
        print("\n🔐 Validando uso de variáveis de ambiente...")
        
        python_files = self.project_root.glob("*.py")
        env_patterns = [
            r"os\.getenv\(['\"]MEILISEARCH_KEY['\"]",
            r"os\.getenv\(['\"]MEILISEARCH_URL['\"]",
        ]
        
        for py_file in python_files:
            if py_file.name.startswith("test_"):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Se o arquivo usa Meilisearch, deve usar os.getenv()
                if "meilisearch" in content.lower() or "meilisearch_key" in content.lower():
                    found_getenv = any(re.search(pattern, content) for pattern in env_patterns)
                    
                    if found_getenv:
                        print(f"   ✅ {py_file.name} usa os.getenv()")
                    elif "os.getenv" in content:
                        print(f"   ✅ {py_file.name} usa variáveis de ambiente")
                    else:
                        print(f"   ⚠️  {py_file.name} pode ter chaves hardcoded")
                        self.issues.append(f"{py_file.name} não encontrado os.getenv() para Meilisearch")
            except:
                pass
    
    def run_validation(self) -> bool:
        """Executa todas as validações"""
        print("=" * 80)
        print("VALIDAÇÃO DE CONFIGURAÇÃO MEILISEARCH")
        print("=" * 80)
        
        # Executar validações
        docker_ok = self.validate_docker_compose()
        self.validate_python_files()
        self.validate_environment_usage()
        
        # Resultados
        print("\n" + "=" * 80)
        print("📊 RESULTADOS")
        print("=" * 80)
        
        if self.successes:
            print("\n✅ SUCESSOS:")
            for success in self.successes:
                print(f"   {success}")
        
        if self.issues:
            print("\n❌ PROBLEMAS:")
            for issue in self.issues:
                print(f"   {issue}")
            return False
        else:
            print("\n🎉 TUDO ESTÁ CORRETO!")
            return True
    
    def get_summary(self) -> Dict:
        """Retorna resumo da validação"""
        return {
            "total_issues": len(self.issues),
            "total_successes": len(self.successes),
            "is_valid": len(self.issues) == 0,
            "issues": self.issues,
            "successes": self.successes
        }


if __name__ == "__main__":
    validator = MeilisearchKeyValidator(project_root=".")
    is_valid = validator.run_validation()
    summary = validator.get_summary()
    
    print("\n" + "=" * 80)
    print(f"Status Final: {'✅ VÁLIDO' if is_valid else '❌ INVÁLIDO'}")
    print(f"Total de Sucessos: {summary['total_successes']}")
    print(f"Total de Problemas: {summary['total_issues']}")
    print("=" * 80)
    
    exit(0 if is_valid else 1)
