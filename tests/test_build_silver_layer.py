"""Unit tests for the run_pipeline function in the silver layer job."""

from unittest.mock import MagicMock, patch

import pytest
from pyspark.sql.utils import ParseException

from jobs.silver_layer.build_silver_layer import run_pipeline


@patch("jobs.silver_layer.build_silver_layer.set_spark_session")
@patch("jobs.silver_layer.build_silver_layer.get_path")
@patch("jobs.silver_layer.build_silver_layer.logger")
def test_run_pipeline_parse_json_error(logger_mock, get_path_mock, set_spark_mock):
    """
    Test that run_pipeline raises ParseException and logs the error when JSON parsing fails.
    """
    spark_mock = MagicMock()
    set_spark_mock.return_value = spark_mock
    get_path_mock.side_effect = lambda key, src: f"/fake/path/{key}/{src}"

    spark_mock.read.schema.return_value.json.side_effect = ParseException("Erro de parse")

    with pytest.raises(ParseException):
        run_pipeline(source="local", target="local")

    logger_mock.error.assert_called()
    spark_mock.stop.assert_called_once()
