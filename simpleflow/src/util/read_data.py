import json
import pandas as pd
import pickle

def load_json_to_dataframes(json_data):
    """
    Converts a JSON object with multiple datasets into a dictionary of Pandas DataFrames.

    :param json_data: JSON object as a string or a path to a JSON file.
    :return: Dictionary of Pandas DataFrames.
    """
    # Load JSON data from a file or string
    if isinstance(json_data, str):
        try:
            if json_data.endswith('.json'):
                with open(json_data, 'r') as file:
                    data = json.load(file)
            else:
                data = json.loads(json_data)
        except Exception as e:
            raise ValueError(f"Error loading JSON data: {e}")
    else:
        raise ValueError("Invalid input type for json_data. Must be a string (JSON string or file path).")

    # Convert each key in the JSON object to a DataFrame
    dataframes = {}
    for key, value in data.items():
        if isinstance(value, list):
            dataframes[key] = pd.DataFrame(value)
        else:
            raise ValueError(f"Expected a list of dictionaries for key '{key}', but got {type(value)}")

    return dataframes

def read_data(file_path, file_format='json'):
    """
    Reads data from a file in the specified format.

    :param file_path: Path of the file from which data will be read.
    :param file_format: Format of the file (e.g., 'json', 'csv'). Default is 'json'.
    :return: Data read from the file.
    """
    try:
        if file_format == 'json':
            with open(file_path, 'r') as f:
                return json.load(f)
        elif file_format == 'csv':
            return pd.read_csv(file_path)
        else:
            raise ValueError("Unsupported file format specified.")
    except Exception as e:
        raise ValueError(f"Error reading data: {str(e)}")

def load_graph(file_path):
    """
    Loads a NetworkX graph from a Pickle file.

    :param file_path: Path to the file where the graph is saved.
    :return: Loaded NetworkX graph.
    """
    with open(file_path, 'rb') as f:
        return pickle.load(f)