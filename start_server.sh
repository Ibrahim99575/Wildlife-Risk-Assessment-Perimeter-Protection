# Wildlife Risk Assessment System - Quick Start Script
# This script starts the backend server on Linux/Mac

#!/bin/bash

echo "============================================================"
echo "   Wildlife Risk Assessment System v2.0"
echo "   Starting Backend Server..."
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Dependencies not installed"
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "============================================================"
echo "   Backend Server Starting..."
echo "   URL: http://localhost:5000"
echo "   Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Create necessary directories
mkdir -p logs recordings snapshots database uploads

# Set Python path and start server
export PYTHONPATH=backend
python3 backend/app.py
