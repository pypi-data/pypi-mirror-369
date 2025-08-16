"""
Ultra-Tokenizer - Advanced Tokenizer for Natural Language Processing

A high-performance, production-ready tokenizer supporting multiple subword tokenization
algorithms including BPE, WordPiece, and Unigram. Designed for efficiency and flexibility,
perfect for modern NLP pipelines.

Features:
    - Support for BPE, WordPiece, and Unigram tokenization algorithms
    - High performance with efficient implementations
    - Simple API for training and using tokenizers
    - Comprehensive test coverage and robust error handling
    - Full type annotations for better development experience
    - Multilingual support for various languages and scripts
    - Built-in handling of special tokens
    - Memory efficient with smart caching

Example:
    >>> from ultra_tokenizer import Tokenizer, TokenizerTrainer
    >>> trainer = TokenizerTrainer(vocab_size=30000)
    >>> tokenizer = trainer.train_from_files(["file1.txt", "file2.txt"])
    >>> tokens = tokenizer.encode("Hello, world!")
    >>> print(tokens)

For more information, visit: https://github.com/pranav271103/Ultra-Tokenizer
"""

__version__ = "0.1.0"
__author__ = "Pranav Singh"
__email__ = "pranav.singh01010101@gmail.com"
__license__ = "Apache 2.0"
__url__ = "https://github.com/pranav271103/Ultra-Tokenizer.git"

from .tokenizer import Tokenizer
from .vocab import Vocabulary
from .trainer import TokenizerTrainer

__all__ = ["Tokenizer", "Vocabulary", "TokenizerTrainer"]
