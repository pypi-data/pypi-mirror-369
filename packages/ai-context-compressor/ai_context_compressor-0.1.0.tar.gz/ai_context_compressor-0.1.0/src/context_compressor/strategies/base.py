"""
Base abstract class for compression strategies.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
import time
import logging

from ..core.models import CompressionResult, StrategyMetadata, BatchCompressionResult

logger = logging.getLogger(__name__)


class CompressionStrategy(ABC):
    """
    Abstract base class for all compression strategies.
    
    All compression strategies must inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, **kwargs):
        """Initialize the compression strategy."""
        self._metadata = self._create_metadata()
        self._config = kwargs
        self._is_initialized = False
        
    @property
    def metadata(self) -> StrategyMetadata:
        """Get strategy metadata."""
        return self._metadata
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get strategy configuration."""
        return self._config.copy()
    
    @property
    def is_initialized(self) -> bool:
        """Check if strategy is initialized."""
        return self._is_initialized
    
    @abstractmethod
    def _create_metadata(self) -> StrategyMetadata:
        """
        Create strategy metadata.
        
        Returns:
            StrategyMetadata: Metadata describing this strategy
        """
        pass
    
    def initialize(self) -> None:
        """
        Initialize the strategy.
        
        This method is called before the first compression operation.
        Override this method to perform any initialization tasks like
        loading models, setting up tokenizers, etc.
        """
        logger.info(f"Initializing strategy: {self.metadata.name}")
        self._is_initialized = True
    
    def cleanup(self) -> None:
        """
        Cleanup resources.
        
        This method is called when the strategy is no longer needed.
        Override this method to perform cleanup tasks.
        """
        logger.info(f"Cleaning up strategy: {self.metadata.name}")
        self._is_initialized = False
    
    @abstractmethod
    def _compress_text(
        self, 
        text: str, 
        target_ratio: float,
        query: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Compress the given text.
        
        Args:
            text: The input text to compress
            target_ratio: Target compression ratio (0.0 to 1.0)
            query: Optional query for context-aware compression
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            str: The compressed text
        """
        pass
    
    def compress(
        self, 
        text: str, 
        target_ratio: float,
        query: Optional[str] = None,
        include_metadata: bool = True,
        **kwargs
    ) -> CompressionResult:
        """
        Compress text and return detailed results.
        
        Args:
            text: The input text to compress
            target_ratio: Target compression ratio (0.0 to 1.0)
            query: Optional query for context-aware compression
            include_metadata: Whether to include strategy metadata in result
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            CompressionResult: Detailed compression results
            
        Raises:
            ValueError: If target_ratio is not between 0.0 and 1.0
            RuntimeError: If strategy is not initialized
        """
        # Validate inputs
        if not (0.0 < target_ratio < 1.0):
            raise ValueError(f"Target ratio must be between 0.0 and 1.0, got {target_ratio}")
        
        if not self.is_initialized:
            self.initialize()
        
        # Validate text length
        if len(text.strip()) < self.metadata.min_text_length:
            raise ValueError(
                f"Text too short for {self.metadata.name} strategy. "
                f"Minimum length: {self.metadata.min_text_length}, got: {len(text.strip())}"
            )
        
        if (self.metadata.max_text_length is not None and 
            len(text) > self.metadata.max_text_length):
            logger.warning(
                f"Text length ({len(text)}) exceeds recommended maximum "
                f"({self.metadata.max_text_length}) for {self.metadata.name} strategy"
            )
        
        # Count original tokens
        original_tokens = self._count_tokens(text)
        
        # Perform compression with timing
        start_time = time.time()
        try:
            compressed_text = self._compress_text(text, target_ratio, query, **kwargs)
        except Exception as e:
            logger.error(f"Compression failed with {self.metadata.name}: {e}")
            raise
        
        processing_time = time.time() - start_time
        
        # Count compressed tokens and calculate actual ratio
        compressed_tokens = self._count_tokens(compressed_text)
        actual_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 0.0
        
        # Create result
        result = CompressionResult(
            original_text=text,
            compressed_text=compressed_text,
            strategy_used=self.metadata.name,
            target_ratio=target_ratio,
            actual_ratio=actual_ratio,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            processing_time=processing_time,
            query=query,
            strategy_metadata=self.metadata if include_metadata else None,
            metadata={'strategy_config': self.config}
        )
        
        logger.info(
            f"Compression completed: {original_tokens} -> {compressed_tokens} tokens "
            f"({actual_ratio:.2%} ratio) in {processing_time:.2f}s"
        )
        
        return result
    
    def compress_batch(
        self, 
        texts: List[str], 
        target_ratio: float,
        query: Optional[str] = None,
        parallel: bool = True,
        max_workers: Optional[int] = None,
        include_metadata: bool = True,
        **kwargs
    ) -> BatchCompressionResult:
        """
        Compress multiple texts.
        
        Args:
            texts: List of input texts to compress
            target_ratio: Target compression ratio (0.0 to 1.0)
            query: Optional query for context-aware compression
            parallel: Whether to process texts in parallel
            max_workers: Maximum number of parallel workers
            include_metadata: Whether to include strategy metadata in results
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            BatchCompressionResult: Batch compression results
        """
        if not self.metadata.supports_batch:
            raise NotImplementedError(
                f"Strategy {self.metadata.name} does not support batch processing"
            )
        
        start_time = time.time()
        results = []
        failed_items = []
        
        if parallel and len(texts) > 1:
            results, failed_items = self._compress_batch_parallel(
                texts, target_ratio, query, max_workers, include_metadata, **kwargs
            )
        else:
            results, failed_items = self._compress_batch_sequential(
                texts, target_ratio, query, include_metadata, **kwargs
            )
        
        total_processing_time = time.time() - start_time
        
        return BatchCompressionResult(
            results=results,
            total_processing_time=total_processing_time,
            strategy_used=self.metadata.name,
            target_ratio=target_ratio,
            parallel_processing=parallel and len(texts) > 1,
            failed_items=failed_items,
            metadata={'strategy_config': self.config}
        )
    
    def _compress_batch_sequential(
        self, 
        texts: List[str], 
        target_ratio: float,
        query: Optional[str],
        include_metadata: bool,
        **kwargs
    ) -> tuple[List[CompressionResult], List[Dict[str, Any]]]:
        """Compress texts sequentially."""
        results = []
        failed_items = []
        
        for i, text in enumerate(texts):
            try:
                result = self.compress(text, target_ratio, query, include_metadata, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to compress text {i}: {e}")
                failed_items.append({
                    'index': i,
                    'text': text[:100] + "..." if len(text) > 100 else text,
                    'error': str(e)
                })
        
        return results, failed_items
    
    def _compress_batch_parallel(
        self, 
        texts: List[str], 
        target_ratio: float,
        query: Optional[str],
        max_workers: Optional[int],
        include_metadata: bool,
        **kwargs
    ) -> tuple[List[CompressionResult], List[Dict[str, Any]]]:
        """Compress texts in parallel."""
        import concurrent.futures
        
        results = []
        failed_items = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(
                    self.compress, text, target_ratio, query, include_metadata, **kwargs
                ): i 
                for i, text in enumerate(texts)
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to compress text {index}: {e}")
                    failed_items.append({
                        'index': index,
                        'text': texts[index][:100] + "..." if len(texts[index]) > 100 else texts[index],
                        'error': str(e)
                    })
        
        # Sort results by original order
        results.sort(key=lambda x: texts.index(x.original_text))
        
        return results, failed_items
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Default implementation uses simple whitespace splitting.
        Override this method to use more sophisticated tokenization.
        
        Args:
            text: The text to tokenize
            
        Returns:
            int: Number of tokens
        """
        return len(text.split())
    
    def validate_parameters(self, target_ratio: float, **kwargs) -> None:
        """
        Validate compression parameters.
        
        Args:
            target_ratio: Target compression ratio
            **kwargs: Additional parameters
            
        Raises:
            ValueError: If parameters are invalid
        """
        if not (0.0 < target_ratio < 1.0):
            raise ValueError(f"Target ratio must be between 0.0 and 1.0, got {target_ratio}")
        
        if target_ratio not in self.metadata.optimal_compression_ratios:
            logger.warning(
                f"Target ratio {target_ratio} is not in optimal range for {self.metadata.name}. "
                f"Optimal ratios: {self.metadata.optimal_compression_ratios}"
            )
    
    def get_recommended_ratio(self, text_length: int) -> float:
        """
        Get recommended compression ratio based on text length.
        
        Args:
            text_length: Length of input text
            
        Returns:
            float: Recommended compression ratio
        """
        if text_length < 1000:
            return max(self.metadata.optimal_compression_ratios)
        elif text_length < 5000:
            return self.metadata.optimal_compression_ratios[len(self.metadata.optimal_compression_ratios) // 2]
        else:
            return min(self.metadata.optimal_compression_ratios)
    
    def __str__(self) -> str:
        """String representation of the strategy."""
        return f"{self.metadata.name} v{self.metadata.version}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"{self.__class__.__name__}(name='{self.metadata.name}', "
            f"version='{self.metadata.version}', "
            f"initialized={self.is_initialized})"
        )