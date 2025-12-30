"""
TOON - Text Object Oriented Notation

A token-efficient notation system for representing code structures
optimized for LLM processing and analysis.
"""

from .converter import TOONConverter
from .parser import TOONParser
from .validator import TOONValidator
from .models import TOONNode, TOONFunction, TOONClass, TOONImport

__version__ = "1.0.0"
__all__ = [
    "TOONConverter",
    "TOONParser",
    "TOONValidator",
    "TOONNode",
    "TOONFunction",
    "TOONClass",
    "TOONImport",
]
