"""
structunits: A Python unit conversion framework with operator overloading.

This package provides a robust system for handling units and unit conversions
with full operator overloading support. It's inspired by a C# framework and
implemented in Python.
"""

__version__ = "0.1.0"

# Re-export commonly used classes and enums for convenient star-imports
from .flt import FLT
from .unit import Unit
from .unit_type import UnitType
from .result import Result
from .utilities import Utilities

# Re-export specific units package symbols
from . import specific_units

# Optionally re-export specific unit classes at top level for convenience
from .specific_units import (
    Length, LengthUnit,
    LengthCubed, LengthCubedUnit,
    LengthToThe4th, LengthToThe4thUnit,
    Force, ForceUnit,
    ForcePerLength, ForcePerLengthUnit,
    Moment, MomentUnit,
    Stress, StressUnit,
    Unitless, Undefined,
)

__all__ = [
    # Core
    "FLT",
    "Unit",
    "UnitType",
    "Result",
    "Utilities",
    # Subpackage
    "specific_units",
    # Specific unit classes (re-exported)
    "Length",
    "LengthUnit",
    "LengthCubed",
    "LengthCubedUnit",
    "LengthToThe4th",
    "LengthToThe4thUnit",
    "Force",
    "ForceUnit",
    "ForcePerLength",
    "ForcePerLengthUnit",
    "Moment",
    "MomentUnit",
    "Stress",
    "StressUnit",
    "Unitless",
    "Undefined",
]
