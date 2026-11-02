"""
Search Results Presentation Component.

Renders matching document cards, execution metrics, contextual snippets,
word positions, and full document modal viewers.
"""

from typing import Dict, List, Optional
import pandas as pd
import streamlit as st
from search.search_engine import SearchResponse, SearchResultItem


def render_search_results(response: SearchResponse, documents_body: Dict[str, str]) -> None:
    """
    Renders the complete search response view.

    Parameters:
        response (SearchResponse): Search engine query response.
        documents_body (Dict[str, str]): Full body text dictionary for document viewing.
    """
    st.markdown(f"### Results for `\"{response.query}\"`")

    # Algorithm Performance Metrics Bar
    if response.linear_metrics or response.binary_metrics:
        p_col1, p_col2 = st.columns(2)

        if response.linear_metrics and response.binary_metrics:
            lin = response.linear_metrics
            bin_m = response.binary_metrics

            with p_col1:
                st.markdown("""
                <div style="background-color: #1E293B; border-left: 4px solid #F43F5E;
                            padding: 12px 16px; border-radius: 6px; margin-bottom: 12px;">
                    <b style="color: #F43F5E;">LINEAR SEARCH</b> (O(n))<br>
                    <span style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">
                        {comps} comparisons
                    </span> &nbsp;|&nbsp;
                    <span style="color: #94A3B8;">{time:.4f} ms</span>
                </div>
                """.format(comps=lin.comparisons, time=lin.execution_time_ms), unsafe_allow_html=True)

            with p_col2:
                st.markdown("""
                <div style="background-color: #1E293B; border-left: 4px solid #38BDF8;
                            padding: 12px 16px; border-radius: 6px; margin-bottom: 12px;">
                    <b style="color: #38BDF8;">BINARY SEARCH</b> (O(log n))<br>
                    <span style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">
                        {comps} comparisons
                    </span> &nbsp;|&nbsp;
                    <span style="color: #94A3B8;">{time:.4f} ms</span>
                </div>
                """.format(comps=bin_m.comparisons, time=bin_m.execution_time_ms), unsafe_allow_html=True)

            if lin.comparisons > bin_m.comparisons:
                reduction = lin.comparisons / max(1, bin_m.comparisons)
                st.success(
                    f"⚡ **Algorithmic Efficiency:** Binary Search required **{lin.comparisons - bin_m.comparisons} fewer comparisons** "
                    f"than Linear Search ({reduction:.1f}x reduction in operations) to resolve this query in the vocabulary!"
                )

        elif response.linear_metrics:
            lin = response.linear_metrics
            st.info(f"**Linear Search O(n):** {lin.comparisons} comparisons | {lin.execution_time_ms:.4f} ms")

        elif response.binary_metrics:
            bin_m = response.binary_metrics
            st.info(f"**Binary Search O(log n):** {bin_m.comparisons} comparisons | {bin_m.execution_time_ms:.4f} ms")

    # Match Summary
    if not response.found or not response.items:
        st.warning(f"No campus documents matched the keyword **'{response.query}'** with current filters.")
        st.caption("Try searching for broader keywords like: `examination`, `syllabus`, `attendance`, `placement`, `guidelines`, `credit`.")
        return

    st.caption(
        f"Found **{response.total_matching_documents} matching document(s)** "
        f"with **{response.total_occurrences} total occurrence(s)**."
    )

    # Document Result Cards
    for idx, item in enumerate(response.items, start=1):
        meta = item.metadata
        with st.container():
            st.markdown(f"""
            <div style="background-color: #1E293B; border: 1px solid #334155; border-radius: 8px;
                        padding: 18px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">
                        {idx}. {meta.title}
                    </span>
                    <span style="background-color: #0F172A; border: 1px solid #475569; color: #38BDF8;
                                padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">
                        {meta.category}
                    </span>
                </div>
                <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 10px;">
                    <b>File:</b> {meta.filename} &nbsp;|&nbsp;
                    <b>Department:</b> {meta.department} &nbsp;|&nbsp;
                    <b>Type:</b> {meta.doc_type} &nbsp;|&nbsp;
                    <b>Date:</b> {meta.date} &nbsp;|&nbsp;
                    <b style="color: #FBBF24;">Occurrences:</b> {item.occurrences_count} time(s)
                </div>
                <div style="background-color: #0F172A; padding: 12px; border-radius: 6px;
                            border-left: 3px solid #38BDF8; font-size: 0.95rem; color: #CBD5E1; margin-bottom: 10px;">
                    "{item.snippet}"
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"🔍 Inspect Word Positions & Full Content ({meta.filename})"):
                st.markdown(f"**Word Offset Positions in Document:** `{item.positions}`")
                full_text = documents_body.get(item.doc_id, "")
                st.text_area("Full Document Text:", value=full_text, height=180, disabled=True, key=f"full_doc_{item.doc_id}")

    # Trace Expanders for Educational Inspection
    if response.binary_metrics and response.binary_metrics.trace:
        with st.expander("🪜 Binary Search Pointer Execution Trace (Algorithm Steps)"):
            st.dataframe(pd.DataFrame(response.binary_metrics.trace), use_container_width=True)

    if response.linear_metrics and response.linear_metrics.trace:
        with st.expander("🪜 Linear Search Comparison Trace (First 50 Sequential Steps)"):
            st.dataframe(pd.DataFrame(response.linear_metrics.trace), use_container_width=True)

