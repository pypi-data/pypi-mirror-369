from abc import ABC, abstractmethod


class Unit(ABC):
    """Abstract base class for units"""

    def __init__(self, symbol: str, name: str, conversion_factor: float = None):
        self.symbol = symbol
        self.name = name
        self._conversion_factor = conversion_factor

    @abstractmethod
    def get_conversion_factor(self) -> float:
        """Get conversion factor from this unit to the standard unit"""
        pass

    def __str__(self):
        return self.symbol

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.symbol == other.symbol

    def __hash__(self):
        return hash(self.symbol)