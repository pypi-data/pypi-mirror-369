"""
Tokenizer training wrapper for LLMBuilder.

This module provides unified interfaces for training tokenizers with
multiple backends including Hugging Face Tokenizers and SentencePiece.
"""

import logging
import os
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import json

logger = logging.getLogger(__name__)


@dataclass
class TokenizerConfig:
    """Configuration for tokenizer training parameters."""
    backend: str = "huggingface"  # 'huggingface' or 'sentencepiece'
    vocab_size: int = 16000
    algorithm: str = "bpe"  # 'bpe', 'wordpiece', 'unigram'
    special_tokens: List[str] = field(default_factory=lambda: ["<pad>", "<unk>", "<s>", "</s>"])
    training_params: Dict[str, Any] = field(default_factory=dict)
    
    # Common parameters
    character_coverage: float = 0.9995
    max_sentence_length: int = 4192
    shuffle_input_sentence: bool = True
    
    # Backend-specific parameters
    min_frequency: int = 2
    show_progress: bool = True
    
    SUPPORTED_BACKENDS = ["huggingface", "sentencepiece"]
    SUPPORTED_ALGORITHMS = ["bpe", "wordpiece", "unigram"]
    VOCAB_SIZE_PRESETS = [8000, 16000, 32000, 50000]
    
    def __post_init__(self):
        """Validate tokenizer configuration."""
        if self.backend not in self.SUPPORTED_BACKENDS:
            raise ValueError(f"Unsupported backend: {self.backend}. "
                           f"Supported backends: {self.SUPPORTED_BACKENDS}")
        
        if self.algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}. "
                           f"Supported algorithms: {self.SUPPORTED_ALGORITHMS}")
        
        if self.vocab_size <= 0:
            raise ValueError(f"vocab_size must be positive, got {self.vocab_size}")
        
        # Backend-specific validation
        if self.backend == "sentencepiece" and self.algorithm == "wordpiece":
            logger.warning("WordPiece algorithm not directly supported by SentencePiece, using BPE instead")
            self.algorithm = "bpe"


@dataclass
class ValidationResults:
    """Results from tokenizer validation."""
    is_valid: bool
    vocab_size: int
    test_tokens: List[str]
    test_ids: List[int]
    round_trip_success: bool
    error_message: Optional[str] = None


class TokenizerTrainer(ABC):
    """Abstract base class for tokenizer training."""
    
    @abstractmethod
    def train(self, corpus_path: str, vocab_size: int, **kwargs) -> str:
        """
        Train a tokenizer on the given corpus.
        
        Args:
            corpus_path: Path to the training corpus
            vocab_size: Vocabulary size for the tokenizer
            **kwargs: Additional training parameters
            
        Returns:
            Path to the trained tokenizer
        """
        pass
    
    @abstractmethod
    def save_tokenizer(self, output_path: str) -> None:
        """
        Save the trained tokenizer to disk.
        
        Args:
            output_path: Path to save the tokenizer
        """
        pass
    
    @abstractmethod
    def validate_tokenizer(self, test_text: str) -> ValidationResults:
        """
        Validate the trained tokenizer with test text.
        
        Args:
            test_text: Text to use for validation
            
        Returns:
            ValidationResults with validation details
        """
        pass


