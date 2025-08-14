#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
pexpect-executor --enter whoami
pexpect-executor --ctrl c whoami
pexpect-executor --up --down --left --right --enter --enter --finish cat && exit 1 || true
timeout -sINT 6 pexpect-executor --ctrl '~' cat && exit 1 || true
timeout -sINT 6 pexpect-executor --ctrl '*' cat && exit 1 || true
timeout -sINT 6 pexpect-executor --ctrl 'key' cat && exit 1 || true
