"""
Manual Implementation of Iterative Binary Search Algorithm.

Binary Search operates on a sorted vocabulary by repeatedly halving the
search interval. At each step, it compares the target with the middle element.
"""

from dataclasses import dataclass, field
import time
from typing import Any, List, Optional


@dataclass
class BinarySearchResult:
    """Stores performance metrics and results of a Binary Search execution."""
    target: str
    found: bool
    index: int
    comparisons: int
    execution_time_seconds: float
    execution_time_ms: float
    matched_term: Optional[str] = None
    trace: List[dict] = field(default_factory=list)


def binary_search(
    sorted_vocabulary: List[str],
    target: str,
    record_trace: bool = True
) -> BinarySearchResult:
    """
    Searches for target in a sorted vocabulary using iterative Binary Search.

    Parameters:
        sorted_vocabulary (List[str]): Alphabetically sorted list of unique terms.
        target (str): Keyword to search for.
        record_trace (bool): Whether to record pointer transitions for visualization.

    Returns:
        BinarySearchResult: Dataclass containing index, comparisons, timing, and trace.

    Why Sorted Data is Mandatory:
        Binary Search eliminates half the remaining elements on every comparison.
        This deduction is mathematically valid ONLY if the array is strictly ordered:
        If target < array[mid], all elements at indices > mid are guaranteed to be
        greater than target, so they can safely be pruned. On unsorted data, smaller
        elements could reside in the pruned partition, causing false negative search results.

    Time Complexity:
        - Best Case:    O(1)        - Target is exactly at the initial midpoint.
        - Worst Case:   O(log2 n)   - Target is at the final leaf subdivision or absent.
        - Average Case: O(log2 n)   - Halves the search space at each iteration.

    Space Complexity:
        - Auxiliary Space: O(1)     - Requires only left, right, and mid pointer variables.
    """
    start_time = time.perf_counter()

    clean_target = target.strip().lower()
    comparisons = 0
    found = False
    match_index = -1
    matched_term = None
    trace: List[dict] = []

    left = 0
    right = len(sorted_vocabulary) - 1
    step = 0

    while left <= right:
        step += 1
        # Calculate midpoint safely without integer overflow risk
        mid = left + (right - left) // 2
        current_word = str(sorted_vocabulary[mid]).lower()

        # Each iteration performs 1 key comparison against sorted_vocabulary[mid]
        comparisons += 1

        if current_word == clean_target:
            # Case 1: Target matches middle element exactly
            found = True
            match_index = mid
            matched_term = sorted_vocabulary[mid]

            if record_trace:
                trace.append({
                    "step": step,
                    "left": left,
                    "right": right,
                    "mid": mid,
                    "current_term": current_word,
                    "target": clean_target,
                    "comparison": f"'{clean_target}' == '{current_word}'",
                    "action": "Exact match found! Search terminates successfully."
                })
            break

        elif clean_target < current_word:
            # Case 2: Target is alphabetically smaller than middle element.
            # Prune right half [mid..right].
            if record_trace:
                trace.append({
                    "step": step,
                    "left": left,
                    "right": right,
                    "mid": mid,
                    "current_term": current_word,
                    "target": clean_target,
                    "comparison": f"'{clean_target}' < '{current_word}'",
                    "action": f"Discard right half -> update right = {mid - 1}"
                })
            right = mid - 1

        else:
            # Case 3: Target is alphabetically greater than middle element.
            # Prune left half [left..mid].
            if record_trace:
                trace.append({
                    "step": step,
                    "left": left,
                    "right": right,
                    "mid": mid,
                    "current_term": current_word,
                    "target": clean_target,
                    "comparison": f"'{clean_target}' > '{current_word}'",
                    "action": f"Discard left half -> update left = {mid + 1}"
                })
            left = mid + 1

    elapsed_time = time.perf_counter() - start_time
    elapsed_time_ms = elapsed_time * 1000.0

    return BinarySearchResult(
        target=target,
        found=found,
        index=match_index,
        comparisons=comparisons,
        execution_time_seconds=elapsed_time,
        execution_time_ms=elapsed_time_ms,
        matched_term=matched_term,
        trace=trace
    )

