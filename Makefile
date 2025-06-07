.PHONY: install test run-server run-client clean generate-ssl

# Variables
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
PYTHONPATH = $(PWD)

install: $(VENV)/bin/activate
	$(PIP) install -r requirements.txt

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

run-server:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m src.server.chat_server

run-client:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m src.client.chat_client

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTEST) tests/ -v

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete