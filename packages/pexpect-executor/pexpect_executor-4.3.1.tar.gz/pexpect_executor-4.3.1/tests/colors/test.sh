#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
pexpect-executor echo 'Text with spaces'
pexpect-executor --no-color echo 'Text with spaces'
pexpect-executor echo 'Text with spaces'
pexpect-executor --no-color echo 'Text with spaces'
pexpect-executor --set themes no_color 1
pexpect-executor echo 'Text with spaces'
pexpect-executor --set themes no_color 0
pexpect-executor echo 'Text with spaces'
pexpect-executor --set themes no_color UNSET
pexpect-executor echo 'Text with spaces'
FORCE_COLOR=1 pexpect-executor echo 'Text with spaces'
FORCE_COLOR=0 pexpect-executor echo 'Text with spaces'
NO_COLOR=1 pexpect-executor echo 'Text with spaces'
