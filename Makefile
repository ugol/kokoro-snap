SHELL := /bin/bash
PYTHON ?= python3.12
VENV := .venv
PY := $(VENV)/bin/python

.DEFAULT_GOAL := help

.PHONY: help init dev test build

help:
	@echo "make init   - create virtual environment and install dependencies (Python 3.12)"
	@echo "make dev    - start the local TTS API (requires make init)"
	@echo "make test   - run unit tests (requires make init)"
	@echo "make build  - build the experimental snap"

init:
	@command -v "$(PYTHON)" >/dev/null || { echo "Python interpreter '$(PYTHON)' not found. Install Python 3.12 or run make init PYTHON=/path/to/python3.12"; exit 1; }
	@$(PYTHON) -c 'import sys; assert (3, 10) <= sys.version_info[:2] < (3, 14), "Kokoro ONNX 0.6.1 requires Python >=3.10,<3.14; use Python 3.12"'
	@if test -x "$(PY)" && ! $(PY) -c 'import sys; assert (3, 10) <= sys.version_info[:2] < (3, 14)' >/dev/null 2>&1; then echo "Existing .venv uses an unsupported Python; remove it with rm -rf .venv and retry"; exit 1; fi
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
