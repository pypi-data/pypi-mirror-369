#!/usr/bin/env python3

# Standard libraries
from typing import Any, List, Optional, Union

# Components
from ..system.platform import Platform

# Base class
class Base:

    # Members
    _child: Optional[Any] = None

    # Constructor
    def __init__(self, command: str) -> None:

        # Virtual method
        raise NotImplementedError() # pragma: no cover

    # Read
    def _read(self) -> Union[bytes, List[Union[bytes, str]], str]:

        # Virtual method
        raise NotImplementedError() # pragma: no cover

    # Is alive
    def isalive(self) -> bool:

        # Result
        assert self._child is not None
        return bool(self._child.isalive())

    # Read
    def read(self, masks: Optional[List[str]] = None) -> None:

        # Read stream
        while True:

            # Acquire output
            output = self._read()

            # Interrupted stream
            if not output:
                break

            # Print stream
            if isinstance(output, (bytes, str)):
                if isinstance(output, bytes):
                    output = output.decode('utf-8', errors='ignore')
                output = output.replace('\x1b[6n', '')
                if masks:
                    for mask in masks:
                        output = output.replace(mask, '')
                print(output, end='')
                Platform.flush()

            # Lines lines
            elif isinstance(output, list): # pragma: no cover
                for line in output:
                    if isinstance(line, bytes):
                        line = line.decode('utf-8', errors='ignore')
                    line = line.replace('\x1b[6n', '')
                    if masks:
                        for mask in masks:
                            line = line.replace(mask, '')
                    print(line)
                Platform.flush()

    # Send
    def send(self, key: Union[bytes, str]) -> None:

        # Send key
        assert self._child is not None
        self._child.send(key)

    # Status
    def status(self) -> int:

        # Fallback status
        assert self._child is not None
        if self._child.exitstatus is None:
            return 1

        # Process status
        return int(self._child.exitstatus)

    # Terminate
    def terminate(self, force: bool = False) -> None:

        # Terminate process
        assert self._child is not None
        self._child.terminate(force=force)
