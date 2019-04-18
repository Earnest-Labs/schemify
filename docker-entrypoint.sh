#!/usr/bin/env bash
source ~/.pyenv/bin/init
source ./require_venv
export PYTHONPATH=$(pwd)
echo $PYTHONPATH
exec "$@"
