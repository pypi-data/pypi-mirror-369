from abc import ABC, abstractmethod
import math
from structunits.unit import Unit
from structunits.flt import FLT
from structunits.unit_type import UnitType
from structunits.utilities import Utilities


class Result(ABC):
    """Abstract base class for results with units"""

    def __init__(self, flt: FLT, value: float, display_unit: Unit, input_unit: Unit):
        self.flt = flt
        self.value = value
        self.display_unit = display_unit
        self._input_unit = input_unit

    @property
    def input_unit(self) -> Unit:
        """The unit that this value was created with."""
        return self._input_unit

    @property
    def input_unit_value(self) -> float:
        """Returns the value of this result in the input units."""
        return self.convert_to(self.input_unit)

    @property
    @abstractmethod
    def equality_tolerance(self) -> float:
        """Tolerance used when comparing two values."""
        pass

    @abstractmethod
    def to_latex_string(self, display_unit=None) -> str:
        """Converts the result to a LaTeX string."""
        if display_unit is None:
            return Utilities.to_latex_string(self.value)
        else:
            return Utilities.to_latex_string(self.convert_to(display_unit), display_unit)

    @abstractmethod
    def convert_to(self, target_unit: Unit) -> float:
        """Converts to the target unit."""
        pass

    # Operator overloads
    def __eq__(self, other):
        if other is None:
            return False

        # Reference equality
        if self is other:
            return True

        # Check for equality within tolerance
        if isinstance(other, Result) and self.flt == other.flt:
            if abs(self.value - other.value) <= self.equality_tolerance:
                return True

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        Result._confirm_units_match(self, other)
        return self.value < other.value

    def __le__(self, other):
        Result._confirm_units_match(self, other)
        return self.value <= other.value

    def __gt__(self, other):
        Result._confirm_units_match(self, other)
        return self.value > other.value

    def __ge__(self, other):
        Result._confirm_units_match(self, other)
        return self.value >= other.value

    def __add__(self, other):
        if isinstance(other, Result):
            Result._confirm_units_match(self, other)
            return self._build_typed_result(self.flt, self.value + other.value)
        elif isinstance(other, (int, float)):
            Result._confirm_unitless(self)
            return self._build_typed_result(self.flt, self.value + other)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, (int, float)):
            Result._confirm_unitless(self)
            return self._build_typed_result(self.flt, other + self.value)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Result):
            Result._confirm_units_match(self, other)
            return self._build_typed_result(self.flt, self.value - other.value)
        elif isinstance(other, (int, float)):
            Result._confirm_unitless(self)
            return self._build_typed_result(self.flt, self.value - other)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            Result._confirm_unitless(self)
            return self._build_typed_result(self.flt, other - self.value)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Result):
            return self._build_typed_result(self.flt + other.flt, self.value * other.value)
        elif isinstance(other, (int, float)):
            # When multiplying by a scalar, preserve the original type
            return self.__class__.create_with_standard_units(self.value * other)
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            # When multiplying by a scalar, preserve the original type
            return self.__class__.create_with_standard_units(other * self.value)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Result):
            return self._build_typed_result(self.flt - other.flt, self.value / other.value)
        elif isinstance(other, (int, float)):
            return self._build_typed_result(self.flt, self.value / other)
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return self._build_typed_result(-self.flt, other / self.value)
        return NotImplemented

    def __neg__(self):
        return self._build_typed_result(self.flt, -self.value)

    def __pow__(self, exponent):
        if isinstance(exponent, Result):
            Result._confirm_unitless(exponent)
            exponent_value = exponent.value
        else:
            exponent_value = exponent

        if isinstance(exponent_value, int):
            # Integer exponent - can use FLT multiplication
            return self._build_typed_result(self.flt * exponent_value, self.value ** exponent_value)
        else:
            # Non-integer exponent - result must be unitless
            # Check if it's close to an integer
            if abs(exponent_value - round(exponent_value)) < 1e-10:
                return self._build_typed_result(self.flt * round(exponent_value), self.value ** exponent_value)
            else:
                # Not an integer, result becomes unitless
                return self._build_typed_result(FLT.UNITLESS, self.value ** exponent_value)

    @classmethod
    def _build_typed_result(cls, flt: FLT, value: float):
        """Build a typed result based on the FLT"""
        unit_type = flt.get_type()

        # Import here to avoid circular imports
        from structunits.specific_units.unitless import Unitless
        from structunits.specific_units.undefined import Undefined

        # Try to handle different unit types
        if unit_type == UnitType.LENGTH:
            from structunits.specific_units.length import Length
            return Length.create_with_standard_units(value)
        elif unit_type == UnitType.FORCE:
            from structunits.specific_units.force import Force
            return Force.create_with_standard_units(value)
        elif unit_type == UnitType.MOMENT:
            from structunits.specific_units.moment import Moment
            return Moment.create_with_standard_units(value)
        elif unit_type == UnitType.FORCE_PER_LENGTH:
            from structunits.specific_units.force_per_length import ForcePerLength
            return ForcePerLength.create_with_standard_units(value)
        elif unit_type == UnitType.STRESS:
            from structunits.specific_units.stress import Stress
            return Stress.create_with_standard_units(value)
        elif unit_type == UnitType.LENGTH_TO_THE_4TH:
            from structunits.specific_units.length_to_the_4th import LengthToThe4th
            return LengthToThe4th.create_with_standard_units(value)
        elif unit_type == UnitType.LENGTH_CUBED:
            from structunits.specific_units.length_cubed import LengthCubed
            return LengthCubed.create_with_standard_units(value)
        elif unit_type == UnitType.UNITLESS:
            return Unitless(value)
        else:
            return Undefined(flt, value)

    @staticmethod
    def _confirm_units_match(a, b):
        """Confirm that two results have the same FLT"""
        if a.flt != b.flt:
            raise ValueError(f"Expected units to match: {a.flt} vs {b.flt}")

    @staticmethod
    def _confirm_unitless(a):
        """Confirm that a result is unitless"""
        if a.flt != FLT.UNITLESS:
            raise ValueError("Expected unitless argument")

    @staticmethod
    def _is_basically_an_integer(value: float) -> tuple:
        """Check if a float is very close to an integer"""
        nearest_int = round(value)
        if abs(value - nearest_int) < 1e-10:
            return True, nearest_int
        return False, 0

    # Math functions
    @staticmethod
    def sqrt(a):
        """Takes the square root of the Result"""
        return Result._build_typed_result(a.flt / 2, math.sqrt(a.value))

    @staticmethod
    def third_root(a):
        """Takes the third root of the Result"""
        return Result._build_typed_result(a.flt / 3, a.value ** (1/3))

    @staticmethod
    def fourth_root(a):
        """Takes the fourth root of the Result"""
        return Result._build_typed_result(a.flt / 4, a.value ** (1/4))

    @staticmethod
    def abs(a):
        """Returns the absolute value of the Result"""
        return Result._build_typed_result(a.flt, abs(a.value))

    @staticmethod
    def min(a, b=None):
        """Returns the minimum of two Results or a collection of Results"""
        if b is None and hasattr(a, "__iter__"):
            all_results = list(a)
            if not all_results:  # If a is empty
                raise ValueError("Expected at least one value")

            # Verify all have the same units
            for result in all_results[1:]:
                Result._confirm_units_match(all_results[0], result)

            min_result = all_results[0]
            for result in all_results[1:]:
                if result.value < min_result.value:
                    min_result = result

            return min_result
        elif b is not None:
            Result._confirm_units_match(a, b)
            return a if a.value < b.value else b
        else:
            # Single value passed
            return a

    @staticmethod
    def max(a, b=None):
        """Returns the maximum of two Results or a collection of Results"""
        if b is None and hasattr(a, "__iter__"):
            all_results = list(a)
            if not all_results:  # If a is empty
                raise ValueError("Expected at least one value")

            # Verify all have the same units
            for result in all_results[1:]:
                Result._confirm_units_match(all_results[0], result)

            max_result = all_results[0]
            for result in all_results[1:]:
                if result.value > max_result.value:
                    max_result = result

            return max_result
        elif b is not None:
            Result._confirm_units_match(a, b)
            return a if a.value > b.value else b
        else:
            # Single value passed
            return a

    @staticmethod
    def absolute_value_envelope(a, b=None):
        """Returns the maximum absolute value of Results"""
        if b is None and hasattr(a, "__iter__"):
            all_results = list(a)
            if not all_results:
                raise ValueError("Expected at least one value")

            # Verify all have the same units
            for result in all_results[1:]:
                Result._confirm_units_match(all_results[0], result)

            return Result.max([Result.abs(r) for r in all_results])
        else:
            Result._confirm_units_match(a, b)
            return Result.max(Result.abs(a), Result.abs(b))

    @staticmethod
    def absolute_value_signed_envelope(a, b):
        """Returns the signed maximum absolute value"""
        Result._confirm_units_match(a, b)
        abs_a = Result.abs(a)
        abs_b = Result.abs(b)

        if abs_a.value > abs_b.value:
            return abs_a * (1 if a.value >= 0 else -1)
        else:
            return abs_b * (1 if b.value >= 0 else -1)

    @staticmethod
    def min_value_envelope(a, b):
        """Returns the minimum of two Results"""
        return Result.min(a, b)

    @staticmethod
    def max_value_envelope(a, b):
        """Returns the maximum of two Results"""
        return Result.max(a, b)

    @staticmethod
    def sin(a):
        """Returns the sine of a unitless Result"""
        Result._confirm_unitless(a)
        return Result._build_typed_result(a.flt, math.sin(a.value))

    @staticmethod
    def cos(a):
        """Returns the cosine of a unitless Result"""
        Result._confirm_unitless(a)
        return Result._build_typed_result(a.flt, math.cos(a.value))

    @staticmethod
    def tan(a):
        """Returns the tangent of a unitless Result"""
        Result._confirm_unitless(a)
        return Result._build_typed_result(a.flt, math.tan(a.value))

    @staticmethod
    def asin(a):
        """Returns the arcsine of a unitless Result"""
        Result._confirm_unitless(a)
        return Result._build_typed_result(a.flt, math.asin(a.value))

    @staticmethod
    def acos(a):
        """Returns the arccosine of a unitless Result"""
        Result._confirm_unitless(a)
        return Result._build_typed_result(a.flt, math.acos(a.value))

    @staticmethod
    def atan(a):
        """Returns the arctangent of a unitless Result"""
        Result._confirm_unitless(a)
        return Result._build_typed_result(a.flt, math.atan(a.value))

    @staticmethod
    def srss(a, b):
        """Returns the square root of the sum of squares of two Results"""
        Result._confirm_units_match(a, b)
        return Result._build_typed_result(a.flt, math.sqrt(a.value**2 + b.value**2))