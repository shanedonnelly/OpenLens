#!/bin/bash
# Run the FastAPI app with uvicorn

# Ensure the script exits if any command fails
set -e

# Create the necessary directories
echo "Creating necessary directories..."
python3 -c "from config import Config; Config.create_dirs()"

# Run with uvicorn
echo "Starting API server..."
uvicorn main:app --host 0.0.0.0 --port 8000