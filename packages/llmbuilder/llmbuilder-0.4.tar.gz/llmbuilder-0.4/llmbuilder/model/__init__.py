"""
Model building and management module for LLMBuilder.

This module provides comprehensive model building, loading, saving,
and management capabilities for GPT-style transformer models.
"""

from .builder import ModelBuilder, build_model, load_model, save_model, validate_model
from .gpt import MLP, GPTModel, GPTModelMetadata, MultiHeadAttention, TransformerBlock

__all__ = [
    # GPT Model components
    "GPTModel",
    "GPTModelMetadata",
    "MultiHeadAttention",
    "MLP",
    "TransformerBlock",
    # Model builder and management
    "ModelBuilder",
    "build_model",
    "load_model",
    "save_model",
    "validate_model",
]
