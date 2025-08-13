from structunits.result import Result
from structunits.flt import FLT
from structunits.specific_units.moment_unit import MomentUnit
from structunits.constants import (
    INCHES_PER_FOOT, INCHES_PER_METER,
    MILLIMETERS_PER_METER, CENTIMETERS_PER_METER,
    POUNDS_PER_KIP, NEWTONS_PER_KILONEWTON, KIPS_PER_KILONEWTON
)
from structunits.utilities import Utilities


class Moment(Result):
    """A moment value with unit handling (force × distance)"""

    def __init__(self, value: float, unit: MomentUnit):
        """
        Construct a new moment from an input value and unit.

        Args:
            value: Numeric value
            unit: Moment unit
        """
        # Normalize to standard units (kip-inches)
        std_value = self.normalize_value(value, unit)
        super().__init__(FLT.MOMENT, std_value, self.default_unit(), unit)

    def __repr__(self):
        """String representation of the object."""
        return self.to_latex_string()

    @property
    def equality_tolerance(self) -> float:
        """Tolerance used when comparing two values."""
        return 0.01  # kip-inches

    @staticmethod
    def default_unit() -> MomentUnit:
        """The default unit for moments."""
        return MomentUnit.KIP_INCH

    @staticmethod
    def zero():
        """Returns a moment with a value of zero with the default units."""
        return Moment(0, MomentUnit.KIP_INCH)

    @classmethod
    def create_with_standard_units(cls, value: float) -> 'Moment':
        """
        Returns a new moment from the input value with the standard units.

        Args:
            value: Value in standard units (kip-inches)

        Returns:
            A new Moment instance
        """
        return cls(value, cls.default_unit())

    def convert_to(self, target_unit: MomentUnit) -> float:
        """
        Converts to the target unit.

        Args:
            target_unit: Target unit to convert to

        Returns:
            Value in the target unit
        """
        if target_unit is None:
            return self.value

        if target_unit == MomentUnit.POUND_INCH:
            return self.value * POUNDS_PER_KIP

        if target_unit == MomentUnit.POUND_FOOT:
            return self.value * POUNDS_PER_KIP / INCHES_PER_FOOT

        if target_unit == MomentUnit.KIP_INCH:
            return self.value

        if target_unit == MomentUnit.KIP_FOOT:
            return self.value / INCHES_PER_FOOT

        if target_unit == MomentUnit.NEWTON_METER:
            return self.value / KIPS_PER_KILONEWTON * NEWTONS_PER_KILONEWTON / INCHES_PER_METER

        if target_unit == MomentUnit.KILONEWTON_METER:
            return self.value / KIPS_PER_KILONEWTON / INCHES_PER_METER

        if target_unit == MomentUnit.KILONEWTON_MILLIMETER:
            return (self.value / KIPS_PER_KILONEWTON / INCHES_PER_METER *
                    MILLIMETERS_PER_METER)

        if target_unit == MomentUnit.NEWTON_MILLIMETER:
            return (self.value / KIPS_PER_KILONEWTON * NEWTONS_PER_KILONEWTON /
                    INCHES_PER_METER * MILLIMETERS_PER_METER)

        if target_unit == MomentUnit.KILONEWTON_CENTIMETER:
            return (self.value / KIPS_PER_KILONEWTON / INCHES_PER_METER *
                    CENTIMETERS_PER_METER)

        if target_unit == MomentUnit.NEWTON_CENTIMETER:
            return (self.value / KIPS_PER_KILONEWTON * NEWTONS_PER_KILONEWTON /
                    INCHES_PER_METER * CENTIMETERS_PER_METER)

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
    def normalize_value(value: float, unit: MomentUnit) -> float:
        """
        Normalize a value to standard units (kip-inches).

        Args:
            value: Value in the given unit
            unit: Unit of the value

        Returns:
            Value in standard units (kip-inches)
        """
        if unit == MomentUnit.POUND_INCH:
            return value / POUNDS_PER_KIP

        if unit == MomentUnit.POUND_FOOT:
            return value / POUNDS_PER_KIP * INCHES_PER_FOOT

        if unit == MomentUnit.KIP_INCH:
            return value

        if unit == MomentUnit.KIP_FOOT:
            return value * INCHES_PER_FOOT

        if unit == MomentUnit.NEWTON_METER:
            return value / NEWTONS_PER_KILONEWTON * KIPS_PER_KILONEWTON * INCHES_PER_METER

        if unit == MomentUnit.KILONEWTON_METER:
            return value * KIPS_PER_KILONEWTON * INCHES_PER_METER

        if unit == MomentUnit.KILONEWTON_MILLIMETER:
            return value * KIPS_PER_KILONEWTON / MILLIMETERS_PER_METER * INCHES_PER_METER

        if unit == MomentUnit.NEWTON_MILLIMETER:
            return (value / NEWTONS_PER_KILONEWTON * KIPS_PER_KILONEWTON /
                    MILLIMETERS_PER_METER * INCHES_PER_METER)

        if unit == MomentUnit.KILONEWTON_CENTIMETER:
            return value * KIPS_PER_KILONEWTON / CENTIMETERS_PER_METER * INCHES_PER_METER

        if unit == MomentUnit.NEWTON_CENTIMETER:
            return (value / NEWTONS_PER_KILONEWTON * KIPS_PER_KILONEWTON /
                    CENTIMETERS_PER_METER * INCHES_PER_METER)

        raise ValueError(f"Cannot convert from the source unit: {unit}")
