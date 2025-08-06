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
