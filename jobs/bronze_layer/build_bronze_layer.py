"""Script to fetch random brewery data from OpenBreweryDB and store it partitioned by date."""

import argparse
import json
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

import boto3
import requests

from jobs.utils.logger import logger

AWS_BUCKET = os.getenv("AWS_S3_DATALAKE_BUCKET")
BASE_URL = "https://api.openbrewerydb.org/v1/breweries/random"
s3_client = boto3.client("s3")


def generate_random_date(start_year: int = 2023, end_year: int = 2025) -> datetime:
    """
    Generate a random date between January 1st of start_year and December 31st of end_year.

    Args:
        start_year (int): The starting year of the range (inclusive). Default is 2023.
        end_year (int): The ending year of the range (inclusive). Default is 2025.

    Returns:
        datetime: A randomly generated datetime object within the specified range.
    """
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date

    return start_date + timedelta(days=random.randint(0, delta.days))


def fetch_brewery_data(total_requests: int, delay_seconds: int = 15) -> list:
    """
    Fetches brewery data from the OpenBreweryDB API, making multiple paginated requests.

    Args:
        total_requests (int): Number of requests to perform.
        delay_seconds (int, optional): Delay in seconds between each request. Default is 15.

    Returns:
        list[dict]: A list containing brewery records retrieved from the API.
    """
    all_data = []
    for i in range(total_requests):
        logger.info("Request %s/%s", i + 1, total_requests)
        try:
            response = requests.get(f"{BASE_URL}?size={50}", timeout=10)
            response.raise_for_status()
            all_data.extend(response.json())
        except requests.RequestException as e:
            logger.error("Error on request %s: %s", i + 1, str(e))
        time.sleep(delay_seconds)

    return all_data


def save_data_locally(file_path: Path, content: str) -> None:
    """
    Saves a string content to a local file, creating parent directories if necessary.

    Args:
        file_path (Path): The full path where the content will be saved.
        content (str): The string data to write to the file.

    Returns:
        None
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content)

    logger.info("Data saved locally!!")


def save_data_s3(key_path: str, content: str) -> None:
    """
    Uploads string content to an S3 object, appending to existing content if the key already exists.

    Args:
        key_path (str): The S3 key where the object will be stored.
        content (str): The content to upload.

    Returns:
        None
    """
    try:
        logger.info("Uploading to S3: %s", key_path)
        try:
            existing = s3_client.get_object(Bucket=AWS_BUCKET, Key=key_path)
            existing_content = existing["Body"].read().decode("utf-8")
        except s3_client.exceptions.NoSuchKey:
            existing_content = ""

        final_content = existing_content + content
        s3_client.put_object(
            Bucket=AWS_BUCKET,
            Key=key_path,
            Body=final_content.encode("utf-8"),
        )
        logger.info("Data saved to S3!")
    except Exception as e:
        logger.error("Error uploading to S3: %s", str(e))

def run_pipeline(start_year: int, end_year: int, num_requests: int, target: str) -> None:
    """
    Runs the entire ETL pipeline:
    - Fetches brewery data from the API
    - Assigns a random date to each record
    - Stores the record locally or in S3, partitioned by year/month/day

    Args:
        start_year (int): Minimum year for the generated random dates.
        end_year (int): Maximum year for the generated random dates.
        num_requests (int): Number of requests to perform to the API.
        target (str): Destination to save the data. Use "local" to save in the local filesystem
                      (under /opt/airflow/datalake/bronze_layer) or "s3" to upload to an S3 bucket
                      configured via boto3.

    Returns:
        None
    """
    logger.info("Total requests to be made: %d", num_requests)
    data = fetch_brewery_data(num_requests)
    for record in data:
        date = generate_random_date(start_year, end_year)
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")
        file_name = f"{year}_{month}_{day}_data.jsonl"
        relative_path = f"year={year}/month={month}/day={day}/{file_name}"
        content = json.dumps(record) + "\n"

        if target == "local":
            local_path = Path("/opt/airflow/datalake") / "bronze_layer" / relative_path
            save_data_locally(local_path, content)
        else:
            s3_key = f"bronze_layer/{relative_path}"
            save_data_s3(s3_key, content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and store random brewery data")
    parser.add_argument("--start-year", type=int, default=2023)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--num-requests", type=int, default=1)
    parser.add_argument("--target", type=str, default="local", choices=["local", "s3"])

    args = parser.parse_args()

    logger.info(f"Saving data to: {args.target}")

    run_pipeline(
        start_year=args.start_year,
        end_year=args.end_year,
        num_requests=args.num_requests,
        target=args.target
    )
