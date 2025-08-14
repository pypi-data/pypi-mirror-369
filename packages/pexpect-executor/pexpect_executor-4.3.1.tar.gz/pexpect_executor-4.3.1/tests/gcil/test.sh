#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
pexpect-executor --down --space --enter -- gcil
pexpect-executor --press a --press a --enter -- gcil
pexpect-executor --wait 2 --enter -- gcil
pexpect-executor --ctrl c -- gcil
