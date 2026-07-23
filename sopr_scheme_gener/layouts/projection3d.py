"""Small Qt-independent orthographic/axonometric projection helpers."""

import math
from dataclasses import dataclass
from functools import cached_property

import numpy

from sopr_scheme_gener.scene import Point


@dataclass(frozen=True)
class Projection3D:
	base_x: float
	base_y: float
	z_rotation: float
	x_rotation: float
	axonometric: bool = False
	forty_five_degrees: bool = False
	diagonal_scale: float = 0.5
	diagonal_y_scale: float = 0.5

	@cached_property
	def _matrix(self):
		translation = numpy.array(
			[
				[1, 0, 0, self.base_x],
				[0, 1, 0, 0],
				[0, 0, 1, self.base_y],
				[0, 0, 0, 1],
			]
		)
		z_rotation = numpy.array(
			[
				[
					math.cos(self.z_rotation),
					-math.sin(self.z_rotation),
					0,
					0,
				],
				[
					math.sin(self.z_rotation),
					math.cos(self.z_rotation),
					0,
					0,
				],
				[0, 0, 1, 0],
				[0, 0, 0, 1],
			]
		)
		x_rotation = numpy.array(
			[
				[1, 0, 0, 0],
				[
					0,
					math.cos(self.x_rotation),
					-math.sin(self.x_rotation),
					0,
				],
				[
					0,
					math.sin(self.x_rotation),
					math.cos(self.x_rotation),
					0,
				],
				[0, 0, 0, 1],
			]
		)
		return translation @ x_rotation @ z_rotation

	def point(self, x, y, z):
		if self.axonometric:
			projected = self._matrix @ numpy.array([[x], [y], [-z], [1]])
			return Point(float(projected[0, 0]), float(projected[2, 0]))
		if self.forty_five_degrees:
			return Point(
				self.base_x - y * self.diagonal_scale + x,
				self.base_y + y * self.diagonal_y_scale - z,
			)
		projected = self._matrix @ numpy.array([[0], [y], [0], [1]])
		return Point(float(projected[0, 0]) + x, float(projected[2, 0]) - z)

	def vector(self, value):
		return self.point(*value)
