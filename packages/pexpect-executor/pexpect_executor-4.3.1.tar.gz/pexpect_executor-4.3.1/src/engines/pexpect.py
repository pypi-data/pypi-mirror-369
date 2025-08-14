#!/usr/bin/env python3

# Coverage
# pragma: linux cover file

# Standard libraries
from typing import Union

# Modules libraries
from pexpect import EOF, spawn, TIMEOUT # pylint: disable=import-error

# Components
from .base import Base

# Pexpect class
class Pexpect(Base):

    # Constructor
    def __init__(self, command: str) -> None: # pylint: disable=super-init-not-called

        # Spawn command
        self._child = spawn('sh', ['-c', command])

    # Read
    def _read(self) -> Union[bytes, str]:

        # Acquire output, pylint: disable=duplicate-code
        assert self._child is not None
        try:
            result = self._child.read_nonblocking(size=1024, timeout=1)
            assert isinstance(result, (bytes, str))
            return result
        except (AttributeError, EOF, TIMEOUT):
            pass

        # Empty output
        return ''
