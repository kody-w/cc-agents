"""
Automated API Reverse Engineering Tool

A comprehensive tool for capturing API traffic and generating 
fully-typed client libraries in multiple programming languages.
"""

__version__ = "1.0.0"
__author__ = "Claude Code Agent"

from .capture import TrafficCapture
from .analyzer import RequestAnalyzer
from .generators import PythonGenerator, TypeScriptGenerator, JavaScriptGenerator
from .documentation import DocumentationGenerator
from .types import APISpec, Endpoint, Parameter
from .cli import APIReverseEngineerCLI

__all__ = [
    "TrafficCapture",
    "RequestAnalyzer", 
    "PythonGenerator",
    "TypeScriptGenerator",
    "JavaScriptGenerator",
    "DocumentationGenerator",
    "APIReverseEngineerCLI",
    "APISpec",
    "Endpoint",
    "Parameter"
]