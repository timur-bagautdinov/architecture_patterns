.PHONY: test unit integration e2e

test:
	.venv/bin/python -m pytest

unit:
	.venv/bin/python -m pytest -m unit

integration:
	.venv/bin/python -m pytest -m integration

e2e:
	.venv/bin/python -m pytest -m e2e
