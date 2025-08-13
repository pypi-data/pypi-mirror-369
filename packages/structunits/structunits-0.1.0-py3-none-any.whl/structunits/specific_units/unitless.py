from structunits.result import Result
from structunits.flt import FLT
from structunits.unit import Unit


class Unitless(Result):
    """Unitless quantity"""

    def __init__(self, value: float):
        super().__init__(FLT.UNITLESS, value, None, None)

    def __repr__(self):
        """String representation of the object."""
        return self.to_latex_string()

    @property
    def equality_tolerance(self) -> float:
        return 1e-10

    def to_latex_string(self, display_unit=None) -> str:
        return str(self.value)

    def convert_to(self, target_unit: Unit) -> float:
        if target_unit is None:
            return self.value
        raise ValueError("Cannot convert unitless value to a unit")

    @classmethod
    def create_with_standard_units(cls, value: float) -> 'Unitless':
        return cls(value)
