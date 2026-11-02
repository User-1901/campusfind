"""
Unit Tests for Text Processing, Inverted Index, and Search Engine.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.text_processing import clean_text, tokenize, extract_words_with_positions, parse_frontmatter
from indexing.inverted_index import InvertedIndex
from indexing.text_indexer import TextIndexer
from search.search_engine import CampusSearchEngine


class TestIndexingAndSearch(unittest.TestCase):
    """Test suite covering text parsing, inverted index structure, and search operations."""

    def test_clean_text_normalization(self):
        """Verifies lowercase conversion and punctuation removal."""
        raw = "Notice: Mid-Term Exam, 2026! Check CS501 Syllabus."
        cleaned = clean_text(raw)
        self.assertEqual(cleaned, "notice  mid term exam  2026  check cs501 syllabus ")

    def test_parse_frontmatter_custom(self):
        """Verifies frontmatter header metadata extraction."""
        raw = """---
title: Sample Notice
category: Academic Circulars
doc_type: Notice
department: Academic Cell
date: 2026-10-10
---
This is the document body text."""
        meta, body = parse_frontmatter(raw, default_filename="doc.txt")
        self.assertEqual(meta["title"], "Sample Notice")
        self.assertEqual(meta["category"], "Academic Circulars")
        self.assertEqual(body, "This is the document body text.")

    def test_inverted_index_postings(self):
        """Verifies mapping of terms to documents and positions."""
        idx = InvertedIndex()
        idx.add_term_occurrence("examination", "doc1.txt", 12)
        idx.add_term_occurrence("examination", "doc1.txt", 45)
        idx.add_term_occurrence("examination", "doc2.txt", 8)

        postings = idx.get_postings("examination")
        self.assertIsNotNone(postings)
        self.assertEqual(postings["doc1.txt"], [12, 45])
        self.assertEqual(postings["doc2.txt"], [8])
        self.assertEqual(idx.get_term_frequency("examination"), 3)
        self.assertEqual(idx.get_document_frequency("examination"), 2)

    def test_text_indexer_integration(self):
        """Verifies multi-document indexing and repository statistics."""
        indexer = TextIndexer()
        indexer.add_document("doc1.txt", "The examination schedule is published.")
        indexer.add_document("doc2.txt", "Students must attend examination on time.")

        stats = indexer.get_statistics()
        self.assertEqual(stats["total_documents"], 2)
        self.assertIn("examination", indexer.inverted_index.index)

        # Search engine check
        engine = CampusSearchEngine(indexer)
        response = engine.search("examination", algorithm="compare_both")
        self.assertTrue(response.found)
        self.assertEqual(response.total_matching_documents, 2)
        self.assertEqual(response.total_occurrences, 2)

    def test_category_filtering(self):
        """Verifies category filtering restricts returned results."""
        indexer = TextIndexer()
        doc_a = """---
title: Exam Notice
category: Examination Notices
---
Important examination notice."""
        doc_b = """---
title: Syllabus Guide
category: Course Syllabus
---
Detailed course examination syllabus."""
        indexer.add_document("doc_a.txt", doc_a)
        indexer.add_document("doc_b.txt", doc_b)

        engine = CampusSearchEngine(indexer)
        # Search without filter -> 2 docs
        all_res = engine.search("examination")
        self.assertEqual(all_res.total_matching_documents, 2)

        # Search with Examination Notices filter -> 1 doc
        filtered_res = engine.search("examination", category_filter="Examination Notices")
        self.assertEqual(filtered_res.total_matching_documents, 1)
        self.assertEqual(filtered_res.items[0].metadata.category, "Examination Notices")


if __name__ == "__main__":
    unittest.main()

