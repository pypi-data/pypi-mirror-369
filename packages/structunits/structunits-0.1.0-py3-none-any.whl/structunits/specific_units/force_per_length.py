from structunits.result import Result
from structunits.flt import FLT
from structunits.specific_units.force_per_length_unit import ForcePerLengthUnit
from structunits.constants import (
    INCHES_PER_FOOT, INCHES_PER_METER,
    MILLIMETERS_PER_METER, CENTIMETERS_PER_METER,
    POUNDS_PER_KIP, NEWTONS_PER_KILONEWTON, KIPS_PER_KILONEWTON
)
from structunits.utilities import Utilities


class ForcePerLength(Result):
    """A force per length value with unit handling (distributed load)"""

    def __init__(self, value: float, unit: ForcePerLengthUnit):
        """
        Construct a new force per length from an input value and unit.

        Args:
            value: Numeric value
            unit: Force per length unit
        """
        # Normalize to standard units (kips/inch)
        std_value = self.normalize_value(value, unit)
        super().__init__(FLT.FORCE_PER_LENGTH, std_value, self.default_unit(), unit)

    def __repr__(self):
        """String representation of the object."""
        return self.to_latex_string()

    @property
    def equality_tolerance(self) -> float:
        """Tolerance used when comparing two values."""
        return 0.0001  # kips/inch

    @staticmethod
    def default_unit() -> ForcePerLengthUnit:
        """The default unit for force per length."""
        return ForcePerLengthUnit.KIP_PER_INCH

    @staticmethod
    def zero():
        """Returns a force per length with a value of zero with the default units."""
        return ForcePerLength(0, ForcePerLengthUnit.KIP_PER_INCH)

    @classmethod
    def create_with_standard_units(cls, value: float) -> 'ForcePerLength':
        """
        Returns a new force per length from the input value with the standard units.

        Args:
            value: Value in standard units (kips/inch)

        Returns:
            A new ForcePerLength instance
        """
        return cls(value, cls.default_unit())

    def convert_to(self, target_unit: ForcePerLengthUnit) -> float:
        """
        Converts to the target unit.

        Args:
            target_unit: Target unit to convert to

        Returns:
            Value in the target unit
        """
        if target_unit is None:
            return self.value

        if target_unit == ForcePerLengthUnit.POUND_PER_INCH:
            return self.value * POUNDS_PER_KIP

        if target_unit == ForcePerLengthUnit.POUND_PER_FOOT:
            return self.value * POUNDS_PER_KIP * INCHES_PER_FOOT

        if target_unit == ForcePerLengthUnit.KIP_PER_INCH:
            return self.value

        if target_unit == ForcePerLengthUnit.KIP_PER_FOOT:
            return self.value * INCHES_PER_FOOT

        if target_unit == ForcePerLengthUnit.NEWTON_PER_METER:
            return self.value / KIPS_PER_KILONEWTON * NEWTONS_PER_KILONEWTON * INCHES_PER_METER

        if target_unit == ForcePerLengthUnit.KILONEWTON_PER_METER:
            return self.value / KIPS_PER_KILONEWTON * INCHES_PER_METER

        if target_unit == ForcePerLengthUnit.NEWTON_PER_MILLIMETER:
            return self.value / KIPS_PER_KILONEWTON * NEWTONS_PER_KILONEWTON * INCHES_PER_METER / MILLIMETERS_PER_METER

        if target_unit == ForcePerLengthUnit.KILONEWTON_PER_MILLIMETER:
            return self.value / KIPS_PER_KILONEWTON * INCHES_PER_METER / MILLIMETERS_PER_METER

        if target_unit == ForcePerLengthUnit.NEWTON_PER_CENTIMETER:
            return self.value / KIPS_PER_KILONEWTON * NEWTONS_PER_KILONEWTON * INCHES_PER_METER / CENTIMETERS_PER_METER

        if target_unit == ForcePerLengthUnit.KILONEWTON_PER_CENTIMETER:
            return self.value / KIPS_PER_KILONEWTON * INCHES_PER_METER / CENTIMETERS_PER_METER

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
    def normalize_value(value: float, unit: ForcePerLengthUnit) -> float:
        """
        Normalize a value to standard units (kips/inch).

        Args:
            value: Value in the given unit
            unit: Unit of the value

        Returns:
            Value in standard units (kips/inch)
        """
        if unit == ForcePerLengthUnit.POUND_PER_INCH:
            return value / POUNDS_PER_KIP

        if unit == ForcePerLengthUnit.POUND_PER_FOOT:
            return value / POUNDS_PER_KIP / INCHES_PER_FOOT

        if unit == ForcePerLengthUnit.KIP_PER_INCH:
            return value

        if unit == ForcePerLengthUnit.KIP_PER_FOOT:
            return value / INCHES_PER_FOOT

        if unit == ForcePerLengthUnit.NEWTON_PER_METER:
            return value / NEWTONS_PER_KILONEWTON * KIPS_PER_KILONEWTON / INCHES_PER_METER

        if unit == ForcePerLengthUnit.KILONEWTON_PER_METER:
            return value * KIPS_PER_KILONEWTON / INCHES_PER_METER

        if unit == ForcePerLengthUnit.NEWTON_PER_MILLIMETER:
            return value / NEWTONS_PER_KILONEWTON * KIPS_PER_KILONEWTON / INCHES_PER_METER * MILLIMETERS_PER_METER

        if unit == ForcePerLengthUnit.KILONEWTON_PER_MILLIMETER:
            return value * KIPS_PER_KILONEWTON / INCHES_PER_METER * MILLIMETERS_PER_METER

        if unit == ForcePerLengthUnit.NEWTON_PER_CENTIMETER:
            return value / NEWTONS_PER_KILONEWTON * KIPS_PER_KILONEWTON / INCHES_PER_METER * CENTIMETERS_PER_METER

        if unit == ForcePerLengthUnit.KILONEWTON_PER_CENTIMETER:
            return value * KIPS_PER_KILONEWTON / INCHES_PER_METER * CENTIMETERS_PER_METER

        raise ValueError(f"Cannot convert from the source unit: {unit}")
