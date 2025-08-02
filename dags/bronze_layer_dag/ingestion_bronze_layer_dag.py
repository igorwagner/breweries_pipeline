"""Airflow DAG that triggers a job to fetch random brewery data and save it locally and partitioned by random dates"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="fetch_brewery_data",
    default_args=default_args,
    description="Fetch brewery data and store partitioned locally",
    schedule=None,
    start_date=datetime(2025, 7, 28),
    catchup=False,
    params={
        "start_year": "",
        "end_year": "",
        "num_requests": "",
        "target": "",
    },
) as dag:
    with open("/opt/airflow/dags/bronze_layer_dag/docs/dag_description.md") as file:
        dag.doc_md = file.read()

    fetch_and_save = BashOperator(
        task_id="fetch_and_save_data",
        bash_command=(
            "PYTHONPATH=/opt/airflow python /opt/airflow/jobs/bronze_layer/build_bronze_layer.py "
            "--start-year {{ params.start_year if params.start_year else '2023' }} "
            "--end-year {{ params.end_year if params.end_year else '2025' }} "
            "--num-requests {{ params.num_requests if params.num_requests else '1' }} "
            "--target {{ params.target if params.target else 'local' }}"
        ),
    )

    fetch_and_save
