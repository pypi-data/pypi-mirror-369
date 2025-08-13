"""
Simple Botmaker - A package that simplifies the creation of bots that react to the screen in real time.

This package provides high-level and low-level functions for screen capture, image recognition,
OCR, and automated interaction with Windows applications.

Only works on Windows.
"""

from .globals import Globals, SETTINGS
from .high_level_functions import *
from .low_level_functions import *

__version__ = "1.0.0"
__author__ = "Simple Botmaker Team"
__description__ = "A package that simplifies the creation of bots that react to the screen in real time"

# Make commonly used functions available at package level
__all__ = [
    'Globals', 'SETTINGS',
    'GetPixelColour', 'FindImageInRegion', 'GetBar', 'GetBarByColour', 
    'GetValue', 'GetText', 'Click', 'MouseMove', 'FocusedClick',
    'SaveObject', 'LoadObject', 'SetRegions',
    'TakeRegionScreenshot', 'ConvertToGrayScale', 'ConvertToThreshold',
    'LoadFrameFromPath', 'GetScreenResolution', 'GetWindowByName',
    'Capture2Text', 'ensure_capture2text_installed'
]
