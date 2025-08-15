"""
Training Pipeline for LLMBuilder.

This module provides a high-level training pipeline that handles all the complex
logic of data loading, tokenization, model building, and training.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import torch

from .data import DataLoader, TextDataset, create_dataloader, split_dataset
from .model import build_model
from .tokenizer import TokenizerTrainer, TokenizerManager, TokenizerWrapper, TokenizerWrapper
from .training import Trainer
from .config import TrainingConfig
from .utils import DataError, ModelError, get_logger

logger = get_logger("pipeline")


class TrainingPipeline:
    """
    End-to-end training pipeline for LLMBuilder.

    Handles all the complex logic of data processing, tokenization,
    model building, and training with proper error handling and logging.
    """

    def __init__(
        self,
        data_path: Union[str, Path, List[Union[str, Path]]],
        output_dir: Union[str, Path],
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the training pipeline.

        Args:
            data_path: Path to input data file(s) or directory
            output_dir: Directory to save outputs (tokenizer, checkpoints, etc.)
            config: Optional configuration dictionary
        """
        self.data_path = Path(data_path) if isinstance(data_path, str) else data_path
        self.output_dir = Path(output_dir)
        self.config = config or {}

        # Setup paths
        self.tokenizer_dir = self.output_dir / "tokenizer"
        self.checkpoints_dir = self.output_dir / "checkpoints"
        self.processed_data_file = self.output_dir / "processed_data.txt"
        self.tokenized_data_file = self.output_dir / "tokenized_data.pt"

        # Ensure output directories exist
        self.tokenizer_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.data_loader = DataLoader()
        self.tokenizer_trainer = None  # Will be created with proper config
        self.tokenizer_manager = None
        self.model = None
        self.trainer = None

    def run(self, clean: bool = False):
        """
        Run the complete training pipeline.

        Args:
            clean: If True, clean up previous outputs before starting
        """
        try:
            if clean:
                self._clean_previous_run()

            # Step 1: Process and load data
            logger.info("Processing input data...")
            self._process_data()

            # Step 2: Train or load tokenizer
            logger.info("Setting up tokenizer...")
            self._setup_tokenizer()

            # Step 3: Prepare dataset
            logger.info("Preparing dataset...")
            dataset = self._prepare_dataset()

            # Step 4: Build model
            logger.info("Building model...")
            self._build_model()

            # Step 5: Train model
            logger.info("Starting training...")
            self._train_model(dataset)

            logger.info("Training completed successfully!")

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise

    def _clean_previous_run(self):
        """Clean up outputs from previous runs."""
        if self.processed_data_file.exists():
            self.processed_data_file.unlink()
        if self.tokenized_data_file.exists():
            self.tokenized_data_file.unlink()
        if self.tokenizer_dir.exists():
            shutil.rmtree(self.tokenizer_dir)
            self.tokenizer_dir.mkdir()
        if self.checkpoints_dir.exists():
            shutil.rmtree(self.checkpoints_dir)
            self.checkpoints_dir.mkdir()

    def _process_data(self):
        """Process input data into a clean text corpus."""
        if self.processed_data_file.exists():
            logger.info(f"Using existing processed data: {self.processed_data_file}")
            return

        if isinstance(self.data_path, (list, tuple)):
            # Handle multiple input files
            texts = []
            for path in self.data_path:
                path = Path(path)
                if path.is_file():
                    text = self.data_loader.load_file(path)
                    if text:
                        texts.append(text)
        else:
            # Handle single file or directory
            path = Path(self.data_path)
            if path.is_file():
                text = self.data_loader.load_file(path)
                texts = [text] if text else []
            else:
                # Load all supported files from directory (recursively)
                texts = []
                for ext in DataLoader.SUPPORTED_EXTENSIONS:
                    # Use recursive search to include nested subdirectories
                    for file_path in path.rglob(f"*{ext}"):
                        if not file_path.is_file():
                            continue
                        try:
                            text = self.data_loader.load_file(file_path)
                            if text:
                                texts.append(text)
                        except Exception as e:
                            # Skip files that require optional dependencies or are unreadable
                            logger.warning(f"Skipping {file_path}: {e}")
                            continue

        if not texts:
            raise DataError("No valid text data found in the input path(s)")

        # Combine and save processed text
        combined_text = "\n\n".join(texts)
        with open(self.processed_data_file, "w", encoding="utf-8") as f:
            f.write(combined_text)

        logger.info(f"Processed data saved to {self.processed_data_file}")

    def _setup_tokenizer(self):
        """Train or load tokenizer."""
        tokenizer_model_file = self.tokenizer_dir / "tokenizer.model"

        if tokenizer_model_file.exists():
            # Load existing tokenizer
            manager = TokenizerManager()
            raw_tokenizer = manager.load_tokenizer(str(tokenizer_model_file))
            self.tokenizer_manager = TokenizerWrapper(raw_tokenizer)
            logger.info(f"Loaded tokenizer from {self.tokenizer_dir}")
        else:
            # Train new tokenizer
            vocab_size = self.config.get("vocab_size", 8000)
            logger.info(f"Training new tokenizer with vocab_size={vocab_size}...")

            # Create TokenizerTrainer with correct vocab_size
            from .config import TokenizerConfig
            tokenizer_config = TokenizerConfig(vocab_size=vocab_size)
            self.tokenizer_trainer = TokenizerTrainer(tokenizer_config)

            # Train tokenizer using TokenizerTrainer
            results = self.tokenizer_trainer.train(
                str(self.processed_data_file),
                str(self.tokenizer_dir)
            )
            
            # Load the trained tokenizer
            manager = TokenizerManager()
            raw_tokenizer = manager.load_tokenizer(str(tokenizer_model_file))
            self.tokenizer_manager = TokenizerWrapper(raw_tokenizer)
            logger.info(f"Tokenizer trained and saved to {self.tokenizer_dir}")

    def _prepare_dataset(self):
        """Prepare dataset for training."""
        if not self.tokenizer_manager:
            raise ValueError("Tokenizer not initialized")

        # Tokenize and save if not already done
        if not self.tokenized_data_file.exists():
            logger.info("Tokenizing data...")
            with open(self.processed_data_file, "r", encoding="utf-8") as f:
                text = f.read()

            token_ids = self.tokenizer_manager.encode(text)
            # Convert list to tensor before saving
            token_ids_tensor = torch.tensor(token_ids, dtype=torch.long)
            torch.save(token_ids_tensor, self.tokenized_data_file)
        else:
            logger.info("Loading pre-tokenized data...")

        # Create dataset
        block_size = self.config.get("block_size", 1024)
        
        # Load tokenized data to check size
        token_data = torch.load(self.tokenized_data_file, map_location="cpu")
        num_tokens = len(token_data)
        
        # Adjust block size if token sequence is too short
        if num_tokens < block_size:
            # Use a smaller block size that allows at least a few samples
            block_size = max(16, num_tokens // 4)  # At least 16 tokens, or 1/4 of available tokens
            logger.info(f"Adjusted block size to {block_size} due to small dataset ({num_tokens} tokens)")
        
        return TextDataset(
            self.tokenized_data_file,
            block_size=block_size,
            stride=block_size // 2,  # 50% overlap
        )

    def _build_model(self):
        """Build model from config."""
        model_config = self.config.get("model", {}).copy()
        # Set vocab_size from tokenizer (overrides any config value)
        model_config["vocab_size"] = self.tokenizer_manager.vocab_size
        self.model = build_model(model_config)
        logger.info(
            f"Model built with {sum(p.numel() for p in self.model.parameters()):,} parameters"
        )

    def _train_model(self, dataset):
        """Train the model."""
        if not self.model:
            raise ValueError("Model not built")

        # Prepare training config (without output_dir) and extract val split
        training_cfg_dict = self.config.get("training", {}).copy()
        # Extract validation ratio if provided, default to 0.1
        val_ratio = float(training_cfg_dict.pop("val_ratio", 0.1))
        # Optional seed for deterministic split
        random_seed = int(training_cfg_dict.pop("random_seed", 42))
        train_config = TrainingConfig(**training_cfg_dict)

        # Initialize and run trainer
        self.trainer = Trainer(
            model=self.model,
            config=train_config,
        )

        # Split into train/val if requested
        train_dataset = dataset
        val_dataset = None
        if val_ratio and val_ratio > 0.0:
            # Ensure ratios are valid
            train_ratio = max(0.0, min(1.0, 1.0 - val_ratio))
            try:
                splits = split_dataset(
                    dataset,
                    train_ratio=train_ratio,
                    val_ratio=val_ratio,
                    test_ratio=0.0,
                    random_seed=random_seed,
                )
                # split_dataset returns (train, val) when test_ratio=0.0
                train_dataset, val_dataset = splits
                if len(val_dataset) == 0:
                    logger.warning("Validation split resulted in 0 samples; disabling validation.")
                    val_dataset = None
                else:
                    logger.info(
                        f"Dataset split: train={len(train_dataset)} samples, val={len(val_dataset)} samples (val_ratio={val_ratio})"
                    )
            except Exception as e:
                logger.warning(f"Failed to split dataset for validation, proceeding without val: {e}")
                val_dataset = None

        # Train with dataset(s) and checkpoint directory
        self.trainer.train(
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            checkpoint_dir=self.checkpoints_dir,
        )


def train(
    data_path: Union[str, Path, List[Union[str, Path]]],
    output_dir: Union[str, Path],
    config: Optional[Dict[str, Any]] = None,
    clean: bool = False,
) -> TrainingPipeline:
    """
    High-level training function that handles the complete training pipeline.

    Args:
        data_path: Path to input data file(s) or directory
        output_dir: Directory to save outputs
        config: Optional configuration dictionary
        clean: If True, clean up previous outputs before starting

    Returns:
        TrainingPipeline: The trained pipeline instance
    """
    pipeline = TrainingPipeline(data_path, output_dir, config or {})
    pipeline.run(clean=clean)
    return pipeline
