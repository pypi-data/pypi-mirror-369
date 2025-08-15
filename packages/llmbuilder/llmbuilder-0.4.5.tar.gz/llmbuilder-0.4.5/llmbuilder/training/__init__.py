"""
Training pipeline module for LLMBuilder.

This module provides comprehensive training capabilities including
the main Trainer class, training utilities, metrics tracking,
error handling mechanisms, and advanced tokenizer training.
"""

from .train import (
    Trainer,
    TrainingMetrics,
    TrainingState,
    evaluate_model,
    resume_training,
    train_model,
)

# Advanced tokenizer training
from .train_tokenizer import (
    HuggingFaceTrainer,
    SentencePieceTrainer,
    TokenizerConfig,
    TokenizerTrainer,
    ValidationResults,
    create_tokenizer_trainer,
    get_preset_configs,
)
from .utils import (
    EarlyStopping,
    GradientClipper,
    LearningRateScheduler,
    MetricsTracker,
    TrainingTimer,
    calculate_perplexity,
    cosine_annealing_lr_schedule,
    count_parameters,
    get_model_size_mb,
    load_training_config,
    save_training_config,
    warmup_lr_schedule,
)

__all__ = [
    # Main training components
    "Trainer",
    "TrainingMetrics",
    "TrainingState",
    # Training API functions
    "train_model",
    "resume_training",
    "evaluate_model",
    # Training utilities
    "MetricsTracker",
    "LearningRateScheduler",
    "GradientClipper",
    "EarlyStopping",
    "TrainingTimer",
    # Helper functions
    "count_parameters",
    "get_model_size_mb",
    "calculate_perplexity",
    "warmup_lr_schedule",
    "cosine_annealing_lr_schedule",
    "save_training_config",
    "load_training_config",
    # Tokenizer training
    "TokenizerTrainer",
    "TokenizerConfig",
    "HuggingFaceTrainer",
    "SentencePieceTrainer",
    "ValidationResults",
    "create_tokenizer_trainer",
    "get_preset_configs",
]
