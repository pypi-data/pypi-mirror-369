"""
Tokenization utilities for text processing.
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class TokenizerBase:
    """Base class for tokenizers."""
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into tokens.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of tokens
        """
        raise NotImplementedError
    
    def count(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Input text
            
        Returns:
            int: Number of tokens
        """
        return len(self.tokenize(text))


class WhitespaceTokenizer(TokenizerBase):
    """Simple whitespace-based tokenizer."""
    
    def __init__(self, lowercase: bool = True):
        """
        Initialize tokenizer.
        
        Args:
            lowercase: Whether to convert tokens to lowercase
        """
        self.lowercase = lowercase
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text by splitting on whitespace.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of tokens
        """
        if not text:
            return []
        
        tokens = text.split()
        
        if self.lowercase:
            tokens = [token.lower() for token in tokens]
        
        return tokens


class RegexTokenizer(TokenizerBase):
    """Regex-based tokenizer for more sophisticated tokenization."""
    
    def __init__(
        self, 
        pattern: str = r'\b\w+\b',
        lowercase: bool = True,
        remove_stopwords: bool = False,
        min_token_length: int = 1
    ):
        """
        Initialize regex tokenizer.
        
        Args:
            pattern: Regex pattern for tokenization
            lowercase: Whether to convert tokens to lowercase
            remove_stopwords: Whether to remove common stopwords
            min_token_length: Minimum token length to include
        """
        self.pattern = re.compile(pattern)
        self.lowercase = lowercase
        self.remove_stopwords = remove_stopwords
        self.min_token_length = min_token_length
        
        self.stopwords = self._get_stopwords() if remove_stopwords else set()
    
    def _get_stopwords(self) -> set:
        """Get common English stopwords."""
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'would', 'could', 'should',
            'this', 'these', 'they', 'them', 'their', 'there', 'where', 'when',
            'why', 'how', 'what', 'which', 'who', 'whom', 'whose', 'i', 'me',
            'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
            'yours', 'yourself', 'yourselves', 'she', 'her', 'hers', 'herself',
            'him', 'his', 'himself', 'it', 'itself', 'they', 'them', 'their',
            'theirs', 'themselves', 'am', 'is', 'are', 'was', 'were', 'being',
            'been', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
            'doing', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'cannot', 'cant', 'wont', 'wouldnt', 'couldnt', 'shouldnt',
            'dont', 'doesnt', 'didnt', 'isnt', 'arent', 'wasnt', 'werent'
        }
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text using regex pattern.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of tokens
        """
        if not text:
            return []
        
        tokens = self.pattern.findall(text)
        
        if self.lowercase:
            tokens = [token.lower() for token in tokens]
        
        # Filter tokens
        filtered_tokens = []
        for token in tokens:
            if len(token) >= self.min_token_length:
                if not self.remove_stopwords or token not in self.stopwords:
                    filtered_tokens.append(token)
        
        return filtered_tokens


class SentenceTokenizer:
    """Tokenizer for splitting text into sentences."""
    
    def __init__(self, pattern: Optional[str] = None):
        """
        Initialize sentence tokenizer.
        
        Args:
            pattern: Custom regex pattern for sentence splitting
        """
        self.pattern = re.compile(
            pattern or r'[.!?]+\s+'
        )
    
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of sentences
        """
        if not text:
            return []
        
        sentences = self.pattern.split(text.strip())
        
        # Clean sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Ensure sentence ends with punctuation
                if not sentence[-1] in '.!?':
                    sentence += '.'
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def count(self, text: str) -> int:
        """
        Count sentences in text.
        
        Args:
            text: Input text
            
        Returns:
            int: Number of sentences
        """
        return len(self.tokenize(text))


