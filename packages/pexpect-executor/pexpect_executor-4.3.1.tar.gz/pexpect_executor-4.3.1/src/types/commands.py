#!/usr/bin/env python3

# Standard libraries
from typing import List

# Commands class, pylint: disable=too-few-public-methods
class Commands:

    # Members
    __arguments: List[str]

    # Constructor
    def __init__(self, arguments: List[str]) -> None:

        # Prepare arguments
        if isinstance(arguments, list):
            self.__arguments = arguments
        else: # pragma: no cover
            self.__arguments = []

    # Getter
    def get(self) -> str:

        # Variables
        command: List[str] = []

        # Prepare command
        for argument in self.__arguments:

            # Quoted argument
            if ' ' in argument:
                command += [f'\'{argument}\'']

            # Standard argument
            else:
                command += [argument]

        # Result
        return ' '.join(command)
