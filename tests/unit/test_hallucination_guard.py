#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes Unitários - Hallucination Guard
======================================

Testes unitários detalhados para o módulo de validação de respostas.

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
    Evidence,
    VerificationIssue,
    VerificationResult,
    verify_response,
    split_into_sentences,
    compute_similarity
)


class TestEvidence:
    """Testes para a classe Evidence."""
    
    def test_evidence_creation(self):
        """Testa criação de evidência."""
        evidence = Evidence(
            sentence="Teste de sentença",
            doc_id="doc_123",
            passage_text="Texto da passagem",
            similarity_score=0.85
        )
        
        assert evidence.sentence == "Teste de sentença"
        assert evidence.doc_id == "doc_123"
        assert evidence.similarity_score == 0.85
    
    def test_evidence_to_dict(self):
        """Testa conversão de evidência para dicionário."""
        evidence = Evidence(
            sentence="Teste",
            doc_id="doc_456",
            passage_text="A" * 300,  # Texto longo
            similarity_score=0.92
        )
        
        result = evidence.to_dict()
        
        assert isinstance(result, dict)
        assert result["sentence"] == "Teste"
        assert result["doc_id"] == "doc_456"
        assert result["score"] == 0.92
        assert len(result["passage_text"]) <= 200  # Deve truncar


class TestVerificationIssue:
    """Testes para a classe VerificationIssue."""
    
    def test_issue_creation(self):
        """Testa criação de issue."""
        issue = VerificationIssue(
            sentence="Sentença problemática",
            issue_type="no_evidence",
            details="Nenhuma evidência encontrada"
        )
        
        assert issue.sentence == "Sentença problemática"
        assert issue.issue_type == "no_evidence"
        assert issue.details == "Nenhuma evidência encontrada"
    
    def test_issue_to_dict(self):
        """Testa conversão de issue para dicionário."""
        issue = VerificationIssue(
            sentence="Teste",
            issue_type="low_confidence",
            details="Score: 0.5"
        )
        
        result = issue.to_dict()
        
        assert isinstance(result, dict)
        assert result["sentence"] == "Teste"
        assert result["type"] == "low_confidence"
        assert result["details"] == "Score: 0.5"


