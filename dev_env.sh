#!/bin/bash

# set -o pipefail
# set -o errexit

## This script must be sourced!
if [ "x${BASH}" != "x/bin/bash" ] && [ "x${BASH}" != "x/usr/bin/bash" ]; then
    echo "Error: -- You're not using BASH, so this isn't going to work out between us.  Goodbye!"
    return 42 >/dev/null 2>&1 # Return if being sourced in wrong shell
    exit 42 # Couldn't return, so not being sourced exit instead
fi

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: -- You've not sourced me, so you have failed.  Quitting"
    exit 33
fi

rm -rf .ve || true

virtualenv -p python3.6 .ve

source .ve/bin/activate

pip install -r ./requirements/local.txt
pip install -e .

set +o pipefail
set +o errexit
echo "Done creating the environment"

