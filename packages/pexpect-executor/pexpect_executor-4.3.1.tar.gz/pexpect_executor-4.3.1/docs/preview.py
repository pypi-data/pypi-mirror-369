#!/usr/bin/env python3

# Standard libraries
from os import environ

# Modules libraries, pylint: disable=import-error
from pexpect_executor import Executor

# Terminal
environ['PROMPT_TOOLKIT_NO_CPR'] = '1'

# Configure
Executor.configure(
    host='previews',
    tool='pexpect-executor',
)

# List
Executor(
    'pexpect-executor --space --down --down --space --press a --press a --enter -- gcil'
).\
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
Executor(delay_prompt=2.0, hold_prompt=True)
