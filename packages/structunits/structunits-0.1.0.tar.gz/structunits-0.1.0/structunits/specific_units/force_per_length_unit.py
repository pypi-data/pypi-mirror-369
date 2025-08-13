from typing import ClassVar
from structunits.unit import Unit
from structunits.constants import (
    INCHES_PER_FOOT, INCHES_PER_METER,
    MILLIMETERS_PER_METER, CENTIMETERS_PER_METER,
    POUNDS_PER_KIP, NEWTONS_PER_KILONEWTON, KIPS_PER_KILONEWTON
)


class ForcePerLengthUnit(Unit):
    """Unit for force per length measurements (distributed load)"""

    # Define class variables with type hints for autocomplete
    POUND_PER_INCH: ClassVar['ForcePerLengthUnit']
    POUND_PER_FOOT: ClassVar['ForcePerLengthUnit']
    KIP_PER_INCH: ClassVar['ForcePerLengthUnit']
    KIP_PER_FOOT: ClassVar['ForcePerLengthUnit']
    NEWTON_PER_METER: ClassVar['ForcePerLengthUnit']
    KILONEWTON_PER_METER: ClassVar['ForcePerLengthUnit']
    NEWTON_PER_MILLIMETER: ClassVar['ForcePerLengthUnit']
    KILONEWTON_PER_MILLIMETER: ClassVar['ForcePerLengthUnit']
    NEWTON_PER_CENTIMETER: ClassVar['ForcePerLengthUnit']
    KILONEWTON_PER_CENTIMETER: ClassVar['ForcePerLengthUnit']

    def __init__(self, symbol: str, name: str, conversion_factor: float):
        """
        Initialize a force per length unit.

        Args:
            symbol: Symbol representing the unit
            name: Full name of the unit
            conversion_factor: Conversion factor to standard unit (kips/inch)
        """
        super().__init__(symbol, name)
        self._conversion_factor = conversion_factor

    def get_conversion_factor(self) -> float:
        """
        Get the conversion factor to the standard unit (kips/inch).

        Returns:
            Conversion factor to kips/inch
        """
        return self._conversion_factor


# Define standard force per length units
ForcePerLengthUnit.POUND_PER_INCH = ForcePerLengthUnit(
    "lb/in", "pound per inch", 1.0 / POUNDS_PER_KIP)
ForcePerLengthUnit.POUND_PER_FOOT = ForcePerLengthUnit(
    "lb/ft", "pound per foot", 1.0 / POUNDS_PER_KIP / INCHES_PER_FOOT)
ForcePerLengthUnit.KIP_PER_INCH = ForcePerLengthUnit(
    "k/in", "kip per inch", 1.0)
ForcePerLengthUnit.KIP_PER_FOOT = ForcePerLengthUnit(
    "k/ft", "kip per foot", 1.0 / INCHES_PER_FOOT)
ForcePerLengthUnit.NEWTON_PER_METER = ForcePerLengthUnit(
    "N/m", "newton per meter",
    KIPS_PER_KILONEWTON / NEWTONS_PER_KILONEWTON / INCHES_PER_METER)
ForcePerLengthUnit.KILONEWTON_PER_METER = ForcePerLengthUnit(
    "kN/m", "kilonewton per meter",
    KIPS_PER_KILONEWTON / INCHES_PER_METER)
ForcePerLengthUnit.NEWTON_PER_MILLIMETER = ForcePerLengthUnit(
    "N/mm", "newton per millimeter",
    KIPS_PER_KILONEWTON / NEWTONS_PER_KILONEWTON / INCHES_PER_METER * MILLIMETERS_PER_METER)
ForcePerLengthUnit.KILONEWTON_PER_MILLIMETER = ForcePerLengthUnit(
    "kN/mm", "kilonewton per millimeter",
    KIPS_PER_KILONEWTON / INCHES_PER_METER * MILLIMETERS_PER_METER)
ForcePerLengthUnit.NEWTON_PER_CENTIMETER = ForcePerLengthUnit(
    "N/cm", "newton per centimeter",
    KIPS_PER_KILONEWTON / NEWTONS_PER_KILONEWTON / INCHES_PER_METER * CENTIMETERS_PER_METER)
ForcePerLengthUnit.KILONEWTON_PER_CENTIMETER = ForcePerLengthUnit(
    "kN/cm", "kilonewton per centimeter",
    KIPS_PER_KILONEWTON / INCHES_PER_METER * CENTIMETERS_PER_METER)
