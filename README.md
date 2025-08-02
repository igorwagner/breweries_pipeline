# 📦 Project Overview

This project implements a **medallion architecture** (Bronze → Silver → Gold) for structured data processing
using Apache Airflow.
It serves as a modular and reproducible data pipeline template for orchestrating ingestion, transformation,
and enrichment of data. The pipeline fetches data from public APIs, processes it in multiple stages, and persists
it to either a local file system or an S3-based data lake.

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

# 🟫 Bronze Layer: Raw Data Ingestion

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

| Parameter       | Type | Default | Description                                                           |
|-----------------|------|---------|-----------------------------------------------------------------------|
| `start_year`    | int  | 2023    | The beginning year for generating random dates.                       |
| `end_year`      | int  | 2025    | The ending year for generating random dates.                          |
| `num-requests`  | int  | 1       | Number of times the script will fetch 50 random breweries per request |
| `target`        | str  | "local" | Storage target: "local" for disk or "s3" for S3 bucket.               |

ℹ️ Note: If using s3, be sure the environment variable AWS_S3_DATALAKE_BUCKET is set correctly and AWS credentials
are available.
