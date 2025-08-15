"""
Claude Switch - Anthropic Claude API Configuration Management Tool

A Python CLI tool for managing multiple Anthropic Claude API configurations 
with seamless environment switching.
"""

__version__ = "1.0.0"
__author__ = "Claude"
__email__ = "noreply@anthropic.com"

from .cli import cli

__all__ = ["cli"]