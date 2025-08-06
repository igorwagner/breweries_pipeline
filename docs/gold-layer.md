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
