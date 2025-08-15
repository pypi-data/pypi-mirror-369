"""
Fine-tuning module for LLMBuilder.

This module provides comprehensive fine-tuning capabilities including
the FineTuner class, LoRA adaptation, and optimizations for small datasets.
"""

from .finetune import (
    FineTuner,
    FineTuningConfig,
    LoRALayer,
    create_lora_config,
    create_small_dataset_config,
    finetune_model,
)

__all__ = [
    # Main fine-tuning components
    "FineTuner",
    "FineTuningConfig",
    "LoRALayer",
    # Fine-tuning API functions
    "finetune_model",
    # Configuration helpers
    "create_lora_config",
    "create_small_dataset_config",
]
