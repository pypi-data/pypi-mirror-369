#!/usr/bin/env python3

# Coverage
# pragma: windows cover file

# Standard libraries
# from os import environ
from typing import List, Union

# Modules libraries
# environ['WEXPECT_SPAWN_CLASS'] = 'SpawnPipe'
from wexpect import EOF, spawn, TIMEOUT # pylint: disable=import-error

# Components
from .base import Base

# Wexpect class
class Wexpect(Base):

    # Constructor
    def __init__(self, command: str) -> None: # pylint: disable=super-init-not-called

        # Spawn command
        self._child = spawn(command)

        # Acquire initial output
        assert self._child is not None
        try:
            self._child.expect(EOF, timeout=0)
        except TIMEOUT: # pragma: no cover
            pass

        # Configure timeout
        self._child.timeout = 1

    # Read
    def _read(self) -> Union[bytes, List[Union[bytes, str]], str]:

        # Acquire output
        assert self._child is not None
        try:
            output = self._child.read_nonblocking(size=1024)
            if self._child.before: # pragma: no cover
                output = self._child.before + output
        except EOF:
            output = self._child.before
        except TIMEOUT: # pragma: no cover
            output = self._child.before

        # Handle output
        if output: # pragma: no cover

            # Stream line
            assert isinstance(output, (bytes, str))
            if '\n' in output:
                return output

            # Adapt lines
            length = 80
            return [output[i:i + length] for i in range(0, len(output), length)]

        # Empty output
        return []

    # Send
    def send(self, key: Union[bytes, str]) -> None:

        # Send key
        assert self._child is not None
        try:
            self._child.send(key)
        except EOF:
            pass

    # Status
    def status(self) -> int:

        # Process terminated
        assert self._child is not None
        if self._child.exitstatus is None:
            return 0 if self._child.flag_eof else 1

        # Process status
        return int(self._child.exitstatus) # pragma: no cover

    # Terminate
    def terminate(self, force: bool = False) -> None:

        # Terminate process
        if force:
            assert self._child is not None
            self._child.terminate()

        # Wait process
        else:
            assert self._child is not None
            self._child.wait()
