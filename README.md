# Prediction Market Data Engineering Platform

An end-to-end Data Engineering project that collects prediction market data from the Manifold Markets API, stores historical snapshots, processes data using PySpark, and delivers analytical insights through interactive dashboards.

## Project Overview

Prediction markets allow users to trade on the outcomes of future events. This project builds a local data platform to collect, transform, analyze, and visualize prediction market data.

The platform captures market information over time, making it possible to explore market activity and analyze changes in predicted probabilities.

## Architecture

```text
Manifold Markets API
        |
        v
   Data Extraction
        |
        v
    Raw Data Lake
    (JSON Snapshots)
        |
        v
 Data Transformation
   (Pandas)
        |
        v
 Processed Data
    (Parquet)
        |
        v
  Data Processing
    (PySpark)
        |
        v
 Analytical Datasets
       (CSV)
        |
        +------------------+
        |                  |
        v                  v
 Streamlit Dashboard   Looker Studio
```

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Manifold Markets API | Data source |
| Pandas | Data transformation |
| PyArrow | Parquet storage |
| PySpark | Distributed data processing and analytics |
| PostgreSQL | Not currently used in this project |
| Streamlit | Interactive dashboard |
| Looker Studio | Business intelligence and visualization |
| Git & GitHub | Version control |

## Project Features

- Extracts prediction market data through the Manifold Markets API.
- Supports API pagination and data validation.
- Stores timestamped JSON snapshots in a local data lake.
- Transforms raw data using Pandas.
- Stores processed datasets in Parquet format.
- Processes market data using PySpark.
- Performs historical probability change analysis.
- Generates analytical CSV datasets.
- Provides an interactive Streamlit dashboard.
- Supports Looker Studio reporting through CSV uploads.

## Project Structure

```text
prediction-market-data-platform/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── analytics/
│       └── dashboard/
│
├── src/
│   ├── extraction/
│   ├── storage/
│   ├── transformation/
│   └── processing/
│
├── app.py
├── main.py
├── api_test.py
├── check_dashboard.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Ogabek-Qodirov/prediction-market-data-platform.git

cd prediction-market-data-platform
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Java

PySpark requires Java. This project was developed using Java 17.

Make sure Java 17 is installed and `JAVA_HOME` is configured correctly.

### 5. Run the data pipeline

```bash
python main.py
```

### 6. Launch the Streamlit dashboard

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal to access the dashboard.

## Dashboards

### Streamlit

The Streamlit dashboard provides:

- Total market statistics.
- Average market probability.
- Average trading volume.
- Probability distribution.
- Top markets by trading volume.
- Market search and filtering.
- Historical probability analysis when historical records are available.

### Looker Studio

Looker Studio is used to create business intelligence reports from exported CSV datasets.

The integration currently uses manual CSV uploads.

## Data Storage

The project uses a local data lake architecture:

- **Raw layer:** Original API responses stored as timestamped JSON snapshots.
- **Processed layer:** Cleaned and transformed Parquet datasets.
- **Analytics layer:** CSV datasets prepared for dashboards and reporting.

## Historical Analysis

Historical snapshots allow the project to compare market probabilities over time.

The analysis uses SQL window functions, including `LAG()`, to calculate:

- Previous probability.
- Current probability.
- Probability changes.
- Percentage-point differences.
- Significant increases and decreases.

## Future Improvements

- Implement automated pipeline orchestration with Apache Airflow.
- Add automated data quality tests.
- Improve historical trend analysis.
- Introduce more advanced analytical metrics.
- Improve dashboard reporting.
- Add automated pipeline monitoring and logging.

## Author

**Og'abek Qodirov**

Information Systems and Technologies Student | Aspiring Data Engineer

- GitHub: [Ogabek-Qodirov](https://github.com/Ogabek-Qodirov)

---

*This project is developed as part of a practical Data Engineering learning and portfolio journey.*
