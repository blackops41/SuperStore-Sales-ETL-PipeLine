import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import logging

# =============================================
# LOGGING CONFIGURATION
# =============================================
# Logları hem terminale hem de bir .log dosyasına yazdıracak yapılandırma
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etl_pipeline.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_pipeline():
    try:
        # =============================================
        # STEP 1: EXTRACTION
        # =============================================
        logging.info("--- Step 1: Extraction ---")
        
        # Dosya adını çevresel değişkenden al, bulamazsan varsayılan olarak csv'yi kullan.
        data_file = os.getenv("DATA_FILE", "superstore_son_versiyon.csv")
        logging.info(f"Loading dataset from {data_file}...")
        df = pd.read_csv(data_file, encoding='utf-8')
        logging.info(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns.")

        # =============================================
        # STEP 2: VALIDATION & CLEANING (Data Quality Gate)
        # =============================================
        logging.info("--- Step 2: Validation & Cleaning ---")

        # 1. Duplicate Handling
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            logging.warning(f"{duplicate_count} duplicate rows detected. Dropping duplicates...")
            df = df.drop_duplicates()
            logging.info(f"Duplicates removed. Remaining rows: {len(df)}")
        else:
            logging.info("No duplicate rows found.")

        # 2. Null Value Handling (Targeted Dropping)
        critical_columns = ['Sales', 'Profit']
        missing_in_critical = df[critical_columns].isnull().sum()
        
        if missing_in_critical.sum() > 0:
            logging.warning(f"Missing values detected in critical columns:\n{missing_in_critical[missing_in_critical > 0]}")
            logging.info("Enforcing data integrity: Dropping rows with null values in 'Sales' or 'Profit'...")
            df = df.dropna(subset=critical_columns)
            logging.info(f"Critical null values dropped. Remaining rows: {len(df)}")
        else:
            logging.info("No missing values found in critical columns ('Sales', 'Profit').")

        # 3. Schema Validation
        required_columns = ['Sales', 'Profit', 'Quantity', 'Discount']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Required columns missing from dataset: {missing_cols}")
        logging.info("Schema validation passed: All critical business columns present.")

        # =============================================
        # STEP 3: TRANSFORMATION & AGGREGATION
        # =============================================
        logging.info("--- Step 3: Transformation ---")

        df.columns = [col.replace('.', '_') for col in df.columns]
        df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
        df['Ship_Date'] = pd.to_datetime(df['Ship_Date'], errors='coerce')

        df['Profit_Margin'] = np.where(
            df['Sales'] == 0,
            0,
            (df['Profit'] / df['Sales']) * 100
        )
        logging.info("Data cleaning and safe feature engineering completed.")

        logging.info("--- Generating Aggregated Summary ---")
        agg_df = df.groupby(["Category", "Region"])[["Sales", "Profit"]].sum().reset_index()
        agg_df['Profit_Margin'] = np.where(
            agg_df['Sales'] == 0, 
            0, 
            (agg_df['Profit'] / agg_df['Sales']) * 100
        )
        logging.info(f"Main table rows: {len(df)} | Summary table rows: {len(agg_df)}")

       # =============================================
        # STEP 4: LOADING & SECURITY (MySQL)
        # =============================================
        logging.info("--- Step 4: Loading & Credential Management ---")

        # Tüm ayarları kasadan (.env) çek. (Bulamazsa varsayılan değerleri kullan)
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "superstore_son")

        if not db_password:
            error_msg = "CRITICAL: 'DB_PASSWORD' environment variable is missing. Pipeline cannot connect to MySQL."
            logging.error(error_msg)
            raise EnvironmentError(error_msg)

        # Dinamik Bağlantı Cümlesi (ConnectionString)
        engine_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(engine_url)

        logging.info(f"Connecting to MySQL database '{db_name}' at {db_host}:{db_port}...")

        # KOPYALARKEN EKSİK KALAN KISIM BURASIYDI:
        logging.info("Transferring raw data to MySQL (superstore_orders table)...")
        df.to_sql('superstore_orders', con=engine, if_exists='replace', index=False)

        logging.info("Transferring aggregated data to MySQL (sales_summary table)...")
        agg_df.to_sql('sales_summary', con=engine, if_exists='replace', index=False)
        
        logging.info("Success! Both raw and summary tables loaded into MySQL.")

    except Exception as e:
        logging.error(f"An error occurred during pipeline execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
