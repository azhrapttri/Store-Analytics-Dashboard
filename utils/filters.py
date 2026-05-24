"""
Global filter helpers.
Provides SQL clause builders and the available month list used across all tabs.
"""

import streamlit as st
from config.database import query


@st.cache_data(show_spinner=False)
def get_available_months() -> list:
    """Return ['All'] + sorted list of YYYY-MM strings from the rental table."""
    df = query("SELECT DISTINCT TO_CHAR(rental_date,'YYYY-MM') AS m FROM rental ORDER BY m")
    return ["All"] + df["m"].tolist()


def store_clause(store_filter: str, alias: str = "i") -> str:
    """Return a SQL AND clause that filters by store_id, or empty string for 'All'."""
    if store_filter != "All":
        return f"AND {alias}.store_id = {int(store_filter)}"
    return ""


def month_clause(month_filter: str, alias: str = "r") -> str:
    """Return a SQL AND clause that filters by rental_date month, or empty string for 'All'."""
    if month_filter != "All":
        return f"AND TO_CHAR({alias}.rental_date, 'YYYY-MM') = '{month_filter}'"
    return ""
