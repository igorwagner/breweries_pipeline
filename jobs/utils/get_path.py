"""Utilities for generating data lake paths based on environment mode."""

import os
from pathlib import Path

AWS_BUCKET = os.getenv("AWS_S3_DATALAKE_BUCKET")


def get_path(layer: str, mode: str):
    """
    Generates the appropriate path for a data lake layer (e.g., bronze, silver)
    based on the operation mode ("local" or "s3").

    Args:

        layer(str): Relative path of the desired data lake layer.
        mode(str): The environment mode. Can be one of:
        - "local": returns a `pathlib.Path` pointing to the local file system.
        - "s3": returns a `str` with the full S3 path (using "s3a://" prefix).

    Returns:
        Union[str, Path]:
            - If `mode` is "local", returns a `Path` to the local directory.
            - If `mode` is "s3", returns a `str` with the S3 path.
    """
    base = {
        "local": Path("/opt/airflow/datalake"),
        "s3": f"s3a://{AWS_BUCKET}"
    }[mode]

    if mode == "local":
        return base / layer

    return f"{base}/{layer}"
