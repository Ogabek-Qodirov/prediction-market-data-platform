
import os
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    avg,
    max,
    min,
    round,
    when,
    desc
)


# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

# Configure Java for PySpark on Windows
os.environ["JAVA_HOME"] = r"D:\Apps\Java"
os.environ["PATH"] = (
    os.environ["JAVA_HOME"] + r"\bin;" + os.environ.get("PATH", "")
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
ANALYTICS_DIR = PROJECT_ROOT / "data" / "analytics"


# ==========================================
# 2. CREATE SPARK SESSION
# ==========================================

def create_spark_session():

    spark = (
        SparkSession.builder
        .appName("PredictionMarketDataPlatform")
        .master("local[2]")
        .config("spark.driver.memory", "1g")
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem")
        .config("spark.hadoop.fs.permissions.enabled", "false")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    return spark


# ==========================================
# 3. LOAD PARQUET DATA
# ==========================================

def load_parquet_data(spark):

    parquet_files = list(PROCESSED_DATA_DIR.glob("*.parquet"))

    if not parquet_files:
        raise FileNotFoundError(
            f"No Parquet files found in {PROCESSED_DATA_DIR}"
        )

    file_paths = [str(file) for file in parquet_files]

    print("\n========== LOADING DATA ==========")
    print("Parquet files found:", len(file_paths))

    df = (
        spark.read
        .option("mergeSchema", "true")
        .parquet(*file_paths)
    )

    return df


# ==========================================
# 4. DATA INSPECTION
# ==========================================

def inspect_data(df):

    print("\n========== DATA SCHEMA ==========")
    df.printSchema()

    print("\n========== FIRST 10 MARKETS ==========")
    df.show(10, truncate=False)

    print("\n========== DATA STATISTICS ==========")
    print("Total records:", df.count())
    print("Total columns:", len(df.columns))


# ==========================================
# 5. DATA QUALITY CHECKS
# ==========================================

def check_data_quality(df):

    print("\n========== DATA QUALITY ==========")

    # Count duplicate market IDs
    duplicate_count = (
        df.groupBy("market_id")
        .count()
        .filter(col("count") > 1)
        .count()
    )

    print("Duplicate market IDs:", duplicate_count)

    # Count missing values in important columns
    print("\nMissing values:")

    for column_name in df.columns:

        missing_count = df.filter(
            col(column_name).isNull()
        ).count()

        print(f"{column_name}: {missing_count}")

    # Check probability range
    invalid_probability = df.filter(
        (col("probability") < 0) |
        (col("probability") > 1)
    ).count()

    print("\nInvalid probability records:", invalid_probability)


# ==========================================
# 6. SPARK SQL ANALYTICS
# ==========================================

def run_sql_analytics(spark, df):

    # Register DataFrame as a temporary SQL table
    df.createOrReplaceTempView("markets")
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    print("\n========== OVERALL MARKET ANALYTICS ==========")

    overall_stats = spark.sql("""
        SELECT
            COUNT(*) AS total_markets,
            ROUND(AVG(probability), 4) AS avg_probability,
            ROUND(AVG(volume), 2) AS avg_volume,
            SUM(
                CASE
                    WHEN is_resolved = TRUE THEN 1
                    ELSE 0
                END
            ) AS resolved_markets
        FROM markets
    """)

    overall_stats.show(truncate=False)

    # Market distribution by resolution status
    print("\n========== RESOLUTION DISTRIBUTION ==========")

    resolution_stats = spark.sql("""
        SELECT
            is_resolved,
            COUNT(*) AS market_count
        FROM markets
        GROUP BY is_resolved
        ORDER BY market_count DESC
    """)

    resolution_stats.show()

    # Most traded markets
    print("\n========== TOP 10 MARKETS BY VOLUME ==========")

    top_markets = spark.sql("""
        SELECT
            market_id,
            question,
            probability,
            ROUND(volume, 2) AS volume
        FROM markets
        ORDER BY volume DESC
        LIMIT 10
    """)

    top_markets.show(truncate=False)


# ==========================================
# 7. DATAFRAME ANALYTICS
# ==========================================

def run_dataframe_analytics(df):

    print("\n========== PROBABILITY STATISTICS ==========")

    df.select(
        round(avg("probability"), 4).alias("average_probability"),
        round(max("probability"), 4).alias("maximum_probability"),
        round(min("probability"), 4).alias("minimum_probability")
    ).show()

    print("\n========== HIGH CONFIDENCE MARKETS ==========")

    high_confidence = (
        df.filter(
            (col("probability") >= 0.90) |
            (col("probability") <= 0.10)
        )
        .select(
            "market_id",
            "question",
            "probability",
            "volume"
        )
        .orderBy(desc("volume"))
    )

    high_confidence.show(10, truncate=False)


# ==========================================
# 8. MAIN PIPELINE
# ==========================================

def process_markets():

    spark = create_spark_session()

    try:

        # Load data
        df = load_parquet_data(spark)

        # Inspect data
        inspect_data(df)

        # Check data quality
        check_data_quality(df)

        # Run SQL analytics
        run_sql_analytics(spark, df)

        history_df = run_historical_analysis(spark, df)

        export_dashboard_data(
            spark,
            df,
            history_df
        )

        # Run DataFrame analytics
        run_dataframe_analytics(df)

        print("\n========== PIPELINE COMPLETED ==========")

    finally:

        spark.stop()


# ==========================================
# 9. EXECUTION
# ==========================================

def run_historical_analysis(spark, df):

    df.createOrReplaceTempView("markets")

    print("\n========== HISTORICAL PROBABILITY CHANGES ==========")

    history = spark.sql("""
        WITH market_history AS (
            SELECT
                market_id,
                question,
                snapshot_time,
                probability,

                LAG(probability) OVER (
                    PARTITION BY market_id
                    ORDER BY snapshot_time
                ) AS previous_probability

            FROM markets
            WHERE snapshot_time IS NOT NULL
        )

        SELECT
            market_id,
            question,
            snapshot_time,
            previous_probability,
            probability AS current_probability,

            ROUND(probability - previous_probability, 4)
                AS probability_change,

            ROUND(
                (probability - previous_probability) * 100,
                2
            ) AS change_percentage_points

        FROM market_history

        WHERE previous_probability IS NOT NULL
    """)

    print("\n========== TOP 20 MARKET MOVEMENTS ==========")

    history.orderBy(
        desc("absolute_change")
    ).show(20, truncate=False) if "absolute_change" in history.columns else (
        history.orderBy(
            col("probability_change").desc()
        ).show(20, truncate=False)
    )

    history = history.withColumn(
        "absolute_change",
        col("probability_change").cast("double")
    )

    history = history.withColumn(
        "absolute_change",
        __import__("pyspark.sql.functions", fromlist=["abs"]).abs(
            col("absolute_change")
        )
    )

    history = history.withColumn(
        "movement_type",
        when(col("probability_change") >= 0.05, "Significant Increase")
        .when(col("probability_change") <= -0.05, "Significant Decrease")
        .otherwise("Small Change")
    )

    print("\n========== MOVEMENT DISTRIBUTION ==========")
    history.groupBy("movement_type").count().show()

    output_path = ANALYTICS_DIR / "market_probability_changes.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    history.toPandas().to_parquet(
        output_path,
        index=False,
        engine="pyarrow"
    )

    print(f"Historical data saved: {output_path}")

    print("Historical analytics saved to:", output_path)

    return history

def export_dashboard_data(spark, df, history_df):
    import pandas as pd

    dashboard_dir = ANALYTICS_DIR / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    # 1. Market Summary
    summary = df.agg(
        count("market_id").alias("total_markets"),
        avg("probability").alias("average_probability"),
        avg("volume").alias("average_volume")
    )

    # 2. Top Markets
    top_markets = df.orderBy(
        desc("volume")
    ).limit(20)

    # 3. Probability Distribution
    probability_distribution = df.withColumn(
        "probability_range",
        when(col("probability") < 0.2, "0-20%")
        .when(col("probability") < 0.4, "20-40%")
        .when(col("probability") < 0.6, "40-60%")
        .when(col("probability") < 0.8, "60-80%")
        .otherwise("80-100%")
    ).groupBy(
        "probability_range"
    ).agg(
        count("market_id").alias("market_count")
    )

    # 4. Historical Probability Changes
    datasets = {
        "market_summary": summary,
        "top_markets": top_markets,
        "all_markets": df,
        "probability_distribution": probability_distribution,
        "historical_probability_changes": history_df
    }

    for dataset_name, dataset in datasets.items():
        output_path = dashboard_dir / f"{dataset_name}.csv"

        dataset.toPandas().to_csv(
            output_path,
            index=False
        )

        print(f"Dashboard dataset saved: {output_path}")

    print("\nAll dashboard datasets exported successfully!")
if __name__ == "__main__":
    process_markets()
