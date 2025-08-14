"""
Agents package for Azure Functions integration.
Contains all agent implementations following the BasicAgent pattern.
"""

from .basic_agent import BasicAgent
from .text_analyzer_agent import TextAnalyzerAgent

__all__ = ['BasicAgent', 'TextAnalyzerAgent']