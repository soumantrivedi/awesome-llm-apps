.PHONY: help install register secrets test test-examples docs clean verify

help:
	@echo "Cloudability V2 MCP Server - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make install     - Install dependencies"
	@echo "  make register   - Register MCP server in Cursor IDE"
	@echo "  make secrets     - Prompt user to provide secrets"
	@echo "  make test        - Run test suite"
	@echo "  make test-examples - Run example scripts"
	@echo "  make docs        - Generate documentation"
	@echo "  make clean       - Clean generated files"
	@echo "  make verify      - Verify installation"

install:
	@echo "Installing dependencies..."
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "Installing dependencies into venv..."
	@./venv/bin/pip install -r requirements.txt
	@echo "✓ Dependencies installed in venv"

register:
	@echo "Registering Cloudability V2 MCP Server in Cursor IDE..."
	@python3 register_mcp_server.py

secrets:
	@echo "Setting up secrets..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file..."; \
		touch .env; \
	fi
	@echo ""
	@echo "Please provide your Cloudability credentials:"
	@echo ""
	@read -p "Authentication method (basic/enhanced) [basic]: " auth_method; \
	auth_method=$${auth_method:-basic}; \
	if [ "$$auth_method" = "enhanced" ]; then \
		read -p "CLOUDABILITY_PUBLIC_KEY: " public_key; \
		read -p "CLOUDABILITY_PRIVATE_KEY: " private_key; \
		read -p "CLOUDABILITY_ENVIRONMENT_ID (optional): " env_id; \
		echo "CLOUDABILITY_PUBLIC_KEY=$$public_key" >> .env; \
		echo "CLOUDABILITY_PRIVATE_KEY=$$private_key" >> .env; \
		if [ -n "$$env_id" ]; then \
			echo "CLOUDABILITY_ENVIRONMENT_ID=$$env_id" >> .env; \
		fi; \
		echo "CLOUDABILITY_AUTH_TYPE=opentoken" >> .env; \
	else \
		read -p "CLOUDABILITY_API_KEY: " api_key; \
		echo "CLOUDABILITY_API_KEY=$$api_key" >> .env; \
		echo "CLOUDABILITY_AUTH_TYPE=basic" >> .env; \
	fi; \
	read -p "CLOUDABILITY_BASE_URL [https://api.cloudability.com/v3]: " base_url; \
	base_url=$${base_url:-https://api.cloudability.com/v3}; \
	echo "CLOUDABILITY_BASE_URL=$$base_url" >> .env; \
	echo ""
	@echo "✓ Secrets configured in .env file"
	@echo "Note: Make sure .env is in .gitignore to keep your secrets safe!"

test:
	@echo "Running test suite..."
	@python3 tests/test_tools.py
	@echo "✓ Tests completed"

test-examples:
	@echo "Running example scripts..."
	@python3 examples/test_mcp_server.py
	@echo "✓ Examples completed"

docs:
	@echo "Generating documentation..."
	@echo "Documentation is available in the docs/ folder:"
	@echo "  - README.md - Main documentation"
	@echo "  - API_REFERENCE.md - API reference"
	@echo "  - USAGE_EXAMPLES.md - Usage examples"
	@echo ""
	@echo "To view documentation, open the files in docs/ folder"
	@echo "✓ Documentation available"

clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	rm -rf htmlcov 2>/dev/null || true
	rm -f *.csv 2>/dev/null || true
	rm -f *.json 2>/dev/null || true
	@echo "✓ Clean completed"

verify:
	@echo "Verifying installation..."
	@if [ ! -d "venv" ]; then \
		echo "✗ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@./venv/bin/python3 -c "import sys; sys.path.insert(0, '.'); from src.main import CloudabilityV2MCPServer; print('✓ Import successful')" || (echo "✗ Import failed" && exit 1)
	@./venv/bin/python3 -c "import sys; sys.path.insert(0, '.'); from src.main import CloudabilityV2MCPServer; server = CloudabilityV2MCPServer(); print('✓ Server initialized'); tools = server.get_tools(); print(f'✓ Found {len(tools)} tools')" || (echo "✗ Server initialization failed" && exit 1)
	@echo "✓ Installation verified"

