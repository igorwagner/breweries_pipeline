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
├── dags/                          # DAG definitions for orchestrating data workflows
│   ├── bronze_layer_dag/          # DAGs responsible for raw data ingestion into the Bronze layer
│   ├── datalake_orquestrator_dag/ # DAGs responsible for raw data ingestion into the Bronze layer
│   ├── gold_layer_dag/            # DAGs for data aggregation, enrichment, and exporting to final destinations (Gold layer)
│   ├── silver_layer_dag/          # DAGs for data cleaning, normalization, and transformation (Silver layer)
│   └── utils/                     # Reusable utility functions used across different DAGs
├── jobs/                          # Python scripts that implement the logic for each layer
│   ├── bronze_layer/              # Scripts to fetch, parse, and write raw data to the Bronze layer
│   ├── gold_layer/                # Scripts to aggregate, enrich, and export data from the Silver layer to the Gold layer
│   ├── silver_layer/              # Scripts to clean, normalize, and transform Bronze data into the Silver layer
│   └── utils/                     # Reusable utility functions used across different jobs
├── local_container/               # Docker-based setup for running Apache Airflow locally
│   ├── .env                       # Environment variable definitions for the local Airflow container
│   ├── docker-compose.yaml        # Docker Compose configuration for services like Airflow webserver, scheduler, and database
│   ├── Dockerfile                 # Custom Docker image for the Airflow setup
│   └── requirements.txt           # Python packages required to run inside the local Airflow container
├── requirements/                  # Organized Python dependency files
│   ├── all.txt                    # Aggregates all requirements (dev + run + check)
│   ├── check.txt                  # Tools for linting, formatting, and static code analysis
│   ├── dev.txt                    # Development-only dependencies
│   └── run.txt                    # Runtime dependencies required for running the core application
├── tests/                         # Unit tests for job scripts and utilities
└── README.md                      # Project documentation and setup instructions
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
touch .env
docker compose up
```
This will start the Airflow webserver and scheduler. If any DAG fails, a Discord alert will be triggered automatically
(if `DISCORD_WEBHOOK_URL` is set in `.env`).

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

# ✅ Data Quality Checks

To ensure the reliability of the data being processed, the Silver Layer includes a set of data quality checks and cleaning steps:

- **Deduplication**: Duplicate records are dropped using the unique `id` field.
- **Schema Enforcement**: A strict schema is applied when reading the raw JSON from Bronze.
- **Normalization**: String fields like `city`, `country`, and `state_province` are trimmed, lowercased, and capitalized.
- **Field Derivations**:
  - `has_website`: Boolean indicating if `website_url` is present.
  - `has_phone`: Boolean indicating if `phone` is present.
  - `has_geolocation`: Boolean indicating presence of valid `latitude` and `longitude`.
- **Fallback Columns**: If `address_1` or `state_province` are missing, they are filled from `street` or `state` respectively.
- **Phone & Zip Cleaning**: Non-digit characters are stripped from phone numbers and postal codes to new cleaned columns.
- **Empty String Handling**: Empty strings are converted to `null` for consistency.
- **Critical Null Removal**: Rows missing essential fields (`id`, `name`, `country`, `state_province`) are dropped.

These steps ensure that the Silver layer contains clean, consistent, and analytics-ready data.

# 🧠 Trade-offs & Design Decisions

Throughout the development of this pipeline, several decisions were made to balance complexity, maintainability,
scalability, and robustness. Below are some of the most relevant trade-offs and design choices:

### ✅ API Usage

- **Choice**: The pipeline uses the `/v1/breweries/random` endpoint for ingestion.
- **Reason**: The Open Brewery DB API doesn't provide an updated timestamp field or pagination on random queries. To simulate incremental ingestion over time, each request is tagged with a randomly generated date.
- **Trade-off**: This makes the pipeline more realistic but less deterministic for data reproducibility.

### ✅ Partitioning Strategy

- **Choice**: Bronze data is partitioned by random `year/month/day`, while Silver is partitioned by `country/state_province`.
- **Reason**: Date partitioning is used to simulate real-world ingestion cadence. Location-based partitioning improves query performance and aligns with expected use cases.
- **Trade-off**: Querying by ingestion date is non-reliable in Bronze. In Gold, no partitioning was applied as the data is already aggregated.

### ✅ Schema Enforcement and Normalization

- **Choice**: The Silver layer enforces schema strictly and performs various normalization steps like trimming, lowercasing, and deduplication.
- **Trade-off**: This increases pipeline complexity slightly, but greatly enhances data consistency and usability for downstream consumers.

### ✅ Dockerized Airflow for Orchestration

- **Choice**: Airflow was chosen for its maturity and extensibility. It's deployed locally using Docker Compose.
- **Trade-off**: While not production-ready, this setup allows rapid prototyping and mirrors real-world DAG orchestration behavior.

### ✅ Error Handling

- **Choice**: Specific exception types (e.g., `ParseException`, `AnalysisException`) are caught and logged separately.
- **Trade-off**: This makes debugging easier and improves reliability, but adds verbosity to the code.

### ✅ Alerting via Discord

- **Choice**: Alerts on DAG failure are sent via a Discord webhook.
- **Trade-off**: Easy to implement locally, but would require adaptation (e.g., Slack, PagerDuty) for production-grade systems.

### ✅ AWS Integration

- **Choice**: Integration with S3, Athena, and Glue was done using manual setup for simplicity.
- **Trade-off**: While fast for testing, this could be automated via Terraform or boto3 scripts in a production context.

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

# 🔔 Alerting and Monitoring

The project includes basic alerting capabilities for monitoring Airflow DAG failures using a **Discord webhook**.

## 🚨 Failure Notifications

If any task in a DAG fails, an alert will be sent to a Discord channel with the following structure:

```bash
❌ **DAG `your_dag_id` failed**
Task: `your_task_id`
Execution time: `2025-08-04T12:00:00Z`
🔍 View logs
```

This allows for faster debugging and immediate awareness of issues in the pipeline execution.
## ⚙️ How It Works

- A function named `send_discord_alert` is registered as the `on_failure_callback` of each DAG.
- It constructs a message with DAG name, failed task ID, execution timestamp, and a link to the logs in the Airflow UI.
- The message is posted to a Discord channel via a webhook URL defined as an environment variable (`DISCORD_WEBHOOK_URL`).

✉️ Make sure your `.env` file inside `local_container/` includes:

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url_here
```
✅ This alerting system is designed for **local development monitoring** and can be easily adapted to Slack or email in
production.

