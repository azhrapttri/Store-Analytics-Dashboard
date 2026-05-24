"""
Data access layer — all database queries live here.

Filtering conventions applied consistently across every query:
  - Store attribution  → i.store_id  (actual transaction store, not customer registration store)
  - Time filter        → r.rental_date
  - Revenue            → SUM(p.amount) joined via rental; no payment_date filter
"""

import streamlit as st
import pandas as pd
from config.database import query
from utils.filters import store_clause, month_clause


@st.cache_data(ttl=300, show_spinner=False)
def load_kpi(store_filter: str, month_filter: str) -> pd.DataFrame:
    """Single-row DataFrame with aggregate KPIs: customers, rentals, revenue, inventory, films."""
    sc = store_clause(store_filter)
    mc = month_clause(month_filter)
    # Customers use aliased subquery (i2/r2) to avoid collision with outer aliases
    sc2 = store_clause(store_filter, alias="i2")
    mc2 = month_clause(month_filter, alias="r2")

    return query(f"""
        SELECT
          (SELECT COUNT(DISTINCT r2.customer_id)
           FROM rental r2
           JOIN inventory i2 ON r2.inventory_id = i2.inventory_id
           WHERE 1=1 {sc2} {mc2}
          ) AS customers,

          (SELECT COUNT(DISTINCT r.rental_id)
           FROM rental r
           JOIN inventory i ON r.inventory_id = i.inventory_id
           WHERE 1=1 {sc} {mc}
          ) AS rentals,

          (SELECT COALESCE(SUM(p.amount), 0)
           FROM payment p
           JOIN rental r ON p.rental_id = r.rental_id
           JOIN inventory i ON r.inventory_id = i.inventory_id
           WHERE 1=1 {sc} {mc}
          ) AS revenue,

          (SELECT COUNT(DISTINCT i.inventory_id) FROM inventory i WHERE 1=1 {sc}) AS inventory,
          (SELECT COUNT(DISTINCT i.film_id)       FROM inventory i WHERE 1=1 {sc}) AS films
    """)


@st.cache_data(ttl=300, show_spinner=False)
def load_store_compare(month_filter: str) -> pd.DataFrame:
    """Revenue, rentals, and customer count grouped by store."""
    mc = month_clause(month_filter)
    df = query(f"""
        SELECT
            i.store_id::text AS store_id,
            COALESCE(SUM(p.amount), 0) AS revenue,
            COUNT(DISTINCT r.rental_id) AS rentals,
            COUNT(DISTINCT r.customer_id) AS customers
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        LEFT JOIN payment p ON p.rental_id = r.rental_id
        WHERE 1=1 {mc}
        GROUP BY i.store_id
        ORDER BY i.store_id
    """)
    df["store_id"] = "Store " + df["store_id"]
    return df


@st.cache_data(ttl=300, show_spinner=False)
def load_customer_segments(store_filter: str, month_filter: str) -> pd.DataFrame:
    """Customer distribution bucketed by total rental count."""
    sc = store_clause(store_filter)
    mc = month_clause(month_filter)
    return query(f"""
        SELECT
            CASE
                WHEN rental_count > 40            THEN '1. Elite (40+ Rentals)'
                WHEN rental_count BETWEEN 30 AND 40 THEN '2. Frequent (30-40)'
                WHEN rental_count BETWEEN 20 AND 29 THEN '3. Regular (20-29)'
                ELSE '4. Casual (<20)'
            END AS customer_segment,
            COUNT(customer_id)  AS total_customers,
            SUM(rental_count)   AS total_rentals_by_segment
        FROM (
            SELECT r.customer_id, COUNT(r.rental_id) AS rental_count
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            WHERE 1=1 {sc} {mc}
            GROUP BY r.customer_id
        ) AS cs
        GROUP BY customer_segment
        ORDER BY customer_segment
    """)


@st.cache_data(ttl=300, show_spinner=False)
def load_trend(store_filter: str, month_filter: str):
    """
    Return (DataFrame, granularity_label).
    Aggregates by month when no month filter is active, by day otherwise.
    """
    sc = store_clause(store_filter)
    if month_filter == "All":
        df = query(f"""
            SELECT
                DATE_TRUNC('month', r.rental_date) AS period,
                i.store_id::text AS store,
                COUNT(r.rental_id) AS rentals,
                COALESCE(SUM(p.amount), 0) AS revenue
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            LEFT JOIN payment p ON r.rental_id = p.rental_id
            WHERE 1=1 {sc}
            GROUP BY 1, 2 ORDER BY 1, 2
        """)
        label = "Monthly"
    else:
        df = query(f"""
            SELECT
                r.rental_date::date AS period,
                i.store_id::text AS store,
                COUNT(r.rental_id) AS rentals,
                COALESCE(SUM(p.amount), 0) AS revenue
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            LEFT JOIN payment p ON r.rental_id = p.rental_id
            WHERE TO_CHAR(r.rental_date, 'YYYY-MM') = '{month_filter}' {sc}
            GROUP BY 1, 2 ORDER BY 1, 2
        """)
        label = "Daily"

    df["store"] = "Store " + df["store"]
    return df, label


