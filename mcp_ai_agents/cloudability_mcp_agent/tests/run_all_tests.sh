#!/bin/bash
# Run all comprehensive tests for Cloudability MCP Server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "=========================================="
echo "Cloudability MCP Server - Test Suite"
echo "=========================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run comprehensive tests
echo "1. Running comprehensive test suite (30+ combinations)..."
python tests/test_comprehensive.py

echo ""
echo "2. Running API combination tests..."
python tests/test_api_combinations.py

echo ""
echo "3. Running all tools test..."
python tests/test_all_tools.py

echo ""
echo "=========================================="
echo "All tests completed!"
echo "=========================================="
echo ""
echo "Results saved in tests/ directory:"
echo "  - comprehensive_test_results.json"
echo "  - api_test_results.json"
echo "  - test_results.json"

