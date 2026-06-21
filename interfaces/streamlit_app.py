import streamlit as st
from app.db import get_conn
from app.config import DB_PATH
from app.run_log import get_recent_runs
import os
import pandas as pd
from datetime import datetime

from main import main as run_pipeline
from app.config import OUTPUT_DIR

st.set_page_config(page_title="Auto Report", layout="wide")

st.title("📊 Auto Report Generator")

# -------------------------
# Upload CSV
# -------------------------
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Preview")
    st.dataframe(df.head())

    columns = df.columns.tolist()

    # -------------------------
    # Column mapping
    # -------------------------
    st.subheader("Column Mapping")

    date_col = st.selectbox("Select DATE column", columns)
    value_col = st.selectbox("Select VALUE column", columns)
    category_col = st.selectbox("Select CATEGORY column", columns)

    # -------------------------
    # Date filtering
    # -------------------------
    st.subheader("Date Range")

    try:
        df[date_col] = pd.to_datetime(df[date_col])
        min_date = df[date_col].min()
        max_date = df[date_col].max()

        start_date = st.date_input("Start date", min_value=min_date, max_value=max_date, value=min_date)
        end_date = st.date_input("End date", min_value=min_date, max_value=max_date, value=max_date)

    except Exception:
        st.error("Invalid date column format")
        st.stop()

    # -------------------------
    # Generate button
    # -------------------------
    if st.button("🚀 Generate Report"):
        try:
            with st.spinner("Processing..."):

                # zapis CSV tymczasowo
                os.makedirs("data", exist_ok=True)
                temp_path = os.path.join("data", "input.csv")
                df.to_csv(temp_path, index=False)

                # 🔴 ustawienia dynamiczne (proste MVP)
                import transform
                transform.DATE_COL = date_col
                transform.VALUE_COL = value_col
                transform.CATEGORY_COL = category_col

                # uruchom pipeline
                run_pipeline()

            st.success("Report generated!")

            pdf_path = os.path.join(OUTPUT_DIR, "report.pdf")

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Report",
                    data=f,
                    file_name="report.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.subheader("Recent report runs")

try:
    conn = get_conn(DB_PATH)
    runs = get_recent_runs(conn, limit=10)
    conn.close()

    if not runs:
        st.info("No report runs found yet.")
    else:
        table_rows = []

        for run in runs:
            kpis = run.get("kpis", {})
            table_rows.append(
                {
                    "Run ID": run["id"],
                    "Created at": run["created_at"],
                    "Rows": kpis.get("rows_cnt"),
                    "Total value": kpis.get("total_value"),
                    "Average value": kpis.get("avg_value"),
                    "PDF": run.get("output_pdf"),
                    "Error": run.get("error_text"),
                }
            )

        st.dataframe(table_rows)

except Exception as e:
    st.warning(f"Could not load run history: {e}")