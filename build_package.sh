#!/bin/bash

set -o pipefail
set -o errexit

cd "`dirname "$0"`"

deactivate 2>/dev/null || true

rm -rf ./dist
rm -rf ./.tox
rm -rf ./.eggs
rm -rf ./.pytest_cache
rm -rf ./.mypy_cache

# Setup virtual environment
export venv_dir=`mktemp -d env_figtag_XXXXX -p /tmp`
rm -rf $venv_dir

cleanup()
{
    deactivate 2> /dev/null || true
    rm -rf $venv_dir
    echo "Cleanup..."
}

export -f cleanup
trap 'cleanup' INT QUIT TERM ERR EXIT

virtualenv -p python3.6 $venv_dir
source $venv_dir/bin/activate

# Set up requirements
$venv_dir/bin/python $venv_dir/bin/pip install \
    -q -r requirements/base.txt -e .

# Build our own distribution
$venv_dir/bin/python setup.py -q sdist

