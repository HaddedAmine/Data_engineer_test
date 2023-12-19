from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG, set its start date and schedule interval
dag = DAG(
    'example_dag',
    default_args=default_args,
    description='A simple example DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False
)
def print_pythonpath():
    import os
    print("PYTHONPATH:", os.environ.get("PYTHONPATH"))

print_path_task = PythonOperator(
    task_id='print_pythonpath',
    python_callable=print_pythonpath,
    dag=dag,
)
