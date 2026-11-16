SHELL := /bin/bash
PYTHON ?= python3
VENV := .venv
PY := $(VENV)/bin/python

.DEFAULT_GOAL := help

.PHONY: help init dev test build

help:
	@echo "make init   - create virtual environment and install dependencies"
	@echo "make dev    - start the local TTS API (requires make init)"
	@echo "make test   - run unit tests (requires make init)"
	@echo "make build  - build the experimental snap"

init:
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install -e '.[italian,test]'

dev:
	@test -x "$(PY)" || { echo "Run 'make init' first"; exit 1; }
	$(PY) -m kokoro_server

test:
	@test -x "$(PY)" || { echo "Run 'make init' first"; exit 1; }
	$(PY) -m pytest -q

build:
	snapcraft pack
