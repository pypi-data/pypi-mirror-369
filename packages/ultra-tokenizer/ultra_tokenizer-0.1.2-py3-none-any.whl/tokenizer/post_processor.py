"""
Post-processing utilities

This module contains the PostProcessor class that handles token post-processing
and normalization after tokenization.
"""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class PostProcessor:
    """Post-processing utilities."""

    def __init__(self):
        """Initialize post-processor."""
        pass

    def post_process(self, tokens: List[str]) -> List[str]:
        """Apply post-processing rules to tokens.

        Args:
            tokens: List of tokens to post-process

        Returns:
            Post-processed tokens
        """
        if not tokens:
            return []

        # Apply post-processing rules
        tokens = self._normalize_tokens(tokens)
        tokens = self._handle_special_tokens(tokens)

        return tokens

    def _normalize_tokens(self, tokens: List[str]) -> List[str]:
        """Normalize tokens."""
        # Remove empty tokens
        tokens = [t for t in tokens if t]
        # Convert to lowercase
        tokens = [t.lower() for t in tokens]
        return tokens

    def _handle_special_tokens(self, tokens: List[str]) -> List[str]:
        """Handle special tokens."""
        # Replace special tokens with their original values
        special_tokens = {"[URL]": "URL", "[EMAIL]": "EMAIL", "[NUM]": "NUMBER"}

        return [special_tokens.get(t, t) for t in tokens]
