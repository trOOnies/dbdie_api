COLOUR_GREEN=\033[0;32m
COLOUR_RED=\033[0;31m
COLOUR_BLUE=\033[0;34m
END_COLOUR=\033[0m

.PHONY: venv
venv:
	@if [ -d ".venv" ]; then\
		echo "${COLOUR_RED}The venv already exists, please delete it manually first${END_COLOUR}";\
		false;\
	else\
		python3 -m venv .venv;\
	fi;

.PHONY: activate
activate:
	source .venv/bin/activate

.PHONY: install
install:
	pip install -r requirements.txt
	pip install ../dbdie_ml

.PHONY: core-install
core-install:
	pip install $(core-path)

.PHONY: fmt
fmt:
	ruff format

.PHONY: lint
lint:
	ruff check --output-format=concise

.PHONY: test
test:
	python3 -m pytest --cov=app

.PHONY: api
api:
	uvicorn --host=127.0.0.1 --port 8000 --app-dir=app --env-file=.env main:app