class ApproximateTokenizer(TokenizerBase):
    """
    Approximate tokenizer that estimates token count without full tokenization.
    
    Useful for quick token counting when exact count is not required.
    Based on OpenAI's token estimation heuristics.
    """
    
    def __init__(self, chars_per_token: float = 4.0):
        """
        Initialize approximate tokenizer.
        
        Args:
            chars_per_token: Average characters per token (OpenAI uses ~4)
        """
        self.chars_per_token = chars_per_token
    
    def count(self, text: str) -> int:
        """
        Estimate token count based on character count.
        
        Args:
            text: Input text
            
        Returns:
            int: Estimated token count
        """
        if not text:
            return 0
        
        return max(1, int(len(text) / self.chars_per_token))
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text (fallback to whitespace splitting).
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of tokens
        """
        return text.split()


class TokenizerManager:
    """Manager for different tokenization strategies."""
    
    def __init__(self):
        """Initialize tokenizer manager."""
        self.tokenizers: Dict[str, TokenizerBase] = {
            'whitespace': WhitespaceTokenizer(),
            'regex': RegexTokenizer(),
            'approximate': ApproximateTokenizer()
        }
        
        self.sentence_tokenizer = SentenceTokenizer()
        self.default_tokenizer = 'whitespace'
    
    def register_tokenizer(self, name: str, tokenizer: TokenizerBase) -> None:
        """
        Register a new tokenizer.
        
        Args:
            name: Name of the tokenizer
            tokenizer: Tokenizer instance
        """
        self.tokenizers[name] = tokenizer
        logger.info(f"Registered tokenizer: {name}")
    
    def get_tokenizer(self, name: str) -> Optional[TokenizerBase]:
        """
        Get tokenizer by name.
        
        Args:
            name: Name of the tokenizer
            
        Returns:
            TokenizerBase: Tokenizer instance or None if not found
        """
        return self.tokenizers.get(name)
    
    def tokenize(
        self, 
        text: str, 
        tokenizer_name: Optional[str] = None
    ) -> List[str]:
        """
        Tokenize text using specified tokenizer.
        
        Args:
            text: Input text
            tokenizer_name: Name of tokenizer to use (default if None)
            
        Returns:
            List[str]: List of tokens
        """
        tokenizer_name = tokenizer_name or self.default_tokenizer
        tokenizer = self.tokenizers.get(tokenizer_name)
        
        if tokenizer is None:
            logger.warning(f"Tokenizer '{tokenizer_name}' not found, using default")
            tokenizer = self.tokenizers[self.default_tokenizer]
        
        return tokenizer.tokenize(text)
    
    def count_tokens(
        self, 
        text: str, 
        tokenizer_name: Optional[str] = None
    ) -> int:
        """
        Count tokens in text using specified tokenizer.
        
        Args:
            text: Input text
            tokenizer_name: Name of tokenizer to use (default if None)
            
        Returns:
            int: Number of tokens
        """
        tokenizer_name = tokenizer_name or self.default_tokenizer
        tokenizer = self.tokenizers.get(tokenizer_name)
        
        if tokenizer is None:
            logger.warning(f"Tokenizer '{tokenizer_name}' not found, using default")
            tokenizer = self.tokenizers[self.default_tokenizer]
        
        return tokenizer.count(text)
    
    def count_sentences(self, text: str) -> int:
        """
        Count sentences in text.
        
        Args:
            text: Input text
            
        Returns:
            int: Number of sentences
        """
        return self.sentence_tokenizer.count(text)
    
    def split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of sentences
        """
        return self.sentence_tokenizer.tokenize(text)
    
    def analyze_text(
        self, 
        text: str, 
        tokenizer_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze text with various metrics.
        
        Args:
            text: Input text
            tokenizer_name: Name of tokenizer to use
            
        Returns:
            Dict[str, Any]: Text analysis results
        """
        tokenizer_name = tokenizer_name or self.default_tokenizer
        
        # Basic counts
        char_count = len(text)
        word_count = self.count_tokens(text, tokenizer_name)
        sentence_count = self.count_sentences(text)
        
        # Token analysis
        tokens = self.tokenize(text, tokenizer_name)
        token_lengths = [len(token) for token in tokens]
        token_frequency = Counter(tokens)
        
        # Calculate averages
        avg_token_length = sum(token_lengths) / len(token_lengths) if token_lengths else 0
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        return {
            'character_count': char_count,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'unique_tokens': len(token_frequency),
            'avg_token_length': round(avg_token_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'token_frequency': dict(token_frequency.most_common(10)),
            'tokenizer_used': tokenizer_name
        }
    
    def compare_tokenizers(self, text: str) -> Dict[str, int]:
        """
        Compare token counts across different tokenizers.
        
        Args:
            text: Input text
            
        Returns:
            Dict[str, int]: Token counts for each tokenizer
        """
        results = {}
        
        for name, tokenizer in self.tokenizers.items():
            try:
                results[name] = tokenizer.count(text)
            except Exception as e:
                logger.error(f"Error with tokenizer {name}: {e}")
                results[name] = 0
        
        return results
    
    def estimate_compression_impact(
        self, 
        original: str, 
        compressed: str,
        tokenizer_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate the impact of compression on token count.
        
        Args:
            original: Original text
            compressed: Compressed text
            tokenizer_name: Name of tokenizer to use
            
        Returns:
            Dict[str, Any]: Compression impact analysis
        """
        tokenizer_name = tokenizer_name or self.default_tokenizer
        
        original_tokens = self.count_tokens(original, tokenizer_name)
        compressed_tokens = self.count_tokens(compressed, tokenizer_name)
        
        tokens_saved = original_tokens - compressed_tokens
        compression_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 0
        savings_percentage = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0
        
        return {
            'original_tokens': original_tokens,
            'compressed_tokens': compressed_tokens,
            'tokens_saved': tokens_saved,
            'compression_ratio': round(compression_ratio, 3),
            'savings_percentage': round(savings_percentage, 2),
            'tokenizer_used': tokenizer_name
        }
    
    def set_default_tokenizer(self, name: str) -> None:
        """
        Set default tokenizer.
        
        Args:
            name: Name of the tokenizer to set as default
            
        Raises:
            ValueError: If tokenizer doesn't exist
        """
        if name not in self.tokenizers:
            raise ValueError(f"Tokenizer '{name}' not found")
        
        self.default_tokenizer = name
        logger.info(f"Default tokenizer set to: {name}")
    
    def list_tokenizers(self) -> List[str]:
        """
        List available tokenizers.
        
        Returns:
            List[str]: List of tokenizer names
        """
        return list(self.tokenizers.keys())
    
    def __str__(self) -> str:
        """String representation."""
        return f"TokenizerManager(tokenizers={len(self.tokenizers)}, default='{self.default_tokenizer}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"TokenizerManager(tokenizers={list(self.tokenizers.keys())}, default='{self.default_tokenizer}')"


# Global tokenizer manager instance
tokenizer_manager = TokenizerManager()