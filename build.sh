#!/usr/bin/env bash
export PIPENV_VENV_IN_PROJECT=true
pipenv install && pipenv run build $(pipenv --venv) && echo "Successfully compiled to './dist/rpn'"