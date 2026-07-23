"""Qt-independent layout for editable spatial beam systems."""

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from sopr_scheme_gener.layouts.beam_sections import (
	BeamSectionSpec,
	build_beam_section,
)
from sopr_scheme_gener.layouts.projection3d import Projection3D
from sopr_scheme_gener.scene import (
	BLACK,
	TRANSPARENT,
	WHITE,
	Color,
	Ellipse,
	Fill,
	Group,
	Line,
	Point,
	Polygon,
	Rect,
	Rectangle,
	Scene,
	Stroke,
	Text,
	TextAnchor,
	TextStyle,
	metadata,
)


@dataclass(frozen=True)
class SpatialBeamsLayoutSettings:
	axonometric: bool = True
	z_rotation_degrees: float = 20.0
	x_rotation_degrees: float = 40.0
	z_scale: float = 0.6
	edge_length: float = 150.0
	horizontal_border: float = 10.0
	vertical_border: float = 10.0
	arrow_size: float = 15.0
	font_size: float = 12.0
	line_width: float = 2.0
	note: str = ""
	section: BeamSectionSpec = BeamSectionSpec()
	hovered_node: Optional[int] = None
	hovered_section: Optional[int] = None
	pressed: bool = False
	preview_point: Optional[Tuple[float, float, float]] = None
	selected_label: Optional[int] = None


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _vector(value):
	return tuple(float(component) for component in value)


def _add(a, b):
	return tuple(left + right for left, right in zip(a, b))


def _subtract(a, b):
	return tuple(left - right for left, right in zip(a, b))


def _multiply(value, scalar):
	return tuple(component * scalar for component in value)


class _Bounds:
	def __init__(self):
		self.value = None

	def add(self, rect):
		self.value = rect if self.value is None else self.value.union(rect)

	def geometry(self, points, stroke_width=0.0):
		rect = Rect.around(points)
		half = stroke_width / 2
		self.add(
			Rect(
				rect.x - half,
				rect.y - half,
				rect.width + stroke_width,
				rect.height + stroke_width,
			)
		)

	def line(self, start, end, stroke_width):
		dx, dy = end.x - start.x, end.y - start.y
		length = math.hypot(dx, dy)
		if length == 0:
			extension = stroke_width / 2
		else:
			extension = (
				stroke_width
				/ 2
				* (abs(dx) + abs(dy))
				/ length
			)
		self.add(
			Rect(
				min(start.x, end.x) - extension,
				min(start.y, end.y) - extension,
				abs(dx) + extension * 2,
				abs(dy) + extension * 2,
			)
		)

	def arrow(self, start, end):
		self.add(
			Rect(
				min(start.x, end.x) - 5,
				min(start.y, end.y) - 5,
				abs(end.x - start.x) + 10,
				abs(end.y - start.y) + 10,
			)
		)

	def text(self, center, measurement):
		self.add(
			Rect(
				center.x - measurement.width / 2,
				center.y - measurement.height / 2,
				measurement.width + 5,
				measurement.height,
			)
		)


