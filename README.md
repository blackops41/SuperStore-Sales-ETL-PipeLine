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

| | Sales | Profit | Quantity | Discount |
|---|---|---|---|---|
| count | 51,290 | 51,290 | 51,290 | 51,290 |
| mean | 229.86 | 28.66 | 3.79 | 0.156 |
| std | 623.25 | 234.26 | 2.23 | 0.206 |
| min | 0.44 | **-6,599.98** | 1 | 0.00 |
| median | 54.49 | 8.67 | 3 | 0.20 |
| max | 22,638.48 | 8,399.98 | 14 | 0.80 |

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

**Sample grouped output:**

| Category | Region | Sales ($) | Profit ($) |
|---|---|---|---|
| Furniture | Central | 163,797 | 3,849 |
| Office Supplies | West | 281,137 | 57,821 |
| Technology | West | 251,991 | 56,045 |
| Technology | East | 264,973 | 52,318 |

> ⚠️ **Finding:** Furniture in the Central region generates the lowest profit margin relative to sales — consistent with excessive discounting. Transactions with discounts above 40% systematically produce negative profit, a pattern with direct implications for pricing policy and margin compliance.

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

- **Margin erosion risk** from discount policy → relevant to financial control and audit
- **Regional performance variance** → supports strategic resource allocation decisions
- **Data integrity enforcement** (type correction, naming standardization) → prerequisite for regulatory reporting and compliance workflows

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

*Dataset: Adapted from the Tableau Superstore dataset, widely used in business analytics.*
