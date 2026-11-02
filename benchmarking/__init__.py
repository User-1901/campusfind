"""
CampusFind Benchmarking Package.
Empirical performance profiling of search algorithms across scaling dataset sizes.
"""
from .benchmark import (
    BenchmarkDataPoint,
    BenchmarkSuiteReport,
    run_campus_benchmark,
    generate_synthetic_vocabulary
)

__all__ = [
    "BenchmarkDataPoint",
    "BenchmarkSuiteReport",
    "run_campus_benchmark",
    "generate_synthetic_vocabulary"
]

