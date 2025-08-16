"""
Memory management utilities

This module contains utilities for memory-aware batching and resource management.
"""

from typing import List, Tuple, Generator
import sys
import logging

logger = logging.getLogger(__name__)


class MemoryManager:
    """Memory management utilities for batching."""

    @staticmethod
    def estimate_text_memory(text: str) -> int:
        """Estimate memory usage of a text string.

        Args:
            text: Input text

        Returns:
            Estimated memory usage in bytes
        """
        # Estimate based on string length and average character size
        char_size = sys.getsizeof("")  # Average size per character
        return len(text) * char_size

    @staticmethod
    def estimate_batch_memory(texts: List[str]) -> int:
        """Estimate memory usage of a batch of texts.

        Args:
            texts: List of texts

        Returns:
            Total estimated memory usage in bytes
        """
        return sum(MemoryManager.estimate_text_memory(text) for text in texts)

    @staticmethod
    def create_memory_batches(
        texts: List[str],
        max_memory: int = None,
        min_batch_size: int = 100,
        max_batch_size: int = 1000,
    ) -> Generator[List[str], None, None]:
        """Create memory-aware batches of texts.

        Args:
            texts: List of texts to batch
            max_memory: Maximum memory per batch in bytes (None for unlimited)
            min_batch_size: Minimum batch size
            max_batch_size: Maximum batch size

        Yields:
            Memory-aware batches of texts
        """
        if not texts:
            return

        current_batch = []
        current_memory = 0

        for text in texts:
            text_memory = MemoryManager.estimate_text_memory(text)

            # Check if adding this text would exceed limits
            if (
                max_memory is not None
                and current_memory + text_memory > max_memory
                and current_batch
            ):
                yield current_batch
                current_batch = [text]
                current_memory = text_memory
            else:
                current_batch.append(text)
                current_memory += text_memory

            # Check if we've reached max batch size
            if len(current_batch) >= max_batch_size:
                yield current_batch
                current_batch = []
                current_memory = 0

        # Yield remaining batch if any
        if current_batch:
            yield current_batch

    @staticmethod
    def get_available_memory() -> int:
        """Get available memory in bytes.

        Returns:
            Available memory in bytes
        """
        try:
            import psutil

            return psutil.virtual_memory().available
        except ImportError:
            logger.warning("psutil not installed, using fallback memory estimation")
            # Fallback to a reasonable default
            return 2 * 1024 * 1024 * 1024  # 2GB

    @staticmethod
    def get_recommended_batch_size(
        texts: List[str],
        target_memory_usage: float = 0.7,  # Use 70% of available memory
    ) -> int:
        """Get recommended batch size based on memory constraints.

        Args:
            texts: Sample texts to analyze
            target_memory_usage: Target memory usage ratio

        Returns:
            Recommended batch size
        """
        if not texts:
            return 1

        # Estimate average text size
        avg_text_size = (
            sum(MemoryManager.estimate_text_memory(text) for text in texts[:100]) / 100
        )

        # Calculate available memory
        available_memory = MemoryManager.get_available_memory()
        target_memory = available_memory * target_memory_usage

        # Calculate recommended batch size
        batch_size = int(target_memory / avg_text_size)
        return max(1, min(batch_size, 1000))  # Clamp between 1 and 1000
