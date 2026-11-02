"""
Text Indexer and Document Metadata Coordinator.

Ingests document collections, parses YAML frontmatter metadata, extracts
positional word tokens, and constructs both the InvertedIndex and
document repository catalogs.
"""

from dataclasses import dataclass, field
import os
from typing import Dict, List, Optional, Set
from utils.text_processing import (
    extract_words_with_positions,
    parse_frontmatter,
    tokenize
)
from .inverted_index import InvertedIndex


@dataclass
class DocumentMetadata:
    """Encapsulates catalog metadata for a campus document."""
    doc_id: str
    filename: str
    title: str
    category: str
    doc_type: str
    department: str
    date: str
    total_words: int = 0
    unique_words: int = 0


class TextIndexer:
    """
    High-level document indexing engine for CampusFind.

    Coordinates document storage, metadata extraction, and updates to
    the underlying InvertedIndex.
    """

    def __init__(self) -> None:
        self.inverted_index = InvertedIndex()
        # Catalog: doc_id -> DocumentMetadata
        self.documents_metadata: Dict[str, DocumentMetadata] = {}
        # Document text cache: doc_id -> raw body text
        self.documents_body: Dict[str, str] = {}
        # Available categories and doc_types
        self.categories: Set[str] = set()
        self.doc_types: Set[str] = set()

    def add_document(self, filename: str, raw_content: str) -> DocumentMetadata:
        """
        Indexes a new document into the repository.

        Parameters:
            filename (str): Name of the file (e.g. 'doc_01_exam_schedule.txt').
            raw_content (str): Complete file content including optional frontmatter.

        Returns:
            DocumentMetadata: Created document metadata object.
        """
        doc_id = filename
        metadata_dict, body_text = parse_frontmatter(raw_content, default_filename=filename)

        # Store body text for snippet generation
        self.documents_body[doc_id] = body_text

        # Extract positional word tokens from body text
        words_with_positions = extract_words_with_positions(body_text)
        unique_tokens: Set[str] = set()

        for word, _line_num, word_offset in words_with_positions:
            self.inverted_index.add_term_occurrence(word, doc_id, word_offset)
            unique_tokens.add(word)

        meta = DocumentMetadata(
            doc_id=doc_id,
            filename=filename,
            title=metadata_dict.get("title", filename),
            category=metadata_dict.get("category", "General Document"),
            doc_type=metadata_dict.get("doc_type", "Notice"),
            department=metadata_dict.get("department", "Campus Administration"),
            date=metadata_dict.get("date", "2026-10-01"),
            total_words=len(words_with_positions),
            unique_words=len(unique_tokens)
        )

        self.documents_metadata[doc_id] = meta
        self.categories.add(meta.category)
        self.doc_types.add(meta.doc_type)

        return meta

    def load_directory(self, dir_path: str) -> int:
        """
        Ingests all .txt documents located in dir_path into the search engine.

        Parameters:
            dir_path (str): Path to document folder.

        Returns:
            int: Number of documents successfully indexed.
        """
        if not os.path.exists(dir_path):
            return 0

        count = 0
        for fname in sorted(os.listdir(dir_path)):
            if fname.lower().endswith(".txt"):
                fpath = os.path.join(dir_path, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        raw = f.read()
                        self.add_document(fname, raw)
                        count += 1
                except Exception as err:
                    print(f"Failed to load {fname}: {err}")

        return count

    def get_statistics(self) -> Dict[str, object]:
        """
        Computes summary metrics for the CampusFind homepage dashboard.
        """
        total_docs = len(self.documents_metadata)
        unique_words = self.inverted_index.vocabulary_size
        total_terms = self.inverted_index.total_tokens_indexed

        # Categorize documents
        category_counts: Dict[str, int] = {}
        for meta in self.documents_metadata.values():
            category_counts[meta.category] = category_counts.get(meta.category, 0) + 1

        # Recent documents sorted by date descending
        recent_docs = sorted(
            self.documents_metadata.values(),
            key=lambda m: m.date,
            reverse=True
        )[:5]

        return {
            "total_documents": total_docs,
            "unique_words": unique_words,
            "total_terms": total_terms,
            "categories": sorted(list(self.categories)),
            "category_counts": category_counts,
            "doc_types": sorted(list(self.doc_types)),
            "recent_documents": recent_docs
        }

