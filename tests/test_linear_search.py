"""
Unit Tests for Manual Linear Search Implementation.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from algorithms.linear_search import linear_search


class TestLinearSearch(unittest.TestCase):
    """Test suite for Linear Search algorithm correctness and edge cases."""

    def setUp(self):
        self.vocab = ["academic", "admission", "attendance", "calendar", "examination", "library", "syllabus"]

    def test_existing_keyword_first(self):
        """Best Case: element at index 0 requires exactly 1 comparison."""
        res = linear_search(self.vocab, "academic")
        self.assertTrue(res.found)
        self.assertEqual(res.index, 0)
        self.assertEqual(res.comparisons, 1)

    def test_existing_keyword_middle(self):
        """Average Case: element in middle."""
        res = linear_search(self.vocab, "calendar")
        self.assertTrue(res.found)
        self.assertEqual(res.index, 3)
        self.assertEqual(res.comparisons, 4)

    def test_existing_keyword_last(self):
        """Worst Case (found): element at last index requires n comparisons."""
        res = linear_search(self.vocab, "syllabus")
        self.assertTrue(res.found)
        self.assertEqual(res.index, len(self.vocab) - 1)
        self.assertEqual(res.comparisons, len(self.vocab))

    def test_missing_keyword(self):
        """Worst Case (not found): element not in vocabulary requires n comparisons."""
        res = linear_search(self.vocab, "nonexistent")
        self.assertFalse(res.found)
        self.assertEqual(res.index, -1)
        self.assertEqual(res.comparisons, len(self.vocab))

    def test_case_insensitivity(self):
        """Verifies uppercase and mixed-case queries match."""
        res_upper = linear_search(self.vocab, "EXAMINATION")
        res_mixed = linear_search(self.vocab, "ExAmInAtIoN")
        self.assertTrue(res_upper.found)
        self.assertTrue(res_mixed.found)
        self.assertEqual(res_upper.index, 4)
        self.assertEqual(res_mixed.index, 4)

    def test_empty_query(self):
        """Verifies empty or whitespace query handling."""
        res = linear_search(self.vocab, "   ")
        self.assertFalse(res.found)

    def test_empty_vocabulary(self):
        """Edge Case: Searching within an empty list."""
        res = linear_search([], "examination")
        self.assertFalse(res.found)
        self.assertEqual(res.comparisons, 0)

    def test_single_element_vocabulary(self):
        """Edge Case: Single element list."""
        single = ["examination"]
        hit = linear_search(single, "examination")
        miss = linear_search(single, "attendance")
        self.assertTrue(hit.found)
        self.assertEqual(hit.comparisons, 1)
        self.assertFalse(miss.found)
        self.assertEqual(miss.comparisons, 1)


if __name__ == "__main__":
    unittest.main()

