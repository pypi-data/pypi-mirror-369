"""
Caching utilities for compression results.
"""

import hashlib
import time
from typing import Dict, Optional, Any, Union
from datetime import datetime, timedelta
import threading
import logging

from ..core.models import CompressionResult, BatchCompressionResult, CacheEntry

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Cache manager for storing compression results.
    
    Provides in-memory caching with TTL (time-to-live) support,
    LRU (least recently used) eviction, and cache statistics.
    """
    
    def __init__(
        self, 
        ttl: int = 3600,
        max_size: int = 1000,
        cleanup_interval: int = 300
    ):
        """
        Initialize cache manager.
        
        Args:
            ttl: Time-to-live in seconds for cache entries
            max_size: Maximum number of cache entries
            cleanup_interval: Interval in seconds between cleanup runs
        """
        self.ttl = ttl
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'cleanups': 0
        }
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self._cleanup_thread.start()
    
    def generate_key(
        self, 
        text: str, 
        target_ratio: float,
        strategy: str,
        query: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate cache key for compression parameters.
        
        Args:
            text: Input text
            target_ratio: Target compression ratio
            strategy: Strategy name
            query: Optional query
            **kwargs: Additional parameters
            
        Returns:
            str: Cache key
        """
        # Create key components
        key_data = {
            'text_hash': hashlib.md5(text.encode('utf-8')).hexdigest(),
            'target_ratio': target_ratio,
            'strategy': strategy,
            'query': query,
            'kwargs': sorted(kwargs.items()) if kwargs else None
        }
        
        # Convert to string and hash
        key_string = str(key_data)
        key_hash = hashlib.sha256(key_string.encode('utf-8')).hexdigest()
        
        return key_hash
    
    def put(
        self, 
        key: str, 
        result: Union[CompressionResult, BatchCompressionResult],
        ttl: Optional[int] = None
    ) -> None:
        """
        Store result in cache.
        
        Args:
            key: Cache key
            result: Compression result to cache
            ttl: Time-to-live override for this entry
        """
        with self._lock:
            # Check if cache is full and evict if necessary
            if len(self._cache) >= self.max_size:
                self._evict_lru()
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                result=result,
                ttl_seconds=ttl if ttl is not None else self.ttl
            )
            
            self._cache[key] = entry
            
            logger.debug(f"Cached result with key: {key[:20]}...")
    
    def get(self, key: str) -> Optional[Union[CompressionResult, BatchCompressionResult]]:
        """
        Retrieve result from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Union[CompressionResult, BatchCompressionResult]: Cached result or None
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats['misses'] += 1
                logger.debug(f"Cache miss for key: {key[:20]}...")
                return None
            
            # Check if entry is expired
            if entry.is_expired():
                del self._cache[key]
                self._stats['misses'] += 1
                logger.debug(f"Cache entry expired for key: {key[:20]}...")
                return None
            
            # Update access statistics
            entry.access()
            self._stats['hits'] += 1
            
            logger.debug(f"Cache hit for key: {key[:20]}...")
            return entry.result
    
    def delete(self, key: str) -> bool:
        """
        Delete entry from cache.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if entry was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Deleted cache entry: {key[:20]}...")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return
        
        # Find entry with oldest last_accessed time
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        
        del self._cache[lru_key]
        self._stats['evictions'] += 1
        
        logger.debug(f"Evicted LRU entry: {lru_key[:20]}...")
    
    def _periodic_cleanup(self) -> None:
        """Periodic cleanup of expired entries."""
        while True:
            try:
                time.sleep(self.cleanup_interval)
                self.cleanup_expired()
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            int: Number of entries removed
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                self._stats['cleanups'] += 1
                logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict[str, Any]: Cache statistics
        """
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'ttl': self.ttl,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate_percent': round(hit_rate, 2),
                'evictions': self._stats['evictions'],
                'cleanups': self._stats['cleanups'],
                'memory_usage_estimate': self._estimate_memory_usage()
            }
    
    def _estimate_memory_usage(self) -> str:
        """
        Estimate memory usage of cache.
        
        Returns:
            str: Human-readable memory usage estimate
        """
        # Rough estimate based on average entry size
        if not self._cache:
            return "0 KB"
        
        # Sample a few entries to estimate average size
        sample_keys = list(self._cache.keys())[:min(10, len(self._cache))]
        total_estimated = 0
        
        for key in sample_keys:
            entry = self._cache[key]
            # Rough estimation of object size
            estimated_size = (
                len(key) +
                len(entry.result.original_text) +
                len(entry.result.compressed_text) +
                500  # Overhead for other fields
            )
            total_estimated += estimated_size
        
        avg_size = total_estimated / len(sample_keys)
        total_size = avg_size * len(self._cache)
        
        # Convert to human-readable format
        if total_size < 1024:
            return f"{int(total_size)} B"
        elif total_size < 1024 * 1024:
            return f"{int(total_size / 1024)} KB"
        else:
            return f"{int(total_size / (1024 * 1024))} MB"
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get detailed cache information.
        
        Returns:
            Dict[str, Any]: Detailed cache information
        """
        with self._lock:
            entries_info = []
            
            for key, entry in self._cache.items():
                entries_info.append({
                    'key': key[:20] + "...",
                    'created_at': entry.created_at.isoformat(),
                    'last_accessed': entry.last_accessed.isoformat(),
                    'access_count': entry.access_count,
                    'ttl_seconds': entry.ttl_seconds,
                    'expired': entry.is_expired(),
                    'result_type': type(entry.result).__name__
                })
            
            # Sort by last accessed (most recent first)
            entries_info.sort(key=lambda x: x['last_accessed'], reverse=True)
            
            return {
                'stats': self.get_stats(),
                'entries': entries_info
            }
    
    def reset_stats(self) -> None:
        """Reset cache statistics."""
        with self._lock:
            self._stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'cleanups': 0
            }
            logger.info("Cache statistics reset")
    
    def resize(self, new_max_size: int) -> None:
        """
        Resize cache maximum size.
        
        Args:
            new_max_size: New maximum cache size
        """
        with self._lock:
            self.max_size = new_max_size
            
            # Evict entries if cache is now too large
            while len(self._cache) > self.max_size:
                self._evict_lru()
            
            logger.info(f"Cache resized to {new_max_size}")
    
    def set_ttl(self, new_ttl: int) -> None:
        """
        Set new default TTL for future entries.
        
        Args:
            new_ttl: New TTL in seconds
        """
        self.ttl = new_ttl
        logger.info(f"Cache TTL updated to {new_ttl} seconds")
    
    def __len__(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self._lock:
            return key in self._cache and not self._cache[key].is_expired()
    
    def __str__(self) -> str:
        """String representation."""
        return f"CacheManager(size={len(self._cache)}, max_size={self.max_size}, ttl={self.ttl})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        stats = self.get_stats()
        return (
            f"CacheManager(size={len(self._cache)}, max_size={self.max_size}, "
            f"ttl={self.ttl}, hit_rate={stats['hit_rate_percent']}%)"
        )