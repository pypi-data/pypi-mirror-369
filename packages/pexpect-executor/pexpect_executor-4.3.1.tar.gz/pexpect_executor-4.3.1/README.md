# pexpect-executor

[![Release](https://img.shields.io/pypi/v/pexpect-executor?color=blue)](https://pypi.org/project/pexpect-executor)
[![Python](https://img.shields.io/pypi/pyversions/pexpect-executor?color=blue)](https://pypi.org/project/pexpect-executor)
[![Downloads](https://img.shields.io/pypi/dm/pexpect-executor?color=blue)](https://pypi.org/project/pexpect-executor)
[![License](https://img.shields.io/gitlab/license/RadianDevCore/tools/pexpect-executor?color=blue)](https://gitlab.com/RadianDevCore/tools/pexpect-executor/-/blob/main/LICENSE)
<br />
[![Build](https://gitlab.com/RadianDevCore/tools/pexpect-executor/badges/main/pipeline.svg)](https://gitlab.com/RadianDevCore/tools/pexpect-executor/-/commits/main/)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_pexpect-executor&metric=bugs)](https://sonarcloud.io/dashboard?id=RadianDevCore_pexpect-executor)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_pexpect-executor&metric=code_smells)](https://sonarcloud.io/dashboard?id=RadianDevCore_pexpect-executor)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_pexpect-executor&metric=coverage)](https://sonarcloud.io/dashboard?id=RadianDevCore_pexpect-executor)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_pexpect-executor&metric=ncloc)](https://sonarcloud.io/dashboard?id=RadianDevCore_pexpect-executor)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_pexpect-executor&metric=alert_status)](https://sonarcloud.io/dashboard?id=RadianDevCore_pexpect-executor)
<br />
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](https://commitizen-tools.github.io/commitizen/)
[![gcil](https://img.shields.io/badge/gcil-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/gcil)
[![pre-commit-crocodile](https://img.shields.io/badge/pre--commit--crocodile-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/pre-commit-crocodile)

Automate interactive CLI tools actions to create previews or tests in Python

**Documentation:** <https://radiandevcore.gitlab.io/tools/pexpect-executor>  
**Package:** <https://pypi.org/project/pexpect-executor/>

---

## Preview

![preview.svg](https://gitlab.com/RadianDevCore/tools/pexpect-executor/raw/4.3.1/docs/preview.svg)

---

## CLI examples

```bash
pexpect-executor --help
pexpect-executor --down --down --down --down --down --space --enter -- gcil -H -B
pexpect-executor --press a --press a --enter -- gcil
pexpect-executor --ctrl c -- gcil
```

---

<span class="page-break"></span>

## Python examples

```python
#!/usr/bin/env python3

# Modules libraries
from pexpect_executor import Executor

# Configure
Executor.configure(host='previews', tool='pexpect-executor')

# List
Executor('ls -la', workdir='/').\
    finish()

# More
Executor('ls -la | more -5', delay_press=0.5, workdir='/').\
    read().\
    press('s').\
    read().\
    press('s').\
    read().\
    press('b').\
    read().\
    press('b').\
    read().\
    press(' ').\
    read().\
    wait(1).\
    press(Executor.KEY_ENTER).\
    read().\
    wait(1).\
    press('q').\
    finish()

# Prompt
Executor('').\
    finish()
```

---

<span class="page-break"></span>

## Usage

<!-- prettier-ignore-start -->
<!-- readme-help-start -->

```yaml
usage: pexpect-executor [-h] [--version] [--no-color] [--update-check] [--settings] [--set GROUP KEY VAL]
                        [--delay-init SECS] [--delay-press SECS] [--delay-prompt SECS] [--hold-prompt] [--host HOST]
                        [--tool TOOL] [--mask STRINGS] [--workdir WORKDIR] [--up] [--down] [--left] [--right]
                        [--enter] [--space] [--press KEY] [--ctrl KEY] [--read] [--wait SECS] [--finish] [--]
                        [command ...]

pexpect-executor: Automate interactive CLI tools actions

internal arguments:
  -h, --help           # Show this help message
  --version            # Show the current version
  --no-color           # Disable colors outputs with 'NO_COLOR=1'
                       # (or default settings: [themes] > no_color)
  --update-check       # Check for newer package updates
  --settings           # Show the current settings path and contents
  --set GROUP KEY VAL  # Set settings specific 'VAL' value to [GROUP] > KEY
                       # or unset by using 'UNSET' as 'VAL'

configuration arguments:
  --delay-init SECS    # Delay the initial action execution (in s, default: 1.0)
  --delay-press SECS   # Delay the press actions execution (in s, default: 0.5)
  --delay-prompt SECS  # Delay the prompt actions execution (in s, default: 1.0)
  --hold-prompt        # Hold the prompt execution without a new line
  --host HOST          # Configure the host name (default: preview, env: EXECUTOR_HOST)
  --tool TOOL          # Configure the tool name (default: executor, env: EXECUTOR_TOOL)
  --mask STRINGS       # Mask specific strings from console outputs (credentials for example)
  --workdir WORKDIR    # Use a specific working directory path

actions arguments:
  --up                 # Press the <UP> key
  --down               # Press the <DOWN> key
  --left               # Press the <LEFT> key
  --right              # Press the <RIGHT> key
  --enter              # Press the <ENTER> key
  --space              # Press the <SPACE> key
  --press KEY          # Press the specified <KEY>
  --ctrl KEY           # Press the specified Ctrl+<KEY>
  --read               # Read the buffered data output (forced)
  --wait SECS          # Wait the specified time (in s, example: 1.0)
  --finish             # Finish the execution (forced)

positional arguments:
  --                   # Positional arguments separator (recommended)
  command              # Command arguments to execute (use -- to separate)
```

<!-- readme-help-stop -->
<!-- prettier-ignore-end -->

---

<span class="page-break"></span>

## Userspace available settings

`pexpect-executor` creates a `settings.ini` configuration file in a userspace folder.

For example, it allows to disable the automated updates daily check (`[updates] > enabled`)

The `settings.ini` file location and contents can be shown with the following command:

```bash
pexpect-executor --settings
```

---

## Supported systems

|     Systems      | Supported |
| :--------------: | :-------: |
|  Linux (shell)   |   **✓**   |
|  macOS (shell)   |   **?**   |
| Windows (shell)  |   **~**   |
| Android (Termux) |   **✓**   |

---

## Environment available configurations

`pexpect-executor` uses `colored` for colors outputs.

If colors of both outputs types do not match the terminal's theme,  
an environment variable `NO_COLOR=1` can be defined to disable colors.

---

<span class="page-break"></span>

## Dependencies

- [colored](https://pypi.org/project/colored/): Terminal colors and styles
- [pexpect](https://pypi.org/project/pexpect/): Interactive console applications controller
- [setuptools](https://pypi.org/project/setuptools/): Build and manage Python packages
- [update-checker](https://pypi.org/project/update-checker/): Check for package updates on PyPI
- [wexpect](https://pypi.org/project/wexpect/): Windows alternative of pexpect

---

## References

- [commitizen](https://pypi.org/project/commitizen/): Simple commit conventions for internet citizens
- [git-cliff](https://github.com/orhun/git-cliff): CHANGELOG generator
- [gitlab-release](https://pypi.org/project/gitlab-release/): Utility for publishing on GitLab
- [gcil](https://radiandevcore.gitlab.io/tools/gcil): Launch .gitlab-ci.yml jobs locally
- [mkdocs](https://www.mkdocs.org/): Project documentation with Markdown
- [mkdocs-coverage](https://pawamoy.github.io/mkdocs-coverage/): Coverage plugin for mkdocs documentation
- [mkdocs-exporter](https://adrienbrignon.github.io/mkdocs-exporter/): Exporter plugin for mkdocs documentation
- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/): Material theme for mkdocs documentation
- [mypy](https://pypi.org/project/mypy/): Optional static typing for Python
- [pre-commit](https://pre-commit.com/): A framework for managing and maintaining pre-commit hooks
- [pre-commit-crocodile](https://radiandevcore.gitlab.io/tools/pre-commit-crocodile): Git hooks intended for developers using pre-commit
- [PyPI](https://pypi.org/): The Python Package Index
- [termtosvg](https://pypi.org/project/termtosvg/): Record terminal sessions as SVG animations
- [twine](https://pypi.org/project/twine/): Utility for publishing on PyPI
