.PHONY: test unit e2e

test:
	.venv/bin/python -m pytest

unit:
	.venv/bin/python -m pytest -m unit

e2e:
	.venv/bin/python -m pytest -m e2e
