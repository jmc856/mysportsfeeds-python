# Makefile

build: install test

install:
	pip install -r requirements.txt

test:
	pytest -q tests/tests.py