class TestVerificationResult:
    """Testes para a classe VerificationResult."""
    
    def test_result_creation(self):
        """Testa criação de resultado."""
        result = VerificationResult(
            verified=True,
            evidence=[],
            issues=[],
            overall_confidence=0.9
        )
        
        assert result.verified is True
        assert result.overall_confidence == 0.9
    
    def test_result_to_dict(self):
        """Testa conversão completa para dicionário."""
        evidence = Evidence("sent", "doc_1", "text", 0.8)
        issue = VerificationIssue("sent2", "no_evidence", "details")
        
        result = VerificationResult(
            verified=False,
            evidence=[evidence],
            issues=[issue],
            overall_confidence=0.4
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["verified"] is False
        assert len(result_dict["evidence"]) == 1
        assert len(result_dict["issues"]) == 1
        assert result_dict["overall_confidence"] == 0.4


class TestSentenceSplitting:
    """Testes para divisão de sentenças."""
    
    def test_split_simple_sentences(self):
        """Testa divisão de sentenças simples."""
        text = "Primeira. Segunda. Terceira."
        sentences = split_into_sentences(text)
        
        assert len(sentences) == 3
        assert sentences[0] == "Primeira."
    
    def test_split_with_punctuation(self):
        """Testa divisão com diferentes pontuações."""
        text = "Pergunta? Exclamação! Afirmação."
        sentences = split_into_sentences(text)
        
        assert len(sentences) == 3
    
    def test_split_with_abbreviations(self):
        """Testa que não divide em abreviações."""
        text = "O Sr. Silva trabalha aqui. Ele é gerente."
        sentences = split_into_sentences(text)
        
        # Não deve dividir no "Sr."
        assert len(sentences) == 2
    
    def test_split_multiline(self):
        """Testa divisão com múltiplas linhas."""
        text = """Primeira sentença.
        Segunda sentença.
        Terceira sentença."""
        
        sentences = split_into_sentences(text)
        
        assert len(sentences) == 3
    
    def test_split_empty_text(self):
        """Testa divisão de texto vazio."""
        sentences = split_into_sentences("")
        assert len(sentences) == 0
    
    def test_split_single_sentence(self):
        """Testa com uma única sentença."""
        text = "Uma única sentença sem ponto final"
        sentences = split_into_sentences(text)
        
        assert len(sentences) == 1


class TestSimilarityComputation:
    """Testes para cálculo de similaridade."""
    
    def test_identical_texts(self):
        """Testa similaridade de textos idênticos."""
        text = "Texto idêntico para teste"
        score = compute_similarity(text, text)
        
        assert score == 1.0
    
    def test_similar_texts(self):
        """Testa similaridade de textos similares."""
        text1 = "O sistema permite configurar notificações"
        text2 = "Notificações podem ser configuradas no sistema"
        
        score = compute_similarity(text1, text2)
        
        assert 0.3 < score < 1.0  # Alguma similaridade mas não idêntico
    
    def test_different_texts(self):
        """Testa similaridade de textos diferentes."""
        text1 = "Configuração de relatórios"
        text2 = "Integração com API externa"
        
        score = compute_similarity(text1, text2)
        
        assert score < 0.3  # Baixa similaridade
    
    def test_empty_texts(self):
        """Testa similaridade com textos vazios."""
        score1 = compute_similarity("", "texto")
        score2 = compute_similarity("texto", "")
        score3 = compute_similarity("", "")
        
        assert score1 == 0.0
        assert score2 == 0.0
        assert score3 == 0.0
    
    def test_case_insensitive(self):
        """Testa que similaridade é case-insensitive."""
        text1 = "TEXTO EM MAIÚSCULAS"
        text2 = "texto em minúsculas"
        
        score = compute_similarity(text1, text2)
        
        assert score == 1.0


class TestHallucinationGuardInit:
    """Testes para inicialização do HallucinationGuard."""
    
    def test_default_initialization(self):
        """Testa inicialização com valores padrão."""
        guard = HallucinationGuard()
        
        assert guard.threshold == 0.75
        assert guard._embedding_client is None
    
    def test_custom_threshold(self):
        """Testa inicialização com threshold customizado."""
        guard = HallucinationGuard(threshold=0.85)
        
        assert guard.threshold == 0.85
    
    def test_set_embedding_client(self):
        """Testa configuração de cliente de embeddings."""
        guard = HallucinationGuard()
        mock_client = "mock_embedding_client"
        
        guard.set_embedding_client(mock_client)
        
        assert guard._embedding_client == mock_client


class TestHallucinationGuardVerify:
    """Testes para o método verify."""
    
    def test_verify_with_exact_match(self):
        """Testa verificação com match exato."""
        guard = HallucinationGuard(threshold=0.7)
        
        response = "O sistema permite exportar relatórios em PDF."
        passages = [
            {
                "id": "doc_001",
                "text": "O sistema permite exportar relatórios em formato PDF ou Excel."
            }
        ]
        
        result = guard.verify(response, passages)
        
        assert result.verified is True
        assert len(result.evidence) > 0
        assert result.evidence[0].doc_id == "doc_001"
    
    def test_verify_with_no_match(self):
        """Testa verificação sem match."""
        guard = HallucinationGuard(threshold=0.75)
        
        response = "O sistema integra com blockchain."
        passages = [
            {
                "id": "doc_001",
                "text": "O sistema permite gerar relatórios de vendas."
            }
        ]
        
        result = guard.verify(response, passages)
        
        assert result.verified is False
        assert len(result.issues) > 0
    
    def test_verify_multiple_sentences(self):
        """Testa verificação com múltiplas sentenças."""
        guard = HallucinationGuard(threshold=0.6)
        
        response = """O CRM permite cadastrar clientes.
        Também gera relatórios automáticos.
        E integra com redes sociais."""
        
        passages = [
            {
                "id": "doc_001",
                "text": "O módulo CRM permite o cadastro completo de clientes e prospects."
            },
            {
                "id": "doc_002",
                "text": "Relatórios podem ser gerados automaticamente pelo sistema."
            }
        ]
        
        result = guard.verify(response, passages)
        
        # Primeiras duas sentenças devem ter evidência
        assert len(result.evidence) >= 2
        
        # Terceira sentença deve ter issue
        assert len(result.issues) >= 1
    
    def test_verify_custom_threshold(self):
        """Testa verificação com threshold customizado."""
        guard = HallucinationGuard(threshold=0.75)
        
        response = "Teste de resposta."
        passages = [{"id": "doc_1", "text": "Teste de passagem."}]
        
        # Usar threshold mais baixo
        result = guard.verify(response, passages, threshold=0.5)
        
        # Com threshold mais baixo, pode verificar
        assert isinstance(result, VerificationResult)
    
    def test_verify_empty_response(self):
        """Testa verificação de resposta vazia."""
        guard = HallucinationGuard()
        
        result = guard.verify("", [{"id": "doc", "text": "content"}])
        
        assert result.verified is False
        assert len(result.issues) > 0
        assert result.issues[0].issue_type == "empty_response"
    
    def test_verify_no_passages(self):
        """Testa verificação sem passagens."""
        guard = HallucinationGuard()
        
        result = guard.verify("Alguma resposta.", [])
        
        assert result.verified is False
        assert len(result.issues) > 0
    
    def test_verify_short_sentences_ignored(self):
        """Testa que sentenças muito curtas são ignoradas."""
        guard = HallucinationGuard()
        
        response = "Sim. Não. Ok."  # Sentenças muito curtas
        passages = [{"id": "doc", "text": "Conteúdo da passagem"}]
        
        result = guard.verify(response, passages)
        
        # Sentenças curtas devem ser ignoradas
        assert len(result.evidence) == 0 or len(result.issues) == 0


class TestHallucinationGuardFindBestMatch:
    """Testes para o método _find_best_match."""
    
    def test_find_best_match_exact(self):
        """Testa busca de melhor match com texto exato."""
        guard = HallucinationGuard()
        
        sentence = "O sistema permite exportar relatórios."
        passages = [
            {"id": "doc_1", "text": "Outras funcionalidades."},
            {"id": "doc_2", "text": "O sistema permite exportar relatórios em PDF."},
            {"id": "doc_3", "text": "Configurações gerais."}
        ]
        
        best_passage, score = guard._find_best_match(sentence, passages)
        
        assert best_passage is not None
        assert best_passage["id"] == "doc_2"
        assert score > 0.7
    
    def test_find_best_match_no_passages(self):
        """Testa busca sem passagens."""
        guard = HallucinationGuard()
        
        best_passage, score = guard._find_best_match("sentence", [])
        
        assert best_passage is None
        assert score == 0.0
    
    def test_find_best_match_similarity_ranking(self):
        """Testa que retorna a passagem mais similar."""
        guard = HallucinationGuard()
        
        sentence = "configurar notificações automáticas"
        passages = [
            {"id": "doc_1", "text": "Documentação sobre relatórios"},
            {"id": "doc_2", "text": "Como configurar alertas e notificações automáticas no sistema"},
            {"id": "doc_3", "text": "Integração com APIs externas"}
        ]
        
        best_passage, score = guard._find_best_match(sentence, passages)
        
        assert best_passage["id"] == "doc_2"


class TestVerifyResponseFunction:
    """Testes para a função auxiliar verify_response."""
    
    def test_verify_response_basic(self):
        """Testa função verify_response básica."""
        response = "Teste de resposta."
        passages = [{"id": "doc_1", "text": "Teste de passagem com resposta"}]
        
        result = verify_response(response, passages, threshold=0.5)
        
        assert isinstance(result, dict)
        assert "verified" in result
        assert "evidence" in result
        assert "issues" in result
        assert "overall_confidence" in result
    
    def test_verify_response_returns_dict(self):
        """Testa que verify_response sempre retorna dicionário."""
        result = verify_response("", [], threshold=0.75)
        
        assert isinstance(result, dict)
        assert result["verified"] is False


# Configuração pytest
@pytest.fixture
def guard_instance():
    """Fixture que fornece uma instância do HallucinationGuard."""
    return HallucinationGuard(threshold=0.75)


@pytest.fixture
def sample_passages():
    """Fixture com passagens de exemplo."""
    return [
        {
            "id": "doc_crm_001",
            "text": "O módulo CRM da Senior permite gerenciar clientes, contatos e oportunidades de vendas. Configure notificações automáticas no menu Configurações."
        },
        {
            "id": "doc_reports_001",
            "text": "Relatórios podem ser gerados em diversos formatos: PDF, Excel e CSV. Acesse o menu Relatórios para visualizar e exportar."
        },
        {
            "id": "doc_api_001",
            "text": "A API REST permite integração com sistemas externos. Utilize as chaves de autenticação fornecidas no painel administrativo."
        }
    ]


if __name__ == "__main__":
    # Executar testes diretamente
    pytest.main([__file__, "-v", "--tb=short"])
