#!/bin/bash

set -o pipefail
set -o errexit

## This script must be sourced!
if [ "x${BASH}" != "x/bin/bash" ] && [ "x${BASH}" != "x/usr/bin/bash" ]; then
    echo "Error: -- This file must be sourced" >&2
    return 2 >/dev/null 2>&1 # Return if being sourced in wrong shell
    exit 2 # Couldn't return, so not being sourced exit instead
fi

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: -- File must be sourced" >&2
    exit 2
fi

rm -rf .ve || true

virtualenv -p python3.6 .ve

source .ve/bin/activate

pip install -r ./requirements/local.txt
pip install -e .

set +o pipefail
set +o errexit
echo "Done creating the environment"

