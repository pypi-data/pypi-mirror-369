#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
pexpect-executor --settings
! type sudo >/dev/null 2>&1 || sudo -E env PYTHONPATH="${PYTHONPATH}" pexpect-executor --settings
pexpect-executor --set && exit 1 || true
pexpect-executor --set GROUP && exit 1 || true
pexpect-executor --set GROUP KEY && exit 1 || true
pexpect-executor --set package test 1
pexpect-executor --set package test 0
pexpect-executor --set package test UNSET
pexpect-executor --set updates enabled NaN
pexpect-executor --version
pexpect-executor --set updates enabled UNSET
