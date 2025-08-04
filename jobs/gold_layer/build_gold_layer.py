"""Pipeline to build the Gold Layer by aggregating brewery data from the Silver Layer."""

import argparse

from jobs.utils.logger import logger
from jobs.utils.get_path import get_path
from jobs.utils.spark_session import set_spark_session


def run_pipeline(source: str, target: str):
    """
    Executes the Gold Layer transformation pipeline for brewery data.

    Reads data from the Silver Layer, performs a group-by aggregation
    to count breweries by country, state, city, and type, then writes
    the result to the Gold Layer in Parquet format.

    Args:
        source (str): Source mode for reading the Silver Layer.
                      Must be either "local" or "s3".
        target (str): Target mode for writing the Gold Layer.
                      Must be either "local" or "s3".
    """
    spark = set_spark_session("Build Gold Layer - Views")
    silver_path = get_path("silver_layer/breweries", source)
    gold_path = get_path("gold_layer/breweries_distribution", target)

    df = spark.read.parquet(str(silver_path))

    df_gold = df.groupBy("country", "state_province", "city", "brewery_type").count().withColumnRenamed("count","total_breweries")
    df_gold.write.mode("overwrite").parquet(str(gold_path))

    logger.info("Gold Layer data written to Parquet at: %s", gold_path)

    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and store random brewery data")
    parser.add_argument("--source", type=str, default="local", choices=["local", "s3"])
    parser.add_argument("--target", type=str, default="local", choices=["local", "s3"])

    args = parser.parse_args()

    logger.info(f"Starting Gold Layer Pipeline | Source: {args.source} | Target: {args.target}")
    run_pipeline(source=args.source, target=args.target)
