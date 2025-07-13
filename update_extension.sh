#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Activate Virtual Environment ---
echo "Activating Python virtual environment..."
source .venv/bin/activate

# --- Run Python Scripts ---
echo "
Fetching latest data from ChessGoals..."
python parse_regressions.py

echo "
Calculating new regression models..."
python calculate_regressions.py

echo "
Generating updated plots for README..."
python generate_plots.py

# --- Run Tests ---
echo "
Running Playwright tests..."
pytest tests/test_extension.py

echo "
Running Regression accuracy tests..."
pytest tests/test_regressions.py

# --- Package Extension ---
echo "
Zipping extension files..."

# Remove old zip file if it exists
if [ -f Lichess2Chess.zip ]; then
    rm Lichess2Chess.zip
fi

zip -r Lichess2Chess.zip manifest.json lichess2chess.js regressions.json images/

echo "
---------------------------------------------------"
echo "Extension update complete!"
echo "Lichess2Chess.zip is ready for upload."
echo "-------------------------------------------------"