class HuggingFaceTrainer(TokenizerTrainer):
    """
    Tokenizer trainer using Hugging Face Tokenizers library.
    
    This class provides a wrapper around the Hugging Face tokenizers
    library for training BPE, WordPiece, and Unigram tokenizers.
    """
    
    def __init__(self, config: TokenizerConfig):
        """
        Initialize the Hugging Face tokenizer trainer.
        
        Args:
            config: TokenizerConfig with training parameters
        """
        self.config = config
        self.tokenizer = None
        
        # Lazy import to avoid dependency issues
        self._tokenizers_available = self._check_tokenizers_availability()
    
    def _check_tokenizers_availability(self) -> bool:
        """Check if tokenizers library is available."""
        try:
            import tokenizers
            return True
        except ImportError:
            logger.error("tokenizers library not available. Install with: pip install tokenizers")
            return False
    
    def _create_tokenizer(self):
        """Create a tokenizer based on the configuration."""
        if not self._tokenizers_available:
            raise ImportError("tokenizers library required for Hugging Face training")
        
        from tokenizers import Tokenizer
        from tokenizers.models import BPE, WordPiece, Unigram
        from tokenizers.pre_tokenizers import Whitespace
        from tokenizers.processors import TemplateProcessing
        from tokenizers.trainers import BpeTrainer, WordPieceTrainer, UnigramTrainer
        
        # Create model based on algorithm
        if self.config.algorithm == "bpe":
            model = BPE(unk_token="<unk>")
            trainer = BpeTrainer(
                vocab_size=self.config.vocab_size,
                special_tokens=self.config.special_tokens,
                min_frequency=self.config.min_frequency,
                show_progress=self.config.show_progress
            )
        elif self.config.algorithm == "wordpiece":
            model = WordPiece(unk_token="<unk>")
            trainer = WordPieceTrainer(
                vocab_size=self.config.vocab_size,
                special_tokens=self.config.special_tokens,
                min_frequency=self.config.min_frequency,
                show_progress=self.config.show_progress
            )
        elif self.config.algorithm == "unigram":
            model = Unigram()
            trainer = UnigramTrainer(
                vocab_size=self.config.vocab_size,
                special_tokens=self.config.special_tokens,
                show_progress=self.config.show_progress
            )
        else:
            raise ValueError(f"Unsupported algorithm: {self.config.algorithm}")
        
        # Create tokenizer
        tokenizer = Tokenizer(model)
        tokenizer.pre_tokenizer = Whitespace()
        
        # Add post-processor for special tokens
        tokenizer.post_processor = TemplateProcessing(
            single="<s> $A </s>",
            pair="<s> $A </s> $B:1 </s>:1",
            special_tokens=[
                ("<s>", 2),
                ("</s>", 3),
            ],
        )
        
        return tokenizer, trainer
    
    def train(self, corpus_path: str, vocab_size: int, **kwargs) -> str:
        """
        Train a tokenizer using Hugging Face tokenizers.
        
        Args:
            corpus_path: Path to the training corpus
            vocab_size: Vocabulary size
            **kwargs: Additional parameters
            
        Returns:
            Path to the trained tokenizer
        """
        # Update config with provided parameters
        if vocab_size != self.config.vocab_size:
            self.config.vocab_size = vocab_size
        
        # Create tokenizer and trainer
        self.tokenizer, trainer = self._create_tokenizer()
        
        # Prepare training files
        if Path(corpus_path).is_file():
            files = [corpus_path]
        else:
            # Directory of files
            corpus_dir = Path(corpus_path)
            files = [str(f) for f in corpus_dir.glob("*.txt")]
        
        if not files:
            raise ValueError(f"No training files found in {corpus_path}")
        
        logger.info(f"Training {self.config.algorithm} tokenizer on {len(files)} files")
        
        # Train the tokenizer
        self.tokenizer.train(files, trainer)
        
        logger.info(f"Tokenizer training complete. Vocab size: {self.tokenizer.get_vocab_size()}")
        
        return corpus_path  # Return input path as identifier
    
    def save_tokenizer(self, output_path: str) -> None:
        """
        Save the trained tokenizer.
        
        Args:
            output_path: Path to save the tokenizer
        """
        if self.tokenizer is None:
            raise RuntimeError("No tokenizer trained. Call train() first.")
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save tokenizer
        tokenizer_path = output_dir / "tokenizer.json"
        self.tokenizer.save(str(tokenizer_path))
        
        # Save configuration
        config_path = output_dir / "config.json"
        config_dict = {
            "backend": self.config.backend,
            "vocab_size": self.config.vocab_size,
            "algorithm": self.config.algorithm,
            "special_tokens": self.config.special_tokens,
            "training_params": self.config.training_params
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Tokenizer saved to {output_path}")
    
    def validate_tokenizer(self, test_text: str) -> ValidationResults:
        """
        Validate the trained tokenizer.
        
        Args:
            test_text: Text to use for validation
            
        Returns:
            ValidationResults with validation details
        """
        if self.tokenizer is None:
            return ValidationResults(
                is_valid=False,
                vocab_size=0,
                test_tokens=[],
                test_ids=[],
                round_trip_success=False,
                error_message="No tokenizer trained"
            )
        
        try:
            # Encode test text
            encoding = self.tokenizer.encode(test_text)
            test_ids = encoding.ids
            test_tokens = encoding.tokens
            
            # Decode back to text
            decoded_text = self.tokenizer.decode(test_ids)
            
            # Check round-trip success (allowing for some normalization differences)
            round_trip_success = test_text.strip() == decoded_text.strip()
            
            return ValidationResults(
                is_valid=True,
                vocab_size=self.tokenizer.get_vocab_size(),
                test_tokens=test_tokens,
                test_ids=test_ids,
                round_trip_success=round_trip_success
            )
            
        except Exception as e:
            return ValidationResults(
                is_valid=False,
                vocab_size=self.tokenizer.get_vocab_size() if self.tokenizer else 0,
                test_tokens=[],
                test_ids=[],
                round_trip_success=False,
                error_message=str(e)
            )


class SentencePieceTrainer(TokenizerTrainer):
    """
    Tokenizer trainer using SentencePiece CLI integration.
    
    This class provides integration with SentencePiece for training
    BPE and Unigram tokenizers via command-line interface.
    """
    
    def __init__(self, config: TokenizerConfig):
        """
        Initialize the SentencePiece tokenizer trainer.
        
        Args:
            config: TokenizerConfig with training parameters
        """
        self.config = config
        self.model_path = None
        
        # Check SentencePiece availability
        self._sentencepiece_available = self._check_sentencepiece_availability()
    
    def _check_sentencepiece_availability(self) -> bool:
        """Check if SentencePiece is available."""
        try:
            import sentencepiece as spm
            return True
        except ImportError:
            logger.error("sentencepiece library not available. Install with: pip install sentencepiece")
            return False
    
    def train(self, corpus_path: str, vocab_size: int, **kwargs) -> str:
        """
        Train a tokenizer using SentencePiece.
        
        Args:
            corpus_path: Path to the training corpus
            vocab_size: Vocabulary size
            **kwargs: Additional parameters
            
        Returns:
            Path to the trained model
        """
        if not self._sentencepiece_available:
            raise ImportError("sentencepiece library required for SentencePiece training")
        
        import sentencepiece as spm
        
        # Update config
        if vocab_size != self.config.vocab_size:
            self.config.vocab_size = vocab_size
        
        # Prepare input files
        if Path(corpus_path).is_file():
            input_file = corpus_path
        else:
            # Combine multiple files into one for SentencePiece
            corpus_dir = Path(corpus_path)
            files = list(corpus_dir.glob("*.txt"))
            
            if not files:
                raise ValueError(f"No training files found in {corpus_path}")
            
            # Create combined input file
            combined_path = corpus_dir / "combined_corpus.txt"
            with open(combined_path, 'w', encoding='utf-8') as outf:
                for file_path in files:
                    with open(file_path, 'r', encoding='utf-8') as inf:
                        outf.write(inf.read())
                        outf.write('\n')
            
            input_file = str(combined_path)
        
        # Set up model prefix
        model_prefix = Path(corpus_path).parent / "tokenizer_model"
        self.model_path = f"{model_prefix}.model"
        
        # Map algorithm to SentencePiece model type
        model_type_map = {
            "bpe": "bpe",
            "unigram": "unigram",
            "wordpiece": "bpe"  # SentencePiece doesn't have WordPiece, use BPE
        }
        model_type = model_type_map.get(self.config.algorithm, "bpe")
        
        # Prepare training arguments
        train_args = {
            "input": input_file,
            "model_prefix": str(model_prefix),
            "vocab_size": self.config.vocab_size,
            "model_type": model_type,
            "character_coverage": self.config.character_coverage,
            "max_sentence_length": self.config.max_sentence_length,
            "shuffle_input_sentence": self.config.shuffle_input_sentence,
            "pad_id": 0,
            "unk_id": 1,
            "bos_id": 2,
            "eos_id": 3,
        }
        
        # Add special tokens
        if self.config.special_tokens:
            # SentencePiece handles special tokens differently
            user_defined_symbols = [token for token in self.config.special_tokens 
                                  if token not in ["<pad>", "<unk>", "<s>", "</s>"]]
            if user_defined_symbols:
                train_args["user_defined_symbols"] = ",".join(user_defined_symbols)
        
        logger.info(f"Training SentencePiece {model_type} tokenizer")
        
        # Train the model
        spm.SentencePieceTrainer.train(**train_args)
        
        logger.info(f"SentencePiece training complete. Model saved to {self.model_path}")
        
        return self.model_path
    
    def save_tokenizer(self, output_path: str) -> None:
        """
        Save the trained tokenizer.
        
        Args:
            output_path: Path to save the tokenizer
        """
        if self.model_path is None or not Path(self.model_path).exists():
            raise RuntimeError("No tokenizer trained. Call train() first.")
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy model files
        model_file = Path(self.model_path)
        vocab_file = model_file.with_suffix('.vocab')
        
        # Copy to output directory
        import shutil
        shutil.copy2(model_file, output_dir / "tokenizer.model")
        if vocab_file.exists():
            shutil.copy2(vocab_file, output_dir / "tokenizer.vocab")
        
        # Save configuration
        config_path = output_dir / "config.json"
        config_dict = {
            "backend": self.config.backend,
            "vocab_size": self.config.vocab_size,
            "algorithm": self.config.algorithm,
            "special_tokens": self.config.special_tokens,
            "training_params": self.config.training_params
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Tokenizer saved to {output_path}")
    
    def validate_tokenizer(self, test_text: str) -> ValidationResults:
        """
        Validate the trained tokenizer.
        
        Args:
            test_text: Text to use for validation
            
        Returns:
            ValidationResults with validation details
        """
        if self.model_path is None or not Path(self.model_path).exists():
            return ValidationResults(
                is_valid=False,
                vocab_size=0,
                test_tokens=[],
                test_ids=[],
                round_trip_success=False,
                error_message="No tokenizer model available"
            )
        
        try:
            import sentencepiece as spm
            
            # Load the trained model
            sp = spm.SentencePieceProcessor()
            sp.load(self.model_path)
            
            # Encode test text
            test_ids = sp.encode_as_ids(test_text)
            test_tokens = sp.encode_as_pieces(test_text)
            
            # Decode back to text
            decoded_text = sp.decode_ids(test_ids)
            
            # Check round-trip success
            round_trip_success = test_text.strip() == decoded_text.strip()
            
            return ValidationResults(
                is_valid=True,
                vocab_size=sp.get_piece_size(),
                test_tokens=test_tokens,
                test_ids=test_ids,
                round_trip_success=round_trip_success
            )
            
        except Exception as e:
            return ValidationResults(
                is_valid=False,
                vocab_size=0,
                test_tokens=[],
                test_ids=[],
                round_trip_success=False,
                error_message=str(e)
            )


def create_tokenizer_trainer(config: TokenizerConfig) -> TokenizerTrainer:
    """
    Factory function to create appropriate tokenizer trainer.
    
    Args:
        config: TokenizerConfig specifying the backend and parameters
        
    Returns:
        TokenizerTrainer instance
    """
    if config.backend == "huggingface":
        return HuggingFaceTrainer(config)
    elif config.backend == "sentencepiece":
        return SentencePieceTrainer(config)
    else:
        raise ValueError(f"Unsupported backend: {config.backend}")


def get_preset_configs() -> Dict[str, TokenizerConfig]:
    """
    Get predefined tokenizer configurations.
    
    Returns:
        Dictionary of preset configurations
    """
    presets = {
        "small_bpe": TokenizerConfig(
            backend="huggingface",
            vocab_size=8000,
            algorithm="bpe"
        ),
        "medium_bpe": TokenizerConfig(
            backend="huggingface",
            vocab_size=16000,
            algorithm="bpe"
        ),
        "large_bpe": TokenizerConfig(
            backend="huggingface",
            vocab_size=32000,
            algorithm="bpe"
        ),
        "sentencepiece_unigram": TokenizerConfig(
            backend="sentencepiece",
            vocab_size=16000,
            algorithm="unigram"
        ),
        "wordpiece": TokenizerConfig(
            backend="huggingface",
            vocab_size=16000,
            algorithm="wordpiece"
        )
    }
    
    return presets