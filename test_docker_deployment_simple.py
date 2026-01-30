"""
Docker Deployment Test - Simplified Version

Tests Docker deployment and validates document indexing.
"""

import asyncio
import json
import subprocess
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DockerDeploymentTest:
    """Tests Docker deployment and indexing"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "status": "pending"
            }
        }
        self.meilisearch_url = "http://localhost:7700"
        self.meilisearch_key = "meilisearch_master_key_change_me"
    
    def run_command(self, command: str) -> Dict[str, Any]:
        """Run command and return result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Timeout",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def add_test_result(self, test_name: str, passed: bool, details: Dict[str, Any]):
        """Add test result"""
        self.results["tests"].append({
            "name": test_name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })
        
        if passed:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
        
        self.results["summary"]["total"] += 1
    
    async def test_docker_build(self) -> bool:
        """Test docker build"""
        print("[1/8] Testing Docker build...")
        
        result = self.run_command("docker-compose -f docker-compose.yml build --no-cache")
        
        if result["success"]:
            self.add_test_result("Docker build", True, {"message": "Build completed"})
            print("  [OK] Docker build completed")
            return True
        else:
            self.add_test_result("Docker build", False, {"error": result["stderr"][:200]})
            print(f"  [FAIL] Build error: {result['stderr'][:100]}")
            return False
    
    async def test_docker_up(self) -> bool:
        """Test docker-compose up"""
        print("[2/8] Starting Docker containers...")
        
        result = self.run_command("docker-compose -f docker-compose.yml up -d")
        
        if result["success"]:
            self.add_test_result("Docker up", True, {"message": "Containers started"})
            print("  [OK] Containers started")
            time.sleep(5)
            return True
        else:
            self.add_test_result("Docker up", False, {"error": result["stderr"][:200]})
            print(f"  [FAIL] Start error: {result['stderr'][:100]}")
            return False
    
    async def test_meilisearch_health(self) -> bool:
        """Test Meilisearch health"""
        print("[3/8] Checking Meilisearch health...")
        
        try:
            response = requests.get(f"{self.meilisearch_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.add_test_result("Meilisearch health", True, {"status": data.get("status")})
                print(f"  [OK] Meilisearch healthy")
                return True
            else:
                self.add_test_result("Meilisearch health", False, {"status": response.status_code})
                print(f"  [FAIL] Status: {response.status_code}")
                return False
        
        except Exception as e:
            self.add_test_result("Meilisearch health", False, {"error": str(e)})
            print(f"  [FAIL] Error: {str(e)}")
            return False
    
    async def test_indexes_list(self) -> bool:
        """List all indexes"""
        print("[4/8] Listing indexes...")
        
        try:
            headers = {"Authorization": f"Bearer {self.meilisearch_key}"}
            response = requests.get(f"{self.meilisearch_url}/indexes", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                indexes = data.get("results", [])
                index_names = [idx.get("uid") for idx in indexes]
                
                self.add_test_result("List indexes", True, {
                    "count": len(indexes),
                    "indexes": index_names
                })
                
                print(f"  [OK] Found {len(indexes)} indexes")
                for name in index_names:
                    print(f"    - {name}")
                
                return len(indexes) > 0
            else:
                self.add_test_result("List indexes", False, {"status": response.status_code})
                print(f"  [FAIL] Status: {response.status_code}")
                return False
        
        except Exception as e:
            self.add_test_result("List indexes", False, {"error": str(e)})
            print(f"  [FAIL] Error: {str(e)}")
            return False
    
    async def test_documentation_index(self) -> bool:
        """Test documentation index"""
        print("[5/8] Checking documentation index...")
        
        try:
            headers = {"Authorization": f"Bearer {self.meilisearch_key}"}
            response = requests.get(
                f"{self.meilisearch_url}/indexes/documentation",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                doc_count = data.get("numberOfDocuments", 0)
                fields = data.get("fieldsDistribution", {})
                
                self.add_test_result("Documentation index", True, {
                    "documents": doc_count,
                    "fields": list(fields.keys())
                })
                
                print(f"  [OK] Documentation index found")
                print(f"    - Documents: {doc_count}")
                print(f"    - Fields: {len(fields)}")
                
                return doc_count > 0
            else:
                self.add_test_result("Documentation index", False, {"status": response.status_code})
                print(f"  [FAIL] Index not found: {response.status_code}")
                return False
        
        except Exception as e:
            self.add_test_result("Documentation index", False, {"error": str(e)})
            print(f"  [FAIL] Error: {str(e)}")
            return False
    
    async def test_search_query(self) -> bool:
        """Test search"""
        print("[6/8] Testing search query...")
        
        try:
            headers = {"Authorization": f"Bearer {self.meilisearch_key}"}
            
            query = {"q": "documento", "limit": 10}
            response = requests.post(
                f"{self.meilisearch_url}/indexes/documentation/search",
                json=query,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("hits", [])
                
                self.add_test_result("Search query", True, {
                    "query": "documento",
                    "results": len(results),
                    "time_ms": data.get("processingTimeMs", 0)
                })
                
                print(f"  [OK] Search executed")
                print(f"    - Query: 'documento'")
                print(f"    - Results: {len(results)}")
                print(f"    - Time: {data.get('processingTimeMs', 0)}ms")
                
                return True
            else:
                self.add_test_result("Search query", False, {"status": response.status_code})
                print(f"  [FAIL] Status: {response.status_code}")
                return False
        
        except Exception as e:
            self.add_test_result("Search query", False, {"error": str(e)})
            print(f"  [FAIL] Error: {str(e)}")
            return False
    
    async def test_containers_running(self) -> bool:
        """Check containers status"""
        print("[7/8] Checking containers...")
        
        result = self.run_command("docker-compose -f docker-compose.yml ps")
        
        if result["success"]:
            lines = result["stdout"].split("\n")
            running = sum(1 for line in lines if "Up" in line)
            
            self.add_test_result("Containers running", running >= 1, {
                "running": running,
                "output": result["stdout"][:500]
            })
            
            print(f"  [OK] {running} container(s) running")
            
            return running >= 1
        else:
            self.add_test_result("Containers running", False, {"error": result["stderr"][:200]})
            print(f"  [FAIL] Error: {result['stderr'][:100]}")
            return False
    
    async def test_logs(self) -> bool:
        """Collect logs"""
        print("[8/8] Collecting logs...")
        
        result = self.run_command("docker-compose -f docker-compose.yml logs --tail 50")
        
        if result["success"]:
            stdout = result["stdout"]
            has_errors = "error" in stdout.lower() or "failed" in stdout.lower()
            
            self.add_test_result("Container logs", not has_errors, {
                "lines": len(stdout.split("\n")),
                "has_errors": has_errors
            })
            
            print(f"  [OK] Logs collected ({len(stdout.split(chr(10)))} lines)")
            
            return True
        else:
            self.add_test_result("Container logs", False, {"error": result["stderr"][:200]})
            print(f"  [FAIL] Error: {result['stderr'][:100]}")
            return False
    
    async def cleanup(self):
        """Cleanup containers"""
        print("\n[CLEANUP] Stopping containers...")
        
        result = self.run_command("docker-compose -f docker-compose.yml down")
        
        if result["success"]:
            print("  [OK] Containers stopped")
        else:
            print(f"  [FAIL] Error: {result['stderr'][:100]}")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        print("\n" + "="*70)
        print("DOCKER DEPLOYMENT TEST SUITE")
        print("="*70)
        
        try:
            tests = [
                self.test_docker_build,
                self.test_docker_up,
                self.test_meilisearch_health,
                self.test_indexes_list,
                self.test_documentation_index,
                self.test_search_query,
                self.test_containers_running,
                self.test_logs,
            ]
            
            for test in tests:
                try:
                    await test()
                except Exception as e:
                    print(f"  [ERROR] {test.__name__}: {str(e)}")
        
        finally:
            await self.cleanup()
        
        self.results["summary"]["status"] = "completed"
        
        return self.results
    
    def save_report(self, filepath: str):
        """Save report to JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\nReport saved: {filepath}")
    
    def print_summary(self):
        """Print summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        summary = self.results["summary"]
        
        print(f"\nTotal tests: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        
        if summary['total'] > 0:
            rate = (summary['passed']/summary['total']*100)
            print(f"Success rate: {rate:.1f}%")
        
        print("\nTest details:")
        for test in self.results["tests"]:
            status = "[OK]" if test["passed"] else "[FAIL]"
            print(f"  {status} {test['name']}")


async def main():
    """Main"""
    tester = DockerDeploymentTest()
    results = await tester.run_all_tests()
    tester.save_report("docker_deployment_test.json")
    tester.print_summary()
    
    print("\n" + "="*70)
    if results["summary"]["passed"] == results["summary"]["total"]:
        print("SUCCESS: All tests passed!")
    else:
        print(f"WARNING: {results['summary']['failed']} test(s) failed")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
