"""
Visualization Component for Algorithm Benchmarking.

Renders four publication-ready Matplotlib plots:
1. Execution Time Comparison (Linear vs. Binary)
2. Comparison Count Comparison (Linear vs. Binary)
3. Dataset Size vs. Execution Time (Detailed Scalability)
4. Dataset Size vs. Number of Comparisons (Theoretical vs. Empirical)
"""

import os
import tempfile
import matplotlib.pyplot as plt
from benchmarking.benchmark import BenchmarkSuiteReport

# Prevent Matplotlib temporary directory write warnings
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "campusfind_mpl"))


def render_benchmark_charts(report: BenchmarkSuiteReport):
    """
    Constructs a 2x2 figure containing all 4 required benchmarking charts.

    Parameters:
        report (BenchmarkSuiteReport): Benchmark results containing data points.

    Returns:
        matplotlib.figure.Figure: Rendered 4-panel figure.
    """
    sizes = [p.size for p in report.points]
    lin_times = [p.linear_time_ms for p in report.points]
    bin_times = [p.binary_time_ms for p in report.points]
    lin_comps = [p.linear_comparisons for p in report.points]
    bin_comps = [p.binary_comparisons for p in report.points]

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10), dpi=100)
    fig.patch.set_facecolor("#0F172A")  # Deep SaaS slate navy

    axes = [ax1, ax2, ax3, ax4]
    for ax in axes:
        ax.set_facecolor("#1E293B")
        ax.tick_params(colors="#94A3B8")
        ax.xaxis.label.set_color("#E2E8F0")
        ax.yaxis.label.set_color("#E2E8F0")
        ax.title.set_color("#F8FAFC")
        for spine in ax.spines.values():
            spine.set_color("#334155")
        ax.grid(True, linestyle="--", alpha=0.25, color="#64748B")

    # Chart 1: Execution Time Comparison (Linear vs Binary)
    ax1.plot(sizes, lin_times, marker="o", linewidth=2.2, color="#F43F5E", label="Linear Search O(n)")
    ax1.plot(sizes, bin_times, marker="s", linewidth=2.2, color="#38BDF8", label="Binary Search O(log n)")
    ax1.set_title("1. Execution Time Comparison", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Vocabulary Size (N)")
    ax1.set_ylabel("Execution Time (ms)")
    leg1 = ax1.legend(facecolor="#0F172A", edgecolor="#334155")
    for t in leg1.get_texts():
        t.set_color("#F8FAFC")

    # Chart 2: Comparison Count Comparison
    ax2.plot(sizes, lin_comps, marker="o", linewidth=2.2, color="#F43F5E", label="Linear Comparisons O(n)")
    ax2.plot(sizes, bin_comps, marker="s", linewidth=2.2, color="#10B981", label="Binary Comparisons O(log n)")
    ax2.set_title("2. Key Comparison Count", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Vocabulary Size (N)")
    ax2.set_ylabel("Number of Key Comparisons")
    leg2 = ax2.legend(facecolor="#0F172A", edgecolor="#334155")
    for t in leg2.get_texts():
        t.set_color("#F8FAFC")

    # Chart 3: Dataset Size vs. Execution Time (Bar Representation)
    x_indices = range(len(sizes))
    width = 0.35
    ax3.bar([x - width/2 for x in x_indices], lin_times, width=width, color="#F43F5E", alpha=0.85, label="Linear (ms)")
    ax3.bar([x + width/2 for x in x_indices], bin_times, width=width, color="#38BDF8", alpha=0.85, label="Binary (ms)")
    ax3.set_xticks(list(x_indices))
    ax3.set_xticklabels([f"{s:,}" for s in sizes])
    ax3.set_title("3. Dataset Size vs. Execution Time (Grouped)", fontsize=11, fontweight="bold")
    ax3.set_xlabel("Vocabulary Size (N)")
    ax3.set_ylabel("Time (ms)")
    leg3 = ax3.legend(facecolor="#0F172A", edgecolor="#334155")
    for t in leg3.get_texts():
        t.set_color("#F8FAFC")

    # Chart 4: Dataset Size vs. Comparisons (Log Scale for Binary Growth)
    ax4.plot(sizes, bin_comps, marker="s", linewidth=2.5, color="#10B981", label="Empirical Binary Comparisons")
    theoretical_bin = [p.theoretical_binary_ops for p in report.points]
    ax4.plot(sizes, theoretical_bin, linestyle=":", linewidth=2, color="#FCD34D", label="Theoretical Bound (ceil(log2 N))")
    ax4.set_title("4. Binary Search Logarithmic Curve", fontsize=11, fontweight="bold")
    ax4.set_xlabel("Vocabulary Size (N)")
    ax4.set_ylabel("Comparisons (Logarithmic Scale)")
    leg4 = ax4.legend(facecolor="#0F172A", edgecolor="#334155")
    for t in leg4.get_texts():
        t.set_color("#F8FAFC")

    plt.tight_layout()
    return fig

