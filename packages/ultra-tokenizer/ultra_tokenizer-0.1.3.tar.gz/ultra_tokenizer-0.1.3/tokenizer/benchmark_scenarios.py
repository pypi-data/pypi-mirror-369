"""
Benchmark scenarios for tokenizer

This module contains various benchmark scenarios to test different use cases and edge cases.
"""

from typing import List, Dict, Any, Optional
import logging
import random
import string

logger = logging.getLogger(__name__)


class BenchmarkScenarios:
    """Benchmark scenarios for tokenizer."""

    def __init__(self, num_samples: int = 1000):
        """Initialize benchmark scenarios.

        Args:
            num_samples: Number of samples to generate for each scenario
        """
        self.num_samples = num_samples

    def generate_random_text(
        self, min_length: int = 100, max_length: int = 1000
    ) -> str:
        """Generate random text.

        Args:
            min_length: Minimum text length
            max_length: Maximum text length

        Returns:
            Randomly generated text
        """
        length = random.randint(min_length, max_length)
        return "".join(
            random.choices(
                string.ascii_letters + string.digits + string.punctuation, k=length
            )
        )

    def generate_long_texts(self) -> List[str]:
        """Generate long texts scenario.

        Returns:
            List of long texts
        """
        return [self.generate_random_text(1000, 5000) for _ in range(self.num_samples)]

    def generate_short_texts(self) -> List[str]:
        """Generate short texts scenario.

        Returns:
            List of short texts
        """
        return [self.generate_random_text(10, 100) for _ in range(self.num_samples)]

    def generate_mixed_lengths(self) -> List[str]:
        """Generate texts with mixed lengths.

        Returns:
            List of texts with varying lengths
        """
        return [self.generate_random_text() for _ in range(self.num_samples)]

    def generate_repeated_patterns(self) -> List[str]:
        """Generate texts with repeated patterns.

        Returns:
            List of texts with repeated patterns
        """
        patterns = [
            "This is a test sentence. It contains some common words and patterns.",
            "The quick brown fox jumps over the lazy dog.",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Python is a popular programming language used for various applications.",
        ]

        return [random.choice(patterns) for _ in range(self.num_samples)]

    def generate_multilingual_text(self) -> List[str]:
        """Generate multilingual text scenario.

        Returns:
            List of multilingual texts
        """
        languages = [
            "こんにちは、これは日本語の文章です。",
            "Bonjour, c'est un texte en français.",
            "Hola, esto es un texto en español.",
            "Привет, это текст на русском языке.",
            "你好，这是中文文本。",
        ]

        return [random.choice(languages) for _ in range(self.num_samples)]

    def generate_special_characters(self) -> List[str]:
        """Generate texts with special characters.

        Returns:
            List of texts containing special characters
        """
        special_chars = string.punctuation + "\n\t\r\v\f"
        return [
            "".join(random.choices(string.ascii_letters + special_chars, k=100))
            for _ in range(self.num_samples)
        ]

    def generate_all_scenarios(self) -> Dict[str, List[str]]:
        """Generate all benchmark scenarios.

        Returns:
            Dictionary of scenario name to text samples
        """
        return {
            "long_texts": self.generate_long_texts(),
            "short_texts": self.generate_short_texts(),
            "mixed_lengths": self.generate_mixed_lengths(),
            "repeated_patterns": self.generate_repeated_patterns(),
            "multilingual": self.generate_multilingual_text(),
            "special_chars": self.generate_special_characters(),
        }
