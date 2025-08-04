"""Airflow DAG to orchestrate a Spark job that builds the gold layer by aggregating silver layer brewery data."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from utils.discord_webhook import send_discord_alert

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": send_discord_alert,
}

with DAG(
    dag_id="ingestion_gold_layer_dag",
    default_args=default_args,
    description="Create aggregate view from silver data",
    schedule=None,
    start_date=datetime(2025, 7, 28),
    catchup=False,
    params={
        "source": "",
        "target": "",
    },
) as dag:
    with open("/opt/airflow/dags/gold_layer_dag/docs/dag_description.md") as file:
        dag.doc_md = file.read()

    fetch_and_save = BashOperator(
        task_id="fetch_and_save_data",
        bash_command=(
            "PYTHONPATH=/opt/airflow python /opt/airflow/jobs/gold_layer/build_gold_layer.py "
            "--source {{ params.source if params.source else 'local' }} "
            "--target {{ params.target if params.target else 'local' }}"
        ),
    )
