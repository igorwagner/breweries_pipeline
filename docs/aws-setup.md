# ☁️ AWS Cloud Setup for Testing

To test the project’s cloud functionalities on AWS, the following setup steps were performed:

1. **IAM User Creation**
An IAM user was created with the necessary permissions to access S3, Glue, and Athena services securely.
(AmazonS3FullAccess and AWSGlueConsoleFullAccess policies)

2. **AWS Credentials Configuration**
The AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`) were added to the `.env`
file located in the `local_container` folder to enable Airflow and the jobs to authenticate and interact with
AWS services.

Example `.env` content:
```bash
AIRFLOW_UID=50000
AWS_ACCESS_KEY_ID=your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_DEFAULT_REGION=us-east-1
```
⚠️ AWS_S3_DATALAKE_BUCKET must also be defined at docker-compose.yaml to let the pipeline locate the correct S3 bucket
for reading and writing data across the Bronze, Silver, and Gold layers.

3. **S3 Buckets Setup**
Two S3 buckets were provisioned:

- One bucket to serve as the data lake storage, where Bronze, Silver and Gold layers data are ingested.
- Another bucket dedicated to Athena query results storage.

4. **Athena Databases Creation**
The silver and gold databases are automatically created in Athena at runtime using utility functions in the pipeline.

5. **Glue Catalog Integration**
Glue databases and tables are managed programmatically using the `glue_utils.py` module.
This utility:

- Checks if a Glue database exists — and creates it if it doesn't.
- Checks if a Glue table exists — and creates it if needed using the schema inferred from a Spark DataFrame.
- Ensures compatibility between Spark and Glue by mapping data types accordingly.
- Automatically registers external tables using the correct Parquet input/output formats.
- This approach eliminates the need for manual table registration and guarantees consistent schema management across environments.
