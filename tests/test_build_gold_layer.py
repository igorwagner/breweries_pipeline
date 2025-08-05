"""Unit tests for the Gold Layer pipeline that aggregates brewery data using PySpark."""

from unittest.mock import MagicMock, patch

import pytest
from pyspark.sql.utils import IllegalArgumentException

from jobs.gold_layer.build_gold_layer import run_pipeline


@patch("jobs.gold_layer.build_gold_layer.set_spark_session")
@patch("jobs.gold_layer.build_gold_layer.get_path")
@patch("jobs.gold_layer.build_gold_layer.logger")
def test_run_pipeline_success(logger_mock, get_path_mock, set_spark_mock):
    """
    Tests successful execution of the gold layer pipeline with mocked Spark and I/O.
    """
    spark_mock = MagicMock()
    set_spark_mock.return_value = spark_mock
    get_path_mock.side_effect = lambda key, src: f"/fake/path/{key}/{src}"
    df_mock = MagicMock()
    spark_mock.read.parquet.return_value = df_mock

    df_group_mock = MagicMock()
    df_mock.groupBy.return_value = df_group_mock
    df_group_mock.count.return_value = df_group_mock
    df_group_mock.withColumnRenamed.return_value = df_group_mock

    run_pipeline(source="local", target="local")

    set_spark_mock.assert_called_once_with("Build Gold Layer - Views")
    get_path_mock.assert_any_call("silver_layer/breweries", "local")
    get_path_mock.assert_any_call("gold_layer/breweries_distribution", "local")
    spark_mock.read.parquet.assert_called_once_with("/fake/path/silver_layer/breweries/local")
    df_mock.groupBy.assert_called_once_with("country", "state_province", "city", "brewery_type")
    df_group_mock.count.assert_called_once()
    df_group_mock.withColumnRenamed.assert_called_once_with("count", "total_breweries")
    df_group_mock.write.mode.assert_called_once_with("overwrite")
    df_group_mock.write.mode().parquet.assert_called_once_with("/fake/path/gold_layer/breweries_distribution/local")
    spark_mock.stop.assert_called_once()
    logger_mock.info.assert_any_call("Stopping Spark session")


@patch("jobs.gold_layer.build_gold_layer.set_spark_session")
@patch("jobs.gold_layer.build_gold_layer.get_path")
@patch("jobs.gold_layer.build_gold_layer.logger")
def test_run_pipeline_read_parquet_error(logger_mock, get_path_mock, set_spark_mock):
    """
    Tests handling of errors when reading parquet files in the gold layer pipeline.
    """
    spark_mock = MagicMock()
    set_spark_mock.return_value = spark_mock
    get_path_mock.side_effect = lambda key, src: f"/fake/path/{key}/{src}"

    spark_mock.read.parquet.side_effect = IllegalArgumentException("Erro leitura parquet")

    with pytest.raises(Exception):
        run_pipeline(source="local", target="local")

    logger_mock.error.assert_called()
    spark_mock.stop.assert_called_once()


@patch("jobs.gold_layer.build_gold_layer.set_spark_session")
@patch("jobs.gold_layer.build_gold_layer.get_path")
@patch("jobs.gold_layer.build_gold_layer.logger")
def test_run_pipeline_write_parquet_error(logger_mock, get_path_mock, set_spark_mock):
    """
    Tests handling of errors when writing parquet files in the gold layer pipeline.
    """
    spark_mock = MagicMock()
    set_spark_mock.return_value = spark_mock
    get_path_mock.side_effect = lambda key, src: f"/fake/path/{key}/{src}"
    df_mock = MagicMock()
    spark_mock.read.parquet.return_value = df_mock

    df_group_mock = MagicMock()
    df_mock.groupBy.return_value = df_group_mock
    df_group_mock.count.return_value = df_group_mock
    df_group_mock.withColumnRenamed.return_value = df_group_mock

    df_group_mock.write.mode.return_value.parquet.side_effect = OSError("Erro escrita parquet")

    with pytest.raises(OSError):
        run_pipeline(source="local", target="local")

    logger_mock.error.assert_called()
    spark_mock.stop.assert_called_once()
