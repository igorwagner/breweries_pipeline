This Airflow DAG orchestrates a data transformation pipeline that processes raw brewery data from the
**bronze_layer** and stores the cleaned and structured output into the **silver_layer** of a data lake.

## 📌 Overview

- **Source**: Local or S3-stored JSONL files in the bronze_layer
- **Output**: Parquet files in the silver_layer of a data lake
- **Partitioning**: By country and  state_province
- **Technology**: Apache Airflow + BashOperator + Apache Spark

## ⚙️ Parameters

The DAG accepts parameters via "params", which are rendered into the Bash command:

| Parameter | Type | Default | Description                                             |
|-----------|------|---------|---------------------------------------------------------|
| `source`  | str  | "local" | Storage source: "local" for disk or "s3" for S3 bucket. |
| `target`  | str  | "local" | Storage target: "local" for disk or "s3" for S3 bucket. |

If no parameter is provided when triggering the DAG, defaults will be used.

## 🧱 DAG Structure

- **fetch_and_save_data**: Executes the "build_silver_layer.py" job via "BashOperator".

## 📁 Output Path

Files are saved in the following structure locally:
```bash
/opt/airflow/datalake/silver_layer/breweries/
└── country=xxxx/
    └── state_province=yyyy/
        └── part-xxx-yyy.snappy.parquet
```

Files are saved in the following structure at **S3**:
```bash
s3://AWS_S3_DATALAKE_BUCKET/silver_layer/breweries/
└── country=xxxx/
    └── state_province=yyyy/
        └── part-xxx-yyy.snappy.parquet
```
ℹ️ Note: If using s3, be sure the environment variable AWS_S3_DATALAKE_BUCKET is set correctly and AWS credentials
are available.
