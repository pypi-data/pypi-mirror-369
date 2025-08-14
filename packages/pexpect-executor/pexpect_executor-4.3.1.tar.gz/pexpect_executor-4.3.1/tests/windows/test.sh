#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Detect Windows host
if [ "${OSTYPE}" = 'msys' ] || [ "${OSTYPE}" = 'win32' ]; then
  echo 'INFO: Test "windows" running on a Windows host'

# Detect Wine support
elif type wine >/dev/null 2>&1 && wine python --version >/dev/null 2>&1; then
  echo 'INFO: Test "windows" running in a Wine Python environment'
  if wine pexpect-executor --version >/dev/null 2>&1; then
    alias pexpect-executor='wine pexpect-executor'
  fi

# Unsupported host
else
  echo 'INFO: Test "windows" was ignored as it is not supported on this host'
  exit 0
fi

# Configure helpers
unstable() {
  (
    set +x
    echo ' '
    printf " \033[1;31mWARNING:\033[1;33m Result unstable (${*})...\033[0m"
    echo ' '
    echo ' '
    sleep 3
  )
}

# Configure tests
set -ex

# Run tests (arguments)
pexpect-executor --help
pexpect-executor --version
pexpect-executor </dev/null && exit 1 || true

# Run tests (Pexpect_Popen engine)
EXECUTOR_ENGINE=pexpect_popen pexpect-executor whoami
EXECUTOR_ENGINE=pexpect_popen pexpect-executor whoami-missing && exit 1 || true
EXECUTOR_ENGINE=pexpect_popen pexpect-executor --enter whoami && exit 1 || true
EXECUTOR_ENGINE=pexpect_popen pexpect-executor --finish whoami
EXECUTOR_ENGINE=pexpect_popen pexpect-executor python exit-test.py 0
EXECUTOR_ENGINE=pexpect_popen pexpect-executor python exit-test.py 1 1 && exit 1 || true
EXECUTOR_ENGINE=pexpect_popen pexpect-executor python slow-test.py

# Run tests (Wexpect engine)
EXECUTOR_ENGINE=wexpect pexpect-executor whoami
EXECUTOR_ENGINE=wexpect pexpect-executor whoami-missing && exit 1 || true
EXECUTOR_ENGINE=wexpect pexpect-executor --enter whoami
EXECUTOR_ENGINE=wexpect pexpect-executor --finish whoami
EXECUTOR_ENGINE=wexpect pexpect-executor python exit-test.py 0
EXECUTOR_ENGINE=wexpect pexpect-executor python exit-test.py 1 1 && unstable "${LINENO}:" exit 1 || true # unstable: Wine
EXECUTOR_ENGINE=wexpect pexpect-executor python slow-test.py

# Run tests (Unknown engine)
EXECUTOR_ENGINE=unknown-engine pexpect-executor whoami && exit 1 || true
