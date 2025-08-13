from typing import ClassVar
from structunits.unit import Unit
from structunits.constants import INCHES_PER_FOOT, INCHES_PER_METER, MILLIMETERS_PER_METER, CENTIMETERS_PER_METER


class LengthUnit(Unit):
    """Unit for length measurements"""

    # Define class variables with type hints for autocomplete
    INCH: ClassVar['LengthUnit']
    FOOT: ClassVar['LengthUnit']
    MILLIMETER: ClassVar['LengthUnit']
    METER: ClassVar['LengthUnit']
    CENTIMETER: ClassVar['LengthUnit']

    def __init__(self, symbol: str, name: str, conversion_factor: float):
        """
        Initialize a length unit.

        Args:
            symbol: Symbol representing the unit
            name: Full name of the unit
            conversion_factor: Conversion factor to standard unit (inches)
        """
        super().__init__(symbol, name)
        self._conversion_factor = conversion_factor

    def get_conversion_factor(self) -> float:
        """
        Get the conversion factor to the standard unit (inches).

        Returns:
            Conversion factor to inches
        """
        return self._conversion_factor


# Define standard length units
LengthUnit.INCH = LengthUnit("in", "inch", 1.0)
LengthUnit.FOOT = LengthUnit("ft", "foot", INCHES_PER_FOOT)
LengthUnit.MILLIMETER = LengthUnit("mm", "millimeter", 1.0 / INCHES_PER_METER * MILLIMETERS_PER_METER)
LengthUnit.CENTIMETER = LengthUnit("cm", "centimeter", 1.0 / INCHES_PER_METER * CENTIMETERS_PER_METER)
LengthUnit.METER = LengthUnit("m", "meter", INCHES_PER_METER)
