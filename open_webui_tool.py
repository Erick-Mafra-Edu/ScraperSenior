import requests
from pydantic import BaseModel, Field

class Tools:
    def __init__(self):
        # Usar localhost:8000 como padrão (API local)
        # Para usar people-fy.com:8000, alterar para "http://people-fy.com:8000"
        self.api_url = "http://localhost:8000"
    
    def search_documentation(
        self,
        query: str = Field(..., description="Palavras-chave ou pergunta sobre documentação Senior (ex: 'configurar NTLM', 'como fazer backup', 'guia de implantação')"),
        module: str = Field(None, description="[OPCIONAL] Módulo específico (RH, FINANCEIRO, TECNOLOGIA, BPM, etc). Deixar vazio para buscar em todos."),
        limit: int = Field(10, description="Número de resultados desejados (padrão: 10)")
    ) -> str:
        """
        Busca documentação técnica Senior Sistemas usando a API de busca.
        Retorna documentos com título, módulo, conteúdo e relevância.
        """
        try:
            payload = {
                "query": query,
                "module": module,
                "limit": limit
            }
            response = requests.post(f"{self.api_url}/search", json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get("success") and result.get("results"):
                formatted = f"Encontrados {result['total']} documentos relevantes:\n\n"
                for doc in result["results"][:5]:
                    score = doc.get("score", "N/A")
                    module_name = doc.get("module", "Unknown")
                    title = doc.get("title", "Sem título")
                    preview = doc.get("content_preview", "")[:150]
                    formatted += f"📄 **{title}**\nMódulo: {module_name}\nScore: {score}\nResumo: {preview}...\n\n"
                return formatted
            else:
                return "Nenhum documento encontrado para essa busca. Tente outras palavras-chave."
        except requests.exceptions.RequestException as e:
            return f"Erro ao conectar com a API: {str(e)}"
        except Exception as e:
            return f"Erro ao buscar documentação: {str(e)}"
