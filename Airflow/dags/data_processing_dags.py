import os 
import sys
from datetime import datetime, timedelta
from airflow import DAG

# Get the directory of the current file
# current_dir = os.path.dirname(os.path.abspath(__file__))

# # Construct the path to the src directory
# src_dir = os.path.join(current_dir, '..', 'src')

# # Add the src directory to sys.path
# sys.path.append(src_dir)

from airflow.operators.python import PythonOperator
from src.data_processing.dataloader import Dataloader
from src.pipeline.mention_extraction import MentionExtraction
from src.pipeline.graph_generation import GraphGeneration
from src.output.json_writer import JsonWriter

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'data_processing_dag',
    default_args=default_args,
    description='A DAG for data processing',
    schedule_interval=timedelta(days=1),
)

def load_and_clean_data(**kwargs):
    loader = Dataloader()
    loaded_data = loader.load_data()
    loader.clean_data(loaded_data)

def extract_mentions(**kwargs):
    extractor = MentionExtraction()
    extractor.extract()

def generate_graph(**kwargs):
    grah_gen = GraphGeneration()
    grah_gen.generate_graph()
    # grah_gen.run_app()

# def display_graph(**kwargs):
#     grah_display = GraphGeneration()
#     grah_display.run_app()

def write_to_json(**kwargs):
    json_writer = JsonWriter()
    json_writer.write()

load_and_clean_data_task = PythonOperator(
    task_id='load_and_clean_data',
    python_callable=load_and_clean_data,
    dag=dag,
)

extract_mentions_task = PythonOperator(
    task_id='extract_mentions',
    python_callable=extract_mentions,
    dag=dag,
)

generate_graph_task = PythonOperator(
    task_id='generate_graph',
    python_callable=generate_graph,
    dag=dag,
)

# display_graph_task = PythonOperator(
#     task_id='display_graph',
#     python_callable=display_graph,
#     dag=dag,
# )

write_to_json_task = PythonOperator(
    task_id='write_to_json',
    python_callable=write_to_json,
    dag=dag,
)

load_and_clean_data_task >> extract_mentions_task >> generate_graph_task >> write_to_json_task
