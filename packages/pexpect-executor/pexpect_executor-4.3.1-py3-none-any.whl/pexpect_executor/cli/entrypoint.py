#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from enum import Enum

# Components
from ..features.actions import ActionsFeature
from ..types.commands import Commands

# Entrypoint class, pylint: disable=too-few-public-methods
class Entrypoint:

    # Enumerations
    Result = Enum('Result', [
        'SUCCESS',
        'FINALIZE',
        'ERROR',
        'CRITICAL',
    ])

    # CLI, pylint: disable=too-many-branches,too-many-locals,too-many-return-statements
    @staticmethod
    def cli(options: Namespace) -> Result:

        # Variables
        result: Entrypoint.Result = Entrypoint.Result.ERROR

        # Prepare command
        command: str = Commands(options.command).get()

        # Action executor
        if ActionsFeature(command, options).run():
            result = Entrypoint.Result.SUCCESS

        # Result
        return result
