#!/bin/bash
set -o errexit

echo 'Building figtag PEX binary...'

rm -rf .artifacts

echo 'Downloading PIP packages ...'
pip download -q -r requirements/base.txt -d .artifacts

echo 'Building figtag PEX binary...'
pex . \
    --python=python3 \
    -o dist/figtag \
    -r requirements/base.txt \
    --disable-cache \
    -f ./.artifacts \
    -e figtag.manage:main \
    --validate-entry-point

rm -rf .artifacts
