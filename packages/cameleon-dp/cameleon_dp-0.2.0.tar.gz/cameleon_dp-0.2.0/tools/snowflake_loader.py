"""
Snowflake loader example for CAMELEON-DP Parquet exports.

Prereqs:
- `pip install snowflake-connector-python snowflake-sqlalchemy`
- A Snowflake stage (internal) and permissions to create tables.

Workflow:
1) Export Parquet locally:
   python -m cameleon_dp.cli summarize ledger.json --export-parquet out_parquet
2) Upload Parquet files to a stage (e.g., @my_stage/cameleon/records.parquet)
3) Run this script to create/replace a table and copy in the data.

Environment variables:
  SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT, SNOWFLAKE_WAREHOUSE,
  SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA
"""
import os
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, help="Snowflake stage path prefix, e.g. @my_stage/cameleon")
    parser.add_argument("--table", default="CAMELEON_RECORDS", help="Destination table name")
    args = parser.parse_args()

    try:
        import snowflake.connector  # type: ignore
    except Exception as e:
        raise SystemExit("Install Snowflake connector: pip install snowflake-connector-python") from e

    conn = snowflake.connector.connect(
        user=os.environ.get("SNOWFLAKE_USER"),
        password=os.environ.get("SNOWFLAKE_PASSWORD"),
        account=os.environ.get("SNOWFLAKE_ACCOUNT"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE"),
        database=os.environ.get("SNOWFLAKE_DATABASE"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA"),
    )
    cs = conn.cursor()
    try:
        cs.execute(f"CREATE OR REPLACE TABLE {args.table} (\n"
                   "block_id INT, j_lo INT, j_hi INT, i_lo INT, i_hi INT,\n"
                   "cert STRING, template STRING, eps FLOAT, runtime_sec FLOAT, depth INT, orientation STRING\n"
                   ")")
        cs.execute(f"COPY INTO {args.table} FROM '{args.stage}/records.parquet'\n"
                   "FILE_FORMAT=(TYPE=PARQUET)\n"
                   "MATCH_BY_COLUMN_NAME=CASE_INSENSITIVE")
        print(f"Loaded Parquet from {args.stage} into {args.table}")
    finally:
        cs.close()
        conn.close()


if __name__ == "__main__":
    main()


