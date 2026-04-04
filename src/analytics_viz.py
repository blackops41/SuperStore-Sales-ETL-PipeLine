import os

import pandas as pd

import matplotlib.pyplot as plt

import matplotlib.ticker as mticker

import seaborn as sns

from sqlalchemy import create_engine

from dotenv import load_dotenv



# ------------------------------------------------------------

# Setup

# ------------------------------------------------------------

load_dotenv()



OUTPUT_DIR = "images"

os.makedirs(OUTPUT_DIR, exist_ok=True)   # klasör yoksa oluştur



def get_engine():

    url = (

        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"

        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 3306)}/{os.getenv('DB_NAME')}"

    )

    return create_engine(url)





def save(filename):

    path = os.path.join(OUTPUT_DIR, filename)

    plt.tight_layout()

    plt.savefig(path, dpi=150)

    plt.close()

    print(f"  ✅ Saved → {path}")





# ------------------------------------------------------------

# 1. EXECUTIVE SUMMARY — KPI Cards

# ------------------------------------------------------------

def plot_executive_summary(engine):

    print("Generating Executive Summary...")

    query = """

        SELECT

            ROUND(SUM(Sales), 2)                                     AS total_sales,

            ROUND(SUM(Profit), 2)                                    AS total_profit,

            ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2)     AS margin_pct

        FROM superstore_orders;

    """

    df = pd.read_sql(query, engine).iloc[0]



    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    kpis = [

        ("Total Sales",   f"${df['total_sales']:,.0f}",   "#2ecc71"),

        ("Total Profit",  f"${df['total_profit']:,.0f}",  "#3498db"),

        ("Margin %",      f"{df['margin_pct']}%",         "#e74c3c"),

    ]

    for ax, (label, value, color) in zip(axes, kpis):

        ax.set_facecolor(color)

        ax.text(0.5, 0.6, value, ha='center', va='center',

                fontsize=26, fontweight='bold', color='white', transform=ax.transAxes)

        ax.text(0.5, 0.25, label, ha='center', va='center',

                fontsize=13, color='white', transform=ax.transAxes)

        ax.axis('off')



    fig.suptitle('Executive Summary — Superstore', fontsize=15, fontweight='bold')

    save("01_executive_summary.png")





# ------------------------------------------------------------

# 2. MONTHLY SALES TREND — Line Chart

# ------------------------------------------------------------

def plot_monthly_trend(engine):

    print("Generating Monthly Sales Trend...")

    query = """

        SELECT DATE_FORMAT(Order_Date, '%Y-%m') AS month,

               ROUND(SUM(Sales), 2)             AS total_sales,

               ROUND(SUM(Profit), 2)            AS total_profit

        FROM superstore_orders

        GROUP BY DATE_FORMAT(Order_Date, '%Y-%m')

        ORDER BY month;

    """

    df = pd.read_sql(query, engine)



    plt.figure(figsize=(14, 6))

    sns.lineplot(data=df, x='month', y='total_sales',  marker='o',

                 color='#2ecc71', linewidth=2.5, label='Sales')

    sns.lineplot(data=df, x='month', y='total_profit', marker='s',

                 color='#3498db', linewidth=2,   label='Profit')

    plt.title('Monthly Sales & Profit Trend', fontsize=15, fontweight='bold')

    plt.xticks(rotation=45, ha='right')

    plt.xlabel("Month")

    plt.ylabel("USD")

    plt.legend()

    save("02_monthly_trend.png")





# ------------------------------------------------------------

# 3. YEAR-OVER-YEAR GROWTH — Bar + Annotation

# ------------------------------------------------------------

def plot_yoy_growth(engine):

    print("Generating YoY Growth...")

    query = """

        WITH yearly AS (

            SELECT YEAR(Order_Date) AS year, SUM(Sales) AS total_sales

            FROM superstore_orders

            GROUP BY YEAR(Order_Date)

        )

        SELECT year,

               ROUND(total_sales, 2) AS total_sales,

               ROUND(

                   (total_sales - LAG(total_sales) OVER (ORDER BY year))

                   / NULLIF(LAG(total_sales) OVER (ORDER BY year), 0) * 100

               , 2) AS yoy_growth_pct

        FROM yearly ORDER BY year;

    """

    df = pd.read_sql(query, engine)



    fig, ax1 = plt.subplots(figsize=(10, 6))

    bars = ax1.bar(df['year'].astype(str), df['total_sales'],

                   color='#3498db', alpha=0.8, label='Total Sales')

    ax1.set_ylabel("Total Sales (USD)")

    ax1.set_xlabel("Year")



    ax2 = ax1.twinx()

    ax2.plot(df['year'].astype(str), df['yoy_growth_pct'],

             marker='o', color='#e74c3c', linewidth=2, label='YoY Growth %')

    ax2.set_ylabel("YoY Growth (%)")

    ax2.axhline(0, color='gray', linestyle='--', linewidth=0.8)



    fig.suptitle('Year-over-Year Sales Growth', fontsize=15, fontweight='bold')

    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.88))

    save("03_yoy_growth.png")





