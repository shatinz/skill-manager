---
id: databases-storage.olap-embedded.duckdb-polars-analytics
name: duckdb-polars-analytics
title: DuckDB & Polars High-Speed Embedded OLAP Analytics
category: databases-storage
subcategory: olap-embedded
version: 1.3.0
tags:
- duckdb
- polars
- python
- arrow
- parquet
- olap
- analytics
trust_rating: 0.97
estimated_tokens: 1550
description: Perform high-speed in-process analytical SQL queries, zero-copy Arrow
  data transfers, and lazy DataFrame aggregations over gigabytes of Parquet files
  using DuckDB and Polars.
trigger_patterns:
- duckdb polars fast analytics
- duckdb scan parquet files sql
- polars lazy dataframe query
- duckdb arrow zero copy python
---

# DuckDB & Polars High-Speed Embedded OLAP Analytics

## Objective
Process multi-gigabyte datasets directly in-process with sub-second response times using DuckDB columnar SQL execution, Polars lazy evaluation, and zero-copy Apache Arrow buffers.

## Production Python Analytics Pipeline
```python
import duckdb
import polars as pl

def analyze_telemetry_dataset(parquet_glob: str) -> pl.DataFrame:
    # 1. Initialize DuckDB in-memory engine with multithreading
    con = duckdb.connect(database=":memory:")
    con.execute("PRAGMA threads=8;")
    con.execute("PRAGMA memory_limit='8GB';")

    # 2. Query Parquet files directly without loading raw data into memory
    query = (
        "SELECT "
        "  service_name, "
        "  date_trunc('hour', timestamp) AS hour_bucket, "
        "  count(*) AS total_requests, "
        "  avg(duration_ms) AS avg_duration, "
        "  quantile_cont(duration_ms, 0.99) AS p99_duration, "
        "  sum(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) AS error_count "
        f"FROM read_parquet('{parquet_glob}') "
        "WHERE timestamp >= now() - INTERVAL '7 days' "
        "GROUP BY service_name, hour_bucket "
        "HAVING count(*) > 100 "
        "ORDER BY hour_bucket DESC, p99_duration DESC;"
    )
    
    # 3. Export to Apache Arrow and convert to Polars LazyFrame with zero-copy
    arrow_table = con.execute(query).arrow()
    df = pl.from_arrow(arrow_table)

    # 4. Perform further transformations in Polars
    result = (
        df.lazy()
        .with_columns(
            (pl.col("error_count") / pl.col("total_requests") * 100).alias("error_rate_pct")
        )
        .filter(pl.col("error_rate_pct") > 1.0)
        .collect()
    )

    return result
```

## Anti-Patterns
- ❌ Loading massive CSV/Parquet files entirely into memory with Pandas before filtering.
- ❌ Running OLTP transaction workloads on columnar OLAP engines like DuckDB.
