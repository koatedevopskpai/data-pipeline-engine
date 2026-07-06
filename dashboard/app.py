# Streamlit dashboard for pipeline observability. Why Streamlit over a JS framework?
#
# 1. Speed of development: Streamlit turns a Python script into a UI in minutes.
#    For a portfolio project, this means I can demonstrate the pipeline's output
#    without building a React app.
# 2. Single language: the entire stack (pipeline + API + dashboard) is Python.
#    A data engineering role doesn't require React — it requires data visualisation
#    literacy. Streamlit + Plotly proves that.
# 3. Plotly integration: plotly.express gives us interactive charts with one line
#    of code. The scatter plot in this dashboard demonstrates I can create
#    meaningful data visualisations from pipeline output.
#
# The dashboard reads directly from SQLite rather than calling the FastAPI.
# This is a deliberate simplicity tradeoff: having the dashboard call the API
# would demonstrate service-oriented architecture, but for a portfolio demo,
# direct DB access means fewer moving parts that can fail during a demo.
# The dashboard is a development/monitoring tool, not a customer-facing product.
import sqlite3
from pathlib import Path

import plotly.express as px
import streamlit as st

from pipeline.config import Settings

st.set_page_config(page_title="Data Pipeline Dashboard", layout="wide")
st.title("Data Pipeline Engine — Observability Dashboard")


def get_db_connection():
    settings = Settings()
    db_path = settings.db_url.replace("sqlite:///", "")
    if not Path(db_path).exists():
        return None
    return sqlite3.connect(db_path)


col1, col2, col3 = st.columns(3)

conn = get_db_connection()
if conn is None:
    st.info("No pipeline database found. Run a pipeline first.")
    st.stop()

cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

with col1:
    st.metric("Tables", len(tables))

total_rows = 0
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    total_rows += cursor.fetchone()[0]

with col2:
    st.metric("Total Records", total_rows)

with col3:
    st.metric("Data Sources", len(tables))

st.divider()
st.subheader("Table Browser")

if tables:
    selected = st.selectbox("Select table", tables)
    df = conn.execute(f"SELECT * FROM {selected} LIMIT 100").fetchall()
    columns = [desc[0] for desc in conn.execute(f"SELECT * FROM {selected} LIMIT 0").description]
    st.dataframe(
        [dict(zip(columns, row)) for row in df],
        use_container_width=True,
    )

    cursor.execute(f"SELECT COUNT(*) FROM {selected}")
    row_count = cursor.fetchone()[0]
    st.caption(f"Showing {min(100, row_count)} of {row_count} rows")

    # Auto-detect numeric columns for plotting.
    # This is deliberately simple: we check the sqlite3 type affinity of each column.
    # A more sophisticated version would use Pandas profiling or a statistical
    # library, but for a portfolio dashboard this is sufficient — it handles
    # the common case (INTEGER/REAL columns) without additional dependencies.
    numeric_cols = []
    cursor.execute(f"SELECT * FROM {selected} LIMIT 1")
    for desc in cursor.description:
        if desc[1] in (int, float):
            numeric_cols.append(desc[0])

    if len(numeric_cols) >= 2:
        st.subheader("Data Profile")
        x_axis = st.selectbox("X-axis", numeric_cols, key="x")
        y_axis = st.selectbox("Y-axis", numeric_cols, key="y")
        plot_df = conn.execute(f"SELECT {x_axis}, {y_axis} FROM {selected} LIMIT 500").fetchall()
        if plot_df:
            fig = px.scatter(
                [dict(zip([x_axis, y_axis], row)) for row in plot_df],
                x=x_axis, y=y_axis,
                title=f"{x_axis} vs {y_axis}",
            )
            st.plotly_chart(fig, use_container_width=True)

conn.close()
