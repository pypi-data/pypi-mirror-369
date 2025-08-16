"""
Evaluation metrics and benchmarking for the custom tokenizer.
"""

import numpy as np
from typing import List, Dict, Any
import json
import time
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class TokenizerEvaluator:
    """Class for evaluating tokenizer performance."""

    def __init__(self, tokenizer):
        """Initialize evaluator with a tokenizer instance."""
        self.tokenizer = tokenizer
        self.metrics = {}

    def evaluate_coverage(self, texts: List[str]) -> Dict[str, float]:
        """
        Evaluate vocabulary coverage on a set of texts.
        Returns:
            dict: Contains coverage metrics including:
                - vocab_coverage: percentage of tokens found in vocabulary
                - unknown_token_rate: percentage of unknown tokens
                - avg_token_length: average length of tokens
        """
        total_tokens = 0
        unknown_tokens = 0
        token_lengths = []

        for text in texts:
            tokens = self.tokenizer.tokenize(text)
            total_tokens += len(tokens)

            for token in tokens:
                token_lengths.append(len(token))
                if token == self.tokenizer.vocab.unk_token:
                    unknown_tokens += 1

        vocab_coverage = 100 * (1 - unknown_tokens / total_tokens)
        avg_token_length = np.mean(token_lengths)

        return {
            "vocab_coverage": vocab_coverage,
            "unknown_token_rate": 100 * (unknown_tokens / total_tokens),
            "avg_token_length": avg_token_length,
        }

    def evaluate_speed(self, texts: List[str], num_runs: int = 5) -> Dict[str, float]:
        """
        Measure tokenizer speed.
        Returns:
            dict: Contains timing metrics including:
                - avg_tokenize_time: average time to tokenize a text
                - avg_token_per_second: average tokens processed per second
        """
        times = []
        total_tokens = 0

        for _ in range(num_runs):
            start_time = time.time()
            for text in texts:
                tokens = self.tokenizer.tokenize(text)
                total_tokens += len(tokens)
            end_time = time.time()
            times.append(end_time - start_time)

        avg_time = np.mean(times)
        avg_tokens_per_second = total_tokens / (avg_time * num_runs)

        return {
            "avg_tokenize_time": avg_time,
            "avg_token_per_second": avg_tokens_per_second,
        }

    def evaluate_consistency(self, texts: List[str]) -> Dict[str, Any]:
        """
        Evaluate tokenization consistency.
        Returns:
            dict: Contains consistency metrics including:
                - token_variance: variance in token lengths
                - unique_tokens_ratio: ratio of unique tokens to total tokens
        """
        all_tokens = []
        token_lengths = []

        for text in texts:
            tokens = self.tokenizer.tokenize(text)
            all_tokens.extend(tokens)
            token_lengths.extend([len(token) for token in tokens])

        unique_tokens = set(all_tokens)

        return {
            "token_variance": np.var(token_lengths),
            "unique_tokens_ratio": len(unique_tokens) / len(all_tokens),
        }

    def evaluate_subword_quality(self, texts: List[str]) -> Dict[str, float]:
        """
        Evaluate quality of subword tokenization.
        Returns:
            dict: Contains subword quality metrics including:
                - avg_subwords_per_word: average number of subwords per word
                - subword_repetition_rate: rate of repeated subwords
        """
        total_words = 0
        total_subwords = 0
        subword_counts = Counter()

        for text in texts:
            words = text.split()
            total_words += len(words)

            for word in words:
                tokens = self.tokenizer.tokenize(word)
                total_subwords += len(tokens)
                subword_counts.update(tokens)

        most_common = subword_counts.most_common(1)[0][1]
        repetition_rate = most_common / total_subwords

        return {
            "avg_subwords_per_word": total_subwords / total_words,
            "subword_repetition_rate": repetition_rate,
        }

    def benchmark_against_bert(self, texts: List[str]):
        """
        Compare tokenizer performance against BERT.
        Note: Requires transformers library and bert-base-uncased model.
        """
        try:
            from transformers import BertTokenizer

            bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

            # Compare tokenization results
            bert_metrics = self._evaluate_bert_coverage(bert_tokenizer, texts)
            custom_metrics = self.evaluate_coverage(texts)

            return {
                "bert_coverage": bert_metrics,
                "custom_coverage": custom_metrics,
                "comparison": {
                    "coverage_improvement": custom_metrics["vocab_coverage"]
                    - bert_metrics["vocab_coverage"],
                    "unknown_reduction": bert_metrics["unknown_token_rate"]
                    - custom_metrics["unknown_token_rate"],
                },
            }
        except ImportError:
            logger.warning("Transformers library not found. Skipping BERT benchmark.")
            return None

    def _evaluate_bert_coverage(self, bert_tokenizer, texts):
        """Helper method to evaluate BERT tokenizer coverage."""
        total_tokens = 0
        unknown_tokens = 0

        for text in texts:
            tokens = bert_tokenizer.tokenize(text)
            total_tokens += len(tokens)
            unknown_tokens += tokens.count("[UNK]")

        return {
            "vocab_coverage": 100 * (1 - unknown_tokens / total_tokens),
            "unknown_token_rate": 100 * (unknown_tokens / total_tokens),
        }

    def save_metrics(self, metrics: Dict, filename: str = "tokenizer_metrics.json"):
        """Save evaluation metrics to a JSON file."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=4)
        logger.info(f"Saved metrics to {filename}")
