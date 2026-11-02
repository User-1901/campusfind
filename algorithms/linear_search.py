"""
Manual Implementation of Linear Search Algorithm.

Linear Search sequentially evaluates every element in a list from index 0
to n-1 until a matching keyword is found or the collection is exhausted.
"""

from dataclasses import dataclass, field
import time
from typing import Any, List, Optional


@dataclass
class LinearSearchResult:
    """Stores performance metrics and results of a Linear Search execution."""
    target: str
    found: bool
    index: int
    comparisons: int
    execution_time_seconds: float
    execution_time_ms: float
    matched_term: Optional[str] = None
    trace: List[dict] = field(default_factory=list)


def linear_search(
    vocabulary: List[str],
    target: str,
    record_trace: bool = True,
    max_trace_steps: int = 50
) -> LinearSearchResult:
    """
    Sequentially searches for target within a vocabulary list.

    Parameters:
        vocabulary (List[str]): List of indexed vocabulary words.
        target (str): Keyword to search for.
        record_trace (bool): Whether to record comparison steps for visualization.
        max_trace_steps (int): Safety cap on trace history size.

    Returns:
        LinearSearchResult: Dataclass containing index, comparisons, timing, and trace.

    Time Complexity:
        - Best Case:    O(1) - Target is at index 0.
        - Worst Case:   O(n) - Target is at index n-1 or absent.
        - Average Case: O(n) - Target found after ~n/2 comparisons.

    Space Complexity:
        - Auxiliary Space: O(1) - Only scalar index and counter variables.
    """
    start_time = time.perf_counter()

    clean_target = target.strip().lower()
    comparisons = 0
    found = False
    match_index = -1
    matched_term = None
    trace: List[dict] = []

    # Iterate sequentially through the vocabulary
    for i in range(len(vocabulary)):
        current_word = str(vocabulary[i]).lower()
        comparisons += 1
        is_match = (current_word == clean_target)

        if record_trace and len(trace) < max_trace_steps:
            trace.append({
                "step": comparisons,
                "current_index": i,
                "current_term": current_word,
                "target": clean_target,
                "is_match": is_match,
                "action": "Target Matched! Terminating." if is_match else "Mismatch -> Advance index."
            })

        if is_match:
            found = True
            match_index = i
            matched_term = vocabulary[i]
            break

    elapsed_time = time.perf_counter() - start_time
    elapsed_time_ms = elapsed_time * 1000.0

    return LinearSearchResult(
        target=target,
        found=found,
        index=match_index,
        comparisons=comparisons,
        execution_time_seconds=elapsed_time,
        execution_time_ms=elapsed_time_ms,
        matched_term=matched_term,
        trace=trace
    )

