"""Pipeline to transform brewery data from bronze to silver layer using Spark."""

import argparse
import os
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

from jobs.utils.logger import logger


AWS_BUCKET = os.getenv("AWS_S3_DATALAKE_BUCKET")


def get_path(layer: str, mode: str):
    """
    Generates the appropriate path for a data lake layer (e.g., bronze, silver)
    based on the operation mode ("local" or "s3").

    Args:

        layer(str): Relative path of the desired data lake layer.
        mode(str): The environment mode. Can be one of:
        - "local": returns a `pathlib.Path` pointing to the local file system.
        - "s3": returns a `str` with the full S3 path (using "s3a://" prefix).

    Returns:
        Union[str, Path]:
            - If `mode` is "local", returns a `Path` to the local directory.
            - If `mode` is "s3", returns a `str` with the S3 path.
    """
    base = {
        "local": Path("/opt/airflow/datalake"),
        "s3": f"s3a://{AWS_BUCKET}"
    }[mode]

    if mode == "local":
        return base / layer

    return f"{base}/{layer}"

def run_pipeline(source: str, target: str) -> None:
    """
    Runs a Spark pipeline that reads raw brewery data from the bronze layer,
    deduplicates it by 'id', and writes it in partitioned Parquet format to the silver layer.

    Parameters:
        source (str): The source of the bronze data. Either "local" or "s3".
        target (str): The destination of the silver data. Either "local" or "s3".

    Returns:
        None
    """
    bronze_path = get_path("bronze_layer", source)
    silver_path = get_path("silver_layer/breweries", target)

    jars = [
        "/opt/airflow/jars/aws-java-sdk-bundle-1.12.262.jar",
        "/opt/airflow/jars/hadoop-aws-3.3.4.jar",
        "/opt/airflow/jars/hadoop-client-api-3.3.4.jar",
        "/opt/airflow/jars/hadoop-client-runtime-3.3.4.jar",
        "/opt/airflow/jars/hadoop-common-3.3.4.jar",
    ]

    spark = (
        SparkSession.builder
        .appName("Build Silver Layer - Breweries")
        .config("spark.jars", ",".join(jars))
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain")
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com")
        .getOrCreate()
    )

    schema = StructType([
        StructField("id", StringType(), nullable=True),
        StructField("name", StringType(), nullable=True),
        StructField("brewery_type", StringType(), nullable=True),
        StructField("address_1", StringType(), nullable=True),
        StructField("address_2", StringType(), nullable=True),
        StructField("address_3", StringType(), nullable=True),
        StructField("city", StringType(), nullable=True),
        StructField("state_province", StringType(), nullable=True),
        StructField("postal_code", StringType(), nullable=True),
        StructField("country", StringType(), nullable=True),
        StructField("longitude", DoubleType(), nullable=True),
        StructField("latitude", DoubleType(), nullable=True),
        StructField("phone", StringType(), nullable=True),
        StructField("website_url", StringType(), nullable=True),
        StructField("state", StringType(), nullable=True),
        StructField("street", StringType(), nullable=True),
    ])

    logger.info(f"Reading from bronze layer: {bronze_path}")
    df = spark.read.schema(schema).json(str(bronze_path))

    logger.info("Dropping duplicate rows by 'id'")
    df = df.dropDuplicates(["id"])

    logger.info(f"Writing to silver layer: {silver_path}")
    df.write.mode("overwrite").partitionBy("country", "state_province").parquet(str(silver_path))

    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and store random brewery data")
    parser.add_argument("--source", type=str, default="local", choices=["local", "s3"])
    parser.add_argument("--target", type=str, default="local", choices=["local", "s3"])

    args = parser.parse_args()

    if args.target not in ["local", "s3"]:
        raise ValueError("Invalid target parameter. Use 'local' or 's3'.")

    logger.info(f"Starting pipeline | Source: {args.source} | Target: {args.target}")
    run_pipeline(source=args.source, target=args.target)
