"""
Tab 2 — Inventory & Categories
Shows revenue-per-inventory-unit, category rental share,
and top films by utilisation rate.
"""

import pandas as pd
import streamlit as st
import plotly.express as px


def render(cat_df, inv_df, chart_theme):
    """Render the Inventory & Categories tab."""

    # ── Revenue per inventory unit ────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Revenue per Inventory Unit</div>', unsafe_allow_html=True)
    fig = px.bar(
        cat_df.sort_values("rev_per_inv", ascending=True),
        x="rev_per_inv", y="category", orientation="h",
        text_auto=".1f", color="rev_per_inv",
        color_continuous_scale=["#1E3A8A", "#F9A8D4"],
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_traces(textfont_size=9)
    st.plotly_chart(chart_theme(fig, h=360, t=10), use_container_width=True)

    # ── Category rental share + top films table ───────────────────────────────
    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown('<div class="section-hdr">Category Rental Share</div>', unsafe_allow_html=True)
        fig = px.pie(
            cat_df, names="category", values="rentals", hole=0.45,
            color_discrete_sequence=["#1E3A8A", "#2E4FB8", "#EC4899", "#F9A8D4", "#FBCFE8", "#7DD3FC"],
        )
        fig.update_traces(textinfo="percent", textfont_size=8,
                          marker=dict(line=dict(color="#0A1628", width=1)))
        fig.update_layout(legend=dict(font=dict(size=8)))
        st.plotly_chart(chart_theme(fig, h=200, t=10), use_container_width=True)

    with c2:
        st.markdown('<div class="section-hdr">Top 15 Films by Utilization Rate</div>', unsafe_allow_html=True)
        top_util = (
            inv_df.nlargest(15, "util_rate")
            [["title", "category", "copies", "times_rented", "util_rate", "revenue"]]
            .copy()
        )
        top_util.columns = ["Film", "Category", "Copies", "Rentals", "Util Rate", "Revenue ($)"]
        top_util["Revenue ($)"] = top_util["Revenue ($)"].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) else "$0"
        )
        st.dataframe(top_util, use_container_width=True, height=200, hide_index=True)

    # ── Insight ───────────────────────────────────────────────────────────────
    low_util  = inv_df[inv_df["util_rate"] < 1].shape[0]
    high_util = inv_df[inv_df["util_rate"] >= 5].shape[0]
    st.markdown(f"""
    <div class="insight-box">
      📌 <strong>Inventory Intelligence:</strong> <strong>{high_util}</strong> films achieve
      ≥5× utilization (top performers). <strong>{low_util}</strong> films have &lt;1 rental per
      copy — repositioning or liquidating these titles would free up capital.
      Focus stocking on high-revenue-per-inventory categories.
    </div>""", unsafe_allow_html=True)
