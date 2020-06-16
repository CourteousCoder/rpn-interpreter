#!/usr/bin/env bash
export PIPENV_VENV_IN_PROJECT=true
pipenv install --dev && pipenv run build $(pipenv --venv) && echo "Successfully compiled to '$PWD/dist/rpn'"
