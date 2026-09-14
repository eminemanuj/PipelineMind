"""
airflow/dags/pipelinemind_dbt_dag.py — Real Airflow DAG
------------------------------------------------------------
This DAG runs our real dbt project on a schedule. When schema drift has
been injected (via scripts/inject_schema_drift.py), the dbt run task
genuinely fails, and Airflow marks it as failed in the UI — a real
pipeline failure that PipelineMind's agents will detect and respond to.
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "pipelinemind",
    "retries": 0,  # no auto-retry — we WANT failures to surface immediately for the agent to catch
}

with DAG(
    dag_id="pipelinemind_dbt_pipeline",
    default_args=default_args,
    description="Runs the PipelineMind dbt project against the DuckDB warehouse",
    schedule=None,  # triggered manually or by the agent system, not on a timer, for demo control
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["pipelinemind", "dbt"],
) as dag:

    run_dbt = BashOperator(
        task_id="run_dbt_models",
        bash_command=(
            "cd /opt/airflow/dbt_project && "
            "DBT_PROFILES_DIR=. dbt run"
        ),
    )

    test_dbt = BashOperator(
        task_id="test_dbt_models",
        bash_command=(
            "cd /opt/airflow/dbt_project && "
            "DBT_PROFILES_DIR=. dbt test"
        ),
    )

    run_dbt >> test_dbt