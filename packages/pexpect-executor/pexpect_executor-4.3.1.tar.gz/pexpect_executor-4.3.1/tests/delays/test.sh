#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
pexpect-executor --delay-prompt 2 && exit 1 || true
timeout -sINT 10 pexpect-executor --delay-press 0.2 --press a --press b --press c cat && exit 1 || true
timeout -sINT 3 pexpect-executor --delay-init 5 cat && exit 1 || true
timeout -sINT 5 pexpect-executor cat && exit 1 || true
timeout -sINT 3 pexpect-executor --wait 5 echo hi && exit 1 || true
timeout -sINT 4 pexpect-executor --wait 5 echo hi && exit 1 || true
