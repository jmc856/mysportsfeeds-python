# Makefile

PROJECT = "MySportsFeed Wrapper-Python"

build: install test clean

clean: ;@echo "Cleaning .pyc files....."; \
	find . -name \*.pyc -delete

install: ;@echo "Installing ${PROJECT} Dependencies....."; \
	pip install -r requirements.txt

test: ;@echo "Testing ${PROJECT}....."; \
	pytest -q tests/tests.py
