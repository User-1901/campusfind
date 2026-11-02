"""
CampusFind Performance Benchmarking Engine.

Performs live, empirical benchmarking comparing Linear Search vs. Binary Search
across dataset sizes from 100 to 10,000 terms. Measures execution time using
time.perf_counter() and tracks exact comparison counts without artificial data.
"""

from dataclasses import dataclass, field
import math
import os
import random
import tempfile
import time
from typing import List, Optional

# Prevent Matplotlib temporary directory write warnings
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "campusfind_mpl"))

from algorithms.linear_search import linear_search
from algorithms.binary_search import binary_search


@dataclass
class BenchmarkDataPoint:
    """Stores performance metrics for a specific dataset size."""
    size: int
    linear_time_ms: float
    binary_time_ms: float
    linear_comparisons: int
    binary_comparisons: int
    successful_searches: int
    unsuccessful_searches: int
    theoretical_linear_ops: int
    theoretical_binary_ops: int


@dataclass
class BenchmarkSuiteReport:
    """Encapsulates full benchmarking suite results across multiple dataset sizes."""
    scenario: str
    points: List[BenchmarkDataPoint] = field(default_factory=list)
    hardware_notes: str = ""


def generate_synthetic_vocabulary(size: int, base_words: Optional[List[str]] = None) -> List[str]:
    """
    Generates a deterministic, sorted vocabulary of exact size `size`.

    Parameters:
        size (int): Number of unique terms needed.
        base_words (Optional[List[str]]): Seed words extracted from campus documents.

    Returns:
        List[str]: Alphabetically sorted list of lowercase words.
    """
    if base_words:
        unique_seeds = sorted(list({w.lower() for w in base_words if w.isalpha()}))
    else:
        unique_seeds = [
            "academic", "admission", "algorithm", "announcement", "attendance",
            "calendar", "campus", "circular", "course", "curriculum",
            "department", "document", "engineering", "examination", "faculty",
            "guidelines", "hostel", "laboratory", "library", "manual",
            "notice", "placement", "policy", "registration", "research",
            "schedule", "scholarship", "semester", "student", "syllabus"
        ]

    vocab_set = set(unique_seeds[:size])
    counter = 1

    while len(vocab_set) < size:
        base = unique_seeds[(counter - 1) % len(unique_seeds)]
        vocab_set.add(f"{base}_{counter:05d}")
        counter += 1

    return sorted(list(vocab_set))[:size]


def run_campus_benchmark(
    sizes: Optional[List[int]] = None,
    scenario: str = "average",
    iterations: int = 5,
    seed_words: Optional[List[str]] = None
) -> BenchmarkSuiteReport:
    """
    Executes live empirical profiling on both algorithms using identical datasets and queries.

    Parameters:
        sizes: Dataset sizes to evaluate. Defaults to [100, 500, 1000, 5000, 10000].
        scenario: 'average', 'worst_case', 'best_case', or 'unsuccessful'.
        iterations: Number of test queries executed per size to compute a stable average.
        seed_words: Vocabulary seeds extracted from indexed documents.

    Returns:
        BenchmarkSuiteReport containing empirical data points.
    """
    if sizes is None:
        sizes = [100, 500, 1000, 5000, 10000]

    report = BenchmarkSuiteReport(
        scenario=scenario,
        hardware_notes=(
            "Timings measured using Python time.perf_counter(). Wall-clock execution time reflects "
            "CPU cache hierarchy, RAM latency, and Python bytecode interpretation. "
            "Key comparison count is hardware-invariant and reflects exact asymptotic growth."
        )
    )

    for n in sizes:
        vocab = generate_synthetic_vocabulary(n, seed_words)

        total_lin_time = 0.0
        total_bin_time = 0.0
        total_lin_comps = 0
        total_bin_comps = 0
        success_count = 0
        unsuccess_count = 0

        rng = random.Random(42 + n)

        for _ in range(iterations):
            # Select target based on scenario
            if scenario == "best_case":
                # For linear search, best case is index 0.
                # For binary search, best case is midpoint.
                target = vocab[(n - 1) // 2]
            elif scenario == "worst_case":
                # Last element in array
                target = vocab[-1]
            elif scenario == "unsuccessful":
                # Non-existent query term
                target = "zz_unindexed_campus_query_9999"
            else:
                # Average case: randomly chosen term
                target = vocab[rng.randint(0, n - 1)]

            # Profile Linear Search
            lin_res = linear_search(vocab, target, record_trace=False)
            total_lin_time += lin_res.execution_time_ms
            total_lin_comps += lin_res.comparisons

            # Profile Binary Search
            bin_res = binary_search(vocab, target, record_trace=False)
            total_bin_time += bin_res.execution_time_ms
            total_bin_comps += bin_res.comparisons

            if bin_res.found:
                success_count += 1
            else:
                unsuccess_count += 1

        avg_lin_time = total_lin_time / iterations
        avg_bin_time = total_bin_time / iterations
        avg_lin_comps = int(round(total_lin_comps / iterations))
        avg_bin_comps = int(round(total_bin_comps / iterations))

        theo_linear = n if scenario in ("worst_case", "unsuccessful") else n // 2
        theo_binary = int(math.ceil(math.log2(n + 1)))

        report.points.append(
            BenchmarkDataPoint(
                size=n,
                linear_time_ms=avg_lin_time,
                binary_time_ms=avg_bin_time,
                linear_comparisons=avg_lin_comps,
                binary_comparisons=avg_bin_comps,
                successful_searches=success_count,
                unsuccessful_searches=unsuccess_count,
                theoretical_linear_ops=theo_linear,
                theoretical_binary_ops=theo_binary
            )
        )

    return report

