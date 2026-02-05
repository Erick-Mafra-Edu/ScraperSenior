#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Pipeline - Pipeline de Geração com Validação
==================================================

Pipeline completo para:
1. Recuperar documentos relevantes (retrieval)
2. Re-ranquear por relevância (rerank)
3. Formatar prompt com template rígido
4. Gerar resposta com modelo (LLM)
5. Validar resposta contra documentos (hallucination guard)
6. Retornar resposta verificada ou mensagem de erro

Autor: Sistema de Validação Senior
Data: 2026-02-05
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

# Importar módulos do projeto
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from libs.validators.hallucination_guard import HallucinationGuard, VerificationResult


@dataclass
class GenerationConfig:
    """Configuração para geração de respostas."""
    temperature: float = 0.1  # Baixa temperatura para respostas mais determinísticas
    top_p: float = 0.8
    max_tokens: int = 1000
    model: str = "gpt-3.5-turbo"  # TODO: Configurar modelo real
    
    
@dataclass
class PipelineResult:
    """Resultado do pipeline completo."""
    success: bool
    response: str
    verification: Optional[Dict[str, Any]] = None
    retrieved_docs: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultado para dicionário."""
        return {
            "success": self.success,
            "response": self.response,
            "verification": self.verification,
            "retrieved_docs": [
                {
                    "id": doc.get("id", ""),
                    "title": doc.get("title", ""),
                    "url": doc.get("url", "")
                }
                for doc in self.retrieved_docs
            ],
            "metadata": self.metadata
        }


class ModelPipeline:
    """
    Pipeline completo de geração e validação de respostas.
    
    Integra retrieval, reranking, geração e validação em um
    fluxo único e robusto.
    """
    
    def __init__(
        self,
        retrieval_client: Optional[Any] = None,
        reranker_client: Optional[Any] = None,
        llm_client: Optional[Any] = None,
        validation_threshold: float = 0.75,
        config: Optional[GenerationConfig] = None
    ):
        """
        Inicializa o pipeline.
        
        Args:
            retrieval_client: Cliente para busca de documentos (Meilisearch, etc.)
            reranker_client: Cliente para reranking (opcional)
            llm_client: Cliente do modelo de linguagem
            validation_threshold: Limiar para validação de respostas
            config: Configuração de geração
        """
        self.retrieval_client = retrieval_client
        self.reranker_client = reranker_client
        self.llm_client = llm_client
        self.hallucination_guard = HallucinationGuard(threshold=validation_threshold)
        self.config = config or GenerationConfig()
        
        # Carregar system prompt
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Carrega o system prompt do arquivo."""
        prompt_path = Path(__file__).parent.parent / "docs" / "prompt_templates" / "grounded_system_prompt.txt"
        
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        else:
            # Fallback para prompt inline
            return """Você é um assistente especializado em documentação técnica Senior.
REGRA FUNDAMENTAL: Apenas use informação das passagens fornecidas.
Se não houver evidência, responda: "Não encontrei evidência nos documentos fornecidos."
Sempre cite as fontes usando [doc_id]."""
    
    async def generate_and_validate(
        self,
        query: str,
        limit: int = 5,
        module_filter: Optional[str] = None
    ) -> PipelineResult:
        """
        Pipeline completo: retrieve -> rerank -> generate -> validate.
        
        Args:
            query: Consulta do usuário
            limit: Número de documentos a recuperar
            module_filter: Filtro opcional por módulo
            
        Returns:
            PipelineResult com resposta validada ou erro
        """
        try:
            # Etapa 1: Retrieve - Buscar documentos relevantes
            retrieved_docs = await self._retrieve_documents(
                query, limit, module_filter
            )
            
            if not retrieved_docs:
                return PipelineResult(
                    success=False,
                    response="Não encontrei evidência nos documentos fornecidos.",
                    retrieved_docs=[],
                    metadata={"stage": "retrieval", "reason": "no_documents_found"}
                )
            
            # Etapa 2: Rerank - Re-ordenar por relevância (opcional)
            if self.reranker_client:
                retrieved_docs = await self._rerank_documents(query, retrieved_docs)
            
            # Etapa 3: Format Prompt - Criar prompt com contexto
            formatted_prompt = self._format_prompt_with_context(query, retrieved_docs)
            
            # Etapa 4: Generate - Chamar modelo para gerar resposta
            response = await self._generate_response(formatted_prompt)
            
            if not response or len(response.strip()) < 10:
                return PipelineResult(
                    success=False,
                    response="Não encontrei evidência nos documentos fornecidos.",
                    retrieved_docs=retrieved_docs,
                    metadata={"stage": "generation", "reason": "empty_response"}
                )
            
            # Etapa 5: Validate - Verificar resposta contra documentos
            passages = [
                {"id": doc.get("id", ""), "text": doc.get("content", "")}
                for doc in retrieved_docs
            ]
            
            verification = self.hallucination_guard.verify(response, passages)
            
            # Etapa 6: Decide - Retornar resposta ou erro
            if verification.verified:
                return PipelineResult(
                    success=True,
                    response=response,
                    verification=verification.to_dict(),
                    retrieved_docs=retrieved_docs,
                    metadata={"stage": "complete", "verified": True}
                )
            else:
                # Resposta não verificada - retornar mensagem padrão
                return PipelineResult(
                    success=False,
                    response="Não encontrei evidência nos documentos fornecidos.",
                    verification=verification.to_dict(),
                    retrieved_docs=retrieved_docs,
                    metadata={
                        "stage": "validation",
                        "reason": "verification_failed",
                        "confidence": verification.overall_confidence
                    }
                )
                
        except Exception as e:
            return PipelineResult(
                success=False,
                response=f"Erro ao processar consulta: {str(e)}",
                metadata={"stage": "error", "error": str(e)}
            )
    
    async def _retrieve_documents(
        self,
        query: str,
        limit: int,
        module_filter: Optional[str]
    ) -> List[Dict[str, str]]:
        """
        Recupera documentos relevantes.
        
        TODO: Integrar com Meilisearch ou índice local
        
        Args:
            query: Consulta
            limit: Número máximo de documentos
            module_filter: Filtro opcional
            
        Returns:
            Lista de documentos
        """
        if not self.retrieval_client:
            # Mock para desenvolvimento/testes
            return self._mock_retrieve_documents(query, limit)
        
        # TODO: Implementar integração real
        # results = await self.retrieval_client.search(
        #     query=query,
        #     limit=limit,
        #     filter={"module": module_filter} if module_filter else None
        # )
        # return results
        
        raise NotImplementedError("Retrieval client integration pending")
    
    def _mock_retrieve_documents(
        self,
        query: str,
        limit: int
    ) -> List[Dict[str, str]]:
        """
        Mock de recuperação de documentos para testes.
        
        Args:
            query: Consulta
            limit: Limite
            
        Returns:
            Lista de documentos mock
        """
        # Documentos fictícios para testes
        return [
            {
                "id": "doc_001",
                "title": "Configuração de Notificações CRM",
                "url": "https://docs.senior.com/crm/notificacoes",
                "module": "CRM",
                "content": "Para configurar notificações no CRM, acesse Configurações > Notificações. Você pode ativar alertas por email e definir regras de notificação."
            },
            {
                "id": "doc_002",
                "title": "Relatórios Automáticos",
                "url": "https://docs.senior.com/crm/relatorios",
                "module": "CRM",
                "content": "Os relatórios podem ser agendados para envio automático diário, semanal ou mensal. Configure no menu Relatórios > Agendamento."
            }
        ][:limit]
    
    async def _rerank_documents(
        self,
        query: str,
        documents: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Re-ordena documentos por relevância.
        
        TODO: Integrar com reranker (Cohere, local, etc.)
        
        Args:
            query: Consulta
            documents: Documentos a re-ordenar
            
        Returns:
            Documentos re-ordenados
        """
        if not self.reranker_client:
            return documents
        
        # TODO: Implementar reranking
        # scores = self.reranker_client.rerank(
        #     query=query,
        #     documents=[doc["content"] for doc in documents]
        # )
        # return sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        
        return documents
    
    def _format_prompt_with_context(
        self,
        query: str,
        documents: List[Dict[str, str]]
    ) -> str:
        """
        Formata o prompt com contexto dos documentos.
        
        Args:
            query: Consulta do usuário
            documents: Documentos recuperados
            
        Returns:
            Prompt formatado
        """
        # Criar contexto com passagens numeradas
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(
                f"[{doc.get('id', f'doc_{i}')}] {doc.get('title', 'Sem título')}\n"
                f"{doc.get('content', '')}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Montar prompt completo
        prompt = f"""**PASSAGENS DE DOCUMENTAÇÃO:**

{context}

**CONSULTA DO USUÁRIO:**
{query}

**INSTRUÇÕES:**
- Responda usando APENAS as informações das passagens acima
- Cite as fontes usando [doc_id]
- Se não houver informação relevante, responda: "Não encontrei evidência nos documentos fornecidos."
"""
        
        return prompt
    
    async def _generate_response(self, prompt: str) -> str:
        """
        Gera resposta usando o modelo.
        
        TODO: Integrar com cliente de LLM (OpenAI, local, etc.)
        
        Args:
            prompt: Prompt formatado
            
        Returns:
            Resposta gerada
        """
        if not self.llm_client:
            # Mock para desenvolvimento/testes
            return self._mock_generate_response(prompt)
        
        # TODO: Implementar integração real
        # response = await self.llm_client.chat.completions.create(
        #     model=self.config.model,
        #     messages=[
        #         {"role": "system", "content": self.system_prompt},
        #         {"role": "user", "content": prompt}
        #     ],
        #     temperature=self.config.temperature,
        #     top_p=self.config.top_p,
        #     max_tokens=self.config.max_tokens
        # )
        # return response.choices[0].message.content
        
        raise NotImplementedError("LLM client integration pending")
    
    def _mock_generate_response(self, prompt: str) -> str:
        """
        Mock de geração de resposta para testes.
        
        Args:
            prompt: Prompt
            
        Returns:
            Resposta mock
        """
        # Resposta genérica que será validada
        return """Para configurar notificações no CRM, acesse Configurações > Notificações [doc_001]. 
Você pode ativar alertas por email e definir regras de notificação [doc_001].

Os relatórios podem ser agendados para envio automático [doc_002].

**Fontes:**
- [doc_001]: Configuração de Notificações CRM
- [doc_002]: Relatórios Automáticos"""


# Função auxiliar para uso direto

async def generate_grounded_response(
    query: str,
    retrieval_client: Optional[Any] = None,
    limit: int = 5,
    validation_threshold: float = 0.75
) -> Dict[str, Any]:
    """
    Função auxiliar para gerar resposta fundamentada.
    
    Args:
        query: Consulta do usuário
        retrieval_client: Cliente de busca (opcional)
        limit: Número de documentos
        validation_threshold: Limiar de validação
        
    Returns:
        Dicionário com resultado
    """
    pipeline = ModelPipeline(
        retrieval_client=retrieval_client,
        validation_threshold=validation_threshold
    )
    
    result = await pipeline.generate_and_validate(query, limit=limit)
    return result.to_dict()
