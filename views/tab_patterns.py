"""
Tab 4 — Rental Patterns
Shows hourly rental distribution, average rental duration by day-of-week,
revenue by day-of-week, and revenue by hour.
"""

import streamlit as st
import plotly.express as px


DAYS_SHORT = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
DAYS_FULL  = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def render(hourly_df, dur_df, chart_theme):
    """Render the Rental Patterns tab."""

    # ── Row 1: Hourly pattern + avg duration ─────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-hdr">Hourly Rental Pattern</div>', unsafe_allow_html=True)
        hourly_agg = hourly_df.groupby("hour")["rentals"].sum().reset_index()
        fig = px.bar(hourly_agg, x="hour", y="rentals",
                     color="rentals", color_continuous_scale=["#0A1628", "#1E3A8A", "#EC4899"])
        fig.update_layout(coloraxis_showscale=False,
                          xaxis=dict(tickmode="linear", dtick=2))
        st.plotly_chart(chart_theme(fig, h=220, t=10), use_container_width=True)

    with c2:
        st.markdown('<div class="section-hdr">Avg Rental Duration by Day of Week (hours)</div>',
                    unsafe_allow_html=True)
        dur_plot = dur_df.copy()
        dur_plot["day"] = dur_plot["dow"].apply(lambda x: DAYS_SHORT[int(x)])
        y_max = float(dur_plot["avg_hours"].max()) + 2 if not dur_plot.empty else None
        fig = px.bar(dur_plot, x="day", y="avg_hours", text_auto=".1f",
                     color="avg_hours", color_continuous_scale=["#1E3A8A", "#EC4899"])
        fig.update_layout(
            coloraxis_showscale=False,
            yaxis=dict(range=[98, y_max] if y_max else None),
        )
        fig.update_traces(textfont_size=9)
        st.plotly_chart(chart_theme(fig, h=220, t=10), use_container_width=True)

    # ── Row 2: Revenue by DOW + revenue by hour ───────────────────────────────
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-hdr">Revenue by Day of Week</div>', unsafe_allow_html=True)
        dow_agg = hourly_df.groupby("dow")["revenue"].sum().reset_index()
        dow_agg["day"] = dow_agg["dow"].apply(lambda x: DAYS_FULL[int(x)])
        fig = px.bar(dow_agg, x="day", y="revenue", text_auto=".3s",
                     color="revenue", color_continuous_scale=["#1E3A8A", "#F9A8D4"])
        fig.update_layout(coloraxis_showscale=False)
        fig.update_traces(textfont_size=8)
        st.plotly_chart(chart_theme(fig, h=200, t=10), use_container_width=True)

    with c4:
        st.markdown('<div class="section-hdr">Revenue by Hour of Day</div>', unsafe_allow_html=True)
        hr_rev = hourly_df.groupby("hour")["revenue"].sum().reset_index()
        fig = px.area(hr_rev, x="hour", y="revenue", color_discrete_sequence=["#1E3A8A"])
        fig.update_traces(fill="tozeroy", fillcolor="rgba(124,58,237,0.15)", line_width=2)
        fig.update_layout(xaxis=dict(tickmode="linear", dtick=2))
        st.plotly_chart(chart_theme(fig, h=200, t=10), use_container_width=True)

    # ── Insight box ───────────────────────────────────────────────────────────
    if not hourly_df.empty:
        peak_hour = int(hourly_df.groupby("hour")["rentals"].sum().idxmax())
        peak_day  = DAYS_FULL[int(hourly_df.groupby("dow")["rentals"].sum().idxmax())]
        st.markdown(f"""
        <div class="insight-box">
          ⏰ <strong>Peak Pattern:</strong> Highest rental activity occurs at <strong>{peak_hour}:00</strong>.
          <strong>{peak_day}</strong> is the busiest day of the week. Rental duration data uses
          <em>return_date − rental_date</em> directly — no payment timing involved, so this is
          fully reliable. Staff scheduling and promotions should align with these peak windows.
        </div>""", unsafe_allow_html=True)
