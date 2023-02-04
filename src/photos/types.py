from dataclasses import dataclass
from fractions import Fraction


@dataclass
class Zero:
    """Class to represent a Zero."""


FractionOrZero = Fraction | Zero
