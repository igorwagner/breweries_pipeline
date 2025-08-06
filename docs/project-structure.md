# 📁 Project Structure

```bash
.
├── dags/                          # DAG definitions for orchestrating data workflows
│   ├── bronze_layer_dag/          # DAGs responsible for raw data ingestion into the Bronze layer
│   ├── datalake_orquestrator_dag/ # DAGs responsible for orchestrating the full pipeline
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
