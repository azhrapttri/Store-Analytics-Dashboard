"""
DVDRental Intelligence Hub
Entry point — run with: streamlit run app.py
"""

import warnings
warnings.filterwarnings("ignore")

import streamlit as st

from config.theme import get_palette, apply_chart_theme
from config.styles import get_stylesheet
from utils.filters import get_available_months
from services.queries import (
    load_kpi,
    load_store_compare,
    load_customer_segments,
    load_trend,
    load_category,
    load_geo,
    load_hourly,
    load_top_customers,
    load_inventory_util,
    load_rental_duration,
)
from views import tab_overview, tab_inventory, tab_customers, tab_patterns, tab_ml

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DVDRental Intelligence Hub",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme ─────────────────────────────────────────────────────────────────────
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

palette = get_palette(st.session_state.theme_mode)


def chart_theme(fig, **kwargs):
    return apply_chart_theme(fig, palette, st.session_state.theme_mode, **kwargs)


st.markdown(get_stylesheet(palette), unsafe_allow_html=True)

# ── Navigation bar ────────────────────────────────────────────────────────────
with st.container(border=True):
    nav_left, nav_right = st.columns([5, 1.2], vertical_alignment="center")
    with nav_left:
        st.markdown("""
        <div style="padding:2px 6px;">
          <div class="nav-brand">🎬 Store Analytics Dashboard</div>
          <div class="nav-subtitle">DVD Rental Database · Rental-Based Analytics</div>
        </div>
        """, unsafe_allow_html=True)
    with nav_right:
        is_dark  = st.toggle("🌙 Dark Mode", value=(st.session_state.theme_mode == "Dark"),
                             key="theme_toggle", help="Toggle Dark / Light mode")
        new_mode = "Dark" if is_dark else "Light"
        if new_mode != st.session_state.theme_mode:
            st.session_state.theme_mode = new_mode
            st.rerun()

st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

# ── Global filters ────────────────────────────────────────────────────────────
fc1, fc2, fc3 = st.columns([1, 1, 5])
with fc1:
    store_f = st.selectbox("🏪 Store", ["All", "1", "2"],
                           label_visibility="collapsed", key="sf")
with fc2:
    month_f = st.selectbox("📅 Month", get_available_months(),
                           label_visibility="collapsed", key="mf")
with fc3:
    if month_f == "2005-05":
        st.markdown("""
        <div style="padding-top:6px;font-size:0.68rem;color:#F59E0B;">
          ⚠️ May 2005: Rental activity available but revenue = $0 (payments recorded post-period).
          Rental counts &amp; patterns are still valid.
        </div>""", unsafe_allow_html=True)
    else:
        store_label = f"Store {store_f}" if store_f != "All" else "All Stores"
        month_label = month_f if month_f != "All" else "All Months (May 2005 – Feb 2006)"
        st.markdown(
            f'<div style="padding-top:6px;font-size:0.68rem;color:{palette["muted"]};">'
            f"{store_label} &nbsp;|&nbsp; {month_label}</div>",
            unsafe_allow_html=True,
        )

# ── Data loading ──────────────────────────────────────────────────────────────
kpi                  = load_kpi(store_f, month_f)
store_df             = load_store_compare(month_f)
cust_seg_df          = load_customer_segments(store_f, month_f)
trend_df, trend_type = load_trend(store_f, month_f)
cat_df               = load_category(store_f, month_f)
geo_df               = load_geo(store_f, month_f)
hourly_df            = load_hourly(store_f, month_f)
dur_df               = load_rental_duration(store_f, month_f)
top_custs            = load_top_customers(store_f, month_f)
inv_df               = load_inventory_util()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📦 Inventory & Categories",
    "👥 Customers & Geo",
    "⏱️ Rental Patterns",
    "🤖 ML Predictions",
])

with tab1:
    tab_overview.render(kpi, store_df, trend_df, trend_type, cust_seg_df, cat_df,
                        month_f, palette, chart_theme)

with tab2:
    tab_inventory.render(cat_df, inv_df, chart_theme)

with tab3:
    tab_customers.render(geo_df, top_custs, palette, chart_theme)

with tab4:
    tab_patterns.render(hourly_df, dur_df, chart_theme)

with tab5:
    tab_ml.render(palette, chart_theme)
