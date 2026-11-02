"""
Inverted Index Data Structure Implementation.

An Inverted Index is an associative data structure mapping each unique
vocabulary term to a posting list containing document identifiers and
the positional offsets where that term appears.

Example schema:
{
    "examination": {
        "doc_01_exam_schedule.txt": [12, 45],
        "doc_02_admit_card_circular.txt": [8]
    }
}
"""

import json
from typing import Dict, List, Optional, Tuple


class InvertedIndex:
    """
    Manages the mapping from normalized vocabulary terms to document occurrences.

    Structure:
        self.index: Dict[str, Dict[str, List[int]]]
        term -> { doc_id: [word_offset_1, word_offset_2, ...] }
    """

    def __init__(self) -> None:
        # Inverted index map: term -> { doc_id: [positions] }
        self.index: Dict[str, Dict[str, List[int]]] = {}
        # Cached sorted vocabulary keys for Binary Search
        self._sorted_vocabulary: List[str] = []
        # Total tokens indexed across all documents
        self.total_tokens_indexed: int = 0

    def add_term_occurrence(self, term: str, doc_id: str, position: int) -> None:
        """
        Records a single positional occurrence of a term in a document.

        Parameters:
            term (str): Normalized word token.
            doc_id (str): Unique document identifier / filename.
            position (int): 1-based sequential word index in the document.
        """
        self.total_tokens_indexed += 1

        if term not in self.index:
            self.index[term] = {}

        if doc_id not in self.index[term]:
            self.index[term][doc_id] = []

        self.index[term][doc_id].append(position)
        # Invalidate sorted vocabulary cache on modification
        self._sorted_vocabulary = []

    def get_postings(self, term: str) -> Optional[Dict[str, List[int]]]:
        """
        Retrieves the posting dictionary for a specific term.

        Returns:
            Dict[str, List[int]] mapping doc_id to list of positions,
            or None if the term is absent from the index.
        """
        return self.index.get(term.lower())

    def get_term_frequency(self, term: str) -> int:
        """Returns the total number of times a term appears across all documents."""
        postings = self.get_postings(term)
        if not postings:
            return 0
        return sum(len(positions) for positions in postings.values())

    def get_document_frequency(self, term: str) -> int:
        """Returns the number of distinct documents containing the term."""
        postings = self.get_postings(term)
        if not postings:
            return 0
        return len(postings)

    def get_sorted_vocabulary(self) -> List[str]:
        """
        Returns all unique indexed terms sorted in ascending lexicographical order.

        Why sorting is required:
            Binary Search eliminates half of the search interval at each step
            based on monotonic ordering (term < mid_term). Without a sorted
            vocabulary, Binary Search cannot deduce whether to search the left
            or right partition.
        """
        if not self._sorted_vocabulary and self.index:
            self._sorted_vocabulary = sorted(self.index.keys())
        return self._sorted_vocabulary

    def get_unsorted_vocabulary(self) -> List[str]:
        """
        Returns all unique indexed terms in their raw insertion order.
        Used to demonstrate that Linear Search succeeds on unsorted data,
        while Binary Search fails.
        """
        return list(self.index.keys())

    @property
    def vocabulary_size(self) -> int:
        """Returns total number of unique terms in the index."""
        return len(self.index)

    def to_json(self, file_path: str) -> None:
        """Serializes the inverted index to a JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2)

    def load_json(self, file_path: str) -> None:
        """Loads an inverted index from a precomputed JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            self.index = json.load(f)
        self._sorted_vocabulary = []
        self.total_tokens_indexed = sum(
            sum(len(pos) for pos in doc_map.values())
            for doc_map in self.index.values()
        )

