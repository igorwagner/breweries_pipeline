from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(dag_id="dag_teste", start_date=datetime(2025, 7, 28), schedule=None, catchup=False) as dag:
    check_airflow = BashOperator(
        task_id="check_installed_packages",
        bash_command="pip list",
    )
