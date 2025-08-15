"""
WindAdjustment: A Python package for wind speed adjustment using meteorological data
"""

__version__ = "1.0.0"
__author__ = "Danilo Couto de Souza"
__email__ = "danilo.oceano@gmail.com"

# Import main classes for easy access
from .PointAdjustment import PointAdjustment
from .RegionAdjustment import RegionAdjustment
from .WindSpeedVisualizer import WindSpeedVisualizer

# Define what gets imported with "from windadjustment import *"
__all__ = [
    'PointAdjustment',
    'RegionAdjustment', 
    'WindSpeedVisualizer'
]