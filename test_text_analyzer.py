#!/usr/bin/env python3
"""
Test script for the TextAnalyzer agent.
Demonstrates the agent's functionality with sample text.
"""

import json
from agents.text_analyzer_agent import TextAnalyzerAgent


def test_text_analyzer():
    """Test the TextAnalyzer agent with sample text."""
    
    # Create agent instance
    agent = TextAnalyzerAgent()
    
    # Sample text for testing
    sample_text = """
    This is a sample text for testing the TextAnalyzer agent. 
    It contains multiple sentences with various words. 
    The agent should be able to count words, characters, and sentences effectively. 
    This text also includes some repeated words to test the most common words functionality.
    The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet!
    """
    
    print("=== TextAnalyzer Agent Test ===")
    print(f"Agent Name: {agent.name}")
    print(f"Agent Description: {agent.metadata['description']}")
    print("\n=== Sample Text ===")
    print(sample_text.strip())
    
    print("\n=== Analysis Results ===")
    
    # Test with default parameters
    result = agent.perform(text=sample_text)
    parsed_result = json.loads(result)
    
    if parsed_result.get('success'):
        analysis = parsed_result['analysis']
        print(f"Word Count: {analysis['word_count']}")
        print(f"Character Count (with spaces): {analysis['character_count_with_spaces']}")
        print(f"Character Count (without spaces): {analysis['character_count_without_spaces']}")
        print(f"Sentence Count: {analysis['sentence_count']}")
        print(f"Average Word Length: {analysis['average_word_length']}")
        print(f"Average Words per Sentence: {analysis['reading_statistics']['average_words_per_sentence']}")
        print(f"Estimated Reading Time: {analysis['reading_statistics']['estimated_reading_time_minutes']} minutes")
        
        print("\nMost Common Words (excluding stopwords):")
        for word_info in analysis['most_common_words']:
            print(f"  - {word_info['word']}: {word_info['frequency']} times ({word_info['percentage']}%)")
    else:
        print(f"Error: {parsed_result.get('error')}")
    
    # Test with stopwords included
    print("\n=== Analysis with Stopwords Included ===")
    result_with_stopwords = agent.perform(
        text=sample_text, 
        include_stopwords=True, 
        max_common_words=10
    )
    parsed_result_stopwords = json.loads(result_with_stopwords)
    
    if parsed_result_stopwords.get('success'):
        analysis_stopwords = parsed_result_stopwords['analysis']
        print("Most Common Words (including stopwords):")
        for word_info in analysis_stopwords['most_common_words']:
            print(f"  - {word_info['word']}: {word_info['frequency']} times ({word_info['percentage']}%)")
    
    # Test edge cases
    print("\n=== Edge Case Tests ===")
    
    # Empty text
    empty_result = agent.perform(text="")
    empty_parsed = json.loads(empty_result)
    print(f"Empty text test: {empty_parsed.get('error', 'Success')}")
    
    # Single word
    single_word_result = agent.perform(text="Hello")
    single_word_parsed = json.loads(single_word_result)
    if single_word_parsed.get('success'):
        single_analysis = single_word_parsed['analysis']
        print(f"Single word test - Word count: {single_analysis['word_count']}, Sentence count: {single_analysis['sentence_count']}")


if __name__ == "__main__":
    test_text_analyzer()