class SpatialBeamsLayoutBuilder:
	def build(self, task, settings, text_metrics, text_transform=None):
		text_transform = text_transform or (lambda value: value)
		sections = tuple(task.get("sections", ()))
		nodes = tuple(task.get("nodes", ()))
		labels = tuple(task.get("labels", ()))
		main = Stroke(width=settings.line_width)
		half = Stroke(width=max(1, int(settings.line_width / 2)))
		axis = Stroke(
			width=max(1, int(settings.line_width / 2)),
			line_style="dash-dot",
		)
		green = Stroke(color=self._color(0, 255, 0), width=settings.line_width)
		blue = Stroke(color=self._color(0, 0, 255), width=settings.line_width)
		style = TextStyle(point_size=settings.font_size, italic=True)
		projection = self._projection(settings)
		objects = []
		bounds = _Bounds()

		def projected(value):
			return projection.point(*value)

		def node_position(node):
			return projected(
				(
					float(_value(node, "x")) * settings.edge_length,
					float(_value(node, "y")) * settings.edge_length,
					float(_value(node, "z")) * settings.edge_length,
				)
			)

		def add_line(start, end, stroke=main, object_id=None):
			objects.append(Line(start, end, stroke, object_id=object_id))
			bounds.line(start, end, stroke.width)

		def add_ellipse(center, radius, stroke=main, fill=Fill(), object_id=None):
			rect = Rect(center.x - radius, center.y - radius, radius * 2, radius * 2)
			objects.append(
				Ellipse(rect, stroke=stroke, fill=fill, object_id=object_id)
			)
			bounds.geometry(
				(Point(rect.left, rect.top), Point(rect.right, rect.bottom)),
				0 if stroke is None else stroke.width,
			)

		def arrow_group(start, end, stroke, size, object_id):
			dx, dy = end.x - start.x, end.y - start.y
			length = math.hypot(dx, dy)
			ux, uy = dx / length, dy / length
			normal = Point(uy, -ux)
			base = Point(end.x - ux * size[0], end.y - uy * size[0])
			bounds.arrow(start, end)
			return Group(
				(
					Line(start, end, stroke),
					Polygon(
						(
							end,
							Point(
								base.x + normal.x * size[1],
								base.y + normal.y * size[1],
							),
							Point(
								base.x - normal.x * size[1],
								base.y - normal.y * size[1],
							),
						),
						stroke,
						Fill(BLACK),
					),
				),
				object_id=object_id,
				metadata=metadata(kind="legacy-arrow"),
			)

		for index, section in enumerate(sections):
			start3 = (
				float(_value(section, "ax")) * settings.edge_length,
				float(_value(section, "ay")) * settings.edge_length,
				float(_value(section, "az")) * settings.edge_length,
			)
			end3 = (
				float(_value(section, "bx")) * settings.edge_length,
				float(_value(section, "by")) * settings.edge_length,
				float(_value(section, "bz")) * settings.edge_length,
			)
			start, end = projected(start3), projected(end3)
			add_line(start, end, main, "section/{}/beam".format(index))
			distributed = _value(section, "distrib")
			if distributed is not None:
				vector = projected(_multiply(_vector(distributed), 30))
				children = []
				for arrow_index in range(8):
					ratio = arrow_index / 7
					base = Point(
						start.x * (1 - ratio) + end.x * ratio,
						start.y * (1 - ratio) + end.y * ratio,
					)
					offset = Point(base.x - vector.x, base.y - vector.y)
					children.append(
						arrow_group(
							offset,
							base,
							half,
							(8, 2),
							"section/{}/distributed/arrow/{}".format(
								index, arrow_index
							),
						)
					)
				children.append(
					Line(
						Point(start.x - vector.x, start.y - vector.y),
						Point(end.x - vector.x, end.y - vector.y),
						half,
					)
				)
				objects.append(
					Group(
						children,
						object_id="section/{}/distributed".format(index),
						metadata=metadata(kind="distributed-load", index=index),
					)
				)
				bounds.add(
					Rect.around(
						(
							start,
							end,
							Point(start.x - vector.x, start.y - vector.y),
							Point(end.x - vector.x, end.y - vector.y),
						)
					)
				)

		for index, node in enumerate(nodes):
			self._add_support(
				node,
				index,
				settings,
				projected,
				objects,
				bounds,
				main,
			)
			base3 = (
				float(_value(node, "x")) * settings.edge_length,
				float(_value(node, "y")) * settings.edge_length,
				float(_value(node, "z")) * settings.edge_length,
			)
			for axis_name in ("x", "y", "z"):
				force = _value(node, "force_" + axis_name)
				if force is None:
					continue
				start = projected(_add(base3, _multiply(_vector(force[0]), 40)))
				end = projected(_add(base3, _multiply(_vector(force[1]), 40)))
				objects.append(
					arrow_group(
						start,
						end,
						main,
						(8, 4),
						"node/{}/force-{}".format(index, axis_name),
					)
				)
			torque = _value(node, "torque")
			if torque is not None and tuple(torque[0]) != (0, 0, 0):
				xvector = _multiply(_vector(torque[0]), 25)
				yvector = _multiply(_vector(torque[1]), 30)
				first = projected(_add(base3, xvector))
				second = projected(_subtract(base3, xvector))
				third = projected(_add(_add(base3, xvector), yvector))
				fourth = projected(_subtract(_subtract(base3, xvector), yvector))
				objects.append(
					Group(
						(
							arrow_group(
								first,
								third,
								half,
								(8, 4),
								"node/{}/torque/first".format(index),
							),
							arrow_group(
								second,
								fourth,
								half,
								(8, 4),
								"node/{}/torque/second".format(index),
							),
							Line(first, second, half),
						),
						object_id="node/{}/torque".format(index),
						metadata=metadata(kind="moment", node=index),
					)
				)
				bounds.add(
					Rect(
						min(p.x for p in (first, second, third, fourth)) - 5,
						min(p.y for p in (first, second, third, fourth)) - 5,
						max(p.x for p in (first, second, third, fourth))
						- min(p.x for p in (first, second, third, fourth))
						+ 10,
						max(p.y for p in (first, second, third, fourth))
						- min(p.y for p in (first, second, third, fourth))
						+ 10,
					)
				)

			center = node_position(node)
			objects.append(
				Ellipse(
					Rect(center.x - 40, center.y - 40, 80, 80),
					stroke=None,
					fill=Fill(TRANSPARENT),
					object_id="node/{}/hit".format(index),
					metadata=metadata(kind="node", index=index),
				)
			)

		for index, label in enumerate(labels):
			value = text_transform(_value(label, "text", ""))
			position = Point(*_value(label, "pos"))
			measurement = text_metrics.measure(value, style)
			if settings.selected_label == index:
				objects.append(
					Rectangle(
						Rect(
							position.x - measurement.width / 2,
							position.y - measurement.height / 2,
							measurement.width + 5,
							measurement.height,
						),
						stroke=None,
						fill=Fill(self._color(0, 255, 0, 178)),
					)
				)
			objects.append(
				Text(
					position,
					value,
					style,
					TextAnchor.CENTER,
					object_id="label/{}".format(index),
					metadata=metadata(kind="label", index=index),
				)
			)
			bounds.text(position, measurement)

		if bounds.value is None:
			bounds.add(Rect(-20, -20, 40, 40))
			objects.append(
				Rectangle(
					Rect(-20, -20, 40, 40),
					stroke=Stroke(TRANSPARENT),
					fill=Fill(TRANSPARENT),
				)
			)

		pre_section = bounds.value
		if settings.section.section_type != "Нет":
			section_objects = build_beam_section(
				settings.section,
				right=175,
				hcenter=0,
				arrow_size=settings.arrow_size,
				main=main,
				half=half,
				axis=axis,
				text_style=style,
				text_metrics=text_metrics,
				text_transform=text_transform,
			)
			offset = Point(
				pre_section.right,
				pre_section.y + pre_section.height / 2,
			)
			objects.append(
				Group(
					section_objects,
					offset=offset,
					object_id="cross-section",
					metadata=metadata(kind="cross-section"),
				)
			)
			# SectionItem historically publishes a fixed compatibility bound.
			bounds.add(Rect(offset.x + 35, offset.y - 110, 140, 220))

		if settings.hovered_node is not None:
			node = nodes[settings.hovered_node]
			center = node_position(node)
			add_ellipse(center, 3, green, Fill(self._color(0, 255, 0)))
			if settings.pressed:
				origin = (
					float(_value(node, "x")),
					float(_value(node, "y")),
					float(_value(node, "z")),
				)
				for candidate_index, delta in enumerate(
					(
						(1, 0, 0),
						(-1, 0, 0),
						(0, 1, 0),
						(0, -1, 0),
						(0, 0, 1),
						(0, 0, -1),
					)
				):
					candidate = _add(origin, delta)
					if self._has_section(sections, origin, candidate):
						continue
					end = projected(_multiply(candidate, settings.edge_length))
					add_ellipse(end, 3, green, object_id=None)
					add_line(center, end, green)
					objects.append(
						Ellipse(
							Rect(end.x - 20, end.y - 20, 40, 40),
							stroke=None,
							fill=Fill(TRANSPARENT),
							object_id="candidate/{}".format(candidate_index),
							metadata=metadata(
								kind="candidate",
								x=candidate[0],
								y=candidate[1],
								z=candidate[2],
							),
						)
					)
				if settings.preview_point is not None:
					end = projected(
						_multiply(settings.preview_point, settings.edge_length)
					)
					add_ellipse(end, 3, blue)
					add_line(center, end, blue)

		if settings.hovered_section is not None:
			section = sections[settings.hovered_section]
			add_line(
				projected(
					_multiply(
						(
							float(_value(section, "ax")),
							float(_value(section, "ay")),
							float(_value(section, "az")),
						),
						settings.edge_length,
					)
				),
				projected(
					_multiply(
						(
							float(_value(section, "bx")),
							float(_value(section, "by")),
							float(_value(section, "bz")),
						),
						settings.edge_length,
					)
				),
				blue,
			)

		for index, section in enumerate(sections):
			midpoint = (
				(float(_value(section, "ax")) + float(_value(section, "bx"))) / 2,
				(float(_value(section, "ay")) + float(_value(section, "by"))) / 2,
				(float(_value(section, "az")) + float(_value(section, "bz"))) / 2,
			)
			center = projected(_multiply(midpoint, settings.edge_length))
			objects.append(
				Ellipse(
					Rect(center.x - 35, center.y - 35, 70, 70),
					stroke=None,
					fill=Fill(TRANSPARENT),
					object_id="section/{}/hit".format(index),
					metadata=metadata(kind="section", index=index),
				)
			)

		note_lines = tuple(text_transform(settings.note).splitlines())
		note_base = bounds.value
		for index, line in enumerate(note_lines):
			line_y = (
				note_base.bottom
				+ text_metrics.measure(line, style).height * index
			)
			objects.append(
				Text(
					Point(
						note_base.x,
						line_y,
					),
					line,
					style,
					TextAnchor.TOP_LEFT,
					object_id="note/{}".format(index),
					metadata=metadata(kind="qgraphics-text"),
				)
			)
			measurement = text_metrics.measure(line, style)
			bounds.add(
				Rect(
					note_base.x,
					line_y,
					measurement.width + 8,
					measurement.height + 8,
				)
			)

		content = bounds.value
		border = Rect(
			content.x - settings.horizontal_border,
			content.y - settings.vertical_border,
			content.width + settings.horizontal_border * 2,
			content.height + settings.vertical_border * 2,
		)
		objects.append(
			Rectangle(
				border,
				stroke=Stroke(TRANSPARENT),
				fill=Fill(TRANSPARENT),
				object_id="viewport-border",
			)
		)
		viewport = Rect(
			border.x - 0.5,
			border.y - 0.5,
			border.width + 1,
			border.height + 1,
		)
		return Scene(viewport, tuple(objects), content_bounds=content)

	@staticmethod
	def _projection(settings):
		pitch = math.radians(settings.x_rotation_degrees)
		return Projection3D(
			0,
			0,
			math.radians(settings.z_rotation_degrees),
			pitch,
			axonometric=settings.axonometric,
			forty_five_degrees=not settings.axonometric,
			diagonal_scale=math.cos(pitch) * settings.z_scale,
			diagonal_y_scale=math.sin(pitch) * settings.z_scale,
		)

	@staticmethod
	def _add_support(node, index, settings, projected, objects, bounds, main):
		support = _value(node, "sharn", "нет")
		if support == "нет":
			return
		base = (
			float(_value(node, "x")) * settings.edge_length,
			float(_value(node, "y")) * settings.edge_length,
			float(_value(node, "z")) * settings.edge_length,
		)
		if support == "врез":
			center = projected(base)
			objects.append(
				Ellipse(
					Rect(center.x - 4.5, center.y - 4.5, 9, 9),
					main,
					Fill(WHITE),
					object_id="node/{}/support".format(index),
					metadata=metadata(kind="support", support_type=support),
				)
			)
			bounds.geometry(
				(
					Point(center.x - 4.5, center.y - 4.5),
					Point(center.x + 4.5, center.y + 4.5),
				),
				main.width,
			)
			return
		direction = _vector(_value(node, "sharn_vec", (0, 0, 0)))
		secondary = _vector(_value(node, "sharn_vec2", (0, 0, 0)))
		if support == "zadelka":
			if direction[0] == 1:
				e1, e2, e0 = (0, 1, 0), (0, 0, 1), (-1, 0, 0)
			elif direction[1] == 1:
				e1, e2, e0 = (1, 0, 0), (0, 0, 1), (0, -1, 0)
			else:
				e1, e2, e0 = (1, 0, 0), (0, 1, 0), (0, 0, -1)
			points = tuple(
				_add(base, _add(_multiply(e1, sx * 20), _multiply(e2, sy * 20)))
				for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))
			)
			rear = tuple(_add(point, _multiply(e0, 20)) for point in points)
			projected_points = tuple(projected(point) for point in points)
			projected_rear = tuple(projected(point) for point in rear)
			children = []
			for start, end in zip(
				projected_points,
				projected_points[1:] + projected_points[:1],
			):
				children.append(Line(start, end, main))
				bounds.geometry((start, end), main.width)
			for point_index in (1, 2, 3):
				children.append(
					Line(
						projected_points[point_index],
						projected_rear[point_index],
						main,
					)
				)
				bounds.geometry(
					(
						projected_points[point_index],
						projected_rear[point_index],
					),
					main.width,
				)
			objects.append(
				Group(
					children,
					object_id="node/{}/support".format(index),
					metadata=metadata(kind="support", support_type=support),
				)
			)
			return
		point = _add(base, _multiply(direction, 6))
		vector = _multiply(direction, 20)
		xvector = _multiply(secondary, 20)
		yvector = _multiply(direction, 15)
		a = projected(base)
		b = projected(_add(point, vector))
		corners = (
			projected(_add(_add(point, vector), xvector)),
			projected(_add(_add(_add(point, vector), xvector), yvector)),
			projected(_add(_subtract(_add(point, vector), xvector), yvector)),
			projected(_subtract(_add(point, vector), xvector)),
		)
		objects.append(
			Group(
				(
					Line(a, b, main),
					Line(corners[0], corners[3], main),
					Polygon(corners, stroke=None, fill=Fill(BLACK, "backward-diagonal")),
					Ellipse(Rect(a.x - 3.5, a.y - 3.5, 7, 7), main, Fill(WHITE)),
					Ellipse(Rect(b.x - 3.5, b.y - 3.5, 7, 7), main, Fill(WHITE)),
				),
				object_id="node/{}/support".format(index),
				metadata=metadata(kind="support", support_type=support),
			)
		)
		center = projected(_add(point, vector))
		bounds.add(Rect(center.x - 25, center.y - 25, 50, 50))

	@staticmethod
	def _has_section(sections, start, end):
		for section in sections:
			a = (
				float(_value(section, "ax")),
				float(_value(section, "ay")),
				float(_value(section, "az")),
			)
			b = (
				float(_value(section, "bx")),
				float(_value(section, "by")),
				float(_value(section, "bz")),
			)
			if (a == start and b == end) or (a == end and b == start):
				return True
		return False

	@staticmethod
	def _color(red, green, blue, alpha=255):
		return Color(red, green, blue, alpha)
