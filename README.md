# 📦 Project Overview

This project implements a **medallion architecture** (Bronze → Silver → Gold) for structured data processing
using Apache Airflow and Apache Spark.
It serves as a modular and reproducible data pipeline template for orchestrating ingestion, transformation,
and enrichment of data. The pipeline fetches data from a public API, processes it in multiple stages, and persists
it to either a local file system or a S3-based data lake.

# 🥉🥈🏅 Medallion Architecture Overview

The Medallion Architecture is a design pattern for organizing data lakes or data platforms into multiple layers that improve data quality and manageability progressively:

- 🥉 **Bronze Layer**: The raw ingestion layer, where data is captured in its original format without transformations. This data is often immutable and serves as the single source of truth.
- 🥈 **Silver Layer**: The cleaned and enriched layer, where data is transformed, normalized, and standardized. This layer makes data more usable for analysis and downstream processing.
- 🥇 **Gold Layer**: The aggregated and curated layer, designed for business-level consumption. Data here is typically aggregated, joined, and optimized for reporting, dashboards, or machine learning.

This layered approach helps ensure data quality, improves pipeline modularity, and supports scalable, maintainable data processing workflows.

# 📁 Project Structure

```bash
.
├── dags/                    # DAG definitions for orchestrating data workflows
│   ├── bronze_layer_dag/    # DAGs responsible for raw data ingestion into the Bronze layer
│   ├── silver_layer_dag/    # DAGs for data cleaning, normalization, and transformation (Silver layer)
│   └── gold_layer_dag/      # DAGs for data aggregation, enrichment, and exporting to final destinations (Gold layer)
├── jobs/                    # Python scripts that implement the logic for each layer
│   ├── bronze_layer/        # Scripts to fetch, parse, and write raw data to the Bronze layer
│   ├── silver_layer/        # Scripts to clean, normalize, and transform Bronze data into the Silver layer
│   ├── gold_layer/          # Scripts to aggregate, enrich, and export data from the Silver layer to the Gold layer
│   └── utils/               # Reusable utility functions used across different layers and DAGs
├── local_container/         # Docker-based setup for running Apache Airflow locally
│   ├── .env                 # Environment variable definitions for the local Airflow container
│   ├── docker-compose.yaml  # Docker Compose configuration for services like Airflow webserver, scheduler, and database
│   ├── Dockerfile           # Custom Docker image for the Airflow setup
│   └── requirements.txt     # Python packages required to run inside the local Airflow container
├── requirements/            # Organized Python dependency files
│   ├── all.txt              # Aggregates all requirements (dev + run + check)
│   ├── check.txt            # Tools for linting, formatting, and static code analysis
│   ├── dev.txt              # Development-only dependencies
│   └── run.txt              # Runtime dependencies required for running the core application
├── tests/                   # Unit tests for job scripts and utilities
└── README.md                # Project documentation and setup instructions
```

# 🧪 Local Setup Instructions

Follow these steps to set up and run the project locally.

---

## ✅ 1. Install Python with `pyenv`