@st.cache_data(ttl=300, show_spinner=False)
def load_category(store_filter: str, month_filter: str) -> pd.DataFrame:
    """Revenue, rentals, inventory, and revenue-per-inventory by film category."""
    sc = store_clause(store_filter)
    mc = month_clause(month_filter)
    return query(f"""
        SELECT
            cat.name AS category,
            COUNT(DISTINCT i.inventory_id) AS inventory,
            COALESCE(SUM(p.amount), 0) AS revenue,
            COUNT(r.rental_id) AS rentals,
            ROUND(COALESCE(SUM(p.amount), 0) / NULLIF(COUNT(DISTINCT i.inventory_id), 0), 2) AS rev_per_inv
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film_category fc ON i.film_id = fc.film_id
        JOIN category cat ON fc.category_id = cat.category_id
        LEFT JOIN payment p ON p.rental_id = r.rental_id
        WHERE 1=1 {sc} {mc}
        GROUP BY cat.name
        ORDER BY revenue DESC
    """)


@st.cache_data(ttl=300, show_spinner=False)
def load_geo(store_filter: str, month_filter: str) -> pd.DataFrame:
    """Revenue, customers, and rentals grouped by country."""
    sc = store_clause(store_filter)
    mc = month_clause(month_filter)
    return query(f"""
        SELECT
            co.country,
            COUNT(DISTINCT r.customer_id) AS customers,
            COALESCE(SUM(p.amount), 0) AS revenue,
            COUNT(r.rental_id) AS rentals
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN customer cu ON r.customer_id = cu.customer_id
        LEFT JOIN payment p ON p.rental_id = r.rental_id
        JOIN address a ON cu.address_id = a.address_id
        JOIN city ci ON a.city_id = ci.city_id
        JOIN country co ON ci.country_id = co.country_id
        WHERE co.country IS NOT NULL {sc} {mc}
        GROUP BY co.country
        ORDER BY revenue DESC
    """)


@st.cache_data(ttl=300, show_spinner=False)
def load_hourly(store_filter: str, month_filter: str) -> pd.DataFrame:
    """Rental and revenue counts by hour and day-of-week."""
    sc = store_clause(store_filter)
    mc = month_clause(month_filter)
    return query(f"""
        SELECT
            EXTRACT(HOUR FROM r.rental_date) AS hour,
            EXTRACT(DOW  FROM r.rental_date) AS dow,
            COUNT(r.rental_id) AS rentals,
            COALESCE(SUM(p.amount), 0) AS revenue
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        LEFT JOIN payment p ON p.rental_id = r.rental_id
        WHERE 1=1 {sc} {mc}
        GROUP BY 1, 2 ORDER BY 1, 2
    """)


@st.cache_data(ttl=300, show_spinner=False)
def load_top_customers(store_filter: str, month_filter: str) -> pd.DataFrame:
    """Top 15 customers ranked by revenue."""
    sc = store_clause(store_filter)
    mc = month_clause(month_filter)
    return query(f"""
        SELECT
            r.customer_id,
            cu.first_name || ' ' || cu.last_name AS name,
            COUNT(r.rental_id) AS rentals,
            COALESCE(SUM(p.amount), 0) AS revenue,
            MAX(r.rental_date)::date AS last_rental
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN customer cu ON r.customer_id = cu.customer_id
        LEFT JOIN payment p ON r.rental_id = p.rental_id
        WHERE 1=1 {sc} {mc}
        GROUP BY r.customer_id, cu.first_name, cu.last_name
        ORDER BY revenue DESC
        LIMIT 15
    """)


@st.cache_data(ttl=300, show_spinner=False)
def load_inventory_util() -> pd.DataFrame:
    """
    Top 100 films by utilisation rate (rentals per copy).
    Global — no store/time filter — to show the full catalogue picture.
    """
    return query("""
        SELECT
            f.title,
            cat.name AS category,
            COUNT(DISTINCT i.inventory_id) AS copies,
            COUNT(r.rental_id) AS times_rented,
            ROUND(COUNT(r.rental_id)::numeric / NULLIF(COUNT(DISTINCT i.inventory_id), 0), 1) AS util_rate,
            COALESCE(SUM(p.amount), 0) AS revenue
        FROM film f
        JOIN inventory i ON f.film_id = i.film_id
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category cat ON fc.category_id = cat.category_id
        LEFT JOIN rental r ON i.inventory_id = r.inventory_id
        LEFT JOIN payment p ON r.rental_id = p.rental_id
        GROUP BY f.film_id, f.title, cat.name
        ORDER BY util_rate DESC
        LIMIT 100
    """)


@st.cache_data(ttl=300, show_spinner=False)
def load_rental_duration(store_filter: str, month_filter: str) -> pd.DataFrame:
    """Average rental duration (hours) grouped by day-of-week."""
    sc = store_clause(store_filter)
    mc = month_clause(month_filter)
    return query(f"""
        SELECT
            EXTRACT(DOW FROM r.rental_date) AS dow,
            ROUND(AVG(EXTRACT(EPOCH FROM (r.return_date - r.rental_date)) / 3600)::numeric, 1) AS avg_hours,
            COUNT(r.rental_id) AS rentals
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        WHERE r.return_date IS NOT NULL {sc} {mc}
        GROUP BY 1 ORDER BY 1
    """)
