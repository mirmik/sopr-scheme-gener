"""Qt-independent layout for the stress-cube task."""

import math
from dataclasses import dataclass

from sopr_scheme_gener.scene import (
	BLACK,
	Fill,
	Group,
	Line,
	Point,
	Polygon,
	Rect,
	Scene,
	Stroke,
	Text,
	TextAnchor,
	TextStyle,
	metadata,
)


@dataclass(frozen=True)
class StressCubeLayoutSettings:
	second_cube: bool = False
	axonom: bool = False
	yaw_degrees: float = 20.0
	pitch_degrees: float = 40.0
	z_scale: float = 0.6
	edge: float = 50.0
	horizontal_border: float = 10.0
	vertical_border: float = 0.0
	line_width: float = 2.0
	font_size: float = 12.0
	note: str = ""


class Projection:
	"""The historical cube projection, expressed without numpy or Qt."""

	def __init__(
		self,
		yaw_degrees=20.0,
		pitch_degrees=40.0,
		z_scale=0.6,
		axonom=False,
		offset_x=0.0,
	):
		self.yaw = math.radians(yaw_degrees)
		self.pitch = -math.radians(pitch_degrees)
		self.z_scale = z_scale
		self.axonom = axonom
		self.offset_x = offset_x

	def __call__(self, x, y, z):
		if not self.axonom:
			projected_x = x - math.cos(self.pitch) * self.z_scale * y
			projected_z = math.sin(self.pitch) * self.z_scale * y + z
		else:
			cos_yaw = math.cos(self.yaw)
			sin_yaw = math.sin(self.yaw)
			rotated_x = cos_yaw * x - sin_yaw * y
			rotated_y = sin_yaw * x + cos_yaw * y
			projected_x = rotated_x
			projected_z = (
				math.sin(self.pitch) * rotated_y
				+ math.cos(self.pitch) * z
			)
		return Point(projected_x + self.offset_x, -projected_z)


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _union(bounds, other):
	return other if bounds is None else bounds.union(other)


def _expanded(bounds, amount):
	return Rect(
		bounds.x - amount,
		bounds.y - amount,
		bounds.width + amount * 2,
		bounds.height + amount * 2,
	)


def _line_bounds(start, end, width):
	# QGraphicsLineItem uses a square-cap stroke. The exact shape matters only
	# when a line forms an outer edge of the layout.
	length = math.hypot(end.x - start.x, end.y - start.y)
	if not length:
		return Rect(start.x, start.y, 0, 0)
	ux = (end.x - start.x) / length
	uy = (end.y - start.y) / length
	half = width / 2
	points = (
		Point(start.x - ux * half - uy * half, start.y - uy * half + ux * half),
		Point(start.x - ux * half + uy * half, start.y - uy * half - ux * half),
		Point(end.x + ux * half - uy * half, end.y + uy * half + ux * half),
		Point(end.x + ux * half + uy * half, end.y + uy * half - ux * half),
	)
	return Rect.around(points)


def _legacy_text_bounds(center, value, style, text_metrics):
	measurement = text_metrics.measure(value, style)
	return Rect(
		center.x - measurement.width / 2,
		center.y - measurement.height / 2,
		measurement.width + 5,
		measurement.height,
	)


def _arrow(start, end, stroke, head_length, half_width, object_id):
	dx = end.x - start.x
	dy = end.y - start.y
	length = math.hypot(dx, dy)
	ux, uy = dx / length, dy / length
	normal = Point(uy, -ux)
	base = Point(end.x - ux * head_length, end.y - uy * head_length)
	head = Polygon(
		(
			end,
			Point(base.x + normal.x * half_width, base.y + normal.y * half_width),
			Point(base.x - normal.x * half_width, base.y - normal.y * half_width),
		),
		stroke=stroke,
		fill=Fill(BLACK),
	)
	return Group(
		(Line(start, end, stroke=stroke), head),
		object_id=object_id,
		metadata=metadata(kind="arrow"),
	)


