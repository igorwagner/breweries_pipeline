This Airflow DAG orchestrates the full data ingestion pipeline of a medallion architecture, coordinating the execution
of three independent layers: **bronze**, **silver**, and **gold**.

It triggers the "ingestion_bronze_layer_dag", waits for its completion, then triggers "ingestion_silver_layer_dag",
and finally "ingestion_gold_layer_dag". Each layer transforms and enriches brewery data, moving it closer to analytical
readiness.

## 📌 Overview

- **Input**: Brewery data from the [OpenBreweryDB API](https://www.openbrewerydb.org/)
- **Layers**:
  - **Bronze**: Raw API data, randomly dated and stored
  - **Silver**: Cleaned and structured data
  - **Gold**: Aggregated insights for analytical queries
- **Technology**: Apache Airflow + TriggerDagRunOperator

## ⚙️ Parameters

This DAG accepts parameters via "params" and forwards them to the respective sub-DAGs using the "conf" argument.

| Parameter        | Type | Default | Description                                                            |
|------------------|------|---------|------------------------------------------------------------------------|
| `start_year`     | int  | 2023    | The beginning year for generating random dates.                        |
| `end_year`       | int  | 2025    | The ending year for generating random dates.                           |
| `num_requests`   | int  | 1       | Number of times the script will fetch 50 random breweries per request. |
| `source`         | str  | "local" | Storage target: "local" for disk or "s3" for S3 bucket.                |
| `target`         | str  | "local" | Storage target: "local" for disk or "s3" for S3 bucket.                |

ℹ️ If parameters are not explicitly passed, these default values will be used.

## 🧱 DAG Structure

- **trigger_bronze_dag**: Triggers "ingestion_bronze_layer_dag" with specified parameters.
- **trigger_silver_dag**: Waits for bronze to finish, then triggers "ingestion_silver_layer_dag".
- **trigger_gold_dag**: Waits for silver to finish, then triggers "ingestion_gold_layer_dag".

Each task uses "wait_for_completion=True" to ensure strict sequential execution.

## 📌 Use Case

This orchestration DAG is ideal when you want to:

- Automate the full daily ingestion pipeline with a single schedule.
- Ensure dependency between layers (bronze → silver → gold).
- Centralize parameter management across all layers.

## 🕒 Schedule

- **Cron**: "0 12 * * *" → Executes daily at 12:00 PM (UTC)
