"""
Quality evaluation for compression results.
"""

import re
import math
from typing import List, Dict, Optional, Set, Tuple, Any
from collections import Counter
import logging

from .models import QualityMetrics

logger = logging.getLogger(__name__)


class QualityEvaluator:
    """
    Evaluator for assessing compression quality using various metrics.
    
    Provides comprehensive quality assessment including semantic similarity,
    ROUGE scores, entity preservation, and readability metrics.
    """
    
    def __init__(
        self,
        semantic_weight: float = 0.3,
        rouge_weight: float = 0.3,
        entity_weight: float = 0.2,
        readability_weight: float = 0.2
    ):
        """
        Initialize quality evaluator.
        
        Args:
            semantic_weight: Weight for semantic similarity score
            rouge_weight: Weight for ROUGE scores
            entity_weight: Weight for entity preservation score
            readability_weight: Weight for readability score
        """
        self.semantic_weight = semantic_weight
        self.rouge_weight = rouge_weight
        self.entity_weight = entity_weight
        self.readability_weight = readability_weight
        
        # Ensure weights sum to 1.0
        total_weight = sum([semantic_weight, rouge_weight, entity_weight, readability_weight])
        if abs(total_weight - 1.0) > 1e-6:
            logger.warning(f"Quality weights sum to {total_weight}, not 1.0. Normalizing.")
            self.semantic_weight /= total_weight
            self.rouge_weight /= total_weight
            self.entity_weight /= total_weight
            self.readability_weight /= total_weight
    
    def evaluate(
        self,
        original: str,
        compressed: str,
        query: Optional[str] = None
    ) -> QualityMetrics:
        """
        Evaluate compression quality.
        
        Args:
            original: Original text
            compressed: Compressed text
            query: Optional query for context-aware evaluation
            
        Returns:
            QualityMetrics: Comprehensive quality metrics
        """
        # Calculate individual metrics
        semantic_similarity = self._calculate_semantic_similarity(original, compressed)
        rouge_scores = self._calculate_rouge_scores(original, compressed)
        entity_preservation = self._calculate_entity_preservation(original, compressed)
        readability_score = self._calculate_readability(compressed)
        compression_ratio = self._calculate_compression_ratio(original, compressed)
        
        # Calculate overall score
        overall_score = (
            self.semantic_weight * semantic_similarity +
            self.rouge_weight * rouge_scores['rouge_l'] +  # Use ROUGE-L for overall
            self.entity_weight * entity_preservation +
            self.readability_weight * (readability_score / 100.0)  # Normalize readability
        )
        
        return QualityMetrics(
            semantic_similarity=semantic_similarity,
            rouge_1=rouge_scores['rouge_1'],
            rouge_2=rouge_scores['rouge_2'],
            rouge_l=rouge_scores['rouge_l'],
            entity_preservation_rate=entity_preservation,
            readability_score=readability_score,
            compression_ratio=compression_ratio,
            overall_score=overall_score
        )
    
    def _calculate_semantic_similarity(self, original: str, compressed: str) -> float:
        """
        Calculate semantic similarity using simple word overlap.
        
        This is a basic implementation. In production, you might want to use
        sentence embeddings (BERT, Sentence-BERT) for better semantic understanding.
        
        Args:
            original: Original text
            compressed: Compressed text
            
        Returns:
            float: Semantic similarity score (0.0 to 1.0)
        """
        # Tokenize and normalize
        original_words = set(self._normalize_text(original).split())
        compressed_words = set(self._normalize_text(compressed).split())
        
        if not original_words:
            return 1.0 if not compressed_words else 0.0
        
        # Calculate Jaccard similarity
        intersection = original_words.intersection(compressed_words)
        union = original_words.union(compressed_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_rouge_scores(self, original: str, compressed: str) -> Dict[str, float]:
        """
        Calculate ROUGE scores for compression evaluation.
        
        Args:
            original: Original text (reference)
            compressed: Compressed text (candidate)
            
        Returns:
            Dict[str, float]: ROUGE-1, ROUGE-2, and ROUGE-L scores
        """
        # Tokenize texts
        original_tokens = self._normalize_text(original).split()
        compressed_tokens = self._normalize_text(compressed).split()
        
        # ROUGE-1 (unigram overlap)
        rouge_1 = self._calculate_rouge_n(original_tokens, compressed_tokens, n=1)
        
        # ROUGE-2 (bigram overlap)
        rouge_2 = self._calculate_rouge_n(original_tokens, compressed_tokens, n=2)
        
        # ROUGE-L (longest common subsequence)
        rouge_l = self._calculate_rouge_l(original_tokens, compressed_tokens)
        
        return {
            'rouge_1': rouge_1,
            'rouge_2': rouge_2,
            'rouge_l': rouge_l
        }
    
    def _calculate_rouge_n(self, reference: List[str], candidate: List[str], n: int) -> float:
        """
        Calculate ROUGE-N score.
        
        Args:
            reference: Reference tokens
            candidate: Candidate tokens
            n: N-gram size
            
        Returns:
            float: ROUGE-N F1 score
        """
        if n > len(reference) or n > len(candidate):
            return 0.0
        
        # Generate n-grams
        ref_ngrams = self._get_ngrams(reference, n)
        cand_ngrams = self._get_ngrams(candidate, n)
        
        if not ref_ngrams:
            return 1.0 if not cand_ngrams else 0.0
        
        # Calculate overlap
        overlap = sum((ref_ngrams & cand_ngrams).values())
        
        # Calculate precision and recall
        precision = overlap / sum(cand_ngrams.values()) if cand_ngrams else 0.0
        recall = overlap / sum(ref_ngrams.values()) if ref_ngrams else 0.0
        
        # Calculate F1 score
        if precision + recall == 0:
            return 0.0
        
        f1 = 2 * (precision * recall) / (precision + recall)
        return f1
    
    def _calculate_rouge_l(self, reference: List[str], candidate: List[str]) -> float:
        """
        Calculate ROUGE-L score based on longest common subsequence.
        
        Args:
            reference: Reference tokens
            candidate: Candidate tokens
            
        Returns:
            float: ROUGE-L F1 score
        """
        if not reference or not candidate:
            return 1.0 if not reference and not candidate else 0.0
        
        # Calculate LCS length
        lcs_length = self._lcs_length(reference, candidate)
        
        # Calculate precision and recall
        precision = lcs_length / len(candidate)
        recall = lcs_length / len(reference)
        
        # Calculate F1 score
        if precision + recall == 0:
            return 0.0
        
        f1 = 2 * (precision * recall) / (precision + recall)
        return f1
    
    def _get_ngrams(self, tokens: List[str], n: int) -> Counter:
        """
        Get n-grams from token list.
        
        Args:
            tokens: List of tokens
            n: N-gram size
            
        Returns:
            Counter: N-gram counts
        """
        if n > len(tokens):
            return Counter()
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            ngrams.append(ngram)
        
        return Counter(ngrams)
    
    def _lcs_length(self, seq1: List[str], seq2: List[str]) -> int:
        """
        Calculate longest common subsequence length.
        
        Args:
            seq1: First sequence
            seq2: Second sequence
            
        Returns:
            int: LCS length
        """
        m, n = len(seq1), len(seq2)
        
        # Create DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def _calculate_entity_preservation(self, original: str, compressed: str) -> float:
        """
        Calculate entity preservation rate.
        
        Uses simple pattern matching for common entity types.
        In production, you might want to use NER models.
        
        Args:
            original: Original text
            compressed: Compressed text
            
        Returns:
            float: Entity preservation rate (0.0 to 1.0)
        """
        # Extract entities using patterns
        original_entities = self._extract_entities(original)
        compressed_entities = self._extract_entities(compressed)
        
        if not original_entities:
            return 1.0
        
        # Calculate preservation rate
        preserved = len(original_entities.intersection(compressed_entities))
        preservation_rate = preserved / len(original_entities)
        
        return preservation_rate
    
    def _extract_entities(self, text: str) -> Set[str]:
        """
        Extract entities from text using pattern matching.
        
        Args:
            text: Input text
            
        Returns:
            Set[str]: Set of extracted entities
        """
        entities = set()
        
        # Numbers (including dates, years, percentages)
        number_pattern = r'\b\d+(?:\.\d+)?(?:%|\$|€|£)?\b'
        numbers = re.findall(number_pattern, text)
        entities.update(numbers)
        
        # Capitalized words (potential proper nouns)
        proper_noun_pattern = r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b'
        proper_nouns = re.findall(proper_noun_pattern, text)
        entities.update(proper_nouns)
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        entities.update(emails)
        
        # URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+|www\.[^\s<>"{}|\\^`[\]]+'
        urls = re.findall(url_pattern, text)
        entities.update(urls)
        
        # Dates (simple patterns)
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY, MM-DD-YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD, YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, text)
            entities.update(dates)
        
        return entities
    
    def _calculate_readability(self, text: str) -> float:
        """
        Calculate readability score using Flesch Reading Ease formula.
        
        Args:
            text: Input text
            
        Returns:
            float: Flesch Reading Ease score (0-100, higher is better)
        """
        if not text.strip():
            return 0.0
        
        # Count sentences
        sentence_pattern = r'[.!?]+\s*'
        sentences = re.split(sentence_pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        if sentence_count == 0:
            return 0.0
        
        # Count words and syllables
        words = text.split()
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
        
        syllable_count = sum(self._count_syllables(word) for word in words)
        
        # Calculate average sentence length and syllables per word
        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count
        
        # Flesch Reading Ease formula
        flesch_score = (
            206.835 - 
            (1.015 * avg_sentence_length) - 
            (84.6 * avg_syllables_per_word)
        )
        
        # Clamp to 0-100 range
        return max(0.0, min(100.0, flesch_score))
    
    def _count_syllables(self, word: str) -> int:
        """
        Estimate syllable count for a word.
        
        Args:
            word: Input word
            
        Returns:
            int: Estimated syllable count
        """
        word = word.lower().strip()
        
        if not word:
            return 0
        
        # Remove non-alphabetic characters
        word = re.sub(r'[^a-z]', '', word)
        
        if not word:
            return 0
        
        # Count vowel groups
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        # Every word has at least one syllable
        return max(1, syllable_count)
    
    def _calculate_compression_ratio(self, original: str, compressed: str) -> float:
        """
        Calculate actual compression ratio.
        
        Args:
            original: Original text
            compressed: Compressed text
            
        Returns:
            float: Compression ratio (compressed length / original length)
        """
        original_length = len(original.split())
        compressed_length = len(compressed.split())
        
        if original_length == 0:
            return 1.0 if compressed_length == 0 else float('inf')
        
        return compressed_length / original_length
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Input text
            
        Returns:
            str: Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation for word comparison
        text = re.sub(r'[^\w\s]', '', text)
        
        return text.strip()
    
    def get_detailed_analysis(
        self,
        original: str,
        compressed: str,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed quality analysis with explanations.
        
        Args:
            original: Original text
            compressed: Compressed text
            query: Optional query
            
        Returns:
            Dict[str, Any]: Detailed analysis
        """
        metrics = self.evaluate(original, compressed, query)
        
        # Get component scores
        semantic_sim = self._calculate_semantic_similarity(original, compressed)
        rouge_scores = self._calculate_rouge_scores(original, compressed)
        entity_preservation = self._calculate_entity_preservation(original, compressed)
        readability = self._calculate_readability(compressed)
        
        # Extract entities for analysis
        original_entities = self._extract_entities(original)
        compressed_entities = self._extract_entities(compressed)
        
        # Text statistics
        original_stats = {
            'words': len(original.split()),
            'sentences': len(re.split(r'[.!?]+', original)),
            'characters': len(original)
        }
        
        compressed_stats = {
            'words': len(compressed.split()),
            'sentences': len(re.split(r'[.!?]+', compressed)),
            'characters': len(compressed)
        }
        
        return {
            'metrics': metrics.to_dict(),
            'component_scores': {
                'semantic_similarity': semantic_sim,
                'rouge_1': rouge_scores['rouge_1'],
                'rouge_2': rouge_scores['rouge_2'],
                'rouge_l': rouge_scores['rouge_l'],
                'entity_preservation': entity_preservation,
                'readability': readability
            },
            'entity_analysis': {
                'original_entities': list(original_entities),
                'compressed_entities': list(compressed_entities),
                'preserved_entities': list(original_entities.intersection(compressed_entities)),
                'lost_entities': list(original_entities - compressed_entities)
            },
            'text_statistics': {
                'original': original_stats,
                'compressed': compressed_stats,
                'reduction': {
                    'words': original_stats['words'] - compressed_stats['words'],
                    'sentences': original_stats['sentences'] - compressed_stats['sentences'],
                    'characters': original_stats['characters'] - compressed_stats['characters']
                }
            },
            'quality_interpretation': self._interpret_quality(metrics.overall_score)
        }
    
    def _interpret_quality(self, score: float) -> str:
        """
        Interpret quality score with human-readable description.
        
        Args:
            score: Overall quality score
            
        Returns:
            str: Quality interpretation
        """
        if score >= 0.9:
            return "Excellent - Very high quality compression with minimal information loss"
        elif score >= 0.8:
            return "Very Good - High quality compression with acceptable information loss"
        elif score >= 0.7:
            return "Good - Decent compression quality with some information loss"
        elif score >= 0.6:
            return "Fair - Moderate compression quality with noticeable information loss"
        elif score >= 0.5:
            return "Poor - Low compression quality with significant information loss"
        else:
            return "Very Poor - Very low compression quality with substantial information loss"