import json
import pandas as pd
import logging
import pickle

def save_data_dfs(data, file_path, indent=4):
    """
    Saves a dictionary of DataFrames to a JSON file. Each key in the dictionary corresponds 
    to a DataFrame. The DataFrames are converted to a JSON-serializable format.

    :param data: Dictionary of DataFrames to be saved.
    :param file_path: Path of the JSON file where data will be saved.
    :param indent: Indentation level for the JSON file.
    """
    try:
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary of DataFrames.")

        json_serializable_data = {}
        for key, df in data.items():
            if not isinstance(df, pd.DataFrame):
                logging.error(f"Data under key '{key}' is not a DataFrame.")
                continue

            # Convert DataFrame to a JSON-serializable format
            json_serializable_data[key] = df.to_dict(orient='records')

        with open(file_path, 'w') as f:
            json.dump(json_serializable_data, f, indent=indent)

    except Exception as e:
        logging.error(f"Error saving data: {str(e)}")
        raise

def save_data(data, file_path, file_format='json', indent=4):
    """
    Saves data to a file in the specified format.

    :param data: Data to be saved.
    :param file_path: Path of the file where data will be saved.
    :param file_format: Format of the file (e.g., 'json', 'csv'). Default is 'json'.
    """
    try:
        if file_format == 'json':
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=indent)
        elif file_format == 'csv':
            pd.DataFrame(data).to_csv(file_path, index=False)
        else:
            raise ValueError("Unsupported file format specified.")
    except Exception as e:
        raise ValueError(f"Error saving data: {str(e)}")

def save_graph(graph, file_path):
    """
    Saves a NetworkX graph to a file using Pickle.

    :param graph: NetworkX graph.
    :param file_path: Path to the file where the graph should be saved.
    """
    with open(file_path, 'wb') as f:
        pickle.dump(graph, f)