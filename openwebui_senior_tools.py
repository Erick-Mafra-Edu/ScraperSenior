"""
Senior Documentation API Client para Open WebUI
Compatível com os novos endpoints REST do MCP HTTP Server
"""

import httpx
from typing import Optional, List, Dict, Any
from urllib.parse import quote


class Tools:
    def __init__(self):
        """
        Inicializa o cliente de API para a documentação Senior.
        Use 'host.docker.internal:8000' quando executar dentro de um container Docker.
        Use 'localhost:8000' para testes locais.
        """
        # Para containers Docker, use host.docker.internal
        self.base_url = "http://host.docker.internal:8000"
        self.timeout = 15.0

    async def consultar_documentacao_senior(
        self, 
        termo: str, 
        modulo: Optional[str] = None,
        strategy: str = "auto",
        limite: int = 5
    ) -> str:
        """
        Busca informações na documentação Senior com parsing inteligente de query.
        
        Use para: LSP (Linguagem Senior de Programação), regras de negócio, 
        configurações, manuais técnicos, etc.
        
        Args:
            termo: O termo ou frase para pesquisar (ex: "configurar LSP", "implantação")
            modulo: Opcional - filtrar por módulo específico (ex: "Help Center", "Release Notes")
            strategy: Estratégia de parsing ('auto' recomendado, 'quoted', 'and')
            limite: Máximo de resultados (padrão: 5, máximo: 100)
            
        Returns:
            String formatada com resultados da busca
        """
        url = f"{self.base_url}/api/search"
        
        try:
            async with httpx.AsyncClient() as client:
                # GET /api/search?query=...&limit=5&module=...&strategy=auto
                params = {
                    "query": termo,
                    "limit": min(limite, 100),  # Max 100
                    "strategy": strategy
                }
                if modulo:
                    params["module"] = modulo
                
                response = await client.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") != "success":
                    return f"❌ Erro na busca: {data.get('error', 'Erro desconhecido')}"
                
                count = data.get("count", 0)
                if count == 0:
                    return f"⚠️ Nenhum resultado encontrado para **'{termo}'**.\n\n_Dica: Tente simplificar seu termo ou use palavras-chave diferentes._"
                
                parsed_query = data.get("parsed_query", termo)
                strategy_used = data.get("strategy", "auto")
                
                output = f"### 📚 Resultados para: **'{termo}'**\n"
                output += f"_Encontrados: {count} documento(s) | Estratégia: {strategy_used}_\n\n"
                
                results = data.get("results", [])
                for i, doc in enumerate(results, 1):
                    title = doc.get("title", "Sem título")
                    module = doc.get("module", "Sem módulo")
                    url_doc = doc.get("url", "")
                    content = doc.get("content", doc.get("summary", ""))
                    
                    output += f"**{i}. {title}**\n"
                    output += f"   📁 Módulo: _{module}_\n"
                    if content:
                        # Truncar conteúdo a 150 caracteres
                        preview = content[:150] + "..." if len(content) > 150 else content
                        output += f"   💬 {preview}\n"
                    if url_doc:
                        output += f"   🔗 [Abrir Documento]({url_doc})\n"
                    output += "\n"
                
                return output
                
        except httpx.HTTPStatusError as e:
            return f"❌ Erro HTTP {e.response.status_code}: {str(e)}"
        except Exception as e:
            return f"❌ Erro ao acessar a API: {str(e)}"

    async def consultar_modulo_especifico(
        self,
        nome_modulo: str,
        limite: int = 20
    ) -> str:
        """
        Retorna todos os documentos de um módulo específico.
        
        Use para: explorar um módulo, listar documentos disponíveis em uma categoria
        
        Args:
            nome_modulo: Nome do módulo (ex: "Help Center", "Release Notes")
            limite: Máximo de documentos a retornar (padrão: 20, máximo: 100)
            
        Returns:
            String formatada com lista de documentos do módulo
        """
        url = f"{self.base_url}/api/modules/{quote(nome_modulo)}"
        
        try:
            async with httpx.AsyncClient() as client:
                params = {"limit": min(limite, 100)}
                response = await client.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") != "success":
                    return f"❌ Erro ao buscar módulo: {data.get('error', 'Módulo não encontrado')}"
                
                count = data.get("count", 0)
                module = data.get("module", nome_modulo)
                
                output = f"### 📂 Documentos do Módulo: **{module}**\n"
                output += f"_Total: {count} documento(s)_\n\n"
                
                if count == 0:
                    output += "Nenhum documento encontrado neste módulo."
                    return output
                
                docs = data.get("docs", [])
                for i, doc in enumerate(docs, 1):
                    title = doc.get("title", "Sem título")
                    url_doc = doc.get("url", "")
                    summary = doc.get("summary", doc.get("content", ""))
                    
                    output += f"**{i}. {title}**\n"
                    if summary:
                        preview = summary[:120] + "..." if len(summary) > 120 else summary
                        output += f"   {preview}\n"
                    if url_doc:
                        output += f"   🔗 [Abrir]({url_doc})\n"
                    output += "\n"
                
                return output
                
        except httpx.HTTPStatusError as e:
            return f"❌ Erro HTTP {e.response.status_code}: {str(e)}"
        except Exception as e:
            return f"❌ Erro ao acessar a API: {str(e)}"

    async def listar_todos_modulos(self) -> str:
        """
        Lista todos os módulos de documentação disponíveis.
        
        Use para: descobrir quais módulos existem, ajudar o usuário a escolher
        
        Returns:
            String formatada com lista de módulos
        """
        url = f"{self.base_url}/api/modules"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") != "success":
                    return f"❌ Erro ao listar módulos: {data.get('error', 'Erro desconhecido')}"
                
                total = data.get("total_modules", 0)
                modules = data.get("modules", [])
                
                output = f"### 📚 Módulos de Documentação Disponíveis\n"
                output += f"_Total: {total} módulo(s)_\n\n"
                
                if not modules:
                    output += "Nenhum módulo encontrado."
                    return output
                
                for i, module in enumerate(modules, 1):
                    output += f"{i}. **{module}**\n"
                
                return output
                
        except httpx.HTTPStatusError as e:
            return f"❌ Erro HTTP {e.response.status_code}: {str(e)}"
        except Exception as e:
            return f"❌ Erro ao acessar a API: {str(e)}"

    async def obter_estatisticas_base(self) -> str:
        """
        Retorna estatísticas gerais da base de documentação.
        
        Use para: entender o escopo da documentação, informar ao usuário
        sobre a base disponível
        
        Returns:
            String formatada com estatísticas
        """
        url = f"{self.base_url}/api/stats"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") != "success":
                    return f"❌ Erro ao obter estatísticas: {data.get('error', 'Erro desconhecido')}"
                
                stats = data.get("data", {})
                total_docs = stats.get("total_documents", "N/A")
                total_modules = stats.get("total_modules", "N/A")
                indexed_date = stats.get("indexed_date", "N/A")
                index_size = stats.get("index_size", "N/A")
                
                output = "### 📊 Estatísticas da Base de Documentação\n\n"
                output += f"📄 **Total de Documentos:** {total_docs}\n"
                output += f"📁 **Total de Módulos:** {total_modules}\n"
                output += f"📅 **Data da Indexação:** {indexed_date}\n"
                output += f"💾 **Tamanho do Índice:** {index_size}\n"
                
                return output
                
        except httpx.HTTPStatusError as e:
            return f"❌ Erro HTTP {e.response.status_code}: {str(e)}"
        except Exception as e:
            return f"❌ Erro ao acessar a API: {str(e)}"

    async def recuperar_documento_completo(
        self,
        documento_id: str
    ) -> str:
        """
        Recupera o conteúdo completo de um documento específico.
        
        Use quando: o LLM quer mais detalhes após uma busca inicial, 
        precisa do documento inteiro para responder melhor
        
        Args:
            documento_id: ID único do documento (obtido de resultados de busca)
            
        Returns:
            String com conteúdo completo do documento
        """
        url = f"{self.base_url}/api/document/{quote(documento_id)}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") != "success":
                    return f"❌ Erro ao recuperar documento: {data.get('error', 'Documento não encontrado')}"
                
                doc = data.get("document", {})
                title = doc.get("title", "Sem título")
                module = doc.get("module", "Sem módulo")
                content = doc.get("content", "")
                url_doc = doc.get("url", "")
                
                output = f"# {title}\n\n"
                output += f"_📁 Módulo: {module}_\n"
                if url_doc:
                    output += f"_🔗 [Link Original]({url_doc})_\n"
                output += "\n---\n\n"
                output += content
                
                return output
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"❌ Documento '{documento_id}' não encontrado"
            return f"❌ Erro HTTP {e.response.status_code}: {str(e)}"
        except Exception as e:
            return f"❌ Erro ao acessar a API: {str(e)}"


# ============================================================================
# Exemplos de uso para Open WebUI
# ============================================================================

if __name__ == "__main__":
    import asyncio
    import sys
    
    # Fix encoding para Windows
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    
    async def main():
        tools = Tools()
        
        print("=" * 70)
        print("TESTE DOS ENDPOINTS REST DO MCP SERVER")
        print("=" * 70)
        
        # Teste 1: Buscar por termo
        print("\n[1] Buscando 'LSP'...")
        result = await tools.consultar_documentacao_senior("LSP", limite=3)
        print(result)
        
        # Teste 2: Listar módulos
        print("\n[2] Listando módulos...")
        result = await tools.listar_todos_modulos()
        print(result)
        
        # Teste 3: Estatísticas
        print("\n[3] Estatísticas da base...")
        result = await tools.obter_estatisticas_base()
        print(result)
        
        # Teste 4: Documentos de módulo
        print("\n[4] Documentos do Help Center...")
        result = await tools.consultar_modulo_especifico("Help Center", limite=5)
        print(result)
    
    asyncio.run(main())
