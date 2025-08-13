from typing import ClassVar
from structunits.unit import Unit
from structunits.constants import POUNDS_PER_KIP, NEWTONS_PER_KILONEWTON, KIPS_PER_KILONEWTON


class ForceUnit(Unit):
    """Unit for force measurements"""

    # Define class variables with type hints for autocomplete
    POUND: ClassVar['ForceUnit']
    KIP: ClassVar['ForceUnit']
    NEWTON: ClassVar['ForceUnit']
    KILONEWTON: ClassVar['ForceUnit']

    def __init__(self, symbol: str, name: str, conversion_factor: float):
        """
        Initialize a force unit.

        Args:
            symbol: Symbol representing the unit
            name: Full name of the unit
            conversion_factor: Conversion factor to standard unit (kips)
        """
        super().__init__(symbol, name)
        self._conversion_factor = conversion_factor

    def get_conversion_factor(self) -> float:
        """
        Get the conversion factor to the standard unit (kips).

        Returns:
            Conversion factor to kips
        """
        return self._conversion_factor


# Define standard force units
ForceUnit.POUND = ForceUnit("lb", "pound", 1.0 / POUNDS_PER_KIP)
ForceUnit.KIP = ForceUnit("kip", "kip", 1.0)
ForceUnit.NEWTON = ForceUnit("N", "newton", KIPS_PER_KILONEWTON / NEWTONS_PER_KILONEWTON)
ForceUnit.KILONEWTON = ForceUnit("kN", "kilonewton", KIPS_PER_KILONEWTON)
