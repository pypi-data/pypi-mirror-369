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
    train_model,
    resume_training,
    evaluate_model,
)
from .utils import (
    MetricsTracker,
    LearningRateScheduler,
    GradientClipper,
    EarlyStopping,
    TrainingTimer,
    count_parameters,
    get_model_size_mb,
    calculate_perplexity,
    warmup_lr_schedule,
    cosine_annealing_lr_schedule,
    save_training_config,
    load_training_config,
)

# Advanced tokenizer training
from .train_tokenizer import (
    TokenizerTrainer,
    TokenizerConfig,
    HuggingFaceTrainer,
    SentencePieceTrainer,
    ValidationResults,
    create_tokenizer_trainer,
    get_preset_configs,
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