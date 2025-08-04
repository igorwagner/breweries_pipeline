"""Utility module for creating and configuring a SparkSession for AWS S3 integration."""

from pyspark.sql import SparkSession

JARS = [
    "/opt/airflow/jars/aws-java-sdk-bundle-1.12.262.jar",
    "/opt/airflow/jars/hadoop-aws-3.3.4.jar",
    "/opt/airflow/jars/hadoop-client-api-3.3.4.jar",
    "/opt/airflow/jars/hadoop-client-runtime-3.3.4.jar",
    "/opt/airflow/jars/hadoop-common-3.3.4.jar",
]


def set_spark_session(app_name: str) -> SparkSession:
    """
    Creates and returns a configured SparkSession for accessing data on AWS S3.

    Args:
        app_name (str): The name to assign to the Spark application.

    Returns:
        SparkSession: A configured SparkSession instance with support for S3A file system.

    Configuration includes:
        - Adding necessary AWS and Hadoop JARs for S3 access
        - Setting S3A as the default file system implementation
        - Using the DefaultAWSCredentialsProviderChain to retrieve AWS credentials
        - Defining the endpoint as 's3.amazonaws.com'
    """
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.jars", ",".join(JARS))
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain")
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com")
        .getOrCreate()
    )
