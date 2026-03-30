<img width="589" height="372" alt="image" src="https://github.com/user-attachments/assets/812f518b-4a82-407a-9e8f-beeaa3dd81d5" /># SuperStore-Sales-ETL-PipeLine
An end-to-end ETL pipeline that extracts retail sales data from CSV, transforms it using Python (Pandas), and loads it into a MySQL database for business analysis.

# Superstore Sales ETL Pipeline

## 📌 Project Overview
This project demonstrates an end-to-end **ETL (Extract, Transform, Load)** pipeline developed to process and analyze retail sales data. The workflow involves extracting raw data from a CSV source, performing complex data cleaning and transformation using **Python (Pandas)**, and loading the structured data into a **MySQL** relational database for advanced business intelligence querying.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Data Manipulation:** Pandas, NumPy
* **Database:** MySQL
* **Database Connectivity:** SQLAlchemy, PyMySQL
* **Environment:** VS Code / Jupyter Notebook

## The ETL Process

### 1. Extraction
* The raw dataset (Superstore Sales) consisting of **51,290 rows** was imported into a Python environment using `pandas`.
* Initial data exploration was conducted using `.info()`, `.describe()`, and `.head()` to understand data distribution and identify inconsistencies.

### 2. Transformation (Data Cleaning & Feature Engineering)
* **Column Standardization:** Replaced dots with underscores in column names (e.g., `Order.ID` → `Order_ID`) to ensure compatibility with SQL naming conventions.
* **Data Type Correction:** Converted `Order_Date` and `Ship_Date` strings into proper `datetime` objects.
* **Feature Engineering:** Calculated a new metric, `Profit_Margin`, to provide deeper insights into the profitability of sales.
* **Aggregation:** Performed grouping by `Category` and `Region` to validate total sales and profit figures before the loading phase.

### 3. Loading
* Established a secure connection to the MySQL server using an **SQLAlchemy Engine**.
* Utilized the `.to_sql()` method with the `replace` parameter to programmatically create the table schema and insert the entire dataset into the `superstore_son` database.

## 📂 Repository Structure
```text
├── src/
│   └── data_pipeline.py      # Main ETL script
├── sql/
│   └── business_queries.sql  # SQL scripts for data analysis
├── data/
│   └── superstore_data.csv   # Raw dataset
├── README.md                 # Project documentation
└── requirements.txt          # Required Python libraries
