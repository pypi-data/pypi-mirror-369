"""
File Manager Package

Provides utilities for managing files, directories, compression, synchronization,
hashing, and monitoring with a progress bar.
"""

from .progress import ProgressPercentage
from . import file_ops, zip_ops, hash_ops, search_ops, stats_ops, sync_ops, monitor_ops, temp_file_utils

__all__ = [
    "ProgressPercentage",
    "file_ops", "zip_ops", "hash_ops", "search_ops",
    "stats_ops", "sync_ops", "monitor_ops", "temp_file_utils",
]