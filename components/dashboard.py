"""
CampusFind Home Dashboard Component.

Renders SaaS-style repository statistics, category overview cards,
recent notices, and a prominent hero search bar.
"""

from typing import Callable, Dict
import pandas as pd
import streamlit as st
from indexing.text_indexer import TextIndexer


def render_home_dashboard(indexer: TextIndexer, on_search_callback: Callable[[str], None]) -> None:
    """
    Renders the central CampusFind institutional overview dashboard.

    Parameters:
        indexer (TextIndexer): The active text indexing service.
        on_search_callback (Callable): Callback triggered when a search is executed from the hero bar.
    """
    stats = indexer.get_statistics()

    # Hero Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
                padding: 32px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 24px;">
        <h1 style="color: #38BDF8; margin: 0; font-size: 2.4rem; font-weight: 800;">CampusFind</h1>
        <p style="color: #94A3B8; font-size: 1.15rem; margin-top: 6px; margin-bottom: 20px;">
            Your Campus Information, One Search Away. Centralized document repository powered by classical search algorithms.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Prominent Hero Search Bar
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        hero_query = st.text_input(
            "Search Campus Repository:",
            placeholder="Type a keyword (e.g. examination, syllabus, attendance, placement, hackathon, lab)...",
            label_visibility="collapsed",
            key="hero_search_input"
        )
    with h_col2:
        search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)

    if (search_clicked or hero_query) and hero_query.strip():
        on_search_callback(hero_query.strip())
        return

    # Popular Search Tag Pills
    st.markdown("**🔥 Frequently Searched Topics:**")
    pill_cols = st.columns(6)
    popular_terms = ["examination", "syllabus", "attendance", "placement", "hackathon", "library"]
    for i, term in enumerate(popular_terms):
        if pill_cols[i].button(term, key=f"pill_{term}", use_container_width=True):
            on_search_callback(term)
            return

    st.markdown("<br>", unsafe_allow_html=True)

    # Repository KPI Statistics Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Documents Indexed", f"{stats['total_documents']}", delta="21 Active Records")
    with m2:
        st.metric("Unique Vocabulary Words", f"{stats['unique_words']:,}", delta="Lexicographically Sorted")
    with m3:
        st.metric("Total Searchable Terms", f"{stats['total_terms']:,}", delta="Indexed In-Memory")
    with m4:
        st.metric("Active Categories", f"{len(stats['categories'])}", delta="All Departments")

    st.markdown("---")

    # Layout: Available Categories & Recent Campus Notices
    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown("### 📂 Available Document Categories")
        st.caption("Centralized institutional classifications:")

        cat_counts = stats["category_counts"]
        cat_data = [{"Category": cat, "Total Documents": count} for cat, count in sorted(cat_counts.items())]
        st.dataframe(pd.DataFrame(cat_data), use_container_width=True, hide_index=True)

    with c_right:
        st.markdown("### 🕒 Recently Published Notices")
        st.caption("Latest gazetted academic circulars and administrative guidelines:")

        recent_rows = []
        for doc in stats["recent_documents"]:
            recent_rows.append({
                "Date": doc.date,
                "Title": doc.title,
                "Category": doc.category,
                "Type": doc.doc_type
            })

        st.dataframe(pd.DataFrame(recent_rows), use_container_width=True, hide_index=True)

