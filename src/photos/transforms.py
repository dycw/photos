from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from PIL.Image import Image


@dataclass
class Transform(ABC):
    @abstractmethod
    def __call__(self, image: Image, /) -> Image:
        raise NotImplementedError


@dataclass
class Rotate(Transform):
    angle: int

    def __call__(self, image: Image, /) -> Image:
        return image.rotate(self.angle)


Rotate90 = Rotate(90)
Rotate180 = Rotate(180)
