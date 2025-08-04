"""Utility functions to send Discord alerts for Airflow DAG failures."""

import os

import requests

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_discord_alert(context):
    """
    Sends a failure alert message to a Discord channel via webhook when a DAG task fails.

    This function is intended to be used as the `on_failure_callback` in an Airflow DAG or task.
    It extracts context information such as DAG ID, task ID, execution date, and the log URL,
    and sends a formatted message to a specified Discord webhook URL.

    Parameters:
        context (dict): Airflow context dictionary passed automatically by Airflow when a task fails.
                        Contains metadata about the DAG, task instance, execution time, and log URL.

    Raises:
        Exception: If the Discord webhook POST request fails (i.e., response status code is not 204).
    """
    dag_id = context.get("dag").dag_id
    task_id = context.get("task_instance").task_id
    execution_date = context.get("execution_date")
    log_url = context.get("task_instance").log_url

    message = (
        f"❌ **DAG `{dag_id}` failed**\n"
        f"Task: `{task_id}`\n"
        f"Execution time: `{execution_date}`\n"
        f"[🔍 View logs]({log_url})"
    )

    response = requests.post(WEBHOOK_URL, json={"content": message})
    if response.status_code != 204:
        raise Exception(f"Failed to send Discord alert: {response.text}")
