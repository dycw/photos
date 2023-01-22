from dataclasses import dataclass
from fractions import Fraction
from typing import Union


@dataclass
class Zero:
    """Class to represent a Zero."""


FractionOrZero = Union[Fraction, Zero]