class _Cube:
	def __init__(self, settings, task, index, offset_x, text_metrics, text_transform):
		self.settings = settings
		self.task = task
		self.index = index
		self.proj = Projection(
			settings.yaw_degrees,
			settings.pitch_degrees,
			settings.z_scale,
			settings.axonom,
			offset_x,
		)
		self.text_metrics = text_metrics
		self.text_transform = text_transform
		self.main = Stroke(width=settings.line_width)
		self.half = Stroke(width=max(1, int(settings.line_width / 2)))
		self.style = TextStyle(point_size=settings.font_size, italic=True)
		self.objects = []
		self.bounds = None

	def add_line(self, start, end, object_id):
		self.objects.append(Line(start, end, stroke=self.main, object_id=object_id))
		self.bounds = _union(
			self.bounds,
			_line_bounds(start, end, self.main.width),
		)

	def add_arrow(self, start, end, head_length, half_width, object_id, reverse=False):
		if reverse:
			start, end = end, start
		self.objects.append(
			_arrow(start, end, self.main if half_width == 5 else self.half, head_length, half_width, object_id)
		)
		# ArrowItem deliberately advertised a fixed five-pixel margin.
		self.bounds = _union(
			self.bounds,
			_expanded(Rect.around((start, end)), 5),
		)

	def add_text(self, center, value, object_id, kind="text"):
		item = Text(
			center,
			value,
			style=self.style,
			anchor=TextAnchor.CENTER,
			object_id=object_id,
			metadata=metadata(kind=kind, cube=self.index),
		)
		self.objects.append(item)
		bounds = _legacy_text_bounds(center, value, self.style, self.text_metrics)
		self.bounds = _union(self.bounds, bounds)

	def build(self):
		p = self.settings.edge
		proj = self.proj
		edges = (
			((+p, +p, +p), (-p, +p, +p)),
			((+p, +p, +p), (+p, -p, +p)),
			((+p, +p, +p), (+p, +p, -p)),
			((+p, +p, -p), (-p, +p, -p)),
			((+p, +p, -p), (+p, -p, -p)),
			((-p, +p, -p), (-p, +p, +p)),
			((+p, -p, -p), (+p, -p, +p)),
			((-p, -p, +p), (-p, +p, +p)),
			((-p, -p, +p), (+p, -p, +p)),
		)
		for edge_index, (start, end) in enumerate(edges):
			self.add_line(
				proj(*start),
				proj(*end),
				"cube/{}/edge/{}".format(self.index, edge_index),
			)

		axes = (
			((+p, -p, -p), (+2 * p, -p, -p), "x", Point(0, -10)),
			((-p, +p, -p), (-p, +2 * p, -p), "z", Point(-8, 0)),
			((-p, -p, +p), (-p, -p, +2 * p), "y", Point(-8, 0)),
		)
		for start, end, name, label_offset in axes:
			end_point = proj(*end)
			self.add_arrow(
				proj(*start),
				end_point,
				15,
				3,
				"cube/{}/axis/{}".format(self.index, name),
			)
			self.add_text(
				end_point.translated(label_offset),
				name,
				"cube/{}/axis/{}/label".format(self.index, name),
			)

		section = self.task["sections"][self.index]
		load_points = {
			"qx": proj(2.5 * p, 0, 0),
			"qy": proj(0, 0, 2.5 * p),
			"qz": proj(0, 2.5 * p, 0),
		}
		load_starts = {
			"qx": proj(p, 0, 0),
			"qy": proj(0, 0, p),
			"qz": proj(0, p, 0),
		}
		for name in ("qx", "qy", "qz"):
			direction = _value(section, name, "нет")
			if direction != "нет":
				self.add_arrow(
					load_starts[name],
					load_points[name],
					15,
					5,
					"cube/{}/stress/{}".format(self.index, name),
					reverse=direction == "-",
				)

		m = 3 / 4
		moment_segments = {
			"mz": (
				(proj(-p * m, 0, p), proj(p * m, 0, p)),
				(proj(p, 0, -p * m), proj(p, 0, p * m)),
			),
			"my": (
				(proj(-p * m, p, 0), proj(p * m, p, 0)),
				(proj(p, -p * m, 0), proj(p, p * m, 0)),
			),
			"mx": (
				(proj(0, -p * m, p), proj(0, p * m, p)),
				(proj(0, p, -p * m), proj(0, p, p * m)),
			),
		}
		for name in ("mz", "my", "mx"):
			direction = _value(section, name, "нет")
			if direction == "нет":
				continue
			for segment_index, (start, end) in enumerate(moment_segments[name]):
				self.add_arrow(
					start,
					end,
					15,
					5,
					"cube/{}/moment/{}/{}".format(self.index, name, segment_index),
					reverse=direction == "-",
				)

		label_anchors = {
			"qx": load_points["qx"],
			"qy": load_points["qy"],
			"qz": load_points["qz"],
			"mx": proj(0, 0, p),
			"my": proj(0, p, 0),
			"mz": proj(p, 0, 0),
		}
		for label_index, name in enumerate(("qx", "qy", "qz", "mx", "my", "mz")):
			if _value(section, name, "нет") == "нет":
				continue
			label = self.task["labels"][label_index]
			suffix = "" if self.index == 0 else "2"
			value = _value(label, "text" + suffix, "")
			if self.index == 0:
				value = self.text_transform(value)
			center = label_anchors[name].translated(
				Point(
					float(_value(label, "x" + suffix, 0)),
					float(_value(label, "y" + suffix, 0)),
				)
			)
			self.add_text(
				center,
				value,
				"cube/{}/label/{}".format(self.index, name),
				kind="label",
			)

		return Group(
			self.objects,
			object_id="cube/{}".format(self.index),
			metadata=metadata(kind="cube", index=self.index),
		)


