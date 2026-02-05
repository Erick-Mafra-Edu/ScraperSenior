#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hallucination Guard - Verificador de Evidências
================================================

Módulo para verificar se as respostas do modelo estão fundamentadas
nos documentos recuperados. Previne hallucinations ao validar que
cada sentença da resposta tem suporte nas passagens fornecidas.

Autor: Sistema de Validação Senior
Data: 2026-02-05
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Evidence:
    """Representa uma evidência encontrada para uma sentença."""
    sentence: str
    doc_id: str
    passage_text: str
    similarity_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte evidência para dicionário."""
        return {
            "sentence": self.sentence,
            "doc_id": self.doc_id,
            "passage_text": self.passage_text[:200],  # Limitar tamanho
            "score": round(self.similarity_score, 3)
        }


@dataclass
class VerificationIssue:
    """Representa um problema encontrado na verificação."""
    sentence: str
    issue_type: str  # "no_evidence", "low_confidence", "contradictory"
    details: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte issue para dicionário."""
        return {
            "sentence": self.sentence,
            "type": self.issue_type,
            "details": self.details
        }


@dataclass
class VerificationResult:
    """Resultado da verificação de uma resposta."""
    verified: bool
    evidence: List[Evidence] = field(default_factory=list)
    issues: List[VerificationIssue] = field(default_factory=list)
    overall_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultado para dicionário."""
        return {
            "verified": self.verified,
            "evidence": [e.to_dict() for e in self.evidence],
            "issues": [i.to_dict() for i in self.issues],
            "overall_confidence": round(self.overall_confidence, 3)
        }


class HallucinationGuard:
    """
    Verificador de hallucinations em respostas de modelos.
    
    Valida se cada sentença da resposta está suportada pelos
    documentos recuperados usando análise de similaridade.
    """
    
    def __init__(self, threshold: float = 0.75):
        """
        Inicializa o verificador.
        
        Args:
            threshold: Limiar mínimo de similaridade para considerar
                      uma sentença como verificada (0.0 a 1.0)
        """
        self.threshold = threshold
        self._embedding_client = None  # TODO: Integrar com cliente de embeddings
        
    def verify(
        self,
        response: str,
        retrieved_passages: List[Dict[str, str]],
        threshold: Optional[float] = None
    ) -> VerificationResult:
        """
        Verifica se a resposta está fundamentada nas passagens.
        
        Args:
            response: Resposta gerada pelo modelo
            retrieved_passages: Lista de passagens recuperadas
                               Formato: [{"id": "doc_123", "text": "conteúdo..."}, ...]
            threshold: Limiar customizado (opcional)
            
        Returns:
            VerificationResult com evidências e issues encontrados
        """
        threshold = threshold or self.threshold
        
        # Dividir resposta em sentenças
        sentences = self._split_sentences(response)
        
        if not sentences:
            return VerificationResult(
                verified=False,
                issues=[VerificationIssue(
                    sentence="",
                    issue_type="empty_response",
                    details="Resposta vazia ou inválida"
                )]
            )
        
        if not retrieved_passages:
            return VerificationResult(
                verified=False,
                issues=[VerificationIssue(
                    sentence=s,
                    issue_type="no_passages",
                    details="Nenhuma passagem fornecida para verificação"
                ) for s in sentences]
            )
        
        evidence_list = []
        issues_list = []
        verified_count = 0
        total_score = 0.0
        
        # Verificar cada sentença
        for sentence in sentences:
            # Ignorar sentenças muito curtas ou genéricas
            if len(sentence.strip()) < 10:
                continue
                
            best_match, score = self._find_best_match(sentence, retrieved_passages)
            
            if best_match and score >= threshold:
                # Sentença verificada
                evidence_list.append(Evidence(
                    sentence=sentence,
                    doc_id=best_match["id"],
                    passage_text=best_match["text"],
                    similarity_score=score
                ))
                verified_count += 1
                total_score += score
            else:
                # Sentença não verificada
                issue_type = "low_confidence" if best_match else "no_evidence"
                details = f"Score: {score:.2f} (limiar: {threshold})" if best_match else "Nenhuma passagem similar encontrada"
                
                issues_list.append(VerificationIssue(
                    sentence=sentence,
                    issue_type=issue_type,
                    details=details
                ))
        
        # Calcular confiança geral
        total_sentences = len([s for s in sentences if len(s.strip()) >= 10])
        overall_confidence = (verified_count / total_sentences) if total_sentences > 0 else 0.0
        
        # Resultado é verificado se mais de 80% das sentenças foram validadas
        is_verified = overall_confidence >= 0.8
        
        return VerificationResult(
            verified=is_verified,
            evidence=evidence_list,
            issues=issues_list,
            overall_confidence=overall_confidence
        )
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Divide texto em sentenças.
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de sentenças
        """
        # Remover múltiplos espaços e quebras de linha
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Dividir por pontuação de fim de sentença
        # Lida com abreviações comuns (Dr., Sr., etc.)
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        
        return [s.strip() for s in sentences if s.strip()]
    
    def _find_best_match(
        self,
        sentence: str,
        passages: List[Dict[str, str]]
    ) -> Tuple[Optional[Dict[str, str]], float]:
        """
        Encontra a passagem mais similar à sentença.
        
        Args:
            sentence: Sentença a verificar
            passages: Lista de passagens
            
        Returns:
            Tupla (melhor_passagem, score_similaridade)
        """
        if not passages:
            return None, 0.0
        
        # TODO: Integrar com cliente de embeddings real
        # Por enquanto, usa similaridade léxica simples
        best_passage = None
        best_score = 0.0
        
        sentence_lower = sentence.lower()
        sentence_words = set(re.findall(r'\w+', sentence_lower))
        
        for passage in passages:
            passage_text = passage.get("text", "").lower()
            passage_words = set(re.findall(r'\w+', passage_text))
            
            if not sentence_words or not passage_words:
                continue
            
            # Similaridade Jaccard (overlap de palavras)
            intersection = len(sentence_words & passage_words)
            union = len(sentence_words | passage_words)
            jaccard_score = intersection / union if union > 0 else 0.0
            
            # Bonus se a sentença está contida na passagem
            if sentence_lower in passage_text:
                jaccard_score = min(1.0, jaccard_score + 0.3)
            
            # Bonus para correspondência de palavras-chave importantes
            # (palavras com mais de 5 caracteres que não são stopwords comuns)
            important_words = {w for w in sentence_words if len(w) > 5}
            stopwords = {"sobre", "através", "quando", "onde", "porque", "portanto"}
            important_words -= stopwords
            
            if important_words:
                important_match = len(important_words & passage_words) / len(important_words)
                jaccard_score = (jaccard_score + important_match) / 2
            
            if jaccard_score > best_score:
                best_score = jaccard_score
                best_passage = passage
        
        return best_passage, best_score
    
    def set_embedding_client(self, client: Any) -> None:
        """
        Configura cliente de embeddings.
        
        TODO: Implementar quando integrar com provedor de embeddings
        (OpenAI, Cohere, local, etc.)
        
        Args:
            client: Cliente de embeddings
        """
        self._embedding_client = client
    
    def _compute_semantic_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        Calcula similaridade semântica usando embeddings.
        
        TODO: Implementar quando embedding_client estiver disponível
        
        Args:
            text1: Primeiro texto
            text2: Segundo texto
            
        Returns:
            Score de similaridade (0.0 a 1.0)
        """
        if not self._embedding_client:
            # Fallback para similaridade léxica
            return self._compute_lexical_similarity(text1, text2)
        
        # TODO: Implementar com embeddings
        # embedding1 = self._embedding_client.encode(text1)
        # embedding2 = self._embedding_client.encode(text2)
        # return cosine_similarity(embedding1, embedding2)
        
        raise NotImplementedError("Semantic similarity requires embedding client")
    
    def _compute_lexical_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similaridade léxica simples.
        
        Args:
            text1: Primeiro texto
            text2: Segundo texto
            
        Returns:
            Score Jaccard (0.0 a 1.0)
        """
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0


def verify_response(
    response: str,
    retrieved_passages: List[Dict[str, str]],
    threshold: float = 0.75
) -> Dict[str, Any]:
    """
    Função auxiliar para verificar uma resposta rapidamente.
    
    Args:
        response: Resposta do modelo
        retrieved_passages: Lista de passagens
        threshold: Limiar de similaridade
        
    Returns:
        Dicionário com resultado da verificação
    """
    guard = HallucinationGuard(threshold=threshold)
    result = guard.verify(response, retrieved_passages)
    return result.to_dict()


# Funções utilitárias para uso externo

def split_into_sentences(text: str) -> List[str]:
    """
    Utilitário público para dividir texto em sentenças.
    
    Args:
        text: Texto a dividir
        
    Returns:
        Lista de sentenças
    """
    guard = HallucinationGuard()
    return guard._split_sentences(text)


def compute_similarity(text1: str, text2: str) -> float:
    """
    Utilitário público para calcular similaridade entre textos.
    
    Args:
        text1: Primeiro texto
        text2: Segundo texto
        
    Returns:
        Score de similaridade (0.0 a 1.0)
    """
    guard = HallucinationGuard()
    return guard._compute_lexical_similarity(text1, text2)
