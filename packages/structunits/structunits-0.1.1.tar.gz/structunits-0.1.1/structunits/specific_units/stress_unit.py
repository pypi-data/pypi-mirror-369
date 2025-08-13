from typing import ClassVar
from structunits.unit import Unit
from structunits.constants import (
    INCHES_PER_FOOT, INCHES_PER_METER,
    POUNDS_PER_KIP, NEWTONS_PER_KILONEWTON, KIPS_PER_KILONEWTON,
    KILONEWTON_PER_MEGANEWTON
)


class StressUnit(Unit):
    """Unit for stress measurements (force per area)"""

    # Define class variables with type hints for autocomplete
    PSI: ClassVar['StressUnit']
    KSI: ClassVar['StressUnit']
    PSF: ClassVar['StressUnit']
    KSF: ClassVar['StressUnit']
    KPA: ClassVar['StressUnit']
    MPA: ClassVar['StressUnit']
    PA: ClassVar['StressUnit']

    def __init__(self, symbol: str, name: str, conversion_factor: float):
        """
        Initialize a stress unit.

        Args:
            symbol: Symbol representing the unit
            name: Full name of the unit
            conversion_factor: Conversion factor to standard unit (ksi)
        """
        super().__init__(symbol, name)
        self._conversion_factor = conversion_factor

    def get_conversion_factor(self) -> float:
        """
        Get the conversion factor to the standard unit (ksi).

        Returns:
            Conversion factor to ksi
        """
        return self._conversion_factor


# Define standard stress units
StressUnit.PSI = StressUnit("psi", "pounds per square inch", 1.0 / POUNDS_PER_KIP)
StressUnit.KSI = StressUnit("ksi", "kips per square inch", 1.0)
StressUnit.PSF = StressUnit("psf", "pounds per square foot",
                                   1.0 / POUNDS_PER_KIP / (INCHES_PER_FOOT * INCHES_PER_FOOT))
StressUnit.KSF = StressUnit("ksf", "kips per square foot",
                                   1.0 / (INCHES_PER_FOOT * INCHES_PER_FOOT))
StressUnit.KPA = StressUnit("kPa", "kilopascals",
                                   1.0 / (INCHES_PER_METER * INCHES_PER_METER) * KIPS_PER_KILONEWTON)
StressUnit.MPA = StressUnit("MPa", "megapascals",
                                   1.0 / (INCHES_PER_METER * INCHES_PER_METER) *
                                   KIPS_PER_KILONEWTON * KILONEWTON_PER_MEGANEWTON)
StressUnit.PA = StressUnit("Pa", "pascals",
                                 1.0 / (INCHES_PER_METER * INCHES_PER_METER) *
                                 KIPS_PER_KILONEWTON * NEWTONS_PER_KILONEWTON)
