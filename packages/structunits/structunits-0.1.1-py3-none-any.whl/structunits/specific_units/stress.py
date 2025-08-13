from structunits.result import Result
from structunits.flt import FLT
from structunits.specific_units.stress_unit import StressUnit
from structunits.constants import (
    INCHES_PER_FOOT, INCHES_PER_METER,
    POUNDS_PER_KIP, NEWTONS_PER_KILONEWTON, KIPS_PER_KILONEWTON,
    KILONEWTON_PER_MEGANEWTON
)
from structunits.utilities import Utilities


class Stress(Result):
    """A stress value with unit handling (force per area)"""

    def __init__(self, value: float, unit: StressUnit):
        """
        Construct a new stress from an input value and unit.

        Args:
            value: Numeric value
            unit: Stress unit
        """
        # Normalize to standard units (ksi)
        std_value = self.normalize_value(value, unit)
        super().__init__(FLT.STRESS, std_value, self.default_unit(), unit)

    def __repr__(self):
        """String representation of the object."""
        return self.to_latex_string()

    @property
    def equality_tolerance(self) -> float:
        """Tolerance used when comparing two values."""
        return 0.0001  # ksi

    @staticmethod
    def default_unit() -> StressUnit:
        """The default unit for stress."""
        return StressUnit.KSI

    @staticmethod
    def zero():
        """Returns a stress with a value of zero with the default units."""
        return Stress(0, StressUnit.KSI)

    @classmethod
    def create_with_standard_units(cls, value: float) -> 'Stress':
        """
        Returns a new stress from the input value with the standard units.

        Args:
            value: Value in standard units (ksi)

        Returns:
            A new Stress instance
        """
        return cls(value, cls.default_unit())

    def convert_to(self, target_unit: StressUnit) -> float:
        """
        Converts to the target unit.

        Args:
            target_unit: Target unit to convert to

        Returns:
            Value in the target unit
        """
        if target_unit is None:
            return self.value

        if target_unit == StressUnit.PSI:
            return self.value * POUNDS_PER_KIP

        if target_unit == StressUnit.KSI:
            return self.value

        if target_unit == StressUnit.PSF:
            return self.value * POUNDS_PER_KIP * (INCHES_PER_FOOT * INCHES_PER_FOOT)

        if target_unit == StressUnit.KSF:
            return self.value * (INCHES_PER_FOOT * INCHES_PER_FOOT)

        if target_unit == StressUnit.KPA:
            return self.value * (INCHES_PER_METER * INCHES_PER_METER) / KIPS_PER_KILONEWTON

        if target_unit == StressUnit.MPA:
            return self.value * (INCHES_PER_METER * INCHES_PER_METER) / KIPS_PER_KILONEWTON / KILONEWTON_PER_MEGANEWTON

        if target_unit == StressUnit.PA:
            return self.value * (INCHES_PER_METER * INCHES_PER_METER) / KIPS_PER_KILONEWTON * NEWTONS_PER_KILONEWTON

        raise ValueError(f"Cannot convert to the target unit: {target_unit}")

    def to_latex_string(self, display_unit=None) -> str:
        """
        Converts the unit to a LaTeX string.

        Args:
            display_unit: Unit to display

        Returns:
            LaTeX formatted string
        """
        if display_unit is None:
            display_unit = self.display_unit

        return Utilities.to_latex_string(self.convert_to(display_unit), display_unit)

    @staticmethod
    def normalize_value(value: float, unit: StressUnit) -> float:
        """
        Normalize a value to standard units (ksi).

        Args:
            value: Value in the given unit
            unit: Unit of the value

        Returns:
            Value in standard units (ksi)
        """
        if unit == StressUnit.PSI:
            return value / POUNDS_PER_KIP

        if unit == StressUnit.KSI:
            return value

        if unit == StressUnit.PSF:
            return value / POUNDS_PER_KIP / (INCHES_PER_FOOT * INCHES_PER_FOOT)

        if unit == StressUnit.KSF:
            return value / (INCHES_PER_FOOT * INCHES_PER_FOOT)

        if unit == StressUnit.KPA:
            return value / (INCHES_PER_METER * INCHES_PER_METER) * KIPS_PER_KILONEWTON

        if unit == StressUnit.MPA:
            return value / (INCHES_PER_METER * INCHES_PER_METER) * KILONEWTON_PER_MEGANEWTON * KIPS_PER_KILONEWTON

        if unit == StressUnit.PA:
            return value / (INCHES_PER_METER * INCHES_PER_METER) / NEWTONS_PER_KILONEWTON * KIPS_PER_KILONEWTON

        raise ValueError(f"Cannot convert from the source unit: {unit}")