class StressCubeLayoutBuilder:
	def build(self, task, settings, text_metrics, text_transform=None):
		if text_metrics is None:
			raise ValueError("text_metrics is required for stress-cube layout")
		text_transform = text_transform or (lambda value: value)
		if not task.get("sections"):
			raise ValueError("stress-cube task requires at least one section")
		if len(task.get("labels", ())) != 6:
			raise ValueError("stress-cube task requires six labels")

		first = _Cube(settings, task, 0, 0, text_metrics, text_transform)
		objects = [first.build()]
		bounds = first.bounds

		if settings.second_cube:
			if len(task["sections"]) < 2:
				raise ValueError("second cube is enabled without a second section")
			second = _Cube(
				settings,
				task,
				1,
				first.bounds.width,
				text_metrics,
				text_transform,
			)
			objects.append(second.build())
			bounds = bounds.union(second.bounds)

		style = TextStyle(point_size=settings.font_size, italic=True)
		note_top = bounds.bottom
		for index, line in enumerate(text_transform(settings.note).splitlines()):
			measurement = text_metrics.measure(line, style)
			line_top = note_top + measurement.height * index
			objects.append(
				Text(
					Point(bounds.x, line_top + measurement.ascent),
					line,
					style=style,
					object_id="note/{}".format(index),
				)
			)
			note_bounds = Rect(
				bounds.x,
				line_top,
				measurement.width,
				measurement.height,
			)
			bounds = bounds.union(note_bounds)

		border_rect = Rect(
			bounds.x - settings.horizontal_border,
			bounds.y - settings.vertical_border,
			bounds.width + settings.horizontal_border * 2,
			bounds.height + settings.vertical_border * 2,
		)
		# The old transparent QGraphicsRectItem contributed half of its
		# cosmetic pen width to sceneBoundingRect.
		viewport = _expanded(border_rect, 0.5)
		return Scene(
			viewport=viewport,
			content_bounds=bounds,
			objects=objects,
		)
