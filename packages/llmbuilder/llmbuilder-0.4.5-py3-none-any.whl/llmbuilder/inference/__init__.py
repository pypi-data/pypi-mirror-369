"""
Inference and text generation module for LLMBuilder.

This module provides text generation capabilities, interactive CLI,
and various sampling strategies for trained models.
"""

from .cli import InferenceCLI, interactive_cli
from .generate import GenerationConfig, TextGenerator, generate_text

__all__ = [
    # Core generation classes
    "TextGenerator",
    "GenerationConfig",
    "generate_text",
    # Interactive CLI
    "InferenceCLI",
    "interactive_cli",
]
