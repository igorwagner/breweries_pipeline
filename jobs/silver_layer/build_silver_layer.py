"""Pipeline to transform brewery data from bronze to silver layer using Spark."""

# pylint: disable=R0801,R0915

import argparse

from py4j.protocol import Py4JJavaError
from pyspark.errors.exceptions.captured import AnalysisException
from pyspark.sql.functions import col, initcap, lit, lower, regexp_replace, trim, when
from pyspark.sql.types import DoubleType, StringType, StructField, StructType
from pyspark.sql.utils import ParseException

from jobs.utils.get_path import get_path
from jobs.utils.glue_utils import create_glue_table
from jobs.utils.logger import logger
from jobs.utils.spark_session import set_spark_session


def run_pipeline(source: str, target: str) -> None:
    """
    Runs a Spark pipeline that transforms brewery data from the bronze to silver layer.

    The pipeline reads raw JSON data with a predefined schema from the bronze layer (either local or S3),
    deduplicates it by the 'id' field, and writes the results in Parquet format, partitioned by 'country'
    and 'state_province', into the silver layer (also local or S3).

    Args:
        source (str): Location type for input data. Either "local" or "s3".
        target (str): Location type for output data. Either "local" or "s3".

    Raises:
        AnalysisException: If Spark can't resolve path or query issues.
        ParseException: If JSON input is malformed.
        OSError: If system-level issues (e.g. I/O) occur during write.
        PermissionError: If there's a permission issue writing to disk/S3.

    Returns:
        None
    """
    bronze_path = get_path("bronze_layer", source)
    silver_path = get_path("silver_layer/breweries", target)
    spark = set_spark_session("Build Silver Layer - Breweries")

    try:
        schema = StructType(
            [
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
            ]
        )

        logger.info(f"Reading from bronze layer: {bronze_path}")

        try:
            df = spark.read.schema(schema).json(str(bronze_path))
        except (AnalysisException, FileNotFoundError) as error:
            logger.error(f"Error reading JSON from bronze path: {str(error)}")
            raise
        except ParseException as error:
            logger.error(f"Error parsing JSON file at {bronze_path}: {str(error)}")
            raise
        except Py4JJavaError as error:
            logger.error(f"Java backend error when reading from {bronze_path}: {str(error)}")
            raise

        logger.info("Dropping duplicate rows by 'id'")
        df = df.dropDuplicates(["id"])

        df = df.withColumn("brewery_type", lower(col("brewery_type")))
        df = df.withColumn("has_website", col("website_url").isNotNull())
        df = df.withColumn("has_phone", col("phone").isNotNull())
        df = df.withColumn(
            "has_geolocation", when(col("latitude").isNotNull() & col("longitude").isNotNull(), True).otherwise(False)
        )

        df = df.withColumn("address_1", when(col("address_1").isNull(), col("street")).otherwise(col("address_1")))
        df = df.withColumn(
            "state_province", when(col("state_province").isNull(), col("state")).otherwise(col("state_province"))
        )

        for column in ["city", "country", "state_province"]:
            df = df.withColumn(column, initcap(lower(trim(col(column)))))

        df = df.withColumn("cleaned_phone", regexp_replace(col("phone"), r"[^0-9]", ""))
        df = df.withColumn("cleaned_postal_code", regexp_replace(col("postal_code"), r"[^0-9]", ""))

        df = df.drop("street", "state", "year", "month", "day")
        for column in df.columns:
            df = df.withColumn(column, when(col(column) == "", lit(None)).otherwise(col(column)))

        df = df.na.drop(subset=["id", "name", "country", "state_province"])

        logger.info(f"Writing to silver layer: {silver_path}")
        try:
            df.write.mode("overwrite").partitionBy("country", "state_province").parquet(str(silver_path))
        except PermissionError as error:
            logger.error(f"Permission denied when writing to {silver_path}: {error}")
            raise
        except OSError as error:
            logger.error(f"OS error while writing parquet to {silver_path}: {error}")
            raise
        except Py4JJavaError as error:
            logger.error(f"Java backend error when writing to {silver_path}: {str(error)}")
            raise

        logger.info(f"Silver Layer data written to Parquet at: {silver_path}")
        if target == "s3":
            create_glue_table(
                df=df,
                database_name="silver",
                table_name="breweries",
                s3_location=str(silver_path).replace("s3a://", "s3://"),
                partition_columns=["country", "state_province"],
            )
    finally:
        logger.info("Stopping Spark session")
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and store random brewery data")
    parser.add_argument("--source", type=str, default="local", choices=["local", "s3"])
    parser.add_argument("--target", type=str, default="local", choices=["local", "s3"])

    args = parser.parse_args()

    logger.info(f"Starting Silver Layer Pipeline | Source: {args.source} | Target: {args.target}")
    run_pipeline(source=args.source, target=args.target)
