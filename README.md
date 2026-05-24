# DVDRental Intelligence Hub

A full-featured analytics dashboard built with **Streamlit** and **PostgreSQL**, powered by the classic [DVD Rental](https://www.postgresqltutorial.com/postgresql-getting-started/postgresql-sample-database/) sample database. Designed for rental store managers to explore business performance, customer behavior, and revenue forecasts — all in one place.

---

## Dashboard Preview

| Dark Mode | Light Mode |
|-----------|------------|
|  |  |

**Tab previews:**

---

## Features

- **Overview**: KPI cards (revenue, rentals, customers, inventory), store comparison charts, and revenue/rental trends
- **Inventory & Categories**: Revenue per inventory unit, category rental share, and top films by utilisation rate
- **Customers & Geo**: Interactive world map, top countries by revenue, customer value segmentation, and top-15 customer table
- **Rental Patterns**: Hourly and day-of-week rental heatmaps, average rental duration analysis
- **ML Predictions**: 3-month revenue forecast using a pre-trained Gradient Boosting model, plus a business decision simulator (what-if analysis)
- **Dark / Light mode** toggle with a navy + soft pink theme
- Global **Store** and **Month** filters applied consistently across all tabs

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | Streamlit, Plotly |
| Backend / Data | PostgreSQL, psycopg2, pandas, numpy |
| Machine Learning | scikit-learn (Gradient Boosting), joblib |
| Language | Python 3.11 |

---

## Project Structure

```
project-midexam/
├── app.py                      # Entry point — streamlit run app.py
├── train_revenue_model.py      # ML model training script (run once)
├── revenue_forecast_model.pkl  # Pre-trained forecast model artifact
├── requirements.txt
├── .gitignore
│
├── config/
│   ├── database.py             # PostgreSQL connection & query executor
│   ├── theme.py                # Color palettes (Dark/Light) & chart theme
│   └── styles.py               # CSS stylesheet builder
│
├── services/
│   └── queries.py              # All data loading functions (SQL queries)
│
├── utils/
│   └── filters.py              # SQL filter clause helpers & month list
│
├── views/
│   ├── tab_overview.py         # Tab 1: KPI, store comparison, trends
│   ├── tab_inventory.py        # Tab 2: Inventory utilisation, categories
│   ├── tab_customers.py        # Tab 3: Geo map, customer segments
│   ├── tab_patterns.py         # Tab 4: Hourly/DOW rental patterns
│   └── tab_ml.py               # Tab 5: Revenue forecast + simulator
│
└── models/
    ├── churn_model.pkl
    ├── revenue_model.pkl
    └── training_report.json
```

---

## Prerequisites

- Python 3.11+
- PostgreSQL with the `dvdrental` database loaded
  → Download: [PostgreSQL Sample Database](https://www.postgresqltutorial.com/postgresql-getting-started/postgresql-sample-database/)

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/dvdrental-dashboard.git
cd dvdrental-dashboard
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure database credentials**

Open `config/database.py` and update the connection settings:
```python
DB_HOST = "localhost"
DB_NAME = "dvdrental"
DB_USER = "postgres"
DB_PASS = "your_password"
```

---

## Running the App

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

---

## Training the ML Model

The pre-trained model (`revenue_forecast_model.pkl`) is included in the repository. If you want to retrain it against your own database:

```bash
python train_revenue_model.py
```

This will regenerate `revenue_forecast_model.pkl` using Leave-One-Out cross-validation optimised for the small 5-month dataset.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.56.0 | Dashboard framework |
| pandas | 3.0.2 | Data manipulation |
| numpy | 2.4.4 | Numerical operations |
| plotly | 6.7.0 | Interactive charts |
| psycopg2-binary | 2.9.11 | PostgreSQL connection |
| scikit-learn | 1.8.0 | ML model (Gradient Boosting) |
| joblib | 1.5.3 | Model serialisation |
| SQLAlchemy | 2.0.49 | Used by `train_revenue_model.py` only |

---

## Author

**Your Name**
- GitHub: [@azhrapttri](https://github.com/azhrapttri)
- LinkedIn: [linkedin.com/in/azzahraputerikamilah](www.linkedin.com/in/azzahraputerikamilah)

---

> Built as a mid-semester Data Visualization project using the PostgreSQL DVD Rental sample database.
