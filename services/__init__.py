"""
Services Module
===============

Serviços para processamento de consultas e geração de respostas.
"""

from .model_pipeline import ModelPipeline, generate_grounded_response

__all__ = ["ModelPipeline", "generate_grounded_response"]
