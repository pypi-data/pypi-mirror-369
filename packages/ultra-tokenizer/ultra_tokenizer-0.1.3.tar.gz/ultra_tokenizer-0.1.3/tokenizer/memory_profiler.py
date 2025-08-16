"""
Memory profiling utilities

This module contains utilities for memory profiling and monitoring.
"""

from typing import Dict, Any, Optional
import logging
import tracemalloc
import psutil
import time

logger = logging.getLogger(__name__)


class MemoryProfiler:
    """Memory profiling utilities."""

    def __init__(self):
        """Initialize memory profiler."""
        self.tracemalloc_enabled = False
        self.memory_snapshots = []
        self.start_time = None
        self.start_memory = None

    def start(self):
        """Start memory profiling."""
        tracemalloc.start()
        self.tracemalloc_enabled = True
        self.start_time = time.time()
        self.start_memory = self.get_memory_usage()
        logger.info("Memory profiling started")

    def stop(self) -> Dict[str, Any]:
        """Stop memory profiling and return statistics.

        Returns:
            Dictionary containing memory usage statistics
        """
        if not self.tracemalloc_enabled:
            return {}

        current_memory = self.get_memory_usage()
        peak_memory = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        self.tracemalloc_enabled = False

        end_time = time.time()
        duration = end_time - self.start_time

        stats = {
            "start_memory": self.start_memory,
            "end_memory": current_memory,
            "peak_memory": peak_memory,
            "memory_growth": current_memory - self.start_memory,
            "duration": duration,
            "memory_per_second": (
                (current_memory - self.start_memory) / duration if duration > 0 else 0
            ),
        }

        logger.info(f"Memory profiling completed: {stats}")
        return stats

    def snapshot(self, tag: str = None) -> Dict[str, Any]:
        """Take a memory snapshot with optional tag.

        Args:
            tag: Optional tag for the snapshot

        Returns:
            Dictionary containing memory snapshot
        """
        if not self.tracemalloc_enabled:
            return {}

        current_memory = self.get_memory_usage()
        snapshot = {
            "timestamp": time.time(),
            "memory_usage": current_memory,
            "tag": tag,
        }
        self.memory_snapshots.append(snapshot)
        return snapshot

    @staticmethod
    def get_memory_usage() -> int:
        """Get current memory usage in bytes.

        Returns:
            Current memory usage in bytes
        """
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except:
            logger.warning("Failed to get memory usage using psutil")
            return 0

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics.

        Returns:
            Dictionary containing memory statistics
        """
        if not self.memory_snapshots:
            return {}

        return {
            "initial_memory": self.memory_snapshots[0]["memory_usage"],
            "final_memory": self.memory_snapshots[-1]["memory_usage"],
            "max_memory": max(s["memory_usage"] for s in self.memory_snapshots),
            "min_memory": min(s["memory_usage"] for s in self.memory_snapshots),
            "memory_snapshots": self.memory_snapshots,
        }