Make sure you have [pyenv](https://github.com/pyenv/pyenv) installed. Then run:
```bash
pyenv install 3.12.7
```

## ✅ 2. Create a Virtual Environment

Use the Python version installed by pyenv to create a virtual environment:
```bash
~/.pyenv/versions/3.12.7/bin/python3.12 -m venv venv
```

Then activate the environment:
```bash
source venv/bin/activate
```

## ✅ 3. Install Python Dependencies

With the virtual environment activated, install the required Python packages:
```bash
pip install -r requirements/all.txt
```

## ✅ 4. Run Airflow with Docker

📝 You must have Docker installed. If you don't, follow the instructions at: https://docs.docker.com/get-docker/
Navigate to the `local_container` folder and run:
```bash
docker compose up
```
This will start the Airflow webserver and scheduler.

## ✅ 5. Access Airflow UI

Once the services are up, open your browser and go to: `http://localhost:8080`

Login with the following credentials:
- **Username**: airflow
- **Password**: airflow

Then trigger the DAG named `dag_teste` from the UI.

## ✅ 6. Code Quality: Pre-commit Hooks

To ensure code quality, install pre-commit and enable it:
```bash
pre-commit install
```

From now on, each commit will run the linters and formatters automatically.

# 🥉 Bronze Layer: Raw Data Ingestion

The **Bronze layer** is responsible for ingesting raw data from external sources — in this case, the 
[OpenBreweryDB API](https://www.openbrewerydb.org/) — and storing it in a partitioned structure based on randomly
generated dates.

## 🔧 How It Works

1. **API Integration**
The ingestion job fetches brewery data from the `/v1/breweries/random` endpoint of OpenBreweryDB, making multiple
requests as defined by the `--num-requests` parameter.

2. **Random Date Assignment**
Each brewery record is assigned a random date between the years defined by `--start-year` and `--end-year`. This date
is used to partition the data.

3. **Data Partitioning**
Data is stored using the following partitioning structure:
```bash
bronze_layer/
└── year=YYYY/
    └── month=MM/
        └── day=DD/
            └── YYYY_MM_DD_data.jsonl
```

4. **Output Destination (`--target`)**
The `--target` parameter determines where the data will be stored:

- `"local"`: Stored under `/opt/airflow/datalake/bronze_layer/`
- `"s3"`: Uploaded to an S3 bucket (configured via environment variable `AWS_S3_DATALAKE_BUCKET`) under the prefix
`bronze_layer/`

5. **File Format**
The data is stored in `.jsonl` (JSON Lines) format, where each line is a separate brewery record in raw JSON format.

## Input Parameters

| Parameter      | Type | Default | Description                                                           |
|----------------|------|---------|-----------------------------------------------------------------------|
| `start-year`   | int  | 2023    | The beginning year for generating random dates.                       |
| `end-year`     | int  | 2025    | The ending year for generating random dates.                          |
| `num-requests` | int  | 1       | Number of times the script will fetch 50 random breweries per request |
| `target`       | str  | "local" | Storage target: "local" for disk or "s3" for S3 bucket.               |

# 🥈 Silver Layer: Data Cleaning and Normalization

The **Silver layer** is responsible for transforming and cleaning the raw brewery data ingested in the Bronze layer.
This stage applies schema enforcement, deduplication, and partitions the data for optimized querying and analysis.

## 🔧 How It Works

1. **Read Raw Data**
The pipeline reads raw JSON data from the Bronze layer (either local disk or S3), applying a predefined schema to ensure
data consistency.

2. **Data Deduplication**
Duplicate brewery records are removed by considering the unique `id` field.

3. **Partitioning and Writing**
The cleaned data is written in Parquet format, partitioned by `country` and `state_province` fields, into the Silver
layer, stored either locally or on S3 as a parquet file.

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

## Input Parameters

| Parameter | Type | Default | Description                                             |
|-----------|------|---------|---------------------------------------------------------|
| `source`  | str  | "local" | Storage source: "local" for disk or "s3" for S3 bucket. |
| `target`  | str  | "local" | Storage target: "local" for disk or "s3" for S3 bucket. |

# 🏅 Gold Layer: Aggregation and Business-level Views

The **Gold layer** builds upon the cleaned Silver layer data by aggregating and summarizing brewery information into
business-friendly views.

## 🔧 How It Works

1. **Read Silver Layer Data**
The pipeline reads Parquet data from the Silver layer, which contains cleaned and partitioned brewery records.

2. **Aggregation**
Data is grouped by `country`, `state_province`, `city`, and `brewery_type`, and the total number of breweries in each
group is counted.

3. **Writing Aggregated Data**
The aggregated results are saved in Parquet format in the Gold layer, ready for reporting, dashboards, or further
business analytics.

Files are saved in the following structure locally:
```bash
/opt/airflow/datalake/gold_layer/breweries_distribution/
└── part-xxx-yyy.snappy.parquet
```

Files are saved in the following structure at **S3**:
```bash
s3://AWS_S3_DATALAKE_BUCKET/gold_layer/breweries_distribution/
└── part-xxx-yyy.snappy.parquet
```

## Input Parameters

| Parameter | Type | Default | Description                                             |
|-----------|------|---------|---------------------------------------------------------|
| `source`  | str  | "local" | Storage source: "local" for disk or "s3" for S3 bucket. |
| `target`  | str  | "local" | Storage target: "local" for disk or "s3" for S3 bucket. |


ℹ️ Note: If using s3, be sure the environment variable AWS_S3_DATALAKE_BUCKET is set correctly and AWS credentials
are available.

# ☁️ AWS Cloud Setup for Testing

To test the project’s cloud functionalities on AWS, the following setup steps were performed:

1. **IAM User Creation**
An IAM user was created with the necessary permissions to access S3, Glue, and Athena services securely.

2. **AWS Credentials Configuration**
The AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`) were added to the `.env`
file located in the `local_container` folder to enable Airflow and the jobs to authenticate and interact with
AWS services.

Example `.env` content:
```bash
AWS_ACCESS_KEY_ID=your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_DEFAULT_REGION=us-east-1
```

3. **S3 Buckets Setup**
Two S3 buckets were provisioned:

- One bucket to serve as the data lake storage, where Parquet files for the Silver and Gold layers are ingested.
- Another bucket dedicated to Athena query results storage.

4. **Athena Databases Creation**
    Using Athena's query editor, the Silver and Gold databases were created with:

```sql
CREATE DATABASE silver;
CREATE DATABASE gold;
```

5. **Glue Schema Registration**
Since Athena relies on Glue Data Catalog for table metadata, the schemas for the Silver and Gold tables were manually
added in the AWS Glue console. This step enables Athena to recognize the tables and display them in the UI for querying.

This setup allows seamless integration and testing of the data pipelines end-to-end using AWS managed services.
