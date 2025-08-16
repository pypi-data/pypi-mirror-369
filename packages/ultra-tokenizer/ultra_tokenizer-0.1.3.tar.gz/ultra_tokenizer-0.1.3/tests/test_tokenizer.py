import os
import tempfile
import unittest
from pathlib import Path

from tokenizer import Tokenizer, TokenizerTrainer


class TestTokenizer(unittest.TestCase):
    """Test cases for the Tokenizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_texts = [
            "This is a test sentence.",
            "This is another test sentence!",
            "And here's a third one?",
        ]
        self.test_file = tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".txt"
        )
        self.test_file.write("\n".join(self.test_texts))
        self.test_file.close()

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)

    def test_tokenizer_initialization(self):
        """Test tokenizer initialization."""
        tokenizer = Tokenizer()
        self.assertIsNotNone(tokenizer)

    def test_trainer_initialization(self):
        """Test tokenizer trainer initialization."""
        trainer = TokenizerTrainer(
            vocab_size=1000, min_frequency=1, lowercase=True, strip_accents=True
        )
        self.assertIsNotNone(trainer)

    def test_tokenizer_training(self):
        """Test tokenizer training."""
        trainer = TokenizerTrainer(vocab_size=100, min_frequency=1, lowercase=True)

        # Train the tokenizer
        tokenizer = trainer.train(
            files=[self.test_file.name], algorithm="bpe", num_workers=1
        )

        # Test tokenization
        test_sentence = "This is a test."
        tokens = tokenizer.tokenize(test_sentence)
        self.assertIsInstance(tokens, list)
        self.assertGreater(len(tokens), 0)

    def test_tokenizer_save_load(self):
        """Test saving and loading the tokenizer."""
        # Create a temporary directory for saving
        with tempfile.TemporaryDirectory() as temp_dir:
            trainer = TokenizerTrainer(vocab_size=100, min_frequency=1, lowercase=True)

            # Train and save
            tokenizer = trainer.train(
                files=[self.test_file.name], algorithm="bpe", num_workers=1
            )
            save_path = os.path.join(temp_dir, "test_tokenizer")
            trainer.save(save_path)

            # Load and test
            loaded_trainer = TokenizerTrainer.load(save_path)
            loaded_tokenizer = loaded_trainer.tokenizer

            # Test if loaded tokenizer works
            test_sentence = "This is a test."
            original_tokens = tokenizer.tokenize(test_sentence)
            loaded_tokens = loaded_tokenizer.tokenize(test_sentence)

            self.assertEqual(original_tokens, loaded_tokens)

    def test_special_tokens(self):
        """Test special tokens handling."""
        tokenizer = Tokenizer()
        self.assertIn("[UNK]", tokenizer.vocab)
        self.assertIn("[PAD]", tokenizer.vocab)
        self.assertIn("[CLS]", tokenizer.vocab)
        self.assertIn("[SEP]", tokenizer.vocab)
        self.assertIn("[MASK]", tokenizer.vocab)


if __name__ == "__main__":
    unittest.main()
