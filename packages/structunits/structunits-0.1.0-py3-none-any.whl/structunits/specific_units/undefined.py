from structunits.result import Result
from structunits.flt import FLT
from structunits.unit import Unit


class Undefined(Result):
    """Undefined unit type, used for custom FLT combinations"""

    def __init__(self, flt: FLT, value: float):
        super().__init__(flt, value, None, None)

    def __repr__(self):
        """String representation of the object."""
        return self.to_latex_string()

    @property
    def equality_tolerance(self) -> float:
        return 1e-10

    def to_latex_string(self, display_unit=None) -> str:
        return f"{self.value} [{self.flt}]"

    def convert_to(self, target_unit: Unit) -> float:
        if target_unit is None:
            return self.value
        raise ValueError(f"Cannot convert undefined unit to a target unit: {target_unit}")

    @classmethod
    def create_with_standard_units(cls, flt: FLT, value: float) -> 'Undefined':
        return cls(flt, value)
