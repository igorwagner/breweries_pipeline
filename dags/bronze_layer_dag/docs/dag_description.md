This Airflow DAG orchestrates a data ingestion pipeline that retrieves random brewery data from the
[OpenBreweryDB API](https://www.openbrewerydb.org/) and stores it in a local data lake, partitioned by
randomly generated dates.

## 📌 Overview

- **Source**: OpenBreweryDB API (/v1/breweries/random)
- **Output**: Local JSONL files in the bronze_layer of a data lake
- **Partitioning**: By randomly generated year/month/day
- **Technology**: Apache Airflow + BashOperator

## ⚙️ Parameters

The DAG accepts parameters via "params", which are rendered into the Bash command:

| Parameter        | Type | Default | Description                                                            |
|------------------|------|---------|------------------------------------------------------------------------|
| `start_year`     | int  | 2023    | The beginning year for generating random dates.                        |
| `end_year`       | int  | 2025    | The ending year for generating random dates.                           |
| `num-requests`   | int  | 1       | Number of times the script will fetch 50 random breweries per request. |
| `target`         | str  | "local" | Storage target: "local" for disk or "s3" for S3 bucket.                |

If no parameter is provided when triggering the DAG, defaults will be used.

## 🧱 DAG Structure

- **fetch_and_save_data**: Executes the "build_bronze_layer.py" job via "BashOperator".

## 📁 Output Path

Files are saved in the following structure locally:
```bash
/opt/airflow/datalake/bronze_layer/
└── year=YYYY/
    └── month=MM/
        └── day=DD/
            └── YYYY_MM_DD_data.jsonl
```

Files are saved in the following structure at **S3**:
```bash
s3://AWS_S3_DATALAKE_BUCKET/bronze_layer/
└── year=YYYY/
    └── month=MM/
        └── day=DD/
            └── YYYY_MM_DD_data.jsonl
```
ℹ️ Note: If using s3, be sure the environment variable AWS_S3_DATALAKE_BUCKET is set correctly and AWS credentials
are available.

Each ".jsonl" file contains brewery records assigned a random date between the defined "start_year" and "end_year".