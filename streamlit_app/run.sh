#!/bin/bash

echo "========================================"
echo "RAG Evaluation Dashboard Launcher"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
source venv/bin/activate

# Check if requirements are installed
echo "Checking dependencies..."
pip install -r requirements.txt --quiet
echo ""

# Launch Streamlit
echo "========================================"
echo "Starting dashboard..."
echo "Dashboard will open at: http://localhost:8501"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py