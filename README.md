# 🛒 Superstore Sales ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.x-013243?logo=numpy&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1?logo=mysql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-cc0000)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

---

## 📌 Project Overview

This project demonstrates an end-to-end ETL (Extract, Transform, Load) pipeline developed to process and analyze retail sales data. The workflow involves extracting raw data from a CSV source, performing complex data cleaning and transformation using Python (Pandas), enforcing strict data quality and security gates, and loading the structured data into a MySQL relational database for advanced business intelligence querying.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.x** | Core scripting language |
| **Pandas & NumPy** | Data manipulation, validation, and vectorized numerical operations |
| **MySQL** | Relational database (storage layer) |
| **SQLAlchemy & PyMySQL** | Database engine abstraction and connectivity |
| **VS Code / Jupyter Notebook** | Development environment |

---

## 🔄 The ETL Process

### 1. Extraction

- The raw dataset (Superstore Sales) consisting of **51,290 rows** was imported into a Python environment using `pandas`.
- Initial data exploration was conducted using `.info()`, `.describe()`, and `.head()` to understand data distribution and identify inconsistencies.

```python
df = pd.read_csv('superstore_son_versiyon.csv', encoding='utf-8')
df.info()
df[['Sales', 'Profit', 'Quantity', 'Discount']].describe()
```

**Statistical summary (selected columns):**

| | Sales ($) | Profit ($) | Quantity | Discount |
|---|---|---|---|---|
| count | 51,290 | 51,290 | 51,290 | 51,290 |
| mean | 246.50 | 28.61 | 3.48 | 0.14 |
| std | 487.57 | 174.34 | 2.28 | 0.21 |
| min | 0.00 | **-6,599.98** | 1 | 0.00 |
| 25% | 31.00 | 0.00 | 2 | 0.00 |
| median | 85.00 | 9.24 | 3 | 0.00 |
| 75% | 251.00 | 36.81 | 5 | 0.20 |
| max | 22,638.00 | 8,399.98 | 14 | 0.85 |

> **Note:** The 25th percentile of Profit is $0.00, meaning at least 25% of all transactions generate no profit. Combined with a minimum profit of -$6,599.98, this signals a structurally significant discounting problem across the dataset.

---

### 2. Validation (Data Quality Gate)

Before applying business logic, a strict data quality gateway was implemented to ensure reporting accuracy:

- **Duplicate Handling:** Automatically detects and drops duplicate transactions to prevent inflated revenue figures.
- **Null Value Checks:** Scans for missing values across all columns.
- **Schema Validation:** Ensures critical business columns (`Sales`, `Profit`, `Quantity`, `Discount`) exist before processing, raising a safe error if the source data structure changes.

---

### 3. Transformation (Data Cleaning & Feature Engineering)

- **Column Standardization:** Replaced dots with underscores in column names (e.g., `Order.ID` → `Order_ID`) to ensure compatibility with SQL naming conventions.
- **Data Type Correction:** Converted `Order_Date` and `Ship_Date` strings into proper `datetime` objects.
- **Safe Mathematical Operations:** Handled potential DivisionByZero exceptions during margin calculations using vectorized conditional logic (`np.where`), preventing infinite (`inf`) values from corrupting the SQL database.
- **Aggregation:** Performed grouping by `Category` and `Region` to validate total sales and profit figures before the loading phase.

```python
# Safe Feature Engineering (Division by Zero protection)
df['Profit_Margin'] = np.where(
    df['Sales'] == 0,
    0,
    (df['Profit'] / df['Sales']) * 100
)

# Date conversion
df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
df['Ship_Date']  = pd.to_datetime(df['Ship_Date'],  errors='coerce')
```

**Sales & Profit by Category and Region (selected):**

| Category | Region | Sales ($) | Profit ($) |
|---|---|---|---|
| Technology | Central | 1,038,515 | 135,538 |
| Office Supplies | Central | 923,471 | 121,315 |
| Technology | North | 495,802 | 99,272 |
| Office Supplies | South | 515,208 | 67,496 |
| Furniture | East | 208,291 | 3,046 |
| **Furniture** | **Southeast Asia** | **313,391** | **-7,270** ⚠️ |

