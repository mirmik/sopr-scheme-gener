"""Qt-independent layout for the oblique-bending task."""

import math
from dataclasses import dataclass

from sopr_scheme_gener.layouts.beam_sections import (
	BeamSectionSpec,
	beam_section_width,
	build_beam_section,
)
from sopr_scheme_gener.layouts.projection3d import Projection3D
from sopr_scheme_gener.scene import (
	BLACK,
	WHITE,
	Color,
	Ellipse,
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
class ObliqueBendingLayoutSettings:
	width: float
	height: float
	console_enabled: bool = True
	console_width: float = 30.0
	axonometric: bool = False
	forty_five_degrees: bool = False
	x_offset: float = 30.0
	z_rotation_degrees: float = 30.0
	x_rotation_degrees: float = 20.0
	rod_length: float = 600.0
	dimension_offset: float = 100.0
	force_length: float = 60.0
	arrow_size: float = 15.0
	font_size: float = 12.0
	line_width: float = 2.0
	section: BeamSectionSpec = BeamSectionSpec()


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _add(a, b):
	return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(a, value):
	return (a[0] * value, a[1] * value, a[2] * value)


def _arrow_head(tip, angle, size, stroke):
	return Polygon(
		(
			tip,
			Point(
				tip.x - size * math.cos(angle) + size / 3 * math.sin(angle),
				tip.y + size * math.sin(angle) + size / 3 * math.cos(angle),
			),
			Point(
				tip.x - size * math.cos(angle) - size / 3 * math.sin(angle),
				tip.y + size * math.sin(angle) - size / 3 * math.cos(angle),
			),
		),
		stroke,
		Fill(BLACK),
		convex=True,
	)


def _arrow(start, end, stroke, size, object_id=None):
	dx, dy = end.x - start.x, end.y - start.y
	length = math.hypot(dx, dy)
	angle = math.atan2(-dy, dx)
	line_end = Point(
		start.x + dx / length * (length - size),
		start.y + dy / length * (length - size),
	)
	return Group(
		(
			Line(start, line_end, stroke),
			_arrow_head(end, angle, size, stroke),
		),
		object_id=object_id,
	)


def _text_by_points(
	start,
	end,
	value,
	style,
	text_metrics,
	alternate,
	offset,
	object_id,
):
	if start == end:
		return Group((), object_id=object_id)
	dx, dy = end.x - start.x, end.y - start.y
	length = math.hypot(dx, dy)
	ux, uy = dx / length, dy / length
	if alternate:
		ux, uy = -ux, -uy
	nx, ny = -uy, ux
	measurement = text_metrics.measure(value, style)
	return Text(
		Point(
			(start.x + end.x) / 2 + nx * (offset + measurement.width / 2),
			(start.y + end.y) / 2 + measurement.height / 4 + ny * offset,
		),
		value,
		style,
		TextAnchor.BASELINE_CENTER,
		object_id=object_id,
	)


def _dimension(start, end, offset, value, style, text_metrics, half, index):
	a = start.translated(offset)
	b = end.translated(offset)
	dx, dy = b.x - a.x, b.y - a.y
	angle = math.atan2(-dy, dx)
	center = Point((a.x + b.x) / 2, (a.y + b.y) / 2)
	return Group(
		(
			_arrow_head(a, angle + math.pi, 10, half),
			_arrow_head(b, angle, 10, half),
			Line(a, b, half),
			Line(a, b, half),
			Line(start, a, half),
			Line(end, b, half),
			_text_by_points(
				a,
				b,
				value,
				style,
				text_metrics,
				True,
				10,
				"section/{}/dimension/text".format(index),
			),
		),
		object_id="section/{}/dimension".format(index),
		metadata=metadata(kind="dimension", index=index),
	)


def _console(projection, start, end, width, main, axis):
	w = width
	s = 20
	p = projection.point
	objects = [
		Polygon(
			(
				p(w, start, -w),
				p(w, start, w),
				p(w, 0, w),
				p(w, 0, -w),
			),
			main,
			Fill(Color(220, 220, 220)),
		),
		Line(p(-w - s, start, 0), p(w + s, start, 0), axis),
		Line(p(0, start, -w - s), p(0, start, w + s), axis),
		Line(p(-w, 0, w), p(w, 0, w), main),
		Line(p(w, 0, w), p(w, 0, -w), main),
		Line(p(-w, start, -w), p(-w, start, w), main),
		Line(p(-w, start, w), p(w, start, w), main),
		Line(p(w, start, w), p(w, start, -w), main),
		Line(p(w, start, -w), p(-w, start, -w), main),
		Line(p(-w, start, w), p(-w, 0, w), main),
		Line(p(w, start, w), p(w, 0, w), main),
		Line(p(w, start, -w), p(w, 0, -w), main),
	]
	# The historical far end degenerates to a point (w2 == 0); retaining the
	# zero-length lines keeps painter order without introducing a new shape.
	zero = p(0, end, 0)
	root = p(0, start, 0)
	objects.extend(
		(
			Line(root, root, main),
			Line(zero, zero, main),
			Line(zero, root, main),
			Line(zero, root, main),
			Line(zero, root, main),
			Polygon((zero, zero, root, root), main, Fill(WHITE)),
			Polygon((zero, zero, root, root), main, Fill(Color(220, 220, 220))),
		)
	)
	return Group(
		objects,
		object_id="console",
		metadata=metadata(kind="console"),
	)


def _support(projection, point, vector, xvector, yvector, pattern, main, object_id):
	start = projection.vector(point)
	end = projection.vector(_add(point, vector))
	c0 = projection.vector(_add(_add(point, vector), xvector))
	c1 = projection.vector(_add(_add(_add(point, vector), xvector), yvector))
	c2 = projection.vector(_add(_add(_add(point, vector), _scale(xvector, -1)), yvector))
	c3 = projection.vector(_add(_add(point, vector), _scale(xvector, -1)))
	return Group(
		(
			Line(start, end, main),
			Line(c0, c3, main),
			Polygon((c0, c1, c2, c3), stroke=None, fill=Fill(BLACK, pattern)),
			Ellipse(Rect(start.x - 4, start.y - 4, 9, 9), main, Fill(WHITE)),
			Ellipse(Rect(end.x - 4, end.y - 4, 9, 9), main, Fill(WHITE)),
		),
		object_id=object_id,
		metadata=metadata(kind="support"),
	)


class ObliqueBendingLayoutBuilder:
	def build(
		self,
		task,
		settings,
		text_metrics,
		text_transform=None,
		length_text=None,
	):
		text_transform = text_transform or (lambda value: value)
		length_text = length_text or (
			lambda value, suffix="": "{}{}".format(value, suffix)
		)
		sections = task["sections"]
		nodes = task["betsect"]
		loads = task["sectforce"]
		if not sections:
			raise ValueError("oblique-bending requires at least one section")
		if len(nodes) != len(sections) + 1 or len(loads) != len(sections):
			raise ValueError("oblique-bending arrays have inconsistent lengths")
		total = sum(float(_value(section, "l", 0)) for section in sections)
		if total <= 0:
			raise ValueError("oblique-bending total length must be positive")

		main = Stroke(width=settings.line_width)
		half = Stroke(width=max(1, int(settings.line_width / 2)))
		double = Stroke(width=max(1, int(settings.line_width * 2)))
		axis = Stroke(width=max(1, int(settings.line_width / 2)), line_style="dash-dot")
		style = TextStyle(point_size=settings.font_size, italic=True)
		section_width = beam_section_width(settings.section)
		right = settings.width - 20
		right_zone = right - section_width + settings.x_offset
		z_rotation = math.radians(settings.z_rotation_degrees)
		x_rotation = math.radians(settings.x_rotation_degrees)
		sine = (
			0.5
			if settings.axonometric and settings.forty_five_degrees
			else math.sin(z_rotation)
		)
		projection = Projection3D(
			right_zone / 2 + sine * settings.rod_length / 2,
			80,
			z_rotation,
			x_rotation,
			axonometric=settings.axonometric,
			forty_five_degrees=settings.forty_five_degrees,
		)
		start, end = 20.0, 20.0 + settings.rod_length
		cumulative = [0.0]
		for section in sections:
			cumulative.append(cumulative[-1] + float(_value(section, "l", 0)))

		def coordinate(index):
			return start + settings.rod_length * cumulative[index] / total

		objects = list(
			build_beam_section(
				settings.section,
				right,
				settings.height / 2,
				settings.arrow_size,
				main,
				half,
				axis,
				style,
				text_metrics,
				text_transform,
			)
		)
		if settings.console_enabled:
			objects.append(
				_console(
					projection,
					start,
					end,
					settings.console_width,
					main,
					axis,
				)
			)

		screen_offset = Point(0, settings.dimension_offset)
		for index, section in enumerate(sections):
			objects.append(
				_dimension(
					projection.point(0, coordinate(index), 0),
					projection.point(0, coordinate(index + 1), 0),
					screen_offset,
					length_text(_value(section, "l"), "l"),
					style,
					text_metrics,
					half,
					index,
				)
			)

		for index, node in enumerate(nodes):
			y = coordinate(index)
			for axis_name, field, text_field, vector in (
				("x", "xF", "xFtxt", (1, 0, 0)),
				("y", "yF", "yFtxt", (0, 0, -1)),
			):
				variant = _value(node, field, "нет")
				if variant == "нет":
					continue
				sign = 1 if variant.startswith("+") else -1
				toward = variant.endswith("1")
				vector = _scale(vector, sign * settings.force_length)
				center = (0, y, 0)
				outer = _add(center, vector)
				a, b = (outer, center) if toward else (center, outer)
				start_point, end_point = projection.vector(a), projection.vector(b)
				objects.append(
					Group(
						(
							_arrow(start_point, end_point, double, 18),
							_text_by_points(
								start_point,
								end_point,
								text_transform(_value(node, text_field, "")),
								style,
								text_metrics,
								False,
								14 if axis_name == "x" else 10,
								"node/{}/force-{}/text".format(index, axis_name),
							),
						),
						object_id="node/{}/force-{}".format(index, axis_name),
						metadata=metadata(
							kind="force", axis=axis_name, variant=variant
						),
					)
				)

			for axis_name, field, text_field, side_vector in (
				("x", "xM", "xMtxt", (0, 0, 1)),
				("y", "yM", "yMtxt", (1, 0, 0)),
			):
				variant = _value(node, field, "нет")
				if variant == "нет":
					continue
				sign = 1 if variant == "+" else -1
				base = _add((0, y, 0), _scale(side_vector, 30))
				target = _add(base, (0, sign * 40, 0))
				objects.append(
					Group(
						(
							Line(
								projection.vector((0, y, 0)),
								projection.vector(base),
								main,
							),
							_arrow(
								projection.vector(base),
								projection.vector(target),
								main,
								18,
							),
							_text_by_points(
								projection.vector(base),
								projection.vector(target),
								text_transform(_value(node, text_field, "")),
								style,
								text_metrics,
								variant == "-",
								14,
								"node/{}/moment-{}/text".format(index, axis_name),
							),
						),
						object_id="node/{}/moment-{}".format(index, axis_name),
						metadata=metadata(
							kind="moment", axis=axis_name, direction=variant
						),
					)
				)

		objects.append(
			Line(
				projection.point(0, start, 0),
				projection.point(0, end, 0),
				double,
				object_id="rod/axis",
				metadata=metadata(kind="rod"),
			)
		)

		for index, load in enumerate(loads):
			for axis_name, field, text_field, vector in (
				("x", "xF", "xFtxt", (40, 0, 0)),
				("y", "yF", "yFtxt", (0, 0, 40)),
			):
				variant = _value(load, field, "нет")
				if variant == "нет":
					continue
				if variant == "-":
					vector = _scale(vector, -1)
				begin = (0, coordinate(index), 0)
				finish = (0, coordinate(index + 1), 0)
				length = abs(coordinate(index + 1) - coordinate(index))
				count = max(1, int(length / 30))
				children = [
					Line(
						projection.vector(_add(begin, vector)),
						projection.vector(_add(finish, vector)),
						half,
					),
					Line(
						projection.vector(_add(begin, vector)),
						projection.vector(begin),
						half,
					),
					Line(
						projection.vector(_add(finish, vector)),
						projection.vector(finish),
						half,
					),
				]
				for arrow_index in range(count + 1):
					ratio = arrow_index / count
					point = _add(begin, (0, length * ratio, 0))
					children.append(
						_arrow(
							projection.vector(_add(point, vector)),
							projection.vector(point),
							half,
							10,
						)
					)
				children.append(
					_text_by_points(
						projection.vector(_add(begin, vector)),
						projection.vector(_add(finish, vector)),
						text_transform(_value(load, text_field, "")),
						style,
						text_metrics,
						(axis_name == "x") == (variant == "+"),
						10,
						"section/{}/distributed-{}/text".format(
							index, axis_name
						),
					)
				)
				objects.append(
					Group(
						children,
						object_id="section/{}/distributed-{}".format(
							index, axis_name
						),
						metadata=metadata(
							kind="distributed-force",
							axis=axis_name,
							direction=variant,
						),
					)
				)

		for index, node in enumerate(nodes):
			y = coordinate(index)
			for axis_name, field in (("x", "xS"), ("y", "yS"), ("z", "zS")):
				variant = _value(node, field, "нет")
				if variant == "нет":
					continue
				sign = 1 if variant.startswith("+") else -1
				first = variant.endswith("1")
				if axis_name == "x":
					vector = (40 * sign, 0, 0)
					xvector = (0, 40, 0) if first else (0, 0, 80 / 3)
					yvector = (20 * sign, 0, 0) if first else (40 / 3 * sign, 0, 0)
					pattern = "forward-diagonal"
				elif axis_name == "y":
					vector = (0, 0, 35 * sign)
					xvector = (0, 40, 0) if first else (80 / 3, 0, 0)
					yvector = (0, 0, 40 / 3 * sign)
					pattern = "forward-diagonal" if first else "backward-diagonal"
				else:
					vector = (0, 40 * sign, 0)
					xvector = (0, 0, 80 / 3) if first else (80 / 3, 0, 0)
					yvector = (0, 30 * sign, 0)
					pattern = "backward-diagonal"
				objects.append(
					_support(
						projection,
						(0, y, 0),
						vector,
						xvector,
						yvector,
						pattern,
						main,
						"node/{}/support-{}".format(index, axis_name),
					)
				)

		return Scene(Rect(0, 0, settings.width, settings.height), tuple(objects))