# ✅ Testing Strategy

The project includes unit tests to ensure reliability and correctness of each pipeline layer. All tests are written
using `pytest` and make use of the `unittest.mock` library to simulate external dependencies like Spark sessions, file
systems, and logger calls.

## 🧪 What is Tested?

Tests are written for each layer of the medallion architecture and cover:
## 🥉 Bronze Layer

- Data Ingestion Validations
  - Verifies correct HTTP request handling and response parsing from the public API.
  - Ensures data is saved with proper partitioning by random date.
- Error Handling
  - Confirms that network or serialization errors are logged and do not crash the pipeline.

## 🥈 Silver Layer

- Schema Enforcement & Cleaning
  - Verifies that the raw JSON data is parsed using the expected schema.
  - Confirms that duplicates are correctly dropped.
- Error Handling
  - Tests raise and log a `ParseException` when JSON parsing fails.
  - Ensures Spark session is always stopped in error scenarios.

## 🥇 Gold Layer

- Aggregation Logic
  - Checks that grouping by `country`, `state_province`, `city`, and `brewery_type` is performed correctly.
  - Confirms the result is written in Parquet format to the correct path.
- Error Handling
  - Simulates errors while reading or writing Parquet files and verifies they are logged appropriately.
  - Ensures Spark session is stopped even when exceptions occur.

## 🧪 How to Run the Tests

To execute all tests, you can run the following command in the root folder:
```bash
pytest
```

You can also see a summary of test results with:
```bash
pytest -v
```

# 11. Continuous Integration & Continuous Deployment (CI/CD)

This project includes automated CI and CD workflows configured using GitHub Actions to ensure code quality and
demonstrate deployment automation.

## Continuous Integration (CI)

- The CI pipeline triggers automatically on every push or pull request to the `main` branch.
- It runs unit tests using `pytest` to verify the correctness and stability of the codebase.
- Dependencies are installed from the `requirements/all.txt` file along with PySpark and pytest.
- This ensures that all code changes are validated before merging or deployment.

## Continuous Deployment (CD)

- A simple CD workflow runs on every push to the `main` branch.
- Instead of deploying to a production environment, it sends a POST request to a configured Discord webhook.
- This notifies the team that new code has been pushed and validates the CD process.
- The webhook URL is securely stored as a GitHub secret (`DISCORD_WEBHOOK_URL`).
- This setup demonstrates automated deployment triggers and can be extended to real deployment steps in the future.

### How to Use

- Ensure your Discord webhook URL is added as a GitHub secret named `DISCORD_WEBHOOK_URL`.
- Push your code to the `main` branch to trigger both CI tests and the CD webhook notification.
- Check the Actions tab in GitHub to monitor workflow runs and results.
