from enum import Enum, auto


class UnitType(Enum):
    """Enum that contains all of the pre-defined unit types."""
    AREA = auto()
    DENSITY = auto()
    FORCE = auto()
    FORCE_PER_LENGTH = auto()
    FLEXURAL_STIFFNESS = auto()
    LENGTH = auto()
    LENGTH_CUBED = auto()
    LENGTH_TO_THE_4TH = auto()
    LENGTH_TO_THE_6TH = auto()
    MOMENT = auto()
    STRESS = auto()
    TIME = auto()
    UNDEFINED = auto()
    UNITLESS = auto()
    ACCELERATION = auto()

    def __str__(self):
        return {
            UnitType.AREA: "Area",
            UnitType.DENSITY: "Density",
            UnitType.FORCE: "Force",
            UnitType.FORCE_PER_LENGTH: "Force per Length",
            UnitType.FLEXURAL_STIFFNESS: "Flexural Stiffness",
            UnitType.LENGTH: "Length",
            UnitType.LENGTH_CUBED: "Length Cubed",
            UnitType.LENGTH_TO_THE_4TH: "Length to the 4th",
            UnitType.LENGTH_TO_THE_6TH: "Length to the 6th",
            UnitType.MOMENT: "Moment",
            UnitType.STRESS: "Stress",
            UnitType.TIME: "Time",
            UnitType.UNDEFINED: "Undefined",
            UnitType.UNITLESS: "Unitless",
            UnitType.ACCELERATION: "Acceleration"
        }[self]
