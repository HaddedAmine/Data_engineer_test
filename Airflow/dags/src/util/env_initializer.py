import os
from dotenv import load_dotenv

def initialize_env():
    # Path to the directory where this file is located
    current_file_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the .env file (two directories up)
    env_file_path = os.path.join(current_file_dir, '../../.env')

    # Normalize the path (resolves "..")
    env_file_path = os.path.normpath(env_file_path)

    # Load the .env file
    load_dotenv(env_file_path)