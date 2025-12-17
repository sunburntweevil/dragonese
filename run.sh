#!/bin/bash
# Aviation ADS-B Data Checker
# Monitors real-time aviation ADS-B data from the most recent time period

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Install required dependencies if needed
echo "Checking dependencies..."
pip3 install -q requests 2>/dev/null || pip install -q requests 2>/dev/null

# Run the ADS-B checker with arguments passed through
echo "Starting Aviation ADS-B Data Checker..."
echo "Monitoring most recent aircraft ADS-B data..."
echo ""

python3 "$(dirname "$0")/adsb_checker.py" "$@"
