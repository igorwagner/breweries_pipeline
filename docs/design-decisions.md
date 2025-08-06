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
