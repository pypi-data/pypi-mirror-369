from structunits.unit_type import UnitType


class FLT:
    """Force-Length-Time class to represent physical dimensions"""

    def __init__(self, force_degree: int, length_degree: int, time_degree: int):
        self.force_degree = force_degree
        self.length_degree = length_degree
        self.time_degree = time_degree

    def get_type(self) -> UnitType:
        """Get the UnitType corresponding to this FLT"""
        # Check if this FLT matches any predefined ones
        if self == FLT.AREA:
            return UnitType.AREA
        elif self == FLT.DENSITY:
            return UnitType.DENSITY
        elif self == FLT.FORCE:
            return UnitType.FORCE
        elif self == FLT.FORCE_PER_LENGTH:
            return UnitType.FORCE_PER_LENGTH
        elif self == FLT.FLEXURAL_STIFFNESS:
            return UnitType.FLEXURAL_STIFFNESS
        elif self == FLT.LENGTH:
            return UnitType.LENGTH
        elif self == FLT.LENGTH_CUBED:
            return UnitType.LENGTH_CUBED
        elif self == FLT.LENGTH_TO_THE_4TH:
            return UnitType.LENGTH_TO_THE_4TH
        elif self == FLT.LENGTH_TO_THE_6TH:
            return UnitType.LENGTH_TO_THE_6TH
        elif self == FLT.MOMENT:
            return UnitType.MOMENT
        elif self == FLT.STRESS:
            return UnitType.STRESS
        elif self == FLT.TIME:
            return UnitType.TIME
        elif self == FLT.UNITLESS:
            return UnitType.UNITLESS
        elif self == FLT.ACCELERATION:
            return UnitType.ACCELERATION
        else:
            return UnitType.UNDEFINED

    def __eq__(self, other):
        if not isinstance(other, FLT):
            return False
        return (self.force_degree == other.force_degree and
                self.length_degree == other.length_degree and
                self.time_degree == other.time_degree)

    def __hash__(self):
        return hash((self.force_degree, self.length_degree, self.time_degree))

    def __add__(self, other):
        """Add two FLT instances (combine units)"""
        if not isinstance(other, FLT):
            return NotImplemented
        F = self.force_degree + other.force_degree
        L = self.length_degree + other.length_degree
        T = self.time_degree + other.time_degree
        return FLT(F, L, T)

    def __sub__(self, other):
        """Subtract two FLT instances"""
        if not isinstance(other, FLT):
            return NotImplemented
        F = self.force_degree - other.force_degree
        L = self.length_degree - other.length_degree
        T = self.time_degree - other.time_degree
        return FLT(F, L, T)

    def __neg__(self):
        """Negate an FLT instance"""
        return FLT(-self.force_degree, -self.length_degree, -self.time_degree)

    def __mul__(self, other):
        """Multiply an FLT by an integer"""
        if not isinstance(other, (int, float)):
            return NotImplemented
        F = self.force_degree * other
        L = self.length_degree * other
        T = self.time_degree * other
        # Ensure the multiplication by a float results in integers
        if isinstance(other, float):
            F = round(F) if abs(F - round(F)) < 1e-10 else F
            L = round(L) if abs(L - round(L)) < 1e-10 else L
            T = round(T) if abs(T - round(T)) < 1e-10 else T
            # If they're not integers, return unitless
            if not (isinstance(F, int) and isinstance(L, int) and isinstance(T, int)):
                return FLT.UNITLESS
        return FLT(int(F), int(L), int(T))

    def __rmul__(self, other):
        """Right multiplication"""
        return self.__mul__(other)

    def __truediv__(self, other):
        """Divide an FLT by a number"""
        if not isinstance(other, (int, float)):
            return NotImplemented

        F = self.force_degree / other
        L = self.length_degree / other
        T = self.time_degree / other

        # Check if the division results in integers
        if (abs(F - round(F)) < 1e-10 and
                abs(L - round(L)) < 1e-10 and
                abs(T - round(T)) < 1e-10):
            return FLT(int(round(F)), int(round(L)), int(round(T)))
        else:
            return FLT.UNITLESS

    def __str__(self):
        components = []

        if self.force_degree != 0:
            if self.force_degree == 1:
                components.append("F")
            else:
                components.append(f"F^{self.force_degree}")

        if self.length_degree != 0:
            if self.length_degree == 1:
                components.append("L")
            else:
                components.append(f"L^{self.length_degree}")

        if self.time_degree != 0:
            if self.time_degree == 1:
                components.append("T")
            else:
                components.append(f"T^{self.time_degree}")

        if not components:
            return "1"
        else:
            return "·".join(components)


# Static FLT instances
FLT.AREA = FLT(0, 2, 0)
FLT.DENSITY = FLT(1, -3, 0)
FLT.FORCE = FLT(1, 0, 0)
FLT.FORCE_PER_LENGTH = FLT(1, -1, 0)
FLT.FLEXURAL_STIFFNESS = FLT(1, 2, 0)
FLT.LENGTH = FLT(0, 1, 0)
FLT.LENGTH_CUBED = FLT(0, 3, 0)
FLT.LENGTH_TO_THE_4TH = FLT(0, 4, 0)
FLT.LENGTH_TO_THE_6TH = FLT(0, 6, 0)
FLT.MOMENT = FLT(1, 1, 0)
FLT.STRESS = FLT(1, -2, 0)
FLT.TIME = FLT(0, 0, 1)
FLT.UNITLESS = FLT(0, 0, 0)
FLT.ACCELERATION = FLT(0, 1, -2)
