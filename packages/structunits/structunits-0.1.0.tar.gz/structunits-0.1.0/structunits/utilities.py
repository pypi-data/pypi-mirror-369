from structunits.unit import Unit


class Utilities:
    """Utility functions for unit conversion."""

    @staticmethod
    def to_latex_string(value: float, unit: Unit = None) -> str:
        """
        Converts a value and unit to a LaTeX string.

        Args:
            value: The numeric value
            unit: The unit (optional)

        Returns:
            A LaTeX formatted string
        """
        if unit is None:
            return f"{value:.4g}"
        else:
            return f"{value:.4g} \\, \\mathrm{{{unit.symbol}}}"
