"""
Minimal PySpark loader for CAMELEON-DP Parquet exports.

Usage:
  # After exporting Parquet via CLI:
  #   python -m cameleon_dp.cli summarize ledger.json --export-parquet out_parquet
  # Then run the loader:
  #   python -m tools.pyspark_loader --parquet out_parquet

This prints schema, a few rows, and simple aggregations by cert kind.
"""
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", required=True, help="Directory with records.parquet (from CLI export)")
    args = parser.parse_args()

    try:
        from pyspark.sql import SparkSession
        from pyspark.sql import functions as F  # type: ignore
    except Exception as e:
        raise SystemExit("PySpark not installed. Try: pip install pyspark") from e

    spark = SparkSession.builder.appName("cameleon-dp-loader").getOrCreate()
    df = spark.read.parquet(f"{args.parquet}/records.parquet")
    print("Schema:")
    df.printSchema()
    print("Sample rows:")
    df.show(10, truncate=False)

    print("Blocks by cert kind:")
    df.groupBy("cert").agg(F.count("*").alias("count"), F.sum("runtime_sec").alias("runtime_sec")).orderBy(F.desc("count")).show(truncate=False)

    print("Depth histogram:")
    df.groupBy("depth").agg(F.count("*").alias("count")).orderBy("depth").show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()


