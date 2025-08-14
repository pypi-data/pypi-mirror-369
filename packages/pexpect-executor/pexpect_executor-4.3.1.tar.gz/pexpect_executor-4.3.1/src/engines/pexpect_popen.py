#!/usr/bin/env python3

# Coverage
# pragma: windows cover file

# Standard libraries
from signal import SIGTERM
from typing import Union

# Modules libraries
from pexpect import EOF, TIMEOUT # pylint: disable=import-error
from pexpect.popen_spawn import PopenSpawn # pylint: disable=import-error

# Components
from .base import Base

# PexpectPopen class
class PexpectPopen(Base):

    # Constructor
    def __init__(self, command: str) -> None: # pylint: disable=super-init-not-called

        # Spawn command
        self._child = PopenSpawn(command)

    # Read
    def _read(self) -> Union[bytes, str]:

        # Acquire output, pylint: disable=duplicate-code
        assert self._child is not None
        try:
            result = self._child.read_nonblocking(size=1024, timeout=1)
            assert isinstance(result, (bytes, str))
            return result
        except (EOF, TIMEOUT):
            pass

        # Empty output
        return ''

    # Is alive
    def isalive(self) -> bool:

        # Result
        assert self._child is not None
        return not self._child.terminated

    # Terminate
    def terminate(self, force: bool = False) -> None:

        # Terminate process
        assert self._child is not None
        if force:
            try:
                self._child.kill(sig=SIGTERM)
            except PermissionError: # pragma: no cover
                pass

        # Wait process
        self._child.wait()
