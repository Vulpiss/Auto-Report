# Auto-Report: SQL-backed Automated Data Reporting Pipeline

## 1. Problem

Manual reporting is slow, inconsistent, and difficult to reproduce.

This project solves that problem by turning a structured CSV dataset into a repeatable PDF report with KPI metrics, charts, rule-based decision support, AI-style insights, data quality notes, and run logging.

## 2. What this project is

Auto-Report is an end-to-end reporting pipeline:

```text
CSV -> SQLite raw table -> cleaned facts table -> KPI engine -> decision layer -> charts -> PDF report -> run log
```

It is not a pure machine learning model.

It is a deterministic data pipeline with an optional LLM insight layer and fallback mode.

The system is designed to be reproducible, explainable, and resilient to common failure cases such as missing historical baseline data or unavailable LLM access.

## 3. Core features

- CSV input
- SQLite-backed data layer
- Data validation
- Data quality diagnostics
- KPI calculation
- Period-over-period comparison
- Rule-based decision layer
- Charts generated with matplotlib
- PDF report generated with ReportLab
- LLM-ready insight layer with fallback mode
- Run logging to SQLite
- Optional Streamlit UI

## 4. Data contract

The minimum required input columns are:

| Column | Type | Meaning |
|---|---|---|
| `date` | datetime | Event or transaction date |
| `value` | numeric | Metric value, e.g. revenue |
| `category` | string | Business category, e.g. product group |

The current MVP expects these canonical column names:

```text
date,value,category
```

If the source dataset uses different column names, they should be mapped in the transformation layer.

## 5. Architecture

```text
Data Loader
    ↓
SQLite Raw Table
    ↓
Transform / Clean Facts
    ↓
Validation + Data Quality
    ↓
KPI Engine
    ↓
Period Comparison
    ↓
Decision Layer
    ↓
Charts
    ↓
LLM / Fallback Insights
    ↓
PDF Report
    ↓
Run Log
```

## 6. How to run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the reporting pipeline:

```bash
python main.py
```

Run the optional Streamlit UI:

```bash
streamlit run app.py
```

## 7. Example outputs

The generated PDF report includes:

- KPI Summary
- Decision Layer
- Period Comparison
- Trend Chart
- Top Categories Chart
- AI / Fallback Insights
- Data Quality Notes

Example report scenarios:

- `example_no_baseline_report.pdf` — previous-period data is unavailable, so comparison is marked as unavailable.
- `example_with_baseline_report.pdf` — previous-period data exists, so the system calculates real period-over-period changes.

## 8. Failure handling

The system is designed to avoid silent failures.

If required columns are missing, validation fails with a clear error message.

If the LLM layer is unavailable, fallback insights are generated instead of crashing the report.

If previous-period data is unavailable, period comparison is marked as unavailable instead of showing misleading growth.

Each successful report run is logged to SQLite.

## 9. Current limitations

- No real forecasting model yet.
- LLM integration is optional and not required for fallback mode.
- PDF layout is functional and portfolio-ready for MVP, but can still be improved visually.
- Data cleaning is intentionally simple for the MVP.
- The current decision layer is rule-based, not machine-learned.
- The system currently focuses on structured CSV datasets with a date, numeric value, and category column.

## 10. Next steps

Planned improvements:

- Add OpenAI client for real LLM commentary
- Add anomaly detection
- Add forecast module
- Add richer Streamlit controls
- Add export history and report comparison
- Add support for custom column mapping in the UI
- Add more advanced data quality checks
- Add unit tests for KPI, validation, and period comparison logic

## 11. Technical positioning

This project demonstrates:

- data pipeline design
- SQL-backed processing
- deterministic KPI calculation
- reporting automation
- basic decision support
- LLM fallback architecture
- data quality awareness
- reproducible report generation

This is a Data + AI portfolio project, not a black-box ML model.
