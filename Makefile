.PHONY: init lint format typecheck test checks pre-commit

init:
	uv sync --all-groups
	uv run pre-commit install

lint:
	uv run ruff check

format:
	uv run ruff format
	uv run black .
	uv run isort .

typecheck:
	uv run mypy core app scripts

test:
	uv run pytest tests

checks:
	uv run python scripts/run_checks.py

pre-commit:
	uv run pre-commit run --all-files
