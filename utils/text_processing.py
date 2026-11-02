"""
Text Processing and Normalization Utility Module.

Provides functions for:
- Case normalization (lowercase conversion)
- Punctuation stripping
- Tokenization
- Word offset and line position extraction
- Document frontmatter metadata parsing
- Contextual snippet extraction
"""

import re
from typing import Dict, List, Tuple


def clean_text(text: str) -> str:
    """
    Normalizes text by converting to lowercase and replacing punctuation with spaces.

    Parameters:
        text (str): Input text string.

    Returns:
        str: Cleaned lowercase string with punctuation replaced by whitespace.
    """
    if not text:
        return ""
    lowered = text.lower()
    # Replace all non-alphanumeric and non-whitespace characters with spaces
    cleaned = re.sub(r"[^\w\s]", " ", lowered)
    return cleaned


def tokenize(text: str) -> List[str]:
    """
    Tokenizes input text into a list of cleaned words.

    Parameters:
        text (str): Raw or pre-cleaned text.

    Returns:
        List[str]: List of non-empty words.
    """
    cleaned = clean_text(text)
    return [word for word in cleaned.split() if word]


def extract_words_with_positions(text: str) -> List[Tuple[str, int, int]]:
    """
    Extracts words along with their line numbers and word offsets within that line.

    Parameters:
        text (str): Raw document body string.

    Returns:
        List[Tuple[str, int, int]]: List of (word, line_number, word_position_in_line).
    """
    results: List[Tuple[str, int, int]] = []
    if not text:
        return results

    lines = text.splitlines()
    for line_idx, line in enumerate(lines, start=1):
        cleaned_line = clean_text(line)
        words = cleaned_line.split()
        for word_pos, word in enumerate(words, start=1):
            if word:
                results.append((word, line_idx, word_pos))

    return results


def parse_frontmatter(raw_content: str, default_filename: str = "document.txt") -> Tuple[Dict[str, str], str]:
    """
    Parses optional YAML-style frontmatter headers between '---' delimiters.

    Parameters:
        raw_content (str): Entire file content.
        default_filename (str): Fallback filename if title is not specified.

    Returns:
        Tuple[Dict[str, str], str]: (metadata_dict, body_text)
    """
    metadata: Dict[str, str] = {
        "title": default_filename,
        "category": "General Document",
        "doc_type": "Notice",
        "department": "Campus Administration",
        "date": "2026-10-01"
    }

    if not raw_content:
        return metadata, ""

    stripped = raw_content.strip()
    if stripped.startswith("---"):
        parts = stripped.split("---", 2)
        if len(parts) >= 3:
            header_lines = parts[1].strip().splitlines()
            body = parts[2].strip()

            for line in header_lines:
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip().lower()
                    val = val.strip()
                    if key in ("title", "category", "doc_type", "department", "date"):
                        metadata[key] = val

            return metadata, body

    # Fallback when no frontmatter is found
    # Use first line or filename as title
    lines = raw_content.splitlines()
    first_non_empty = next((l.strip() for l in lines if l.strip()), default_filename)
    metadata["title"] = first_non_empty[:60]
    return metadata, raw_content


def extract_snippet(body: str, target_word: str, snippet_len: int = 160) -> str:
    """
    Extracts a contextual snippet from document text centered around the target word.

    Parameters:
        body (str): Full text of document.
        target_word (str): Keyword to highlight.
        snippet_len (int): Length of surrounding character context.

    Returns:
        str: Contextual preview snippet.
    """
    if not body or not target_word:
        return ""

    clean_target = target_word.lower()
    lower_body = body.lower()
    pos = lower_body.find(clean_target)

    if pos == -1:
        # Return first characters if exact match is not found
        return body[:snippet_len].strip() + ("..." if len(body) > snippet_len else "")

    start = max(0, pos - snippet_len // 2)
    end = min(len(body), pos + len(clean_target) + snippet_len // 2)

    snippet = body[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(body):
        snippet = snippet + "..."

    return snippet

