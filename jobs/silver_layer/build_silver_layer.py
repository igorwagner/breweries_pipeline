"""Pipeline to transform brewery data from bronze to silver layer using Spark."""

import argparse

from pyspark.sql.types import StructType, StructField, StringType, DoubleType

from jobs.utils.logger import logger
from jobs.utils.get_path import get_path
from jobs.utils.spark_session import set_spark_session


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
    spark = set_spark_session("Build Silver Layer - Breweries")

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

    logger.info(f"Starting Silver Layer Pipeline | Source: {args.source} | Target: {args.target}")
    run_pipeline(source=args.source, target=args.target)
