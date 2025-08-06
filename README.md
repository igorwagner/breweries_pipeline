# 📦 Medallion Data Pipeline Overview

This project implements a **medallion architecture** (Bronze → Silver → Gold) for structured data processing
using Apache Airflow and Apache Spark.
It serves as a modular and reproducible data pipeline template for orchestrating ingestion, transformation,
and enrichment of data. The pipeline fetches data from a public API, processes it in multiple stages, and persists
it to either a local file system or a S3-based data lake.

## 🧭 Overview

- [Medallion Architecture](docs/medallion-architecture.md) — Overview of the layered medallion architecture.
- [Project Structure](docs/project-structure.md) — Description of project files and folders.
- [Local Setup](docs/local-setup.md) — How to run the project locally.
### Layer Details:
  - [Bronze Layer](docs/bronze-layer.md)  
  - [Silver Layer](docs/silver-layer.md)  
  - [Gold Layer](docs/gold-layer.md)

## 📊 Quality, Monitoring & Testing

- [Data Quality Checks](docs/data-quality.md)
- [Alerting and Monitoring](docs/alerting-monitoring.md)
- [Testing](docs/testing.md)

## ☁️ Cloud & Deployment

- [AWS Setup](docs/aws-setup.md)
- [CI/CD](docs/ci-cd.md)

## 🧠 Design Decisions

- [Trade-offs & Design Decisions](docs/design-decisions.md)
