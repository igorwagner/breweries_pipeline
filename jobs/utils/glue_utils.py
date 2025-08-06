"""Utility functions to check, create, and manage AWS Glue Catalog databases and tables."""

# pylint: disable=too-many-arguments, too-many-positional-arguments

import boto3
from botocore.exceptions import ClientError
from pyspark.sql import DataFrame
from pyspark.sql.types import (
    BooleanType,
    DateType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    StringType,
    TimestampType,
)

from jobs.utils.logger import logger

glue = boto3.client("glue")

SPARK_TO_GLUE_TYPE_MAP = {
    StringType: "string",
    IntegerType: "int",
    LongType: "bigint",
    DoubleType: "double",
    FloatType: "float",
    BooleanType: "boolean",
    TimestampType: "timestamp",
    DateType: "date",
}


def spark_type_to_glue_type(spark_type):
    """
    Converts a given Spark SQL data type to its corresponding AWS Glue data type.

    This function is useful when creating AWS Glue tables programmatically based on
    the schema of a Spark DataFrame. Since Spark and Glue use slightly different
    type systems, this mapping ensures compatibility when defining the schema for
    Glue Catalog tables.

    Args:
        spark_type (pyspark.sql.types.DataType): The Spark data type instance to be converted.

    Returns:
        str: The corresponding AWS Glue data type as a string.

    Raises:
        TypeError: If the given Spark type is not supported by the mapping.
    """
    for spark_cls, glue_type in SPARK_TO_GLUE_TYPE_MAP.items():
        if isinstance(spark_type, spark_cls):
            return glue_type
    raise TypeError(f"Unsupported Spark type: {spark_type}")


def create_glue_database(database_name: str):
    """
    Creates a Glue database in the AWS Glue Catalog if it does not exist.

    This function mimics Athena's behavior by creating the database without specifying a LocationUri.

    Args:
        database_name (str): The name of the Glue database to create.

    Raises:
        ValueError: If database_name is not provided.
        ClientError: If an unexpected error occurs while interacting with AWS Glue.
    """
    try:
        glue.get_database(Name=database_name)
        logger.info(f"Database '{database_name}' already exists.")
    except glue.exceptions.EntityNotFoundException:
        logger.info(f"Creating database '{database_name}'...")
        glue.create_database(DatabaseInput={"Name": database_name})
        logger.info(f"Database '{database_name}' created successfully.")


def database_exists(database_name: str) -> bool:
    """
    Checks whether a database exists in the AWS Glue Catalog.

    Args:
        database_name (str): The name of the Glue database.

    Returns:
        bool: True if the database exists, False if not.

    Raises:
        botocore.exceptions.ClientError: If an unexpected AWS error occurs.
    """
    try:
        glue.get_database(Name=database_name)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityNotFoundException":
            return False
        raise


def table_exists(database_name: str, table_name: str) -> bool:
    """
    Checks whether a table exists in the AWS Glue Catalog.

    Args:
        database_name (str): The name of the Glue database.
        table_name (str): The name of the table to check.

    Returns:
        bool: True if the table exists, False if not.

    Raises:
        botocore.exceptions.ClientError: If an unexpected AWS error occurs other than 'EntityNotFoundException'.
    """
    try:
        glue.get_table(DatabaseName=database_name, Name=table_name)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityNotFoundException":
            return False
        raise


def create_glue_table(
    df: DataFrame,
    database_name: str,
    table_name: str,
    s3_location: str,
    partition_columns: list[str] = None,
    table_parameters: dict = None,
) -> None:
    """
    Creates an external table in the AWS Glue Catalog if it does not already exist.

    If the specified database does not exist, it will be created automatically.

    Args:
        df (DataFrame): Spark DataFrame containing the schema to infer column definitions.
        database_name (str): The name of the Glue database.
        table_name (str): The name of the table to create.
        s3_location (str): The S3 location where the table data is stored.
        partition_columns (List[str], optional): List of column names to use as partitions.
            These will be excluded from the main columns.
        table_parameters (dict, optional): Additional parameters for the Glue table.
            Defaults to {"classification": "parquet"}.

    Returns:
        None

    Raises:
        TypeError: If any Spark type in the DataFrame is unsupported.
        ClientError: If an error occurs while creating the table.
    """
    if not database_exists(database_name):
        create_glue_database(database_name)

    if table_exists(database_name, table_name):
        logger.info(f"Table '{table_name}' already exists in database '{database_name}'.")
        return

    if table_parameters is None:
        table_parameters = {"classification": "parquet"}

    if partition_columns is None:
        partition_columns = []

    columns = []
    partitions = []
    for field in df.schema.fields:
        column_def = {
            "Name": field.name,
            "Type": spark_type_to_glue_type(field.dataType),
        }

        if field.name in partition_columns:
            partitions.append(column_def)
        else:
            columns.append(column_def)

    logger.info(f"Creating table '{table_name}' in database '{database_name}'...")

    glue.create_table(
        DatabaseName=database_name,
        TableInput={
            "Name": table_name,
            "PartitionKeys": partitions,
            "StorageDescriptor": {
                "Columns": columns,
                "Location": s3_location,
                "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
                "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
                "SerdeInfo": {
                    "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
                    "Parameters": {"serialization.format": "1"},
                },
            },
            "TableType": "EXTERNAL_TABLE",
            "Parameters": table_parameters,
        },
    )

    logger.info("Table created successfully.")
