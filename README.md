# 🛒 Superstore Sales ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1?logo=mysql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-cc0000)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

---

## 📌 Project Overview

This project demonstrates an end-to-end ETL (Extract, Transform, Load) pipeline developed to process and analyze retail sales data. The workflow involves extracting raw data from a CSV source, performing complex data cleaning and transformation using Python (Pandas), and loading the structured data into a MySQL relational database for advanced business intelligence querying.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.x** | Core scripting language |
| **Pandas & NumPy** | Data manipulation and numerical operations |
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

### 2. Transformation (Data Cleaning & Feature Engineering)

- **Column Standardization:** Replaced dots with underscores in column names (e.g., `Order.ID` → `Order_ID`) to ensure compatibility with SQL naming conventions.
- **Data Type Correction:** Converted `Order_Date` and `Ship_Date` strings into proper `datetime` objects.
- **Feature Engineering:** Calculated a new metric, `Profit_Margin`, to provide deeper insights into the profitability of sales.
- **Aggregation:** Performed grouping by `Category` and `Region` to validate total sales and profit figures before the loading phase.

```python
# Feature engineering
df['Profit_Margin'] = (df['Profit'] / df['Sales']) * 100

# Date conversion
df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
df['Ship_Date']  = pd.to_datetime(df['Ship_Date'],  errors='coerce')

# Grouped aggregation
df.groupby(["Category", "Region"])[["Sales", "Profit"]].sum()
```

**Profit Margin sample (first 5 rows):**

| Order ID | Country | Sales ($) | Profit ($) | Profit Margin (%) |
|---|---|---|---|---|
| CA-2011-130813 | United States | 19.00 | 9.33 | 49.11% |
| CA-2011-148614 | United States | 19.00 | 9.29 | 48.91% |
| CA-2011-118962 | United States | 21.00 | 9.84 | 46.87% |
| CA-2011-118962 | United States | 111.00 | 53.26 | 47.98% |
| CA-2011-146969 | United States | 6.00 | 3.11 | 51.84% |

**Sales & Profit by Category and Region (selected):**

| Category | Region | Sales ($) | Profit ($) |
|---|---|---|---|
| Technology | Central | 1,038,515 | 135,538 |
| Office Supplies | Central | 923,471 | 121,315 |
| Technology | North | 495,802 | 99,272 |
| Office Supplies | South | 515,208 | 67,496 |
| Furniture | East | 208,291 | 3,046 |
| **Furniture** | **Southeast Asia** | **313,391** | **-7,270** ⚠️ |

> ⚠️ **Key Finding:** Furniture in Southeast Asia generates **$313K in revenue but a net loss of -$7,270** — a negative-margin market. This pattern, where high gross sales mask structural losses, is a critical signal for pricing policy review, regional strategy reassessment, and financial risk management.

---

### 3. Loading

- Established a secure connection to the MySQL server using an **SQLAlchemy Engine**.
- Utilized the `.to_sql()` method with the `replace` parameter to programmatically create the table schema and insert the entire dataset into the `superstore_son` database.

```python
engine = create_engine('mysql+pymysql://user:****@localhost/superstore_son')

df.to_sql(
    'superstore_orders',
    con=engine,
    if_exists='replace',  # Idempotent: safe to re-run
    index=False
)
# ✅ 51,290 rows successfully loaded into MySQL
```

---

## 📂 Repository Structure

```
├── src/
│   └── data_pipeline.py      # Main ETL script
├── sql/
│   └── business_queries.sql  # SQL scripts for data analysis
├── data/
│   └── superstore_data.csv   # Raw dataset
├── README.md                 # Project documentation
└── requirements.txt          # Required Python libraries
```

---

## 💡 Business Relevance

This project reflects an analytical approach informed by both **economics training** and **legal/compliance coursework** — moving beyond technical data handling to identify commercially significant patterns:

- **Margin erosion risk:** At least 25% of transactions yield zero profit; Southeast Asia Furniture operates at a net loss despite high revenue — directly relevant to financial control and audit processes.
- **Regional performance variance:** Profitability diverges sharply across markets, supporting data-driven resource allocation decisions.
- **Data integrity enforcement:** Type correction and naming standardization are prerequisites for reliable regulatory reporting and compliance workflows.

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your database connection in data_pipeline.py

# 3. Run the pipeline
python src/data_pipeline.py
```

---

*Dataset: Adapted from the Tableau Superstore dataset, widely used in business analytics education.*
