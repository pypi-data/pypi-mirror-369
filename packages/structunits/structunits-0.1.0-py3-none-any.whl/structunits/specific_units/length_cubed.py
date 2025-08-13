from structunits.result import Result
from structunits.flt import FLT
from structunits.specific_units.length_cubed_unit import LengthCubedUnit
from structunits.constants import INCHES_PER_FOOT, INCHES_PER_METER, MILLIMETERS_PER_METER, CENTIMETERS_PER_METER
from structunits.utilities import Utilities


class LengthCubed(Result):
    """A length cubed value with unit handling (volume)"""

    def __init__(self, value: float, unit: LengthCubedUnit):
        """
        Construct a new length cubed from an input value and unit.

        Args:
            value: Numeric value
            unit: Length cubed unit
        """
        # Normalize to standard units (in³)
        std_value = self.normalize_value(value, unit)
        super().__init__(FLT.LENGTH_CUBED, std_value, self.default_unit(), unit)

    def __repr__(self):
        """String representation of the object."""
        return self.to_latex_string()

    @property
    def equality_tolerance(self) -> float:
        """Tolerance used when comparing two values."""
        return 0.001  # in³

    @staticmethod
    def default_unit() -> LengthCubedUnit:
        """The default unit for length cubed."""
        return LengthCubedUnit.INCHES_CUBED

    @staticmethod
    def zero():
        """Returns a length cubed with a value of zero with the default units."""
        return LengthCubed(0, LengthCubedUnit.INCHES_CUBED)

    @classmethod
    def create_with_standard_units(cls, value: float) -> 'LengthCubed':
        """
        Returns a new length cubed from the input value with the standard units.

        Args:
            value: Value in standard units (in³)

        Returns:
            A new LengthCubed instance
        """
        return cls(value, cls.default_unit())

    def convert_to(self, target_unit: LengthCubedUnit) -> float:
        """
        Converts to the target unit.

        Args:
            target_unit: Target unit to convert to

        Returns:
            Value in the target unit
        """
        if target_unit is None:
            return self.value

        if target_unit == LengthCubedUnit.INCHES_CUBED:
            return self.value

        if target_unit == LengthCubedUnit.FEET_CUBED:
            return self.value / (INCHES_PER_FOOT**3)

        if target_unit == LengthCubedUnit.MILLIMETERS_CUBED:
            return self.value / (INCHES_PER_METER**3) * (MILLIMETERS_PER_METER**3)

        if target_unit == LengthCubedUnit.METERS_CUBED:
            return self.value / (INCHES_PER_METER**3)

        if target_unit == LengthCubedUnit.CENTIMETERS_CUBED:
            return self.value / (INCHES_PER_METER**3) * (CENTIMETERS_PER_METER**3)

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
    def normalize_value(value: float, unit: LengthCubedUnit) -> float:
        """
        Normalize a value to standard units (in³).

        Args:
            value: Value in the given unit
            unit: Unit of the value

        Returns:
            Value in standard units (in³)
        """
        if unit == LengthCubedUnit.INCHES_CUBED:
            return value

        if unit == LengthCubedUnit.FEET_CUBED:
            return value * (INCHES_PER_FOOT**3)

        if unit == LengthCubedUnit.MILLIMETERS_CUBED:
            return value / (MILLIMETERS_PER_METER**3) * (INCHES_PER_METER**3)

        if unit == LengthCubedUnit.METERS_CUBED:
            return value * (INCHES_PER_METER**3)

        if unit == LengthCubedUnit.CENTIMETERS_CUBED:
            return value / (CENTIMETERS_PER_METER**3) * (INCHES_PER_METER**3)

        raise ValueError(f"Cannot convert from the source unit: {unit}")
