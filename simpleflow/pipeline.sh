#!/bin/bash

# Define the paths
PROJECT_DIR="."
DATA_DIR="../data"
TEMP_DATA_DIR="$PROJECT_DIR/data"

# Copy data folder to project directory
echo "Copying data to project directory..."
cp -R "$DATA_DIR" "$TEMP_DATA_DIR"

# Build and run the Docker container
echo "Building and running Docker container..."
docker build -t simple_flow "$PROJECT_DIR"
docker run -p 8050:8050 simple_flow

# Remove the copied data folder from project directory
echo "Cleaning up..."
rm -rf "$TEMP_DATA_DIR"

echo "Done!"
