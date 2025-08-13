from structunits.unit import Unit
from structunits.constants import (
    INCHES_PER_FOOT, INCHES_PER_METER,
    MILLIMETERS_PER_METER, CENTIMETERS_PER_METER,
    POUNDS_PER_KIP, NEWTONS_PER_KILONEWTON, KIPS_PER_KILONEWTON
)


class MomentUnit(Unit):
    """Unit for moment measurements (force × distance)"""

    def __init__(self, symbol: str, name: str, conversion_factor: float):
        """
        Initialize a moment unit.

        Args:
            symbol: Symbol representing the unit
            name: Full name of the unit
            conversion_factor: Conversion factor to standard unit (kip-inches)
        """
        super().__init__(symbol, name)
        self._conversion_factor = conversion_factor

    def get_conversion_factor(self) -> float:
        """
        Get the conversion factor to the standard unit (kip-inches).

        Returns:
            Conversion factor to kip-inches
        """
        return self._conversion_factor


# Define standard moment units
MomentUnit.POUND_INCH = MomentUnit("lb-in", "pound-inch", 1.0 / POUNDS_PER_KIP)
MomentUnit.POUND_FOOT = MomentUnit("lb-ft", "pound-foot", 1.0 / POUNDS_PER_KIP * INCHES_PER_FOOT)
MomentUnit.KIP_INCH = MomentUnit("k-in", "kip-inch", 1.0)
MomentUnit.KIP_FOOT = MomentUnit("k-ft", "kip-foot", INCHES_PER_FOOT)
MomentUnit.NEWTON_METER = MomentUnit("N-m", "newton-meter",
                                            KIPS_PER_KILONEWTON / NEWTONS_PER_KILONEWTON * INCHES_PER_METER)
MomentUnit.KILONEWTON_METER = MomentUnit("kN-m", "kilonewton-meter",
                                                 KIPS_PER_KILONEWTON * INCHES_PER_METER)
MomentUnit.KILONEWTON_MILLIMETER = MomentUnit("kN-mm", "kilonewton-millimeter",
                                                       KIPS_PER_KILONEWTON * INCHES_PER_METER / MILLIMETERS_PER_METER)
MomentUnit.NEWTON_MILLIMETER = MomentUnit("N-mm", "newton-millimeter",
                                                  KIPS_PER_KILONEWTON / NEWTONS_PER_KILONEWTON * INCHES_PER_METER / MILLIMETERS_PER_METER)
MomentUnit.KILONEWTON_CENTIMETER = MomentUnit("kN-cm", "kilonewton-centimeter",
                                                       KIPS_PER_KILONEWTON * INCHES_PER_METER / CENTIMETERS_PER_METER)
MomentUnit.NEWTON_CENTIMETER = MomentUnit("N-cm", "newton-centimeter",
                                                  KIPS_PER_KILONEWTON / NEWTONS_PER_KILONEWTON * INCHES_PER_METER / CENTIMETERS_PER_METER)
