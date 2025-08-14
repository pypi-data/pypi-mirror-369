#!/usr/bin/env python3

# Bundle class, pylint: disable=too-few-public-methods
class Bundle:

    # Names
    NAME: str = 'pexpect-executor'

    # Packages
    PACKAGE: str = 'pexpect-executor'

    # Details
    DESCRIPTION: str = 'Automate interactive CLI tools actions'

    # Sources
    REPOSITORY: str = 'https://gitlab.com/RadianDevCore/tools/pexpect-executor'

    # Releases
    RELEASE_FIRST_TIMESTAMP: int = 1579337311

    # Environment
    ENV_DEBUG_UPDATES_DAILY: str = 'DEBUG_UPDATES_DAILY'
    ENV_DEBUG_UPDATES_DISABLE: str = 'DEBUG_UPDATES_DISABLE'
    ENV_DEBUG_UPDATES_FAKE: str = 'DEBUG_UPDATES_FAKE'
    ENV_DEBUG_UPDATES_OFFLINE: str = 'DEBUG_UPDATES_OFFLINE'
    ENV_DEBUG_VERSION_FAKE: str = 'DEBUG_VERSION_FAKE'
    ENV_ENGINE: str = 'EXECUTOR_ENGINE'
    ENV_FORCE_COLOR: str = 'FORCE_COLOR'
    ENV_HOST: str = 'EXECUTOR_HOST'
    ENV_NO_COLOR: str = 'NO_COLOR'
    ENV_TOOL: str = 'EXECUTOR_TOOL'
