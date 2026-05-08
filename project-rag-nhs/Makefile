.PHONY: install demo test lint evaluate clean

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt -r requirements-dev.txt
	pip install -e .

demo:
	clinrag demo "What medications is patient SYN-001 taking?"

evaluate:
	clinrag evaluate

test:
	pytest -q

lint:
	ruff check src tests

clean:
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
