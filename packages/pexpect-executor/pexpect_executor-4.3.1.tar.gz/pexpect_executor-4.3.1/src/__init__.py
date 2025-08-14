# Components
from .lib.executor import Executor
from .package.version import Version

# Version
__version__ = Version.get()
