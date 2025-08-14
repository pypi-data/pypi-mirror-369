#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
pexpect-executor --down --space --enter -- gcil
pexpect-executor --down --space --enter \
  --mask 'private_password' -- gcil
pexpect-executor --down --space --enter \
  --mask 'private_password' \
  --mask 'secret_string' \
  --mask 'https://gitlab.com/gitlab-org/gitlab' \
  -- gcil
pexpect-executor --down --space --enter \
  --mask 'private_password' \
  --mask 'secret_string' \
  --mask 'https://gitlab.com/gitlab-org/gitlab' \
  -- gcil \
  | grep 'private_password\|secret_string\|gitlab.com' && exit 1 || true
