.DEFAULT_GOAL := check

check:
	python3 -m ruff format --check
	mypy SideBot

run:
	python3 -m SideBot

install:
	python3 -m pip install -e "."

install/dev:
	python3 -m pip install -e ".[dev]"

.PHONY := check run install install/dev
