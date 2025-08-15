"""
Compression strategies for the context compressor.
"""

from .base import CompressionStrategy
from .extractive import ExtractiveStrategy

__all__ = [
    "CompressionStrategy",
    "ExtractiveStrategy"
]