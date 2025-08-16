#!/bin/bash
uv sync --active --extra test
export PYTHONPATH=./src:./tests
#coverage run -m pytest tests
pytest tests/*.py -vv
