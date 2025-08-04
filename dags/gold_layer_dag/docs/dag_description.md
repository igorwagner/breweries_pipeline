This Airflow DAG orchestrates a data transformation pipeline that aggregates brewery data from the
**silver_layer** and stores the summarized output into the **gold_layer** of a data lake.

## 📌 Overview

- **Source**: Parquet files from the silver_layer (local or S3)
- **Output**: Aggregated Parquet files in the gold_layer of a data lake (local or S3)
- **Aggregation**: Count of breweries grouped by country, state_province, city, and brewery_type
- **Technology**: Apache Airflow + BashOperator + Apache Spark

## ⚙️ Parameters

The DAG accepts parameters via "params", which are rendered into the Bash command:

| Parameter | Type | Default | Description                                             |
|-----------|------|---------|---------------------------------------------------------|
| `source`  | str  | "local" | Storage target: "local" for disk or "s3" for S3 bucket. |
| `target`  | str  | "local" | Storage target: "local" for disk or "s3" for S3 bucket. |

If no parameter is provided when triggering the DAG, defaults will be used.

## 🧱 DAG Structure

- **fetch_and_save_data**: Executes the "build_gold_layer.py" job via "BashOperator".

## 📁 Output Path

Files are saved in the following structure locally:
```bash
/opt/airflow/datalake/gold_layer/breweries_distribution/
└── part-xxx-yyy.snappy.parquet
```

Files are saved in the following structure at S3:
```bash
s3://AWS_S3_DATALAKE_BUCKET/gold_layer/breweries_distribution/
└── part-xxx-yyy.snappy.parquet
```
ℹ️ Note: If using s3, be sure the environment variable AWS_S3_DATALAKE_BUCKET is set correctly and AWS credentials
are available.
