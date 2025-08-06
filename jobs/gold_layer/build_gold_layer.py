"""Pipeline to build the Gold Layer by aggregating brewery data from the Silver Layer."""

# pylint: disable=R0801

import argparse

from py4j.protocol import Py4JJavaError
from pyspark.errors.exceptions.captured import AnalysisException
from pyspark.sql.utils import IllegalArgumentException

from jobs.utils.get_path import get_path
from jobs.utils.glue_utils import create_glue_table
from jobs.utils.logger import logger
from jobs.utils.spark_session import set_spark_session


def run_pipeline(source: str, target: str):
    """
    Executes the Gold Layer transformation pipeline for brewery data.

    Reads data from the Silver Layer (Parquet), aggregates brewery counts by
    country, state_province, city, and brewery_type, and writes the results
    in Parquet format to the Gold Layer.

    Args:
        source (str): Location type for input data. Either "local" or "s3".
        target (str): Location type for output data. Either "local" or "s3".

    Raises:
        AnalysisException: If Spark encounters path or query resolution issues.
        IllegalArgumentException: If Spark receives invalid input parameters.
        OSError: For system-level I/O errors during read/write.
        Py4JJavaError: For Java backend errors during Spark operations.
        Exception: For other unforeseen errors.

    Returns:
        None
    """
    spark = set_spark_session("Build Gold Layer - Views")
    silver_path = get_path("silver_layer/breweries", source)
    gold_path = get_path("gold_layer/breweries_distribution", target)
    try:
        logger.info(f"Reading Silver Layer data from: {silver_path}")

        try:
            df = spark.read.parquet(str(silver_path))
        except (AnalysisException, IllegalArgumentException, OSError, Py4JJavaError) as error:
            logger.error(f"Error reading parquet from silver path: {str(error)}")
            raise

        df_gold = (
            df.groupBy("country", "state_province", "city", "brewery_type")
            .count()
            .withColumnRenamed("count", "total_breweries")
        )
        logger.info(f"Writing aggregated data to Gold Layer at: {gold_path}")

        try:
            df_gold.write.mode("overwrite").parquet(str(gold_path))
        except (OSError, Py4JJavaError, PermissionError) as error:
            logger.error(f"Error saving parquet to gold path: {str(error)}")
            raise

        logger.info(f"Gold Layer data written to Parquet at: {gold_path}")
        if target == "s3":
            create_glue_table(
                df=df_gold,
                database_name="gold",
                table_name="breweries_distribution",
                s3_location=str(gold_path),
            )
    finally:
        logger.info("Stopping Spark session")
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and store random brewery data")
    parser.add_argument("--source", type=str, default="local", choices=["local", "s3"])
    parser.add_argument("--target", type=str, default="local", choices=["local", "s3"])

    args = parser.parse_args()

    logger.info(f"Starting Gold Layer Pipeline | Source: {args.source} | Target: {args.target}")
    run_pipeline(source=args.source, target=args.target)
