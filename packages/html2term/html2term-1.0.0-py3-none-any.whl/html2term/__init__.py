__version__ = "1.0.0"

from .core import convert, printc, _enable_windows_support

_enable_windows_support()

__all__ = ['convert', 'printc']
