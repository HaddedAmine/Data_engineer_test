FROM python:3.11-slim

WORKDIR /usr/src/app

# First, copy only the requirements.txt file
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Run the script data_pipeline
CMD ["python", "./data_pipeline.py"]
