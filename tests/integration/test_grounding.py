#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes de Integração - Grounding e Validação de Respostas
==========================================================

Testes end-to-end para o sistema de validação de respostas e
prevenção de hallucinations.

Autor: Sistema de Validação Senior
Data: 2026-02-05
"""

import pytest
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from libs.validators.hallucination_guard import (
    HallucinationGuard,
    verify_response,
    split_into_sentences,
    compute_similarity
)
from services.model_pipeline import ModelPipeline, GenerationConfig


class TestHallucinationGuard:
    """Testes para o HallucinationGuard."""
    
    def test_sentence_splitting(self):
        """Testa divisão de texto em sentenças."""
        text = "Primeira sentença. Segunda sentença! Terceira sentença?"
        sentences = split_into_sentences(text)
        
        assert len(sentences) == 3
        assert sentences[0] == "Primeira sentença."
        assert sentences[1] == "Segunda sentença!"
        assert sentences[2] == "Terceira sentença?"
    
    def test_similarity_computation(self):
        """Testa cálculo de similaridade léxica."""
        text1 = "O CRM permite configurar notificações automáticas"
        text2 = "Configurar notificações no CRM é possível automaticamente"
        
        score = compute_similarity(text1, text2)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.3  # Deve ter alguma similaridade
    
    def test_verify_response_with_evidence(self):
        """Testa verificação de resposta com evidência clara."""
        guard = HallucinationGuard(threshold=0.6)
        
        response = "O CRM Senior permite configurar notificações por email."
        
        passages = [
            {
                "id": "doc_123",
                "text": "O módulo CRM da Senior oferece configuração de notificações por email e SMS. Acesse o menu Configurações para ativar."
            }
        ]
        
        result = guard.verify(response, passages)
        
        assert result.verified is True
        assert len(result.evidence) > 0
        assert result.evidence[0].doc_id == "doc_123"
        assert result.overall_confidence > 0.6
    
    def test_verify_response_without_evidence(self):
        """Testa verificação de resposta sem evidência."""
        guard = HallucinationGuard(threshold=0.75)
        
        response = "O CRM integra diretamente com o Salesforce."
        
        passages = [
            {
                "id": "doc_123",
                "text": "O módulo CRM da Senior oferece configuração de notificações por email."
            }
        ]
        
        result = guard.verify(response, passages)
        
        assert result.verified is False
        assert len(result.issues) > 0
        assert result.issues[0].issue_type in ["no_evidence", "low_confidence"]
    
    def test_verify_response_empty(self):
        """Testa verificação de resposta vazia."""
        guard = HallucinationGuard()
        
        result = guard.verify("", [{"id": "doc_1", "text": "content"}])
        
        assert result.verified is False
        assert len(result.issues) > 0
        assert result.issues[0].issue_type == "empty_response"
    
    def test_verify_response_no_passages(self):
        """Testa verificação sem passagens fornecidas."""
        guard = HallucinationGuard()
        
        response = "Alguma resposta aqui."
        result = guard.verify(response, [])
        
        assert result.verified is False
        assert len(result.issues) > 0
        assert "no_passages" in result.issues[0].issue_type
    
    def test_verify_response_partial_evidence(self):
        """Testa resposta com evidência parcial."""
        guard = HallucinationGuard(threshold=0.6)
        
        response = """O CRM permite configurar notificações automáticas.
        Também integra com sistemas externos via API REST."""
        
        passages = [
            {
                "id": "doc_123",
                "text": "O CRM permite configurar notificações automáticas por email, SMS e push."
            }
        ]
        
        result = guard.verify(response, passages)
        
        # Primeira sentença deve ter evidência, segunda não
        assert len(result.evidence) >= 1
        assert result.evidence[0].doc_id == "doc_123"
        
        # Deve ter pelo menos um issue para a segunda sentença
        assert len(result.issues) >= 1
    
    def test_verify_response_function(self):
        """Testa função auxiliar verify_response."""
        response = "Configurar notificações é simples."
        passages = [
            {
                "id": "doc_456",
                "text": "A configuração de notificações no sistema é um processo simples e rápido."
            }
        ]
        
        result_dict = verify_response(response, passages, threshold=0.5)
        
        assert isinstance(result_dict, dict)
        assert "verified" in result_dict
        assert "evidence" in result_dict
        assert "issues" in result_dict
        assert "overall_confidence" in result_dict


class TestModelPipeline:
    """Testes para o ModelPipeline."""
    
    @pytest.mark.asyncio
    async def test_pipeline_with_mock_data(self):
        """Testa pipeline completo com dados mock."""
        pipeline = ModelPipeline(validation_threshold=0.7)
        
        # Pipeline usa mocks internos quando não há clients configurados
        result = await pipeline.generate_and_validate(
            query="Como configurar notificações no CRM?",
            limit=5
        )
        
        assert result.success in [True, False]  # Depende da validação
        assert result.response is not None
        assert len(result.response) > 0
        
        # Se houver documentos, deve haver retrieved_docs
        if result.retrieved_docs:
            assert len(result.retrieved_docs) > 0
            assert "id" in result.retrieved_docs[0]
    
    @pytest.mark.asyncio
    async def test_pipeline_no_documents_found(self):
        """Testa pipeline quando nenhum documento é encontrado."""
        pipeline = ModelPipeline(validation_threshold=0.75)
        
        # Forçar retrieval vazio
        pipeline._mock_retrieve_documents = lambda q, l: []
        
        result = await pipeline.generate_and_validate(
            query="Query sem resultados",
            limit=5
        )
        
        assert result.success is False
        assert result.response == "Não encontrei evidência nos documentos fornecidos."
        assert len(result.retrieved_docs) == 0
        assert result.metadata["stage"] == "retrieval"
    
    @pytest.mark.asyncio
    async def test_pipeline_format_prompt(self):
        """Testa formatação de prompt com contexto."""
        pipeline = ModelPipeline()
        
        query = "Como configurar?"
        documents = [
            {
                "id": "doc_123",
                "title": "Configuração Básica",
                "content": "Para configurar, acesse o menu Configurações."
            }
        ]
        
        prompt = pipeline._format_prompt_with_context(query, documents)
        
        assert "doc_123" in prompt
        assert "Configuração Básica" in prompt
        assert query in prompt
        assert "PASSAGENS" in prompt or "passagens" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_pipeline_with_module_filter(self):
        """Testa pipeline com filtro de módulo."""
        pipeline = ModelPipeline()
        
        result = await pipeline.generate_and_validate(
            query="Como gerar relatórios?",
            limit=3,
            module_filter="Help Center"
        )
        
        # Deve processar sem erros
        assert result is not None
        assert hasattr(result, "success")
        assert hasattr(result, "response")


class TestGroundingEndToEnd:
    """Testes end-to-end do sistema de grounding."""
    
    @pytest.mark.asyncio
    async def test_complete_flow_verified_response(self):
        """
        Teste completo: consulta com documento conhecido deve retornar
        resposta verificada.
        """
        # Setup
        pipeline = ModelPipeline(validation_threshold=0.6)
        
        # Mock com documento específico
        def mock_retrieve(query, limit):
            return [
                {
                    "id": "doc_crm_001",
                    "title": "Configuração de Notificações CRM",
                    "url": "https://docs.senior.com/crm/notificacoes",
                    "module": "CRM",
                    "content": "Para configurar notificações no CRM, acesse o menu Configurações > Notificações. Você pode ativar alertas por email e definir regras de notificação automática."
                }
            ]
        
        pipeline._mock_retrieve_documents = mock_retrieve
        
        # Execute
        result = await pipeline.generate_and_validate(
            query="Como configurar notificações no CRM?",
            limit=5
        )
        
        # Assert
        assert result.success is True, "Pipeline deve retornar success=True"
        assert result.verification is not None, "Deve ter informações de verificação"
        assert result.verification["verified"] is True, "Resposta deve ser verificada"
        
        # Verificar que inclui o doc_id esperado
        evidence_docs = [e["doc_id"] for e in result.verification["evidence"]]
        assert "doc_crm_001" in evidence_docs, "Deve incluir doc_id do documento recuperado"
        
        # Verificar que há documentos recuperados
        assert len(result.retrieved_docs) > 0
        assert result.retrieved_docs[0]["id"] == "doc_crm_001"
    
    @pytest.mark.asyncio
    async def test_complete_flow_no_evidence(self):
        """
        Teste completo: consulta sem evidência deve retornar a mensagem
        exata "Não encontrei evidência nos documentos fornecidos."
        """
        # Setup
        pipeline = ModelPipeline(validation_threshold=0.75)
        
        # Mock com documento não relacionado
        def mock_retrieve(query, limit):
            return [
                {
                    "id": "doc_unrelated",
                    "title": "Documento Não Relacionado",
                    "url": "https://docs.senior.com/other",
                    "module": "Other",
                    "content": "Este documento fala sobre um tópico completamente diferente que não tem relação com a consulta."
                }
            ]
        
        # Mock de resposta que não pode ser verificada
        async def mock_generate(prompt):
            return "O sistema permite integração com múltiplos fornecedores externos de terceiros."
        
        pipeline._mock_retrieve_documents = mock_retrieve
        pipeline._generate_response = mock_generate
        
        # Execute
        result = await pipeline.generate_and_validate(
            query="Como integrar com Salesforce?",
            limit=5
        )
        
        # Assert - Deve retornar a mensagem exata
        assert result.success is False, "Pipeline deve retornar success=False"
        assert result.response == "Não encontrei evidência nos documentos fornecidos.", \
            "Deve retornar a mensagem exata quando não há evidência"
        
        # Verificar metadados
        assert result.metadata is not None
        assert "verified" in result.metadata or "reason" in result.metadata
    
    @pytest.mark.asyncio
    async def test_generation_config_respected(self):
        """Testa que a configuração de geração é respeitada."""
        config = GenerationConfig(
            temperature=0.05,
            top_p=0.9,
            max_tokens=500,
            model="custom-model"
        )
        
        pipeline = ModelPipeline(config=config)
        
        assert pipeline.config.temperature == 0.05
        assert pipeline.config.top_p == 0.9
        assert pipeline.config.max_tokens == 500
        assert pipeline.config.model == "custom-model"
    
    def test_system_prompt_loaded(self):
        """Testa que o system prompt é carregado corretamente."""
        pipeline = ModelPipeline()
        
        assert pipeline.system_prompt is not None
        assert len(pipeline.system_prompt) > 100
        
        # Verificar que contém instruções-chave
        prompt_lower = pipeline.system_prompt.lower()
        assert "evidência" in prompt_lower or "evidence" in prompt_lower
        assert "documento" in prompt_lower or "document" in prompt_lower


# Configuração pytest
@pytest.fixture(scope="session")
def pipeline_instance():
    """Fixture que fornece uma instância do pipeline para testes."""
    return ModelPipeline(validation_threshold=0.7)


if __name__ == "__main__":
    # Executar testes diretamente
    pytest.main([__file__, "-v", "--tb=short"])
