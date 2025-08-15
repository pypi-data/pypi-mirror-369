"""
Extractive compression strategy using sentence selection and scoring.
"""

import re
import logging
from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from collections import Counter
import math

from .base import CompressionStrategy
from ..core.models import StrategyMetadata

logger = logging.getLogger(__name__)


class ExtractiveStrategy(CompressionStrategy):
    """
    Extractive compression strategy that selects important sentences based on
    various scoring methods like TF-IDF, position, length, and query relevance.
    
    This strategy works by:
    1. Splitting text into sentences
    2. Scoring each sentence based on multiple criteria
    3. Selecting top-scoring sentences to meet target ratio
    4. Reassembling selected sentences in original order
    """
    
    def __init__(
        self,
        scoring_method: str = "tfidf",
        min_sentence_length: int = 10,
        max_sentence_length: int = 500,
        position_bias: float = 0.2,
        length_bias: float = 0.1,
        query_weight: float = 0.3,
        **kwargs
    ):
        """
        Initialize extractive strategy.
        
        Args:
            scoring_method: Scoring method ("tfidf", "frequency", "position", "combined")
            min_sentence_length: Minimum sentence length to consider
            max_sentence_length: Maximum sentence length to consider
            position_bias: Weight for sentence position scoring
            length_bias: Weight for sentence length scoring
            query_weight: Weight for query relevance scoring
        """
        self.scoring_method = scoring_method
        self.min_sentence_length = min_sentence_length
        self.max_sentence_length = max_sentence_length
        self.position_bias = position_bias
        self.length_bias = length_bias
        self.query_weight = query_weight
        
        # Initialize tokenization patterns
        self.sentence_pattern = re.compile(r'[.!?]+\s+')
        self.word_pattern = re.compile(r'\b\w+\b')
        self.stopwords = self._get_stopwords()
        
        super().__init__(**kwargs)
    
    def _create_metadata(self) -> StrategyMetadata:
        """Create strategy metadata."""
        return StrategyMetadata(
            name="extractive",
            description="Sentence-based extractive compression using TF-IDF and position scoring",
            version="1.0.0",
            author="Context Compressor Team",
            supported_languages=["en"],
            min_text_length=100,
            max_text_length=50000,
            optimal_compression_ratios=[0.3, 0.5, 0.7],
            requires_query=False,
            supports_batch=True,
            supports_streaming=False,
            computational_complexity="medium",
            memory_requirements="low",
            dependencies=[],
            tags=["extractive", "sentence-based", "tfidf", "statistical"]
        )
    
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
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of sentences
        """
        # Simple sentence splitting using regex
        sentences = self.sentence_pattern.split(text.strip())
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) >= self.min_sentence_length and 
                len(sentence) <= self.max_sentence_length):
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of words
        """
        words = self.word_pattern.findall(text.lower())
        return [word for word in words if word not in self.stopwords and len(word) > 2]
    
    def _calculate_tfidf_scores(
        self, 
        sentences: List[str], 
        query_words: Optional[List[str]] = None
    ) -> np.ndarray:
        """
        Calculate TF-IDF scores for sentences.
        
        Args:
            sentences: List of sentences
            query_words: Optional query words for relevance scoring
            
        Returns:
            np.ndarray: TF-IDF scores for each sentence
        """
        if not sentences:
            return np.array([])
        
        # Tokenize sentences
        sentence_words = [self._tokenize(sentence) for sentence in sentences]
        
        # Build vocabulary
        all_words = set()
        for words in sentence_words:
            all_words.update(words)
        
        vocab = sorted(list(all_words))
        word_to_idx = {word: idx for idx, word in enumerate(vocab)}
        
        # Calculate term frequencies
        tf_matrix = np.zeros((len(sentences), len(vocab)))
        for sent_idx, words in enumerate(sentence_words):
            word_count = Counter(words)
            for word, count in word_count.items():
                if word in word_to_idx:
                    tf_matrix[sent_idx, word_to_idx[word]] = count / len(words)
        
        # Calculate inverse document frequencies
        idf_vector = np.zeros(len(vocab))
        for word_idx, word in enumerate(vocab):
            doc_count = sum(1 for words in sentence_words if word in words)
            if doc_count > 0:
                idf_vector[word_idx] = math.log(len(sentences) / doc_count)
        
        # Calculate TF-IDF matrix
        tfidf_matrix = tf_matrix * idf_vector
        
        # Calculate sentence scores as sum of TF-IDF values
        sentence_scores = np.sum(tfidf_matrix, axis=1)
        
        # Boost scores for query relevance if query provided
        if query_words:
            query_boost = np.zeros(len(sentences))
            for sent_idx, words in enumerate(sentence_words):
                relevance = sum(1 for word in query_words if word in words)
                query_boost[sent_idx] = relevance / len(query_words) if query_words else 0
            
            sentence_scores = (
                (1 - self.query_weight) * sentence_scores + 
                self.query_weight * query_boost * np.max(sentence_scores)
            )
        
        return sentence_scores
    
    def _calculate_frequency_scores(self, sentences: List[str]) -> np.ndarray:
        """
        Calculate frequency-based scores for sentences.
        
        Args:
            sentences: List of sentences
            
        Returns:
            np.ndarray: Frequency scores for each sentence
        """
        # Get all words from all sentences
        all_words = []
        sentence_words = []
        
        for sentence in sentences:
            words = self._tokenize(sentence)
            sentence_words.append(words)
            all_words.extend(words)
        
        # Calculate word frequencies
        word_freq = Counter(all_words)
        
        # Score sentences based on word frequencies
        scores = np.zeros(len(sentences))
        for i, words in enumerate(sentence_words):
            if words:
                scores[i] = sum(word_freq[word] for word in words) / len(words)
        
        return scores
    
    def _calculate_position_scores(self, num_sentences: int) -> np.ndarray:
        """
        Calculate position-based scores (beginning and end are more important).
        
        Args:
            num_sentences: Number of sentences
            
        Returns:
            np.ndarray: Position scores
        """
        scores = np.zeros(num_sentences)
        
        for i in range(num_sentences):
            # Higher scores for beginning and end
            if i < num_sentences * 0.1:  # First 10%
                scores[i] = 1.0
            elif i > num_sentences * 0.9:  # Last 10%
                scores[i] = 0.8
            elif i < num_sentences * 0.3:  # First 30%
                scores[i] = 0.6
            else:
                scores[i] = 0.3
        
        return scores
    
    def _calculate_length_scores(self, sentences: List[str]) -> np.ndarray:
        """
        Calculate length-based scores (prefer medium-length sentences).
        
        Args:
            sentences: List of sentences
            
        Returns:
            np.ndarray: Length scores
        """
        lengths = np.array([len(sentence) for sentence in sentences])
        
        # Prefer sentences of medium length
        mean_length = np.mean(lengths)
        std_length = np.std(lengths)
        
        scores = 1.0 - np.abs(lengths - mean_length) / (2 * std_length + 1e-6)
        scores = np.clip(scores, 0.1, 1.0)  # Ensure positive scores
        
        return scores
    
    def _score_sentences(
        self, 
        sentences: List[str], 
        query: Optional[str] = None
    ) -> np.ndarray:
        """
        Score sentences using the selected method.
        
        Args:
            sentences: List of sentences
            query: Optional query for relevance scoring
            
        Returns:
            np.ndarray: Sentence scores
        """
        if not sentences:
            return np.array([])
        
        query_words = self._tokenize(query) if query else None
        
        if self.scoring_method == "tfidf":
            return self._calculate_tfidf_scores(sentences, query_words)
        
        elif self.scoring_method == "frequency":
            return self._calculate_frequency_scores(sentences)
        
        elif self.scoring_method == "position":
            return self._calculate_position_scores(len(sentences))
        
        elif self.scoring_method == "combined":
            # Combine multiple scoring methods
            tfidf_scores = self._calculate_tfidf_scores(sentences, query_words)
            position_scores = self._calculate_position_scores(len(sentences))
            length_scores = self._calculate_length_scores(sentences)
            
            # Normalize scores
            if np.max(tfidf_scores) > 0:
                tfidf_scores = tfidf_scores / np.max(tfidf_scores)
            
            # Combine with weights
            combined_scores = (
                (1.0 - self.position_bias - self.length_bias) * tfidf_scores +
                self.position_bias * position_scores +
                self.length_bias * length_scores
            )
            
            return combined_scores
        
        else:
            raise ValueError(f"Unknown scoring method: {self.scoring_method}")
    
    def _select_sentences(
        self, 
        sentences: List[str], 
        scores: np.ndarray, 
        target_ratio: float
    ) -> Tuple[List[int], List[str]]:
        """
        Select sentences based on scores and target ratio.
        
        Args:
            sentences: List of sentences
            scores: Sentence scores
            target_ratio: Target compression ratio
            
        Returns:
            Tuple[List[int], List[str]]: Selected sentence indices and sentences
        """
        if len(sentences) == 0:
            return [], []
        
        # Calculate target number of sentences
        target_count = max(1, int(len(sentences) * target_ratio))
        
        # Sort sentences by score (descending)
        sorted_indices = np.argsort(scores)[::-1]
        
        # Select top sentences
        selected_indices = sorted_indices[:target_count]
        
        # Sort selected indices to maintain original order
        selected_indices = sorted(selected_indices)
        
        selected_sentences = [sentences[i] for i in selected_indices]
        
        return selected_indices, selected_sentences
    
    def _compress_text(
        self, 
        text: str, 
        target_ratio: float,
        query: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Compress text using extractive strategy.
        
        Args:
            text: Input text
            target_ratio: Target compression ratio
            query: Optional query for relevance
            
        Returns:
            str: Compressed text
        """
        # Split into sentences
        sentences = self._split_sentences(text)
        
        if not sentences:
            return text
        
        if len(sentences) == 1:
            # If only one sentence, return it (can't compress further)
            return sentences[0]
        
        # Score sentences
        scores = self._score_sentences(sentences, query)
        
        # Select sentences
        selected_indices, selected_sentences = self._select_sentences(
            sentences, scores, target_ratio
        )
        
        # Reassemble text
        compressed_text = '. '.join(selected_sentences)
        
        # Ensure proper ending punctuation
        if compressed_text and not compressed_text.endswith(('.', '!', '?')):
            compressed_text += '.'
        
        return compressed_text
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens using simple whitespace splitting.
        
        Args:
            text: Input text
            
        Returns:
            int: Number of tokens
        """
        return len(text.split())
    
    def get_sentence_scores(
        self, 
        text: str, 
        query: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Get sentences with their scores for debugging.
        
        Args:
            text: Input text
            query: Optional query
            
        Returns:
            List[Tuple[str, float]]: List of (sentence, score) tuples
        """
        sentences = self._split_sentences(text)
        scores = self._score_sentences(sentences, query)
        
        return list(zip(sentences, scores))
    
    def explain_compression(
        self, 
        text: str, 
        target_ratio: float,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provide detailed explanation of compression process.
        
        Args:
            text: Input text
            target_ratio: Target compression ratio
            query: Optional query
            
        Returns:
            Dict[str, Any]: Compression explanation
        """
        sentences = self._split_sentences(text)
        scores = self._score_sentences(sentences, query)
        selected_indices, selected_sentences = self._select_sentences(
            sentences, scores, target_ratio
        )
        
        return {
            'total_sentences': len(sentences),
            'selected_sentences': len(selected_sentences),
            'compression_ratio': len(selected_sentences) / len(sentences) if sentences else 0,
            'selected_indices': selected_indices,
            'sentence_scores': list(zip(sentences, scores.tolist())),
            'scoring_method': self.scoring_method,
            'query_provided': query is not None,
            'parameters': {
                'min_sentence_length': self.min_sentence_length,
                'max_sentence_length': self.max_sentence_length,
                'position_bias': self.position_bias,
                'length_bias': self.length_bias,
                'query_weight': self.query_weight
            }
        }