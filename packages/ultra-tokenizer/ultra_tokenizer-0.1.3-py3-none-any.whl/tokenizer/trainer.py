"""
Tokenizer Training Module

This module contains the TokenizerTrainer class that handles training the tokenizer
on a corpus of text data.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Union, Tuple, Iterator
from pathlib import Path
import tqdm
import regex as re
from collections import Counter, defaultdict
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

from .tokenizer import Tokenizer
from .vocab import Vocabulary

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TokenizerTrainer:
    """
    Handles training a tokenizer on a corpus of text data.

    Features:
    - Efficiently processes large text files
    - Supports multiple training algorithms
    - Progress tracking and logging
    - Parallel processing for faster training
    """

    def __init__(
        self,
        tokenizer: Optional[Tokenizer] = None,
        vocab_size: int = 30000,
        min_frequency: int = 2,
        max_token_length: int = 100,
        lowercase: bool = True,
        strip_accents: bool = True,
        tokenize_chinese_chars: bool = True,
        special_tokens: Optional[List[str]] = None,
        unk_token: str = "[UNK]",
        pad_token: str = "[PAD]",
        cls_token: str = "[CLS]",
        sep_token: str = "[SEP]",
        mask_token: str = "[MASK]",
    ):
        """Initialize the tokenizer trainer."""
        self.vocab_size = vocab_size
        self.min_frequency = min_frequency
        self.max_token_length = max_token_length
        self.lowercase = lowercase
        self.strip_accents = strip_accents
        self.tokenize_chinese_chars = tokenize_chinese_chars

        # Initialize or use provided tokenizer
        if tokenizer is None:
            self.tokenizer = Tokenizer(
                vocab=None,
                unk_token=unk_token,
                pad_token=pad_token,
                cls_token=cls_token,
                sep_token=sep_token,
                mask_token=mask_token,
                lower_case=lowercase,
                strip_accents=strip_accents,
                tokenize_chinese_chars=tokenize_chinese_chars,
            )
        else:
            self.tokenizer = tokenizer

        # Initialize vocabulary
        self.vocab = Vocabulary(
            vocab_size=vocab_size,
            min_frequency=min_frequency,
            max_token_length=max_token_length,
            unk_token=unk_token,
            pad_token=pad_token,
            cls_token=cls_token,
            sep_token=sep_token,
            mask_token=mask_token,
        )

        # Training state
        self.trained = False
        self.training_stats = {
            "vocab_size": 0,
            "num_tokens": 0,
            "num_unknown_tokens": 0,
            "coverage": 0.0,
            "training_time": 0.0,
        }

    def train(
        self,
        files: Union[str, List[str]],
        algorithm: str = "bpe",
        num_workers: int = -1,
        chunk_size: int = 10000,
        **kwargs,
    ) -> Tokenizer:
        """
        Train the tokenizer on the given files.

        Args:
            files: Path or list of paths to text files for training
            algorithm: Tokenization algorithm ('bpe', 'wordpiece', 'unigram')
            num_workers: Number of worker processes (-1 for all available cores)
            chunk_size: Number of lines to process in each chunk
            **kwargs: Additional algorithm-specific parameters

        Returns:
            Trained Tokenizer instance
        """
        import time

        start_time = time.time()

        logger.info(f"Starting tokenizer training with {algorithm} algorithm")

        # Convert single file to list
        if isinstance(files, (str, Path)):
            files = [str(files)]

        # Validate files
        for file_path in files:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Training file not found: {file_path}")

        # Count total lines for progress tracking
        total_lines = sum(1 for _ in self._file_line_iterator(files[0]))
        logger.info(f"Processing {len(files)} files with {total_lines:,} total lines")

        # Process files and build vocabulary
        word_counts = self._process_files(
            files,
            num_workers=num_workers,
            chunk_size=chunk_size,
            total_lines=total_lines,
        )

        # Train vocabulary
        logger.info(f"Training vocabulary with {len(word_counts):,} unique words")
        self.vocab.train_on_texts(
            texts=list(word_counts.keys()), algorithm=algorithm, **kwargs
        )

        # Update tokenizer with trained vocabulary
        self.tokenizer.vocab = self.vocab
        self.trained = True

        # Calculate training statistics
        self.training_stats = {
            "vocab_size": len(self.vocab),
            "num_tokens": sum(word_counts.values()),
            "num_unknown_tokens": 0,  # Will be updated in _evaluate_coverage
            "coverage": self._evaluate_coverage(word_counts),
            "training_time": time.time() - start_time,
        }

        logger.info(
            f"Training completed in {self.training_stats['training_time']:.2f} seconds"
        )
        logger.info(f"Vocabulary size: {self.training_stats['vocab_size']:,}")
        logger.info(f"Text coverage: {self.training_stats['coverage']:.2%}")

        return self.tokenizer

    def _process_files(
        self,
        files: List[str],
        num_workers: int = -1,
        chunk_size: int = 10000,
        total_lines: Optional[int] = None,
    ) -> Dict[str, int]:
        """Process files and count word frequencies."""
        if num_workers == -1:
            num_workers = mp.cpu_count()

        word_counts = Counter()

        # Process files in parallel
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = []

            # Submit file processing tasks
            for file_path in files:
                chunks = self._chunk_file(file_path, chunk_size)
                for chunk in chunks:
                    future = executor.submit(self._process_chunk, chunk)
                    futures.append(future)

            # Process results as they complete
            with tqdm.tqdm(total=total_lines, desc="Processing text") as pbar:
                for future in as_completed(futures):
                    chunk_counts = future.result()
                    word_counts.update(chunk_counts)
                    pbar.update(chunk_size)

        return word_counts

    def _chunk_file(self, file_path: str, chunk_size: int) -> Iterator[list]:
        """Split file into chunks of lines."""
        chunk = []
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                chunk.append(line.strip())
                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []
        if chunk:
            yield chunk

    def _process_chunk(self, chunk: List[str]) -> Dict[str, int]:
        """Process a chunk of text and return word counts."""
        word_counts = Counter()

        for line in chunk:
            # Simple whitespace tokenization for initial counting
            # More sophisticated pre-tokenization can be added here
            words = line.lower().split()
            word_counts.update(words)

        return word_counts

    def _evaluate_coverage(self, word_counts: Dict[str, int]) -> float:
        if not self.trained:
            return 0.0

        total_tokens = sum(word_counts.values())
        covered_tokens = 0
        unknown_tokens = 0

        for word, count in word_counts.items():
            # Tokenize the word using our vocabulary
            tokens = self.tokenizer.tokenize(word)

            # Check if any token is the unknown token
            if self.tokenizer.unk_token in tokens:
                unknown_tokens += count
            else:
                covered_tokens += count

        # Update training stats
        self.training_stats["num_unknown_tokens"] = unknown_tokens

        # Calculate coverage
        if total_tokens > 0:
            return covered_tokens / total_tokens
        return 0.0

    def save(self, path: str) -> None:
        """Save the trained tokenizer to disk."""
        if not self.trained:
            raise ValueError("Tokenizer has not been trained yet")

        os.makedirs(path, exist_ok=True)

        # Save tokenizer config
        config = {
            "vocab_size": self.vocab_size,
            "min_frequency": self.min_frequency,
            "max_token_length": self.max_token_length,
            "lowercase": self.lowercase,
            "strip_accents": self.strip_accents,
            "tokenize_chinese_chars": self.tokenize_chinese_chars,
            "special_tokens": [
                self.tokenizer.unk_token,
                self.tokenizer.pad_token,
                self.tokenizer.cls_token,
                self.tokenizer.sep_token,
                self.tokenizer.mask_token,
            ],
            "training_stats": self.training_stats,
        }

        with open(os.path.join(path, "config.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        # Save vocabulary
        self.vocab.save(os.path.join(path, "vocab.json"))

        logger.info(f"Saved tokenizer to {path}")

    @classmethod
    def load(cls, path: str) -> "TokenizerTrainer":
        """Load a trained tokenizer from disk."""
        # Load config
        with open(os.path.join(path, "config.json"), "r", encoding="utf-8") as f:
            config = json.load(f)

        # Create trainer instance
        trainer = cls(
            vocab_size=config["vocab_size"],
            min_frequency=config["min_frequency"],
            max_token_length=config["max_token_length"],
            lowercase=config["lowercase"],
            strip_accents=config["strip_accents"],
            tokenize_chinese_chars=config["tokenize_chinese_chars"],
            unk_token=config["special_tokens"][0],
            pad_token=config["special_tokens"][1],
            cls_token=config["special_tokens"][2],
            sep_token=config["special_tokens"][3],
            mask_token=config["special_tokens"][4],
        )

        # Load vocabulary
        trainer.vocab = Vocabulary.load(os.path.join(path, "vocab.json"))
        trainer.tokenizer.vocab = trainer.vocab
        trainer.trained = True
        trainer.training_stats = config["training_stats"]

        logger.info(f"Loaded tokenizer from {path}")
        return trainer

    def get_training_stats(self) -> Dict[str, any]:
        return self.training_stats.copy()

    def _file_line_iterator(self, file_path: str) -> Iterator[str]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                yield line.strip()
