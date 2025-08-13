"""
Custom Interpreter module for Simple Botmaker.

This module provides a secure interpreter for running user scripts with restricted access
to only allowed functions from the Simple Botmaker package.
"""

from .definitions import *
from .interpreter import *

__all__ = ['Globals', 'SETTINGS', 'static_check']
