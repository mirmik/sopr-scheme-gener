"""Text measurement contract shared by Qt and non-GUI layout code."""

from dataclasses import dataclass
import math
from typing import Protocol

from .model import TextStyle


@dataclass(frozen=True)
class TextMeasurement:
	width: float
	height: float
	ascent: float
	descent: float

	def __post_init__(self):
		for name in ("width", "height", "ascent", "descent"):
			value = getattr(self, name)
			if (
				not isinstance(value, (int, float))
				or isinstance(value, bool)
				or not math.isfinite(value)
				or value < 0
			):
				raise ValueError("{} must be a finite non-negative number".format(name))


class TextMetrics(Protocol):
	def measure(self, text: str, style: TextStyle) -> TextMeasurement:
		...
