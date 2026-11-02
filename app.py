"""
CampusFind: Intelligent Campus Document Search Engine.
Main Streamlit Application.
"""

import os
import sys
import tempfile
import time
import pandas as pd
import streamlit as st

# Ensure Matplotlib uses a writable temporary cache directory
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "campusfind_mpl"))

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from indexing.text_indexer import TextIndexer
from search.search_engine import CampusSearchEngine
from benchmarking.benchmark import run_campus_benchmark
from components.dashboard import render_home_dashboard
from components.search_results import render_search_results
from components.charts import render_benchmark_charts
from algorithms.linear_search import linear_search
from algorithms.binary_search import binary_search

# ==============================================================================
# STREAMLIT CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="CampusFind | Intelligent Campus Search Engine",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional dark-navy SaaS theme
st.markdown("""
<style>
    /* Global Base */
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
    }
    
    /* Navigation Branding */
    .brand-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #38BDF8;
        letter-spacing: -0.5px;
        margin-bottom: 2px;
    }
    .brand-tagline {
        font-size: 0.85rem;
        color: #94A3B8;
        margin-bottom: 16px;
    }
    
    /* Section Headers */
    .page-header {
        font-size: 2rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .page-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 24px;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px 18px;
    }
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 700 !important;
    }

    /* Category Pill */
    .cat-pill {
        display: inline-block;
        background-color: #1E293B;
        border: 1px solid #475569;
        color: #38BDF8;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# STATE & CACHING MANAGEMENT
# ==============================================================================
@st.cache_resource
def initialize_repository() -> TextIndexer:
    """Ingests pre-loaded campus documents and returns the initialized TextIndexer."""
    indexer = TextIndexer()
    doc_dir = os.path.join(BASE_DIR, "data", "documents")
    indexer.load_directory(doc_dir)

    # Save index snapshot to data/index.json
    index_json_path = os.path.join(BASE_DIR, "data", "index.json")
    try:
        indexer.inverted_index.to_json(index_json_path)
    except Exception as e:
        print(f"Warning: Could not serialize index.json: {e}")

    return indexer


if "indexer" not in st.session_state:
    st.session_state.indexer = initialize_repository()

indexer: TextIndexer = st.session_state.indexer
search_engine = CampusSearchEngine(indexer)

if "active_query" not in st.session_state:
    st.session_state.active_query = ""


# ==============================================================================
# SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    st.markdown('<div class="brand-title">🎓 CampusFind</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-tagline">Your Campus Information, One Search Away.</div>', unsafe_allow_html=True)

    menu_option = st.radio(
        "Navigation",
        [
            "🏠 Home Dashboard",
            "🔍 Document Search",
            "📁 Document Library",
            "🔬 Algorithm Lab",
            "📊 Performance Benchmark",
            "📚 How Search Works"
        ],
        index=0
    )

    st.markdown("---")
    st.caption("Centralized Institutional Repository Engine v2.4")
    stats = indexer.get_statistics()
    st.caption(f"Status: **Online** ({stats['total_documents']} Documents Loaded)")


# ==============================================================================
# PAGE 1: HOME DASHBOARD
# ==============================================================================
if menu_option == "🏠 Home Dashboard":
    def on_hero_search(search_term: str):
        st.session_state.active_query = search_term
        st.session_state["nav_to_search"] = True
        st.rerun()

    if st.session_state.get("nav_to_search"):
        st.session_state["nav_to_search"] = False
        # Switch seamlessly to search tab
        menu_option = "🔍 Document Search"

    render_home_dashboard(indexer, on_hero_search)


# ==============================================================================
# PAGE 2: DOCUMENT SEARCH
# ==============================================================================
elif menu_option == "🔍 Document Search":
    st.markdown('<div class="page-header">🔍 Document Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Search across institutional notices, syllabi, manuals, and announcements.</div>', unsafe_allow_html=True)

    # Search Filters Bar
    s_col1, s_col2, s_col3, s_col4 = st.columns([3, 1.5, 1.5, 1.5])

    initial_q = st.session_state.active_query or ""
    with s_col1:
        search_keyword = st.text_input(
            "Search Query:",
            value=initial_q,
            placeholder="Type keyword (e.g. examination, attendance, syllabus)..."
        )
    with s_col2:
        category_options = ["All Categories"] + sorted(list(indexer.categories))
        selected_category = st.selectbox("Category Filter:", category_options)
    with s_col3:
        doc_type_options = ["All Types"] + sorted(list(indexer.doc_types))
        selected_doc_type = st.selectbox("Document Type:", doc_type_options)
    with s_col4:
        algo_choice = st.selectbox(
            "Search Algorithm:",
            ["Compare Both", "Linear Search O(n)", "Binary Search O(log n)"]
        )

    algo_mode = "compare_both"
    if algo_choice == "Linear Search O(n)":
        algo_mode = "linear"
    elif algo_choice == "Binary Search O(log n)":
        algo_mode = "binary"

    if search_keyword:
        st.session_state.active_query = search_keyword
        response = search_engine.search(
            keyword=search_keyword,
            algorithm=algo_mode,
            category_filter=selected_category,
            doc_type_filter=selected_doc_type
        )
        render_search_results(response, indexer.documents_body)
    else:
        st.info("💡 Enter a keyword above or pick a sample search term to view matching documents and search algorithm metrics.")


# ==============================================================================
# PAGE 3: DOCUMENT LIBRARY
# ==============================================================================
elif menu_option == "📁 Document Library":
    st.markdown('<div class="page-header">📁 Central Document Library</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Browse institutional records or upload custom plain text (.txt) documents.</div>', unsafe_allow_html=True)

    lib_tab1, lib_tab2 = st.tabs(["📚 Document Repository (20+ Records)", "📤 Upload Document"])

    with lib_tab1:
        lib_col1, lib_col2 = st.columns([3, 1])
        with lib_col1:
            cat_filter = st.selectbox("Filter by Category:", ["All Categories"] + sorted(list(indexer.categories)), key="lib_cat")
        with lib_col2:
            st.metric("Total Ingested", f"{len(indexer.documents_metadata)}")

        filtered_docs = list(indexer.documents_metadata.values())
        if cat_filter != "All Categories":
            filtered_docs = [d for d in filtered_docs if d.category == cat_filter]

        st.caption(f"Displaying {len(filtered_docs)} document(s):")

        for doc in filtered_docs:
            with st.expander(f"📄 {doc.title} ({doc.category} - {doc.date})"):
                st.markdown(f"**Filename:** `{doc.filename}` &nbsp;|&nbsp; **Department:** {doc.department} &nbsp;|&nbsp; **Type:** {doc.doc_type}")
                st.markdown(f"**Metrics:** Total Words: `{doc.total_words}` | Unique Vocabulary: `{doc.unique_words}`")
                st.markdown("---")
                content = indexer.documents_body.get(doc.doc_id, "")
                st.text_area("Document Content:", value=content, height=180, disabled=True, key=f"lib_view_{doc.doc_id}")

    with lib_tab2:
        st.markdown("### 📤 Upload New Text Document")
        st.markdown("""
        Upload institutional `.txt` files. The indexing engine will automatically extract words,
        compute positional token offsets, and update both the inverted index and sorted vocabulary.
        """)

        uploaded_files = st.file_uploader(
            "Select text documents (.txt):",
            type=["txt"],
            accept_multiple_files=True
        )

        if uploaded_files:
            if st.button("📥 Index Uploaded Documents", type="primary"):
                success_count = 0
                for up in uploaded_files:
                    try:
                        raw_str = up.read().decode("utf-8", errors="ignore")
                        indexer.add_document(up.name, raw_str)
                        success_count += 1
                    except Exception as ex:
                        st.error(f"Error processing {up.name}: {ex}")

                st.success(f"Successfully processed and indexed {success_count} document(s)!")
                # Update snapshot
                try:
                    indexer.inverted_index.to_json(os.path.join(BASE_DIR, "data", "index.json"))
                except Exception:
                    pass
                st.rerun()


# ==============================================================================
# PAGE 4: ALGORITHM LAB
# ==============================================================================
elif menu_option == "🔬 Algorithm Lab":
    st.markdown('<div class="page-header">🔬 Algorithm Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Inspect the inner workings of Linear Search vs. Binary Search on real vocabulary data.</div>', unsafe_allow_html=True)

    sorted_vocab = indexer.inverted_index.get_sorted_vocabulary()
    unsorted_vocab = indexer.inverted_index.get_unsorted_vocabulary()
    vocab_size = len(sorted_vocab)

    col_target, col_algo = st.columns([3, 2])
    with col_target:
        test_term = st.text_input("Enter Search Keyword for Lab Test:", value="examination")
    with col_algo:
        lab_mode = st.radio("Select Mode:", ["Compare Both", "Linear Search Only", "Binary Search Only"], horizontal=True)

    clean_term = test_term.strip().lower()

    if clean_term:
        res_linear = None
        res_binary = None

        if lab_mode in ("Compare Both", "Linear Search Only"):
            res_linear = linear_search(sorted_vocab, clean_term, record_trace=True)
        if lab_mode in ("Compare Both", "Binary Search Only"):
            res_binary = binary_search(sorted_vocab, clean_term, record_trace=True)

        st.markdown("---")

        if lab_mode == "Compare Both":
            c_l, c_b = st.columns(2)
            with c_l:
                st.markdown("#### 🔴 Linear Search O(n)")
                st.metric("Status", "Found ✅" if res_linear.found else "Not Found ❌")
                m1, m2 = st.columns(2)
                m1.metric("Comparisons", f"{res_linear.comparisons}")
                m2.metric("Execution Time", f"{res_linear.execution_time_ms:.4f} ms")
                st.caption(f"Search space: {vocab_size} unique words | Inspected {res_linear.comparisons} items")

            with c_b:
                st.markdown("#### 🔵 Binary Search O(log n)")
                st.metric("Status", "Found ✅" if res_binary.found else "Not Found ❌")
                m1, m2 = st.columns(2)
                m1.metric("Comparisons", f"{res_binary.comparisons}")
                m2.metric("Execution Time", f"{res_binary.execution_time_ms:.4f} ms")
                st.caption(f"Search space: {vocab_size} unique words | Inspected {res_binary.comparisons} items")

            if res_linear.comparisons > res_binary.comparisons:
                st.success(
                    f"⚡ **Efficiency Comparison:** Binary Search required **{res_linear.comparisons - res_binary.comparisons} fewer comparisons** "
                    f"({res_linear.comparisons / max(1, res_binary.comparisons):.1f}x reduction) than Linear Search."
                )

        elif res_linear:
            st.metric("Status", "Found ✅" if res_linear.found else "Not Found ❌")
            st.metric("Linear Comparisons Made", f"{res_linear.comparisons}")
            st.metric("Linear Execution Time", f"{res_linear.execution_time_ms:.4f} ms")

        elif res_binary:
            st.metric("Status", "Found ✅" if res_binary.found else "Not Found ❌")
            st.metric("Binary Comparisons Made", f"{res_binary.comparisons}")
            st.metric("Binary Execution Time", f"{res_binary.execution_time_ms:.4f} ms")

        # Step Traces
        st.markdown("---")
        st.markdown("### 🪜 Step-by-Step Pointer Trace Table")

        if res_binary and res_binary.trace:
            st.markdown("#### 🔵 Binary Search Pointer History")
            st.caption("Watch Left, Right, and Mid pointers repeatedly halve the search interval:")
            st.dataframe(pd.DataFrame(res_binary.trace), use_container_width=True)

        if res_linear and res_linear.trace:
            with st.expander("🔴 View Linear Search Step History (First 50 Steps)"):
                st.dataframe(pd.DataFrame(res_linear.trace), use_container_width=True)

        # Failure Demonstration on Unsorted Data
        st.markdown("---")
        st.markdown("### ⚠️ Experiment: Why Binary Search Fails on Unsorted Data")
        st.markdown("""
        Binary Search eliminates half the array assuming values are monotonically ordered.
        Let's observe what happens when we run Binary Search on an **unsorted** vocabulary:
        """)

        if st.button("Run Failure Experiment on Unsorted Data"):
            l_unsorted = linear_search(unsorted_vocab, clean_term, record_trace=False)
            b_unsorted = binary_search(unsorted_vocab, clean_term, record_trace=False)

            u_col1, u_col2 = st.columns(2)
            with u_col1:
                st.markdown("**Linear Search on Unsorted Data:**")
                st.write(f"Result: {'Found ✅' if l_unsorted.found else 'Not Found ❌'}")
                st.write(f"Comparisons: {l_unsorted.comparisons}")
                st.success("Linear Search succeeded because it doesn't assume any ordering.")

            with u_col2:
                st.markdown("**Binary Search on Unsorted Data:**")
                st.write(f"Result: {'Found ✅' if b_unsorted.found else 'FAILED / MISSED ❌'}")
                st.write(f"Comparisons: {b_unsorted.comparisons}")
                if not b_unsorted.found and l_unsorted.found:
                    st.error("Binary Search FAILED to locate an existing term because unsorted order pruned the wrong partition!")
                else:
                    st.warning("Binary Search may occasionally stumble on an element, but is completely unreliable without sorting.")


# ==============================================================================
# PAGE 5: PERFORMANCE BENCHMARKING
# ==============================================================================
elif menu_option == "📊 Performance Benchmark":
    st.markdown('<div class="page-header">📊 Empirical Benchmarking Suite</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Scientific performance profiling of O(n) Linear Search vs. O(log n) Binary Search.</div>', unsafe_allow_html=True)

    b_col1, b_col2, b_col3 = st.columns([2, 2, 2])
    with b_col1:
        scenario = st.selectbox(
            "Benchmark Scenario:",
            ["average", "worst_case", "best_case", "unsuccessful"],
            format_func=lambda s: {
                "average": "Average Case (Random Query)",
                "worst_case": "Worst Case (Last Element)",
                "best_case": "Best Case (Midpoint Match)",
                "unsuccessful": "Unsuccessful Search (Missing Term)"
            }[s]
        )
    with b_col2:
        iterations = st.slider("Repetitions per Size (for timing stability):", min_value=1, max_value=20, value=5)
    with b_col3:
        sizes_input = st.multiselect(
            "Dataset Sizes (N):",
            [100, 500, 1000, 2500, 5000, 7500, 10000],
            default=[100, 500, 1000, 5000, 10000]
        )

    if st.button("🚀 Run Live Benchmark Experiment", type="primary"):
        sorted_sizes = sorted(sizes_input)
        with st.spinner("Executing empirical experiments across both algorithms..."):
            seeds = list(indexer.inverted_index.index.keys())
            report = run_campus_benchmark(
                sizes=sorted_sizes,
                scenario=scenario,
                iterations=iterations,
                seed_words=seeds
            )

        st.success("✅ Empirical benchmarking completed!")

        # Results Data Table
        st.markdown("### 📋 Empirical Measurement Table")
        table_rows = []
        for pt in report.points:
            comp_ratio = (pt.linear_comparisons / pt.binary_comparisons) if pt.binary_comparisons > 0 else 1.0
            table_rows.append({
                "Dataset Size (N)": f"{pt.size:,}",
                "Linear Time (ms)": f"{pt.linear_time_ms:.5f}",
                "Binary Time (ms)": f"{pt.binary_time_ms:.5f}",
                "Linear Comparisons": f"{pt.linear_comparisons:,}",
                "Binary Comparisons": f"{pt.binary_comparisons:,}",
                "Comparison Reduction": f"{comp_ratio:.1f}x",
                "Theoretical Linear": f"{pt.theoretical_linear_ops:,}",
                "Theoretical Binary": f"{pt.theoretical_binary_ops:,}"
            })

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

        # 4 Matplotlib Plots
        st.markdown("### 📈 Visualizing Asymptotic Behavior (4 Publication Charts)")
        fig = render_benchmark_charts(report)
        st.pyplot(fig)

        # Empirical & Theoretical Caveats
        st.markdown("---")
        st.markdown("### 🔬 Critical Engineering & Measurement Insights")
        st.info("""
        1. **Separation of Indexing/Sorting Overhead:**  
           Sorting an unsorted list takes $\\mathcal{O}(n \\log n)$ time. In a search engine, this overhead is paid **once** during the offline indexing phase. The individual query resolution is purely $\\mathcal{O}(\\log n)$.
        2. **Is Binary Search Always Faster?**  
           No! For very small datasets ($N < 20$), Linear Search is frequently faster in wall-clock time because it has lower pointer calculation overhead and leverages contiguous CPU cache prefetching. Additionally, if an unsorted dataset is only searched once, Linear Search $\\mathcal{O}(n)$ is superior to Sorting + Binary Search $\\mathcal{O}(n \\log n)$.
        3. **Hardware & Measurement Limitations:**  
           Wall-clock timings are subject to CPU clock fluctuations, operating system thread context switching, and Python bytecode interpretation. However, the **number of comparisons** is an absolute mathematical metric that strictly follows $\\mathcal{O}(n)$ and $\\mathcal{O}(\\log n)$ across all systems.
        """)


# ==============================================================================
# PAGE 6: HOW SEARCH WORKS (EDUCATIONAL MODE)
# ==============================================================================
elif menu_option == "📚 How Search Works":
    st.markdown('<div class="page-header">📚 How Search Works</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Master search engine mechanics, inverted indexing, and algorithmic complexity.</div>', unsafe_allow_html=True)

    tab_concepts, tab_lin, tab_bin, tab_dryrun = st.tabs([
        "🧠 Core Indexing Concepts",
        "🔴 Linear Search Deep Dive",
        "🔵 Binary Search Deep Dive",
        "🧪 Interactive Dry-Run Simulator"
    ])

    with tab_concepts:
        st.markdown("### 1. Inverted Index vs. Sorted Vocabulary")
        st.markdown("""
        - **Inverted Index:** A hash map data structure that maps words to their occurrences in documents:
          ```json
          {
            "examination": {
              "doc_01_exam_schedule.txt": [12, 45],
              "doc_02_admit_card_circular.txt": [8]
            }
          }
          ```
        - **Sorted Vocabulary:** The list of unique keys from the inverted index, stored in ascending lexicographical order:
          `["academic", "calendar", "circular", "examination", "library", ...]`
        - **Why both are used:** The sorted vocabulary enables **Binary Search $\\mathcal{O}(\\log n)$** to rapidly determine whether a query word exists. Once found, the inverted index immediately delivers the document postings and positional offsets without scanning document files.
        """)

        st.markdown("### 2. Tokenization & Text Normalization")
        st.markdown("""
        Before indexing, raw documents undergo:
        1. **Case Normalization:** Converting all characters to lowercase so that `EXAM`, `Exam`, and `exam` map to the same token.
        2. **Punctuation Stripping:** Removing non-alphanumeric symbols so attached punctuation (e.g. `schedule.`, `schedule,`) becomes `schedule`.
        3. **Positional Offset Recording:** Recording the sequential word index to power snippet generation and phrase searches.
        """)

        st.markdown("### 3. Asymptotic Time Complexity & Big O")
        st.markdown("""
        - **Big O Notation:** Classifies algorithms based on their growth rate as input size $n \\to \\infty$.
        - **Linear $\\mathcal{O}(n)$:** Time or operations scale proportionally with size.
        - **Logarithmic $\\mathcal{O}(\\log n)$:** Operations increase only by 1 when input size doubles.
        """)

    with tab_lin:
        st.markdown("### 🔴 Linear Search Mechanics")
        st.markdown("""
        **Definition:**  
        Sequential scan checking elements one by one from index 0 to $n-1$.

        **Complexity:**  
        - Best Case: $\\mathcal{O}(1)$ (element at index 0)
        - Average Case: $\\mathcal{O}(n)$ (checks $\\approx n/2$ elements)
        - Worst Case: $\\mathcal{O}(n)$ (checks all $n$ elements)
        - Space Complexity: $\\mathcal{O}(1)$

        **Pros:** Simple, works on unsorted data, works on linked lists.  
        **Cons:** Unacceptable for large web/campus repositories with millions of terms.
        """)

    with tab_bin:
        st.markdown("### 🔵 Binary Search Mechanics")
        st.markdown("""
        **Definition:**  
        Divide-and-Conquer algorithm repeatedly halving the search interval on ordered datasets.

        **The Sorted Data Invariant:**  
        If $\\text{target} < \\text{data}[\\text{mid}]$, all elements after $\\text{mid}$ are guaranteed to be greater than target. This deduction is mathematically valid **only** if the array is strictly sorted.

        **Complexity:**  
        - Best Case: $\\mathcal{O}(1)$ (element at initial mid)
        - Average Case: $\\mathcal{O}(\\log_2 n)$
        - Worst Case: $\\mathcal{O}(\\log_2 n)$
        - Space Complexity: $\\mathcal{O}(1)$ iterative

        **Comparisons:**  
        For $N = 10,000$, Binary Search resolves in at most **14 comparisons** ($2^{14} = 16,384 > 10,000$).
        """)

    with tab_dryrun:
        st.markdown("### 🧪 Step-by-Step Interactive Dry-Run")
        st.caption("Inspect pointer dynamics with a custom array or the default textbook sample:")

        d_col1, d_col2 = st.columns([3, 1])
        with d_col1:
            arr_input = st.text_input("Sorted Array (comma-separated):", value="10, 20, 30, 40, 50, 60, 70")
        with d_col2:
            target_input = st.text_input("Search Target:", value="50")

        try:
            tokens = [x.strip() for x in arr_input.split(",") if x.strip()]
            if all(t.lstrip("-").isdigit() for t in tokens):
                typed_arr = [int(t) for t in tokens]
                typed_target = int(target_input)
            else:
                typed_arr = tokens
                typed_target = target_input

            if typed_arr != sorted(typed_arr):
                st.error("Input array must be sorted in ascending order for Binary Search!")
            else:
                b_run = []
                l = 0
                r = len(typed_arr) - 1
                b_step = 0
                b_found = False

                while l <= r:
                    b_step += 1
                    m = l + (r - l) // 2
                    val = typed_arr[m]

                    if val == typed_target:
                        b_run.append({
                            "Step": b_step, "Left": l, "Right": r, "Mid": m,
                            "Value": val, "Comparison": f"{typed_target} == {val}",
                            "Action": "Match Found! Terminating."
                        })
                        b_found = True
                        break
                    elif typed_target < val:
                        b_run.append({
                            "Step": b_step, "Left": l, "Right": r, "Mid": m,
                            "Value": val, "Comparison": f"{typed_target} < {val}",
                            "Action": f"Prune right half -> Right = {m - 1}"
                        })
                        r = m - 1
                    else:
                        b_run.append({
                            "Step": b_step, "Left": l, "Right": r, "Mid": m,
                            "Value": val, "Comparison": f"{typed_target} > {val}",
                            "Action": f"Prune left half -> Left = {m + 1}"
                        })
                        l = m + 1

                st.markdown("#### 🔵 Binary Search Dry-Run Table")
                st.dataframe(pd.DataFrame(b_run), use_container_width=True)
                st.caption(f"Total Binary Comparisons: **{b_step}** (Result: {'Found' if b_found else 'Not Found'})")

        except Exception as e:
            st.error(f"Error executing dry run: {e}")