# ------------------------------------------------------------

# 4. PARETO ANALYSIS — Bar + Cumulative Line

# ------------------------------------------------------------

def plot_pareto(engine):

    print("Generating Pareto Analysis...")

    query = """

        SELECT Customer_Name, ROUND(SUM(Sales), 2) AS total_sales

        FROM superstore_orders

        GROUP BY Customer_Name

        ORDER BY total_sales DESC

        LIMIT 20;

    """

    df = pd.read_sql(query, engine)

    df['cumulative_pct'] = df['total_sales'].cumsum() / df['total_sales'].sum() * 100



    fig, ax1 = plt.subplots(figsize=(14, 6))

    sns.barplot(data=df, x='Customer_Name', y='total_sales',

                palette='viridis', ax=ax1)

    ax1.set_ylabel("Total Sales (USD)")

    ax1.set_xlabel("")

    ax1.tick_params(axis='x', rotation=45)



    ax2 = ax1.twinx()

    ax2.plot(df['Customer_Name'], df['cumulative_pct'],

             color='#e74c3c', marker='o', linewidth=2, label='Cumulative %')

    ax2.axhline(80, color='gray', linestyle='--', linewidth=1, label='80% Line')

    ax2.set_ylabel("Cumulative %")

    ax2.set_ylim(0, 110)

    ax2.legend(loc='center right')



    fig.suptitle('Top 20 Customers — Pareto Analysis', fontsize=15, fontweight='bold')

    save("04_pareto_analysis.png")





# ------------------------------------------------------------

# 5. SEGMENT ANALYSIS — Heatmap (Category × Region)

# ------------------------------------------------------------

def plot_segment_heatmap(engine):

    print("Generating Segment Heatmap...")

    query = """

        SELECT Category, Region,

               ROUND(SUM(Profit), 2)                                    AS total_profit,

               ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2)     AS margin_pct

        FROM superstore_orders

        GROUP BY Category, Region;

    """

    df = pd.read_sql(query, engine)

    pivot = df.pivot(index='Category', columns='Region', values='total_profit')



    plt.figure(figsize=(10, 5))

    sns.heatmap(pivot, annot=True, fmt=".0f", cmap='RdYlGn',

                cbar_kws={'label': 'Profit (USD)'})   # cbar_klabel → cbar_kws (fixed)

    plt.title('Profitability Heatmap: Category × Region', fontsize=15, fontweight='bold')

    save("05_segment_heatmap.png")





# ------------------------------------------------------------

# 6. REGION PERFORMANCE — Horizontal Bar

# ------------------------------------------------------------

def plot_region_performance(engine):

    print("Generating Region Performance...")

    query = """

        SELECT Region,

               COUNT(DISTINCT Order_ID)                                  AS order_count,

               ROUND(SUM(Sales), 2)                                      AS total_sales,

               ROUND(SUM(Profit) / COUNT(DISTINCT Order_ID), 2)         AS avg_profit_per_order

        FROM superstore_orders

        GROUP BY Region

        ORDER BY total_sales DESC;

    """

    df = pd.read_sql(query, engine)



    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sns.barplot(data=df, x='total_sales',          y='Region',

                palette='Blues_d', ax=axes[0])

    axes[0].set_title('Total Sales by Region')

    axes[0].set_xlabel('USD')



    sns.barplot(data=df, x='avg_profit_per_order', y='Region',

                palette='Greens_d', ax=axes[1])

    axes[1].set_title('Avg Profit per Order by Region')

    axes[1].set_xlabel('USD')



    fig.suptitle('Region Performance Overview', fontsize=15, fontweight='bold')

    save("06_region_performance.png")





# ------------------------------------------------------------

# 7. SUB-CATEGORY MARGIN — Diverging Bar (negative = red)

# ------------------------------------------------------------

def plot_subcategory_margin(engine):

    print("Generating Sub-Category Margin...")

    query = """

        SELECT Sub_Category,

               ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS margin_pct

        FROM superstore_orders

        GROUP BY Sub_Category

        ORDER BY margin_pct;

    """

    df = pd.read_sql(query, engine)

    colors = ['#e74c3c' if x < 0 else '#2ecc71' for x in df['margin_pct']]



    plt.figure(figsize=(10, 7))

    plt.barh(df['Sub_Category'], df['margin_pct'], color=colors)

    plt.axvline(0, color='black', linewidth=0.8)

    plt.title('Profit Margin by Sub-Category', fontsize=15, fontweight='bold')

    plt.xlabel('Margin (%)')

    save("07_subcategory_margin.png")





# ------------------------------------------------------------

# 8. DISCOUNT IMPACT — Scatter (Discount vs Avg Profit)

# ------------------------------------------------------------

def plot_discount_impact(engine):

    print("Generating Discount Impact...")

    query = """

        SELECT Discount,

               COUNT(*)            AS order_count,

               ROUND(AVG(Profit), 2) AS avg_profit

        FROM superstore_orders

        GROUP BY Discount

        ORDER BY Discount;
