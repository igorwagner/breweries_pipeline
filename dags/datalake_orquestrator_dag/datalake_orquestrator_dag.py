from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="datalake_orquestrator_dag",
    default_args=default_args,
    schedule="0 12 * * *",
    start_date=datetime(2025, 8, 1),
    catchup=False,
    params={
        "start_year": "",
        "end_year": "",
        "num_requests": "",
        "source": "",
        "target": "",
    },
) as dag:
    with open("/opt/airflow/dags/datalake_orquestrator_dag/docs/dag_description.md") as file:
        dag.doc_md = file.read()

    trigger_bronze = TriggerDagRunOperator(
        task_id="trigger_bronze_dag",
        trigger_dag_id="ingestion_bronze_layer_dag",
        conf={
            "start_year": "{{ params.start_year if params.start_year else '2023' }}",
            "end_year": "{{ params.end_year if params.end_year else '2025' }}",
            "num_requests": "{{ params.num_requests if params.num_requests else 1 }}",
            "target": "{{ params.target if params.target else 'local' }}",
        },
        wait_for_completion=True,
    )

    trigger_silver = TriggerDagRunOperator(
        task_id="trigger_silver_dag",
        trigger_dag_id="ingestion_silver_layer_dag",
        conf={
            "source": "{{ params.source if params.source else 'local' }}",
            "target": "{{ params.target if params.target else 'local' }}",
        },
        wait_for_completion=True,
    )

    trigger_gold = TriggerDagRunOperator(
        task_id="trigger_gold_dag",
        trigger_dag_id="ingestion_gold_layer_dag",
        conf={
            "source": "{{ params.source if params.source else 'local' }}",
            "target": "{{ params.target if params.target else 'local' }}",
        },
        wait_for_completion=True,
    )

    trigger_bronze >> trigger_silver >> trigger_gold