> ⚠️ **Key Finding:** Furniture in Southeast Asia generates $313K in revenue but a net loss of -$7,270 — a negative-margin market. This pattern, where high gross sales mask structural losses, is a critical signal for pricing policy review, regional strategy reassessment, and financial risk management.

---

### 4. Loading & Security

- Established a secure connection to the MySQL server using an **SQLAlchemy Engine**.
- **Credential Security:** Database passwords are strictly managed via environment variables (`os.getenv`) to prevent hardcoded credential leakage on GitHub.
- Utilized the `.to_sql()` method with the `replace` parameter for idempotency (safe to re-run without duplicating records).

```python
import os

# Secure credential management
db_password = os.getenv("DB_PASSWORD")
engine_url = f"mysql+pymysql://root:{db_password}@localhost/superstore_son"
engine = create_engine(engine_url)

df.to_sql(
    'superstore_orders',
    con=engine,
    if_exists='replace',  # Idempotent: safe to re-run
    index=False
)
# ✅ Rows successfully loaded into MySQL
```

---

## 📂 Repository Structure

```
├── src/
│   └── data_pipeline.py      # Main ETL script with Data Validation
├── sql/
│   └── business_queries.sql  # SQL scripts for data analysis
├── data/
│   └── superstore_data.csv   # Raw dataset (Not uploaded due to size)
├── README.md                 # Project documentation
└── requirements.txt          # Required Python libraries
```

---

## 💡 Business Relevance

This project reflects an analytical approach informed by both **economics training** and **legal/compliance coursework** — moving beyond technical data handling to identify commercially significant patterns:

- **Enterprise-Grade Security & Reliability:** Implemented data validation gates and environment variable protection, demonstrating readiness for production environments and compliance with basic cybersecurity standards.
- **Margin erosion risk:** At least 25% of transactions yield zero profit; Southeast Asia Furniture operates at a net loss despite high revenue — directly relevant to financial control and audit processes.
- **Regional performance variance:** Profitability diverges sharply across markets, supporting data-driven resource allocation decisions.
- **Data integrity enforcement:** Type correction, null dropping, and naming standardization are prerequisites for reliable regulatory reporting.

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your database password as an environment variable
# (Windows)
set DB_PASSWORD=your_password
# (Mac/Linux)
export DB_PASSWORD="your_password"

# 3. Run the pipeline
python src/data_pipeline.py
```

---

*Dataset: Adapted from the Tableau Superstore dataset, widely used in business analytics education.*

---

## 🛠️ Future Roadmap (v2.0)
To scale this pipeline for production environments, the following enhancements are planned:
- **Incremental Loading:** Implementing `MAX(Order_Date)` logic to fetch only new records.
- **Advanced Constraints:** Adding `assert` checks and `schema-enforcement` via Pydantic.
- **Database Indexing:** Optimizing query performance on `Customer_Name` and `Order_Date` columns.

## 📊 Business Analytics Dashboard

Automated insights generated from the MySQL Data Warehouse using Python (Seaborn/Matplotlib).

### 1. Executive Summary
Overview of Total Sales, Profit, and Profit Margin.
![Executive Summary](images/01_executive_summary.png)

### 2. Sales & Profit Trends
Monthly trajectory of business performance.
![Monthly Trend](images/02_monthly_trend.png)

### 3. Year-over-Year Growth
Visualizing annual performance shifts.
![YoY Growth](images/03_yoy_growth.png)

### 4. Pareto Analysis (Top Customers)
Identifying the 20% of customers driving the majority of sales.
![Pareto Analysis](images/04_pareto_analysis.png)

### 5. Profitability Heatmap
Deep dive into Category vs. Region performance.
![Segment Heatmap](images/05_segment_heatmap.png)

> **Note:** For the full list of 9 analytical reports, please check the `/images` directory.
