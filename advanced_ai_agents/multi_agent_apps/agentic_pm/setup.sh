#!/bin/bash

# Setup script for Agentic PM Agent
# This script creates a virtual environment and installs all dependencies

echo "🚀 Setting up Agentic PM Agent..."

# Create virtual environment if it doesn't exist
if [ ! -d "agentic_pm_venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv agentic_pm_venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source agentic_pm_venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "  1. Activate the virtual environment:"
echo "     source agentic_pm_venv/bin/activate"
echo ""
echo "  2. Run Streamlit:"
echo "     streamlit run agentic_pm_agent.py"
echo ""

