"""Unit tests for the Bronze Layer ingestion pipeline."""

import os
from datetime import datetime
from pathlib import Path
from unittest import mock

from botocore.exceptions import ClientError

from jobs.bronze_layer.build_bronze_layer import (
    fetch_brewery_data,
    generate_random_date,
    run_pipeline,
    save_data_locally,
    save_data_s3,
)


def test_generate_random_date_range():
    """
    Test that the generated random date falls within the specified year range.
    """
    start = 2022
    end = 2024
    for _ in range(100):
        date = generate_random_date(start, end)
        assert start <= date.year <= end


@mock.patch("jobs.bronze_layer.build_bronze_layer.requests.get")
def test_fetch_brewery_data_success(mock_get):
    """
    Test that fetch_brewery_data returns a valid list of brewery records
    when the API responds successfully.
    """
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": "brewery-1"}, {"id": "brewery-2"}]
    mock_get.return_value = mock_response

    data = fetch_brewery_data(total_requests=1, delay_seconds=0)
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["id"] == "brewery-1"


@mock.patch("builtins.open", new_callable=mock.mock_open)
def test_save_data_locally(mock_open_file, tmp_path):
    """
    Test that save_data_locally writes the expected content to a file
    using UTF-8 encoding and append mode.
    """
    file_path = tmp_path / "test_dir" / "test_file.jsonl"
    content = '{"test": "value"}\n'

    save_data_locally(file_path, content)

    mock_open_file.assert_called_once_with(file_path, "a", encoding="utf-8")
    mock_open_file().write.assert_called_once_with(content)


@mock.patch("jobs.bronze_layer.build_bronze_layer.s3_client")
def test_save_data_s3_new_file(mock_s3_client):
    """
    Test that save_data_s3 uploads content to S3 when the file does not exist,
    handling NoSuchKey errors correctly.
    """
    error_response = {"Error": {"Code": "NoSuchKey", "Message": "The specified key does not exist."}}
    operation_name = "GetObject"
    mock_s3_client.get_object.side_effect = ClientError(error_response, operation_name)

    bucket_name = "mock-bucket"
    os.environ["AWS_S3_DATALAKE_BUCKET"] = bucket_name

    save_data_s3("test/path/file.jsonl", '{"mock": "data"}\n')

    mock_s3_client.put_object.assert_called_once()
    _, kwargs = mock_s3_client.put_object.call_args
    assert kwargs["Bucket"] == bucket_name
    assert "mock" in kwargs["Body"].decode()


@mock.patch("jobs.bronze_layer.build_bronze_layer.save_data_s3")
@mock.patch("jobs.bronze_layer.build_bronze_layer.fetch_brewery_data")
@mock.patch("jobs.bronze_layer.build_bronze_layer.generate_random_date")
def test_run_pipeline_s3_target(mock_generate_date, mock_fetch_data, mock_save_s3):
    """
    Test the pipeline execution flow for the 's3' target.
    Validates that data is saved with a properly formatted S3 path.
    """
    mock_fetch_data.return_value = [{"id": "123", "name": "Test Brewery"}]
    mock_generate_date.return_value = datetime(2024, 8, 4)

    run_pipeline(start_year=2023, end_year=2025, num_requests=1, target="s3")

    mock_save_s3.assert_called_once()
    s3_key, content = mock_save_s3.call_args[0]
    assert s3_key.startswith("bronze_layer/year=2024/month=08/day=04/")
    assert "Test Brewery" in content


@mock.patch("jobs.bronze_layer.build_bronze_layer.save_data_locally")
@mock.patch("jobs.bronze_layer.build_bronze_layer.fetch_brewery_data")
@mock.patch("jobs.bronze_layer.build_bronze_layer.generate_random_date")
def test_run_pipeline_local_target(mock_generate_date, mock_fetch_data, mock_save_local):
    """
    Test the pipeline execution flow for the 'local' target.
    Validates that data is saved to the correct local path as a Path object.
    """
    mock_fetch_data.return_value = [{"id": "456", "name": "Local Brewery"}]
    mock_generate_date.return_value = datetime(2024, 8, 4)

    run_pipeline(start_year=2023, end_year=2025, num_requests=1, target="local")

    mock_save_local.assert_called_once()
    local_path, content = mock_save_local.call_args[0]
    assert isinstance(local_path, Path)
    assert "Local Brewery" in content
