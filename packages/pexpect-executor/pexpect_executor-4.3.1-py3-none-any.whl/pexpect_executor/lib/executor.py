#!/usr/bin/env python3

# Standard libraries
from errno import ENOENT
from getpass import getuser
from os import chdir, environ
from time import sleep
from typing import List, Optional

# Components
from ..engines.engine import Engine
from ..package.bundle import Bundle
from ..prints.colors import Colors
from ..system.platform import Platform

# Executor
class Executor:

    # Key constants (arrows)
    KEY_UP: str = '\033[A'
    KEY_DOWN: str = '\033[B'
    KEY_LEFT: str = '\033[D'
    KEY_RIGHT: str = '\033[C'

    # Key constants (actions)
    KEY_BACKSPACE: str = '\b'
    KEY_DELETE: str = '\033[3~'
    KEY_END: str = '\033[F'
    KEY_END_2: str = '\033[4~'
    KEY_ENTER: str = '\r'
    KEY_ESC: str = '\033'
    KEY_HOME: str = '\033[H'
    KEY_HOME_2: str = '\033[1~'
    KEY_INSERT: str = '\033[2~'
    KEY_PAGEUP: str = '\033[5~'
    KEY_PAGEDOWN: str = '\033[6~'
    KEY_MACRO: str = '\033[M'
    KEY_PAUSE: str = '\033[P'
    KEY_SPACE: str = ' '
    KEY_TAB: str = '\t'

    # Key constants (Ctrl+?)
    KEY_CTRL_A: str = '\x01'
    KEY_CTRL_B: str = '\x02'
    KEY_CTRL_C: str = '\x03'
    KEY_CTRL_D: str = '\x04'
    KEY_CTRL_E: str = '\x05'
    KEY_CTRL_F: str = '\x06'
    KEY_CTRL_G: str = '\x07'
    KEY_CTRL_H: str = '\x08'
    KEY_CTRL_I: str = '\x09'
    KEY_CTRL_J: str = '\x0A'
    KEY_CTRL_K: str = '\x0B'
    KEY_CTRL_L: str = '\x0C'
    KEY_CTRL_M: str = '\x0D'
    KEY_CTRL_N: str = '\x0E'
    KEY_CTRL_O: str = '\x0F'
    KEY_CTRL_P: str = '\x10'
    KEY_CTRL_Q: str = '\x11'
    KEY_CTRL_R: str = '\x12'
    KEY_CTRL_S: str = '\x13'
    KEY_CTRL_T: str = '\x14'
    KEY_CTRL_U: str = '\x15'
    KEY_CTRL_V: str = '\x16'
    KEY_CTRL_W: str = '\x17'
    KEY_CTRL_X: str = '\x18'
    KEY_CTRL_Y: str = '\x19'
    KEY_CTRL_Z: str = '\x1A'

    # Key constants (F?)
    KEY_F1: str = '\033[[A'
    KEY_F2: str = '\033[[B'
    KEY_F3: str = '\033[[C'
    KEY_F4: str = '\033[[D'
    KEY_F5: str = '\033[[E'
    KEY_F6: str = '\033[17~'
    KEY_F7: str = '\033[18~'
    KEY_F8: str = '\033[19~'
    KEY_F9: str = '\033[20~'
    KEY_F10: str = '\033[21~'
    KEY_F11: str = '\033[23~'
    KEY_F12: str = '\033[24~'

    # Delays
    DELAY_INIT: float = 1.0
    DELAY_PRESS: float = 0.5
    DELAY_PROMPT: float = 1.0

    # Labels
    LABEL_HOST: str = 'preview'
    LABEL_TOOL: str = 'executor'

    # Members
    __delay_init: float
    __delay_press: float
    __delay_prompt: float
    __engine: Optional[Engine]
    __host: str = environ[Bundle.ENV_HOST] if Bundle.ENV_HOST in environ else LABEL_HOST
    __masks: List[str] = []
    __tool: str = environ[Bundle.ENV_TOOL] if Bundle.ENV_TOOL in environ else LABEL_TOOL

    # Constructor, pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        command: str = '',
        delay_init: float = DELAY_INIT,
        delay_press: float = DELAY_PRESS,
        delay_prompt: float = DELAY_PROMPT,
        hold_prompt: bool = False,
        workdir: str = '',
    ) -> None:

        # Prepare delays
        self.__delay_init = float(delay_init)
        self.__delay_press = float(delay_press)
        self.__delay_prompt = float(delay_prompt)

        # Prepare workdir
        if workdir:
            self.__prompt(f'cd {workdir}', hold_prompt=hold_prompt)
            chdir(workdir)

        # Prepare members
        self.__engine = None

        # Prepare command
        self.__prompt(command, hold_prompt=hold_prompt)
        if command:

            # Spawn command
            self.__engine = Engine(command)

            # Delay executor initialization
            if self.__delay_init > 0.0:
                Executor.sleep(self.__delay_init)
                self.read()

    # Configure
    @staticmethod
    def configure(
        host: str = LABEL_HOST,
        tool: str = LABEL_TOOL,
        masks: Optional[List[str]] = None,
        strips: Optional[List[str]] = None,
    ) -> None:

        # Prepare host
        Executor.__host = host

        # Deprecate strips
        if strips: # pragma: no cover
            raise SystemError('Parameter "strips" is deprecated, use "masks" instead')

        # Prepare masks
        if masks:
            Executor.__masks = masks
        else:
            Executor.__masks = []

        # Prepare tool
        Executor.__tool = tool

        # Prepare colors
        Colors.prepare()

    # Control key, pylint: disable=no-self-use
    def __control_key(self, key: str) -> bytes:

        # Acquire key value
        key = key.lower()
        try:
            value = ord(key)
        except TypeError:
            value = 0

        # Handle alphabetical key
        if 97 <= value <= 122:
            value = value - ord('a') + 1
            return bytes([value])

        # List specific keys
        mappings = {
            '@': 0,
            '`': 0,
            '[': 27,
            '{': 27,
            '\\': 28,
            '|': 28,
            ']': 29,
            '}': 29,
            '^': 30,
            '~': 30,
            '_': 31,
            '?': 127
        }

        # Handle specific keys
        if key in mappings:
            return bytes([mappings[key]])

        # Unknown fallback
        return bytes()

    # Prompt
    def __prompt(self, command: str, hold_prompt: bool = False) -> None:

        # Display prompt
        print(
            f'{Colors.GREEN_THIN}{getuser()}{Colors.RESET}'
            f'@{Colors.RED_THIN}{self.__host}{Colors.RESET}'
            f':{Colors.YELLOW_THIN}~/{self.__tool}{Colors.RESET}$ ', end='')
        Platform.flush()

        # Delay prompt
        Executor.sleep(self.__delay_prompt)

        # Display command
        if command:
            print(f'{command} ', end='')
            Platform.flush()
            Executor.sleep(self.__delay_prompt)
            print(' ')
            Platform.flush()

        # Return prompt
        elif not hold_prompt:
            print(' ')
            Platform.flush()

    # Press
    def press(self, key: str, control: bool = False) -> 'Executor':

        # Execution check
        if not self.__engine:
            return self

        # Delay press
        Executor.sleep(self.__delay_press)

        # Press Ctrl+key
        if control:
            self.__engine.send(self.__control_key(key))

        # Press key
        else:
            self.__engine.send(key)

        # Result
        return self

    # Read
    def read(self) -> 'Executor':

        # Execution check
        if not self.__engine:
            return self

        # Read stream
        self.__engine.read(Executor.__masks)

        # Result
        return self

    # Wait
    def wait(self, delay: float) -> 'Executor':

        # Delay execution
        Executor.sleep(delay)

        # Result
        return self

    # Finish
    def finish(self, force: bool = False) -> int:

        # Execution check
        if not self.__engine:
            return ENOENT

        # Read and wait execution
        if not force:
            try:
                while self.__engine.isalive():
                    self.read()
            except KeyboardInterrupt:
                pass

        # Terminate process
        self.__engine.terminate(force=force)

        # Result
        return self.__engine.status()

    # Sleep
    @staticmethod
    def sleep(delay: float) -> None:

        # Delay execution
        sleep(delay)
