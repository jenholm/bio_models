.PHONY: install install-dev install-all test test-unit test-integration smoke clean tree

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-all:
	pip install -e ".[all]"

test:
	pytest -q

test-unit:
	pytest -q tests/unit

test-integration:
	pytest -q tests/integration

smoke:
	python scripts/run_baseline.py

clean:
	find src tests scripts -type d -name "__pycache__" -prune -exec rm -rf {} +
	find src tests scripts -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf src/hsap.egg-info

tree:
	find . -maxdepth 3 -type f | sort
