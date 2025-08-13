from structunits.result import Result
from structunits.flt import FLT
from structunits.specific_units.length_to_the_4th_unit import LengthToThe4thUnit
from structunits.constants import INCHES_PER_FOOT, INCHES_PER_METER, MILLIMETERS_PER_METER, CENTIMETERS_PER_METER
from structunits.utilities import Utilities


class LengthToThe4th(Result):
    """A length to the 4th power value (moment of inertia)"""

    def __init__(self, value: float, unit: LengthToThe4thUnit):
        """
        Construct a new length to the 4th power from an input value and unit.

        Args:
            value: Numeric value
            unit: Length to the 4th power unit
        """
        # Normalize to standard units (in⁴)
        std_value = self.normalize_value(value, unit)
        super().__init__(FLT.LENGTH_TO_THE_4TH, std_value, self.default_unit(), unit)

    def __repr__(self):
        """String representation of the object."""
        return self.to_latex_string()

    @property
    def equality_tolerance(self) -> float:
        """Tolerance used when comparing two values."""
        return 0.001  # in⁴

    @staticmethod
    def default_unit() -> LengthToThe4thUnit:
        """The default unit for length to the 4th power."""
        return LengthToThe4thUnit.INCHES_TO_THE_4TH

    @staticmethod
    def zero():
        """Returns a length to the 4th with a value of zero with the default units."""
        return LengthToThe4th(0, LengthToThe4thUnit.INCHES_TO_THE_4TH)

    @classmethod
    def create_with_standard_units(cls, value: float) -> 'LengthToThe4th':
        """
        Returns a new length to the 4th from the input value with the standard units.

        Args:
            value: Value in standard units (in⁴)

        Returns:
            A new LengthToThe4th instance
        """
        return cls(value, cls.default_unit())

    def convert_to(self, target_unit: LengthToThe4thUnit) -> float:
        """
        Converts to the target unit.

        Args:
            target_unit: Target unit to convert to

        Returns:
            Value in the target unit
        """
        if target_unit is None:
            return self.value

        if target_unit == LengthToThe4thUnit.INCHES_TO_THE_4TH:
            return self.value

        if target_unit == LengthToThe4thUnit.FEET_TO_THE_4TH:
            return self.value / (INCHES_PER_FOOT**4)

        if target_unit == LengthToThe4thUnit.MILLIMETERS_TO_THE_4TH:
            return self.value / (INCHES_PER_METER**4) * (MILLIMETERS_PER_METER**4)

        if target_unit == LengthToThe4thUnit.METERS_TO_THE_4TH:
            return self.value / (INCHES_PER_METER**4)

        if target_unit == LengthToThe4thUnit.CENTIMETERS_TO_THE_4TH:
            return self.value / (INCHES_PER_METER**4) * (CENTIMETERS_PER_METER**4)

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
    def normalize_value(value: float, unit: LengthToThe4thUnit) -> float:
        """
        Normalize a value to standard units (in⁴).

        Args:
            value: Value in the given unit
            unit: Unit of the value

        Returns:
            Value in standard units (in⁴)
        """
        if unit == LengthToThe4thUnit.INCHES_TO_THE_4TH:
            return value

        if unit == LengthToThe4thUnit.FEET_TO_THE_4TH:
            return value * (INCHES_PER_FOOT**4)

        if unit == LengthToThe4thUnit.MILLIMETERS_TO_THE_4TH:
            return value / (MILLIMETERS_PER_METER**4) * (INCHES_PER_METER**4)

        if unit == LengthToThe4thUnit.METERS_TO_THE_4TH:
            return value * (INCHES_PER_METER**4)

        if unit == LengthToThe4thUnit.CENTIMETERS_TO_THE_4TH:
            return value / (CENTIMETERS_PER_METER**4) * (INCHES_PER_METER**4)

        raise ValueError(f"Cannot convert from the source unit: {unit}")
