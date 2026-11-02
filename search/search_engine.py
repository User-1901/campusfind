"""
CampusFind Core Search Engine.

Bridges the low-level search algorithms (Linear Search and Binary Search)
with the InvertedIndex and document catalog to retrieve filtered,
ranked, and contextualized document matches.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from algorithms.linear_search import linear_search, LinearSearchResult
from algorithms.binary_search import binary_search, BinarySearchResult
from indexing.text_indexer import TextIndexer, DocumentMetadata
from utils.text_processing import extract_snippet, clean_text


@dataclass
class SearchResultItem:
    """Represents a matched document with contextual metadata and occurrences."""
    doc_id: str
    metadata: DocumentMetadata
    occurrences_count: int
    positions: List[int]
    snippet: str


@dataclass
class SearchResponse:
    """Encapsulates the complete outcome of a campus document search."""
    query: str
    found: bool
    algorithm_mode: str
    linear_metrics: Optional[LinearSearchResult] = None
    binary_metrics: Optional[BinarySearchResult] = None
    items: List[SearchResultItem] = field(default_factory=list)
    total_matching_documents: int = 0
    total_occurrences: int = 0


class CampusSearchEngine:
    """
    Central search service for CampusFind.

    Executes search algorithms across the inverted index vocabulary and
    retrieves enriched document results with category/type filters.
    """

    def __init__(self, indexer: TextIndexer) -> None:
        self.indexer = indexer

    def search(
        self,
        keyword: str,
        algorithm: str = "compare_both",
        category_filter: Optional[str] = None,
        doc_type_filter: Optional[str] = None
    ) -> SearchResponse:
        """
        Executes a document search using the selected algorithm.

        Parameters:
            keyword (str): The search term entered by the student.
            algorithm (str): 'linear', 'binary', or 'compare_both'.
            category_filter (Optional[str]): Restrict matches to a specific document category.
            doc_type_filter (Optional[str]): Restrict matches to a specific document type.

        Returns:
            SearchResponse: Unified results including timing, comparisons, and matched docs.
        """
        clean_query = clean_text(keyword).strip()
        if not clean_query:
            return SearchResponse(
                query=keyword,
                found=False,
                algorithm_mode=algorithm
            )

        sorted_vocab = self.indexer.inverted_index.get_sorted_vocabulary()
        lin_res: Optional[LinearSearchResult] = None
        bin_res: Optional[BinarySearchResult] = None
        term_found = False

        # Execute chosen algorithm(s)
        if algorithm in ("linear", "compare_both"):
            lin_res = linear_search(sorted_vocab, clean_query, record_trace=True)
            if lin_res.found:
                term_found = True

        if algorithm in ("binary", "compare_both"):
            bin_res = binary_search(sorted_vocab, clean_query, record_trace=True)
            if bin_res.found:
                term_found = True

        # Fetch postings from the inverted index
        postings = self.indexer.inverted_index.get_postings(clean_query)

        result_items: List[SearchResultItem] = []
        total_occurrences = 0

        if postings:
            for doc_id, positions in postings.items():
                meta = self.indexer.documents_metadata.get(doc_id)
                if not meta:
                    continue

                # Apply category filter
                if category_filter and category_filter != "All Categories":
                    if meta.category != category_filter:
                        continue

                # Apply doc_type filter
                if doc_type_filter and doc_type_filter != "All Types":
                    if meta.doc_type != doc_type_filter:
                        continue

                body_text = self.indexer.documents_body.get(doc_id, "")
                snippet = extract_snippet(body_text, clean_query)

                count = len(positions)
                total_occurrences += count

                result_items.append(
                    SearchResultItem(
                        doc_id=doc_id,
                        metadata=meta,
                        occurrences_count=count,
                        positions=positions,
                        snippet=snippet
                    )
                )

        # Sort results by occurrence frequency descending (relevance ranking)
        result_items.sort(key=lambda item: item.occurrences_count, reverse=True)

        return SearchResponse(
            query=clean_query,
            found=term_found and len(result_items) > 0,
            algorithm_mode=algorithm,
            linear_metrics=lin_res,
            binary_metrics=bin_res,
            items=result_items,
            total_matching_documents=len(result_items),
            total_occurrences=total_occurrences
        )

