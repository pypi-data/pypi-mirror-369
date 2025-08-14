#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
pexpect-executor && exit 1 || true
pexpect-executor --enter --read && exit 1 || true
pexpect-executor --hold-prompt && exit 1 || true
