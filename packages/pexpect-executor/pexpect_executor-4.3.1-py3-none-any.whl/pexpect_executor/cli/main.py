#!/usr/bin/env python3

# Standard libraries
from argparse import (
    _ArgumentGroup,
    ArgumentParser,
    Namespace,
    RawTextHelpFormatter,
)
from os import environ
from shutil import get_terminal_size
from sys import exit as sys_exit

# Components
from ..features.actions import ActionsFeature
from ..lib.executor import Executor
from ..package.bundle import Bundle
from ..package.settings import Settings
from ..package.updates import Updates
from ..package.version import Version
from ..prints.colors import Colors
from ..system.platform import Platform
from .entrypoint import Entrypoint

# Constants
HELP_POSITION: int = 23

# Main, pylint: disable=too-many-branches,too-many-statements
def main() -> None:

    # Variables
    group: _ArgumentGroup
    result: Entrypoint.Result

    # Arguments creation
    parser: ArgumentParser = ArgumentParser(
        prog=Bundle.NAME,
        description=f'{Bundle.NAME}: {Bundle.DESCRIPTION}',
        add_help=False,
        formatter_class=lambda prog: RawTextHelpFormatter(
            prog,
            max_help_position=HELP_POSITION,
            width=min(
                120,
                get_terminal_size().columns - 2,
            ),
        ),
    )

    # Arguments internal definitions
    group = parser.add_argument_group('internal arguments')
    group.add_argument(
        '-h',
        '--help',
        dest='help',
        action='store_true',
        help='Show this help message',
    )
    group.add_argument(
        '--version',
        dest='version',
        action='store_true',
        help='Show the current version',
    )
    group.add_argument(
        '--no-color',
        dest='no_color',
        action='store_true',
        help=f'Disable colors outputs with \'{Bundle.ENV_NO_COLOR}=1\'\n'
        '(or default settings: [themes] > no_color)',
    )
    group.add_argument(
        '--update-check',
        dest='update_check',
        action='store_true',
        help='Check for newer package updates',
    )
    group.add_argument(
        '--settings',
        dest='settings',
        action='store_true',
        help='Show the current settings path and contents',
    )
    group.add_argument(
        '--set',
        dest='set',
        action='store',
        metavar=('GROUP', 'KEY', 'VAL'),
        nargs=3,
        help='Set settings specific \'VAL\' value to [GROUP] > KEY\n' \
             'or unset by using \'UNSET\' as \'VAL\'',
    )

    # Arguments configuration definitions
    group = parser.add_argument_group('configuration arguments')
    group.add_argument(
        '--delay-init',
        dest='delay_init',
        type=float,
        default=Executor.DELAY_INIT,
        help='Delay the initial action execution (in s, default: %(default)s)',
        metavar='SECS',
    )
    group.add_argument(
        '--delay-press',
        dest='delay_press',
        type=float,
        default=Executor.DELAY_PRESS,
        help='Delay the press actions execution (in s, default: %(default)s)',
        metavar='SECS',
    )
    group.add_argument(
        '--delay-prompt',
        dest='delay_prompt',
        type=float,
        default=Executor.DELAY_PROMPT,
        help='Delay the prompt actions execution (in s, default: %(default)s)',
        metavar='SECS',
    )
    group.add_argument(
        '--hold-prompt',
        dest='hold_prompt',
        action='store_true',
        help='Hold the prompt execution without a new line',
    )
    group.add_argument(
        '--host',
        dest='host',
        action='store',
        default=Executor.LABEL_HOST,
        help='Configure the host name (default: %(default)s' + ', env: ' +
        Bundle.ENV_HOST + ')',
    )
    group.add_argument(
        '--tool',
        dest='tool',
        action='store',
        default=Executor.LABEL_TOOL,
        help='Configure the tool name (default: %(default)s' + ', env: ' +
        Bundle.ENV_TOOL + ')',
    )
    group.add_argument(
        '--mask',
        dest='masks',
        action='append',
        help='Mask specific strings from console outputs (credentials for example)',
        metavar='STRINGS',
    )
    group.add_argument(
        '--workdir',
        dest='workdir',
        action='store',
        help='Use a specific working directory path',
    )

    # Arguments actions definitions
    group = parser.add_argument_group('actions arguments')
    group.add_argument(
        '--up',
        dest='actions',
        action='append_const',
        const=ActionsFeature.ActionKey(Executor.KEY_UP),
        help='Press the <UP> key',
    )
    group.add_argument(
        '--down',
        dest='actions',
        action='append_const',
        const=ActionsFeature.ActionKey(Executor.KEY_DOWN),
        help='Press the <DOWN> key',
    )
    group.add_argument(
        '--left',
        dest='actions',
        action='append_const',
        const=ActionsFeature.ActionKey(Executor.KEY_LEFT),
        help='Press the <LEFT> key',
    )
    group.add_argument(
        '--right',
        dest='actions',
        action='append_const',
        const=ActionsFeature.ActionKey(Executor.KEY_RIGHT),
        help='Press the <RIGHT> key',
    )
    group.add_argument(
        '--enter',
        dest='actions',
        action='append_const',
        const=ActionsFeature.ActionKey(Executor.KEY_ENTER),
        help='Press the <ENTER> key',
    )
    group.add_argument(
        '--space',
        dest='actions',
        action='append_const',
        const=ActionsFeature.ActionKey(Executor.KEY_SPACE),
        help='Press the <SPACE> key',
    )
    group.add_argument(
        '--press',
        dest='actions',
        action='append',
        type=ActionsFeature.ActionKey,
        help='Press the specified <KEY>',
        metavar='KEY',
    )
    group.add_argument(
        '--ctrl',
        dest='actions',
        action='append',
        type=ActionsFeature.ActionKeyControl,
        help='Press the specified Ctrl+<KEY>',
        metavar='KEY',
    )
    group.add_argument(
        '--read',
        dest='actions',
        action='append_const',
        const=ActionsFeature.ActionRead(),
        help='Read the buffered data output (forced)',
    )
    group.add_argument(
        '--wait',
        dest='actions',
        action='append',
        type=ActionsFeature.ActionWait,
        help='Wait the specified time (in s, example: 1.0)',
        metavar='SECS',
    )
    group.add_argument(
        '--finish',
        dest='actions',
        action='append_const',
        const=ActionsFeature.ActionFinish(),
        help='Finish the execution (forced)',
    )

    # Arguments positional definitions
    group = parser.add_argument_group('positional arguments')
    group.add_argument(
        '--',
        dest='double_dash',
        action='store_true',
        help='Positional arguments separator (recommended)',
    )
    group.add_argument(
        dest='command',
        nargs='*',
        help='Command arguments to execute (use -- to separate)',
    )

    # Arguments parser
    options: Namespace = parser.parse_args()

    # Help informations
    if options.help:
        print(' ')
        parser.print_help()
        print(' ')
        Platform.flush()
        sys_exit(0)

    # Instantiate settings
    settings: Settings = Settings(name=Bundle.NAME)

    # Prepare no_color
    if not options.no_color:
        if settings.has('themes', 'no_color'):
            options.no_color = settings.get_bool('themes', 'no_color')
        else:
            options.no_color = False
            settings.set_bool('themes', 'no_color', options.no_color)

    # Configure no_color
    if options.no_color:
        environ[Bundle.ENV_FORCE_COLOR] = '0'
        environ[Bundle.ENV_NO_COLOR] = '1'

    # Prepare colors
    Colors.prepare()

    # Settings setter
    if options.set:
        settings.set(options.set[0], options.set[1], options.set[2])
        settings.show()
        sys_exit(0)

    # Settings informations
    if options.settings:
        settings.show()
        sys_exit(0)

    # Instantiate updates
    updates: Updates = Updates(
        name=Bundle.PACKAGE,
        settings=settings,
    )

    # Version informations
    if options.version:
        print(
            f'{Bundle.NAME} {Version.get()} from {Version.path()} (python {Version.python()})'
        )
        Platform.flush()
        sys_exit(0)

    # Check for current updates
    if options.update_check:
        if not updates.check():
            updates.check(older=True)
        sys_exit(0)

    # CLI entrypoint
    result = Entrypoint.cli(options)

    # Check for daily updates
    if updates.enabled and updates.daily:
        updates.check()

    # Result
    if result in [
            Entrypoint.Result.SUCCESS,
            Entrypoint.Result.FINALIZE,
    ]:
        sys_exit(0)
    else:
        sys_exit(1)

# Entrypoint
if __name__ == '__main__': # pragma: no cover
    main()
