#!/bin/bash
set -e  # Exit on any error

# Wait for PostgreSQL to be ready (optional but recommended)
until pg_isready -h db -p 5432; do
  echo "Waiting for database..."
  sleep 2
done

# Run FastAPI in the background
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Run Streamlit frontend
streamlit run streamlit_ui/main.py --server.port 8501 --server.runOnSave true --server.enableCORS false
