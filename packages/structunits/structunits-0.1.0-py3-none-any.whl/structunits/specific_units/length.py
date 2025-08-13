from structunits.result import Result
from structunits.flt import FLT
from structunits.specific_units.length_unit import LengthUnit
from structunits.constants import INCHES_PER_FOOT, INCHES_PER_METER, MILLIMETERS_PER_METER, CENTIMETERS_PER_METER
from structunits.utilities import Utilities


class Length(Result):
    """A length value with unit handling"""

    def __init__(self, value: float, unit: LengthUnit):
        """
        Construct a new length from an input value and unit.

        Args:
            value: Numeric value
            unit: Length unit
        """
        # Normalize to standard units (inches)
        std_value = self.normalize_value(value, unit)
        super().__init__(FLT.LENGTH, std_value, self.default_unit(), unit)

    def __repr__(self):
        """String representation of the object."""
        return self.to_latex_string()

    @property
    def equality_tolerance(self) -> float:
        """Tolerance used when comparing two values."""
        return 0.001

    @staticmethod
    def default_unit() -> LengthUnit:
        """The default unit for lengths."""
        return LengthUnit.INCH

    @staticmethod
    def zero():
        """Returns a length with a value of zero with the default units."""
        return Length(0, LengthUnit.INCH)

    @classmethod
    def create_with_standard_units(cls, value: float) -> 'Length':
        """
        Returns a new length from the input value with the standard units.

        Args:
            value: Value in standard units (inches)

        Returns:
            A new Length instance
        """
        return cls(value, cls.default_unit())

    def convert_to(self, target_unit: LengthUnit) -> float:
        """
        Converts to the target unit.

        Args:
            target_unit: Target unit to convert to

        Returns:
            Value in the target unit
        """
        if target_unit is None:
            return self.value

        if target_unit == LengthUnit.INCH:
            return self.value
        elif target_unit == LengthUnit.FOOT:
            return self.value / INCHES_PER_FOOT
        elif target_unit == LengthUnit.MILLIMETER:
            return self.value / INCHES_PER_METER * MILLIMETERS_PER_METER
        elif target_unit == LengthUnit.METER:
            return self.value / INCHES_PER_METER
        elif target_unit == LengthUnit.CENTIMETER:
            return self.value / INCHES_PER_METER * CENTIMETERS_PER_METER

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
    def normalize_value(value: float, unit: LengthUnit) -> float:
        """
        Normalize a value to standard units (inches).

        Args:
            value: Value in the given unit
            unit: Unit of the value

        Returns:
            Value in standard units (inches)
        """
        if unit == LengthUnit.INCH:
            return value
        elif unit == LengthUnit.FOOT:
            return value * INCHES_PER_FOOT
        elif unit == LengthUnit.MILLIMETER:
            return value / MILLIMETERS_PER_METER * INCHES_PER_METER
        elif unit == LengthUnit.METER:
            return value * INCHES_PER_METER
        elif unit == LengthUnit.CENTIMETER:
            return value / CENTIMETERS_PER_METER * INCHES_PER_METER

        raise ValueError(f"Cannot convert from the source unit: {unit}")
