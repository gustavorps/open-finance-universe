.PHONY: help test test-failed install clean lint format

# Python environment
PYTHON := python3
PIP := pip3
PYTEST := pytest

help:
	@echo "Python Openfinance Brazil - Available Commands"
	@echo ""
	@echo "Targets:"
	@echo "  help         Show this help message"
	@echo "  test         Run pytest with auto-discovery (*_test.py files)"
	@echo "  test-failed  Re-run only failed tests from last run"
	@echo "  install      Install project dependencies"
	@echo "  clean        Remove build artifacts and cache"
	@echo "  lint         Run linters (flake8, mypy)"
	@echo "  format       Format code with black and isort"
	@echo ""

# Test target: Run pytest with auto-discovery
test:
	@echo "Running pytest with auto-discovery..."
	$(PYTEST) \
		--tb=short \
		-vv \
		src/openfinance/brazil/

# Re-run only failed tests from last run
test-failed:
	@echo "Re-running failed tests..."
	$(PYTEST) \
		--tb=short \
		-vv \
		--lf \
		src/openfinance/brazil/

# Install dependencies
install:
	@echo "Installing dependencies..."
	$(PIP) install -e .
	$(PIP) install pytest pytest-cov black flake8 mypy isort

# Clean build artifacts and cache
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ .coverage 2>/dev/null || true
	@echo "Clean complete."

# Lint: Run flake8 and mypy
lint:
	@echo "Running linters..."
	flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics || true
	mypy src/ --ignore-missing-imports || true

# Format: Black and isort
format:
	@echo "Formatting code..."
	black src/
	isort src/

# Test with coverage
test-cov:
	@echo "Running pytest with coverage..."
	$(PYTEST) \
		--cov=src/openfinance \
		--cov-report=html \
		--cov-report=term-missing \
		-v \
		src/openfinance/brazil/ -k "_test"

.PHONY: test-cov
