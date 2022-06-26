from dataclasses import dataclass
from fractions import Fraction
from typing import Union


@dataclass
class Zero:
    ...


FractionOrZero = Union[Fraction, Zero]
