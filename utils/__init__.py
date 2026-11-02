"""
CampusFind Utilities Package.
Provides text processing, normalization, tokenization, and frontmatter extraction.
"""
from .text_processing import (
    clean_text,
    tokenize,
    extract_words_with_positions,
    parse_frontmatter,
    extract_snippet
)

__all__ = [
    "clean_text",
    "tokenize",
    "extract_words_with_positions",
    "parse_frontmatter",
    "extract_snippet"
]

