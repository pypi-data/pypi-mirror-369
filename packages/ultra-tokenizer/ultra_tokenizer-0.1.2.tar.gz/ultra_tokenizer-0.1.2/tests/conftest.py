"""Configuration file for pytest."""

import os
import tempfile
import pytest

from tokenizer import Tokenizer, TokenizerTrainer


@pytest.fixture(scope="module")
def sample_text_file():
    """Create a sample text file for testing."""
    texts = [
        "This is a test sentence.",
        "This is another test sentence!",
        "And here's a third one?",
        "Testing different cases and punctuation!",
        "The quick brown fox jumps over the lazy dog.",
    ]

    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt")
    try:
        temp_file.write("\n".join(texts))
        temp_file.close()
        yield temp_file.name
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


@pytest.fixture(scope="module")
def trained_tokenizer(sample_text_file):
    """Create a trained tokenizer for testing."""
    trainer = TokenizerTrainer(
        vocab_size=100, min_frequency=1, lowercase=True, strip_accents=True
    )

    # Train the tokenizer
    tokenizer = trainer.train(files=[sample_text_file], algorithm="bpe", num_workers=1)

    return tokenizer


@pytest.fixture(scope="module")
def tokenizer_trainer():
    """Create a tokenizer trainer for testing."""
    return TokenizerTrainer(
        vocab_size=100, min_frequency=1, lowercase=True, strip_accents=True
    )


@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory that will be cleaned up after the test."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
