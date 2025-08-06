# 🥈 Silver Layer: Data Cleaning and Normalization

The **Silver layer** is responsible for transforming and cleaning the raw brewery data ingested in the Bronze layer.
This stage applies schema enforcement, deduplication, and partitions the data for optimized querying and analysis.

## 🔧 How It Works

1. **Read Raw Data**
   - Reads raw JSON data from the Bronze layer (either from the local disk or S3).
   - Applies a predefined schema to enforce column types and structure.

2. **Data Deduplication**
   - Removes duplicate records using the `id` field as a unique identifier.

3. **Data Enrichment**
   - Adds new boolean fields:
     - `has_website`: `True` if `website_url` is present.
     - `has_phone`: `True` if `phone` is present.
     - `has_geolocation`: `True` if both `latitude` and `longitude` are not null.

4. **Missing Value Handling**
   - Fills `address_1` using the value from `street` if `address_1` is null.
   - Fills `state_province` using the value from `state` if `state_province` is null.

5. **Normalization & Cleanup**
   - Trims whitespace and applies lowercase + title-case formatting to:
     - `city`, `country`, and `state_province`
   - Removes all non-digit characters from:
     - `phone` → `cleaned_phone`
     - `postal_code` → `cleaned_postal_code`
   - Replaces empty strings with null values across all columns.
   - Drops rows where critical fields are missing: `id`, `name`, `country`, `state_province`.

6. **Column Pruning**
   - Drops the following unused or redundant columns:
     - `street`, `state`, `year`, `month`, `day`

7. **Partitioning and Writing**
   - Writes the cleaned data in **Parquet** format.
   - Data is partitioned by:
     - `country`
     - `state_province`

### 🗂️ Output Structure
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
