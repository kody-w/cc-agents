import json
import re
import logging
from collections import Counter
from typing import Dict, List, Any
from agents.basic_agent import BasicAgent


class TextAnalyzerAgent(BasicAgent):
    """
    Agent for analyzing text and providing comprehensive statistics.
    Inherits from BasicAgent and follows Azure Functions integration patterns.
    """
    
    def __init__(self):
        self.name = 'TextAnalyzer'
        self.metadata = {
            "name": self.name,
            "description": "Analyzes text input and returns comprehensive statistics including word count, character count, sentence count, average word length, and most common words. Use this agent when you need detailed text analysis and statistics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text content to analyze for statistics and metrics"
                    },
                    "include_stopwords": {
                        "type": "boolean",
                        "description": "Whether to include common stopwords in the most common words analysis (default: false)"
                    },
                    "max_common_words": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 20,
                        "description": "Maximum number of most common words to return (default: 5)"
                    }
                },
                "required": ["text"]
            }
        }
        
        # Common English stopwords for filtering
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
        }
        
        super().__init__(name=self.name, metadata=self.metadata)
    
    def perform(self, **kwargs) -> str:
        """
        Analyze the provided text and return comprehensive statistics.
        
        Args:
            **kwargs: Contains:
                - text (str): The text to analyze
                - include_stopwords (bool, optional): Include stopwords in common words analysis
                - max_common_words (int, optional): Number of most common words to return
        
        Returns:
            str: JSON string containing text analysis results
        """
        try:
            # Extract parameters with defaults
            text = kwargs.get('text', '').strip()
            include_stopwords = kwargs.get('include_stopwords', False)
            max_common_words = kwargs.get('max_common_words', 5)
            
            # Validate input
            if not text:
                return json.dumps({
                    "error": "No text provided for analysis",
                    "analysis": None
                })
            
            # Validate max_common_words parameter
            if not isinstance(max_common_words, int) or max_common_words < 1 or max_common_words > 20:
                max_common_words = 5
            
            # Perform text analysis
            analysis_results = self._analyze_text(text, include_stopwords, max_common_words)
            
            return json.dumps({
                "success": True,
                "analysis": analysis_results,
                "message": f"Successfully analyzed text with {analysis_results['word_count']} words"
            })
            
        except Exception as e:
            logging.error(f"Error in TextAnalyzerAgent.perform: {str(e)}")
            return json.dumps({
                "error": f"Failed to analyze text: {str(e)}",
                "analysis": None
            })
    
    def _analyze_text(self, text: str, include_stopwords: bool, max_common_words: int) -> Dict[str, Any]:
        """
        Perform comprehensive text analysis.
        
        Args:
            text (str): Text to analyze
            include_stopwords (bool): Whether to include stopwords in analysis
            max_common_words (int): Number of most common words to return
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Basic character counts
        char_count_with_spaces = len(text)
        char_count_without_spaces = len(text.replace(' ', '').replace('\t', '').replace('\n', ''))
        
        # Word analysis
        words = self._extract_words(text)
        word_count = len(words)
        
        # Calculate average word length
        average_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Sentence count (basic sentence detection)
        sentence_count = self._count_sentences(text)
        
        # Most common words analysis
        most_common_words = self._get_most_common_words(words, include_stopwords, max_common_words)
        
        # Reading statistics
        reading_stats = self._calculate_reading_stats(word_count, sentence_count)
        
        return {
            "word_count": word_count,
            "character_count_with_spaces": char_count_with_spaces,
            "character_count_without_spaces": char_count_without_spaces,
            "sentence_count": sentence_count,
            "average_word_length": round(average_word_length, 2),
            "most_common_words": most_common_words,
            "reading_statistics": reading_stats
        }
    
    def _extract_words(self, text: str) -> List[str]:
        """
        Extract words from text, removing punctuation and converting to lowercase.
        
        Args:
            text (str): Input text
            
        Returns:
            List[str]: List of cleaned words
        """
        # Remove punctuation and split into words
        # Keep apostrophes for contractions like "don't", "won't"
        cleaned_text = re.sub(r"[^\w\s']", ' ', text.lower())
        words = cleaned_text.split()
        
        # Filter out empty strings and single characters that aren't meaningful
        return [word for word in words if len(word) > 0 and not word.isspace()]
    
    def _count_sentences(self, text: str) -> int:
        """
        Count sentences in text using basic punctuation detection.
        
        Args:
            text (str): Input text
            
        Returns:
            int: Number of sentences
        """
        if not text.strip():
            return 0
            
        # Split by sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        
        # Filter out empty sentences and whitespace-only sentences
        meaningful_sentences = [s.strip() for s in sentences if s.strip()]
        
        return len(meaningful_sentences)
    
    def _get_most_common_words(self, words: List[str], include_stopwords: bool, max_count: int) -> List[Dict[str, Any]]:
        """
        Get the most common words with their frequencies.
        
        Args:
            words (List[str]): List of words
            include_stopwords (bool): Whether to include stopwords
            max_count (int): Maximum number of words to return
            
        Returns:
            List[Dict[str, Any]]: List of word frequency dictionaries
        """
        if not words:
            return []
        
        # Filter stopwords if requested
        if not include_stopwords:
            filtered_words = [word for word in words if word.lower() not in self.stopwords]
        else:
            filtered_words = words
        
        if not filtered_words:
            return []
        
        # Count word frequencies
        word_counter = Counter(filtered_words)
        
        # Get most common words
        most_common = word_counter.most_common(max_count)
        
        return [
            {
                "word": word,
                "frequency": count,
                "percentage": round((count / len(filtered_words)) * 100, 2)
            }
            for word, count in most_common
        ]
    
    def _calculate_reading_stats(self, word_count: int, sentence_count: int) -> Dict[str, Any]:
        """
        Calculate additional reading statistics.
        
        Args:
            word_count (int): Total number of words
            sentence_count (int): Total number of sentences
            
        Returns:
            Dict[str, Any]: Reading statistics
        """
        if sentence_count == 0:
            average_words_per_sentence = 0
            estimated_reading_time = 0
        else:
            average_words_per_sentence = word_count / sentence_count
            # Estimate reading time assuming 200 words per minute
            estimated_reading_time = word_count / 200
        
        return {
            "average_words_per_sentence": round(average_words_per_sentence, 2),
            "estimated_reading_time_minutes": round(estimated_reading_time, 2)
        }