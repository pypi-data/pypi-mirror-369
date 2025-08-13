from structunits.result import Result
from structunits.flt import FLT
from structunits.specific_units.force_unit import ForceUnit
from structunits.constants import POUNDS_PER_KIP, NEWTONS_PER_KILONEWTON, KIPS_PER_KILONEWTON
from structunits.utilities import Utilities
from structunits.unit import Unit


class Force(Result):
    """A force value with unit handling"""

    def __init__(self, value: float, unit: Unit):
        """
        Construct a new force from an input value and unit.

        Args:
            value: Numeric value
            unit: Force unit (ForceUnit)
        """
        # Normalize to standard units (kips)
        std_value = self.normalize_value(value, unit)
        super().__init__(FLT.FORCE, std_value, self.default_unit(), unit)

    def __repr__(self):
        """String representation of the object."""
        return self.to_latex_string()

    @property
    def equality_tolerance(self) -> float:
        """Tolerance used when comparing two values."""
        return 0.0001  # kips

    @staticmethod
    def default_unit() -> ForceUnit:
        """The default unit for forces."""
        return ForceUnit.KIP

    @staticmethod
    def zero():
        """Returns a force with a value of zero with the default units."""
        return Force(0, ForceUnit.KIP)

    @classmethod
    def create_with_standard_units(cls, value: float) -> 'Force':
        """
        Returns a new force from the input value with the standard units.

        Args:
            value: Value in standard units (kips)

        Returns:
            A new Force instance
        """
        return cls(value, cls.default_unit())

    def convert_to(self, target_unit: Unit) -> float:
        """
        Converts to the target unit.

        Args:
            target_unit: Target unit to convert to

        Returns:
            Value in the target unit
        """
        if target_unit is None:
            return self.value

        # Check for pound unit
        if target_unit == ForceUnit.POUND:
            return self.value * POUNDS_PER_KIP

        # Check for kip unit
        if target_unit == ForceUnit.KIP:
            return self.value

        # Check for newton unit
        if target_unit == ForceUnit.NEWTON:
            return self.value / KIPS_PER_KILONEWTON * NEWTONS_PER_KILONEWTON

        # Check for kilonewton unit
        if target_unit == ForceUnit.KILONEWTON:
            return self.value / KIPS_PER_KILONEWTON

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
    def normalize_value(value: float, unit: Unit) -> float:
        """
        Normalize a value to standard units (kips).

        Args:
            value: Value in the given unit
            unit: Unit of the value

        Returns:
            Value in standard units (kips)
        """
        # Check for pound unit
        if unit == ForceUnit.POUND:
            return value / POUNDS_PER_KIP

        # Check for kip unit
        if unit == ForceUnit.KIP:
            return value

        # Check for newton unit
        if unit == ForceUnit.NEWTON:
            return value / NEWTONS_PER_KILONEWTON * KIPS_PER_KILONEWTON

        # Check for kilonewton unit
        if unit == ForceUnit.KILONEWTON:
            return value * KIPS_PER_KILONEWTON

        raise ValueError(f"Cannot convert from the source unit: {unit}")
