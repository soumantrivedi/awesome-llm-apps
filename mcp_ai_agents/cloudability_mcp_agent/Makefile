.PHONY: help test test-working test-comprehensive test-all install clean lint format

help:
	@echo "Cloudability MCP Server - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make install          - Install dependencies"
	@echo "  make test             - Run all tests"
	@echo "  make test-working     - Run working combinations tests"
	@echo "  make test-comprehensive - Run comprehensive tests"
	@echo "  make test-api         - Run API combination tests"
	@echo "  make lint             - Run linter"
	@echo "  make format           - Format code"
	@echo "  make clean            - Clean generated files"
	@echo "  make verify           - Verify installation"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

test:
	@echo "Running all tests..."
	python -m pytest tests/ -v

test-working:
	@echo "Running working combinations tests..."
	python tests/test_working_combinations.py

test-comprehensive:
	@echo "Running comprehensive tests..."
	python tests/test_comprehensive.py

test-api:
	@echo "Running API combination tests..."
	python tests/test_api_combinations.py

lint:
	@echo "Running linter..."
	@if command -v pylint >/dev/null 2>&1; then \
		pylint src/ --disable=C0111 || true; \
	else \
		echo "pylint not installed, skipping..."; \
	fi

format:
	@echo "Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black src/ tests/ || true; \
	else \
		echo "black not installed, skipping..."; \
	fi

clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	rm -rf tests/*.json.bak 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	rm -rf htmlcov 2>/dev/null || true

verify:
	@echo "Verifying installation..."
	@python -c "import sys; sys.path.insert(0, 'src'); from main import CloudabilityMCPServer; print('✓ Import successful')"
	@echo "✓ Installation verified"

test-quick:
	@echo "Running quick smoke tests..."
	@python -c "import sys; sys.path.insert(0, 'src'); from main import CloudabilityMCPServer; server = CloudabilityMCPServer(); print('✓ Server initialized'); tools = server.get_tools(); print(f'✓ Found {len(tools)} tools')"

