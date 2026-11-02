"""
Unit Tests for Manual Iterative Binary Search Implementation.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from algorithms.binary_search import binary_search
from algorithms.linear_search import linear_search


class TestBinarySearch(unittest.TestCase):
    """Test suite for Binary Search algorithm correctness, bounds, and comparisons."""

    def setUp(self):
        # Alphabetically sorted vocabulary list
        self.sorted_vocab = [
            "academic", "admission", "attendance", "calendar",
            "circular", "examination", "guidelines", "library"
        ]

    def test_existing_keyword_initial_midpoint(self):
        """Best Case: element at initial mid found in 1 comparison."""
        # For N=8, mid = 0 + (7-0)//2 = 3 -> "calendar"
        res = binary_search(self.sorted_vocab, "calendar")
        self.assertTrue(res.found)
        self.assertEqual(res.index, 3)
        self.assertEqual(res.comparisons, 1)

    def test_existing_keyword_left_partition(self):
        """Element in left half."""
        res = binary_search(self.sorted_vocab, "academic")
        self.assertTrue(res.found)
        self.assertEqual(res.index, 0)
        self.assertLessEqual(res.comparisons, 4)  # ceil(log2(8)) + 1

    def test_existing_keyword_right_partition(self):
        """Element in right half."""
        res = binary_search(self.sorted_vocab, "library")
        self.assertTrue(res.found)
        self.assertEqual(res.index, 7)
        self.assertLessEqual(res.comparisons, 4)

    def test_missing_keyword_lower_bound(self):
        """Target smaller than smallest element."""
        res = binary_search(self.sorted_vocab, "aaa_missing")
        self.assertFalse(res.found)
        self.assertEqual(res.index, -1)

    def test_missing_keyword_upper_bound(self):
        """Target larger than largest element."""
        res = binary_search(self.sorted_vocab, "zzz_missing")
        self.assertFalse(res.found)
        self.assertEqual(res.index, -1)

    def test_case_insensitivity(self):
        """Verifies uppercase and mixed case matching."""
        res_upper = binary_search(self.sorted_vocab, "EXAMINATION")
        res_mixed = binary_search(self.sorted_vocab, "ExAmInAtIoN")
        self.assertTrue(res_upper.found)
        self.assertTrue(res_mixed.found)
        self.assertEqual(res_upper.index, 5)

    def test_empty_vocabulary(self):
        """Edge Case: Empty vocabulary."""
        res = binary_search([], "examination")
        self.assertFalse(res.found)
        self.assertEqual(res.comparisons, 0)

    def test_single_element_vocabulary(self):
        """Edge Case: Single element."""
        single = ["examination"]
        hit = binary_search(single, "examination")
        miss = binary_search(single, "attendance")
        self.assertTrue(hit.found)
        self.assertEqual(hit.comparisons, 1)
        self.assertFalse(miss.found)
        self.assertEqual(miss.comparisons, 1)

    def test_identical_results_with_linear_search(self):
        """Verifies that Linear and Binary Search yield identical results for all terms."""
        for term in self.sorted_vocab:
            l_res = linear_search(self.sorted_vocab, term)
            b_res = binary_search(self.sorted_vocab, term)
            self.assertEqual(l_res.found, b_res.found)
            self.assertEqual(l_res.index, b_res.index)

        # Missing term verification
        l_miss = linear_search(self.sorted_vocab, "nonexistent")
        b_miss = binary_search(self.sorted_vocab, "nonexistent")
        self.assertEqual(l_miss.found, b_miss.found)
        self.assertEqual(l_miss.index, b_miss.index)


if __name__ == "__main__":
    unittest.main()

