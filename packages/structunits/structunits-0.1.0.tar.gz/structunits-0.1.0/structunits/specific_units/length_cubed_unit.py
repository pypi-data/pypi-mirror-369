from typing import ClassVar
from structunits.unit import Unit
from structunits.constants import INCHES_PER_FOOT, INCHES_PER_METER, MILLIMETERS_PER_METER, CENTIMETERS_PER_METER


class LengthCubedUnit(Unit):
    """Unit for length cubed measurements (volume)"""

    # Define class variables with type hints for autocomplete
    INCHES_CUBED: ClassVar['LengthCubedUnit']
    FEET_CUBED: ClassVar['LengthCubedUnit']
    MILLIMETERS_CUBED: ClassVar['LengthCubedUnit']
    METERS_CUBED: ClassVar['LengthCubedUnit']
    CENTIMETERS_CUBED: ClassVar['LengthCubedUnit']

    def __init__(self, symbol: str, name: str, conversion_factor: float):
        """
        Initialize a length cubed unit.

        Args:
            symbol: Symbol representing the unit
            name: Full name of the unit
            conversion_factor: Conversion factor to standard unit (in³)
        """
        super().__init__(symbol, name)
        self._conversion_factor = conversion_factor

    def get_conversion_factor(self) -> float:
        """
        Get the conversion factor to the standard unit (in³).

        Returns:
            Conversion factor to in³
        """
        return self._conversion_factor


# Define standard length cubed units
LengthCubedUnit.INCHES_CUBED = LengthCubedUnit("in³", "cubic inch", 1.0)
LengthCubedUnit.FEET_CUBED = LengthCubedUnit("ft³", "cubic foot", INCHES_PER_FOOT**3)
LengthCubedUnit.MILLIMETERS_CUBED = LengthCubedUnit("mm³", "cubic millimeter", (INCHES_PER_METER/MILLIMETERS_PER_METER)**3)
LengthCubedUnit.METERS_CUBED = LengthCubedUnit("m³", "cubic meter", INCHES_PER_METER**3)
LengthCubedUnit.CENTIMETERS_CUBED = LengthCubedUnit("cm³", "cubic centimeter", (INCHES_PER_METER/CENTIMETERS_PER_METER)**3)
