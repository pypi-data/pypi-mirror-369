from typing import ClassVar
from structunits.unit import Unit
from structunits.constants import INCHES_PER_FOOT, INCHES_PER_METER, MILLIMETERS_PER_METER, CENTIMETERS_PER_METER


class LengthToThe4thUnit(Unit):
    """Unit for length to the 4th power (moment of inertia)"""

    # Define class variables with type hints for autocomplete
    INCHES_TO_THE_4TH: ClassVar['LengthToThe4thUnit']
    FEET_TO_THE_4TH: ClassVar['LengthToThe4thUnit']
    MILLIMETERS_TO_THE_4TH: ClassVar['LengthToThe4thUnit']
    METERS_TO_THE_4TH: ClassVar['LengthToThe4thUnit']
    CENTIMETERS_TO_THE_4TH: ClassVar['LengthToThe4thUnit']

    def __init__(self, symbol: str, name: str, conversion_factor: float):
        """
        Initialize a length to the 4th power unit.

        Args:
            symbol: Symbol representing the unit
            name: Full name of the unit
            conversion_factor: Conversion factor to standard unit (in⁴)
        """
        super().__init__(symbol, name)
        self._conversion_factor = conversion_factor

    def get_conversion_factor(self) -> float:
        """
        Get the conversion factor to the standard unit (in⁴).

        Returns:
            Conversion factor to in⁴
        """
        return self._conversion_factor


# Define standard length to the 4th power units
LengthToThe4thUnit.INCHES_TO_THE_4TH = LengthToThe4thUnit("in⁴", "inch to the 4th", 1.0)
LengthToThe4thUnit.FEET_TO_THE_4TH = LengthToThe4thUnit("ft⁴", "foot to the 4th", INCHES_PER_FOOT**4)
LengthToThe4thUnit.MILLIMETERS_TO_THE_4TH = LengthToThe4thUnit("mm⁴", "millimeter to the 4th", (INCHES_PER_METER/MILLIMETERS_PER_METER)**4)
LengthToThe4thUnit.METERS_TO_THE_4TH = LengthToThe4thUnit("m⁴", "meter to the 4th", INCHES_PER_METER**4)
LengthToThe4thUnit.CENTIMETERS_TO_THE_4TH = LengthToThe4thUnit("cm⁴", "centimeter to the 4th", (INCHES_PER_METER/CENTIMETERS_PER_METER)**4)
