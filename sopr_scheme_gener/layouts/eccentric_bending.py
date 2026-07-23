"""Qt-independent layout for the eccentric-bending task."""

import math
from dataclasses import dataclass

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
	Rectangle,
	Scene,
	Stroke,
	Text,
	TextAnchor,
	TextStyle,
	metadata,
)


@dataclass(frozen=True)
class EccentricBendingLayoutSettings:
	width: float
	height: float
	hcenter: float
	x_size: float = 200.0
	y_size: float = 100.0
	x_text: str = "размер_x"
	y_text: str = "размер_y"
	length_text: str = "длина"
	axonometric: bool = False
	sixty_degrees: bool = True
	section_type: str = "труба"
	console_length: float = 100.0
	z_rotation_degrees: float = 30.0
	x_rotation_degrees: float = 30.0
	rod_length: float = 600.0
	dimension_offset: float = 100.0
	force_length: float = 60.0
	font_size: float = 12.0
	line_width: float = 2.0


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _normalized_rect(first, second):
	left, right = sorted((first.x, second.x))
	top, bottom = sorted((first.y, second.y))
	return Rect(left, top, right - left, bottom - top)


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


def _arrow(start, end, stroke, size):
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
		)
	)


def _text_by_points(start, end, value, style, metrics, alternate, offset, object_id):
	if start == end:
		return Group((), object_id=object_id)
	dx, dy = end.x - start.x, end.y - start.y
	length = math.hypot(dx, dy)
	ux, uy = dx / length, dy / length
	if alternate:
		ux, uy = -ux, -uy
	nx, ny = -uy, ux
	measurement = metrics.measure(value, style)
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


def _dimension(
	start,
	end,
	offset,
	text_offset,
	value,
	style,
	metrics,
	half,
	object_id,
	splashed=False,
	textline_from=None,
):
	a = start.translated(offset)
	b = end.translated(offset)
	dx, dy = b.x - a.x, b.y - a.y
	angle = math.atan2(-dy, dx)
	a_angle = angle if splashed else angle + math.pi
	b_angle = angle + math.pi if splashed else angle
	center = Point((a.x + b.x) / 2, (a.y + b.y) / 2)
	measurement = metrics.measure(value, style)
	text_position = Point(
		center.x + text_offset.x - measurement.width / 2,
		center.y + text_offset.y + measurement.height / 4,
	)
	children = [
		_arrow_head(a, a_angle, 12, half),
		_arrow_head(b, b_angle, 12, half),
		Line(a, b, half),
		Line(a, b, half),
		Line(start, a, half),
		Line(end, b, half),
		Text(text_position, value, style, object_id=object_id + "/text"),
	]
	if textline_from is not None:
		shelf_start = Point(
			text_position.x,
			text_position.y + measurement.height / 8,
		)
		shelf_end = Point(
			text_position.x + measurement.width,
			text_position.y + measurement.height / 8,
		)
		children.extend(
			(
				Line(shelf_start, shelf_end, half),
				Line(start if textline_from == "start" else end, shelf_start, half),
			)
		)
	return Group(
		children,
		object_id=object_id,
		metadata=metadata(kind="dimension"),
	)


def _force_label(start, end, value, policy, style, metrics, main, double, object_id):
	if policy in (None, True, False):
		policy = "1"
	if policy in ("5", "6"):
		return Group(
			(
				_text_by_points(
					start,
					end,
					value,
					style,
					metrics,
					policy == "6",
					10 if abs(end.y - start.y) > abs(end.x - start.x) else 14,
					object_id + "/text",
				),
				_arrow(start, end, double, 14),
			),
			object_id=object_id,
			metadata=metadata(kind="force", policy=policy),
		)
	measurement = metrics.measure(value, style)
	if policy == "1":
		position = Point(end.x + 7, end.y + measurement.height / 4)
	elif policy == "2":
		position = Point(
			end.x - 8 - measurement.width,
			end.y + measurement.height / 4,
		)
	elif policy == "3":
		position = Point(start.x + 7, start.y + measurement.height / 4)
	else:
		position = Point(
			start.x - 8 - measurement.width,
			start.y + measurement.height / 4,
		)
	return Group(
		(
			Rectangle(
				Rect(
					position.x - 2,
					position.y + measurement.height / 7,
					measurement.width + 4,
					measurement.height * 11 / 21,
				),
				stroke=None,
				fill=Fill(WHITE),
			),
			Text(position, value, style),
			_arrow(start, end, double, 14),
		),
		object_id=object_id,
		metadata=metadata(kind="force", policy=policy),
	)


class EccentricBendingLayoutBuilder:
	def build(self, task, settings, text_metrics, text_transform=None):
		text_transform = text_transform or (lambda value: value)
		records = task["sections"]
		if len(records) != 8:
			raise ValueError("eccentric-bending requires eight force points")
		main = Stroke(width=settings.line_width)
		half = Stroke(width=max(1, int(settings.line_width / 2)))
		double = Stroke(width=max(1, int(settings.line_width * 2)))
		axis = Stroke(width=max(1, int(settings.line_width / 2)), line_style="dash-dot")
		style = TextStyle(point_size=settings.font_size, italic=True)
		a = settings.x_size
		b = settings.y_size
		length = settings.console_length
		z_rotation = math.radians(settings.z_rotation_degrees)
		x_rotation = math.radians(settings.x_rotation_degrees)
		initial = Projection3D(
			0,
			0,
			z_rotation,
			x_rotation,
			axonometric=settings.axonometric,
			forty_five_degrees=settings.sixty_degrees,
			diagonal_scale=math.cos(math.radians(60)),
			diagonal_y_scale=math.sin(math.radians(60)),
		)
		rear_initial = initial.point(0, -length, 0)
		base_x = settings.width / 2 - rear_initial.x / 2
		base_y = (
			settings.hcenter
			- rear_initial.y / 2
			- settings.dimension_offset / 8 * 3
		)
		projection = Projection3D(
			base_x,
			base_y,
			z_rotation,
			x_rotation,
			axonometric=settings.axonometric,
			forty_five_degrees=settings.sixty_degrees,
			diagonal_scale=math.cos(math.radians(60)),
			diagonal_y_scale=math.sin(math.radians(60)),
		)
		p = projection.point
		dim = settings.dimension_offset
		s = 25
		objects = []

		if settings.section_type in ("круг", "труба"):
			objects.append(
				Polygon(
					(
						p(-a / 2 - s, -length, -a / 2 - s),
						p(-a / 2 - s, -length, a / 2 + s),
						p(a / 2 + s, -length, a / 2 + s),
						p(a / 2 + s, -length, -a / 2 - s),
					),
					stroke=None,
					fill=Fill(Color(220, 220, 220)),
				)
			)
			objects.append(
				Ellipse(
					_normalized_rect(
						p(-a / 2, -length, -a / 2),
						p(a / 2, -length, a / 2),
					),
					main,
					Fill(WHITE),
				)
			)
			rear = p(0, -length, 0)
			front = p(0, 0, 0)
			dx = a / 2 * math.sin(math.radians(60))
			dy = a / 2 * math.cos(math.radians(60))
			rear_left = Point(rear.x - dx, rear.y - dy)
			rear_right = Point(rear.x + dx + 1.5, rear.y + dy + 1.5)
			front_right = Point(front.x + dx + 1.5, front.y + dy + 1.5)
			front_left = Point(front.x - dx, front.y - dy)
			objects.extend(
				(
					Polygon(
						(rear_left, rear_right, front_right, front_left),
						stroke=None,
						fill=Fill(WHITE),
					),
					Line(rear_left, front_left, main),
					Line(rear_right, front_right, main),
					Line(p(a / 2, -length, 0), p(a / 2, 0, 0), half),
					Line(p(0, -length, a / 2), p(0, 0, a / 2), half),
					Ellipse(
						_normalized_rect(
							p(-a / 2, 0, -a / 2),
							p(a / 2, 0, a / 2),
						),
						main,
						Fill(WHITE),
						object_id="section/outer",
						metadata=metadata(kind="section"),
					),
				)
			)
			if settings.section_type == "труба":
				objects.extend(
					(
						Ellipse(
							_normalized_rect(
								p(-b / 2, 0, -b / 2),
								p(b / 2, 0, b / 2),
							),
							main,
							Fill(WHITE),
							object_id="section/inner",
						),
						Ellipse(
							_normalized_rect(
								p(-(a + b) / 4, 0, -(a + b) / 4),
								p((a + b) / 4, 0, (a + b) / 4),
							),
							axis,
							Fill(Color(0, 0, 0, 0)),
							object_id="section/midline",
						),
					)
				)
				radius = (a + b) / 4
			else:
				radius = a / 2

			objects.append(
				_dimension(
					p(radius, 0, 0),
					p(-radius, 0, 0),
					Point(0, dim + a / 2),
					Point(0, 0),
					"",
					style,
					text_metrics,
					half,
					"dimension/diameter",
				)
			)
			if settings.section_type == "труба":
				angle = math.radians(67.5)
				outer = p(a / 2 * math.cos(angle), 0, a / 2 * math.sin(angle))
				inner = p(b / 2 * math.cos(angle), 0, b / 2 * math.sin(angle))
				objects.append(
					_dimension(
						outer,
						inner,
						Point(0, 0),
						Point(
							(outer.x - inner.x) / 2 + 30,
							(outer.y - inner.y) / 2 - 30,
						),
						text_transform(settings.y_text),
						style,
						text_metrics,
						half,
						"dimension/thickness",
						splashed=True,
						textline_from="start",
					)
				)
			objects.append(
				_dimension(
					p(a / 2, -length, 0),
					p(a / 2, 0, 0),
					Point(dim, 0),
					Point(0, 0),
					"",
					style,
					text_metrics,
					half,
					"dimension/length",
				)
			)
			objects.append(
				_text_by_points(
					p(-a / 2, 0, -a / 2).translated(Point(0, dim)),
					p(a / 2, 0, -a / 2).translated(Point(0, dim)),
					text_transform(settings.x_text),
					style,
					text_metrics,
					True,
					14,
					"dimension/diameter/label",
				)
			)
			objects.append(
				_text_by_points(
					p(a / 2, -length, 0).translated(Point(dim, 0)),
					p(a / 2, 0, 0).translated(Point(dim, 0)),
					text_transform(settings.length_text),
					style,
					text_metrics,
					True,
					14,
					"dimension/length/label",
				)
			)
			objects.extend(
				(
					Line(p(-a / 2 - s, 0, 0), p(a / 2 + s, 0, 0), axis),
					Line(p(0, 0, -a / 2 - s), p(0, 0, a / 2 + s), axis),
				)
			)
			ref_radius = (a + b) / 4 if settings.section_type == "труба" else a / 2
			refpoints = [
				p(-ref_radius / math.sqrt(2), 0, ref_radius / math.sqrt(2)),
				p(0, 0, ref_radius),
				p(ref_radius / math.sqrt(2), 0, ref_radius / math.sqrt(2)),
				p(-ref_radius, 0, 0),
				p(ref_radius, 0, 0),
				p(-ref_radius / math.sqrt(2), 0, -ref_radius / math.sqrt(2)),
				p(0, 0, -ref_radius),
				p(ref_radius / math.sqrt(2), 0, -ref_radius / math.sqrt(2)),
			]
		else:
			if settings.section_type == "ромб":
				front_points = (
					p(-a / 2, 0, 0),
					p(0, 0, b / 2),
					p(a / 2, 0, 0),
					p(0, 0, -b / 2),
				)
			else:
				front_points = (
					p(-a / 2, 0, -b / 2),
					p(-a / 2, 0, b / 2),
					p(a / 2, 0, b / 2),
					p(a / 2, 0, -b / 2),
				)
			rear_points = tuple(
				p(
					(-a / 2, -a / 2, a / 2, a / 2)[index],
					-length,
					(-b / 2, b / 2, b / 2, -b / 2)[index],
				)
				for index in range(4)
			)
			objects.append(
				Polygon(
					(
						p(-a / 2 - s, -length, -b / 2 - s),
						p(-a / 2 - s, -length, b / 2 + s),
						p(a / 2 + s, -length, b / 2 + s),
						p(a / 2 + s, -length, -b / 2 - s),
					),
					stroke=None,
					fill=Fill(Color(220, 220, 220)),
				)
			)
			objects.extend(
				(
					Polygon(front_points, main, Fill(WHITE), object_id="section/outer"),
					Polygon(
						(front_points[1], rear_points[1], rear_points[2], front_points[2]),
						main,
						Fill(WHITE),
					),
					Polygon(
						(front_points[2], rear_points[2], rear_points[3], front_points[3]),
						main,
						Fill(WHITE),
					),
				)
			)
			objects.extend(
				(
					Line(p(-a / 2 - s, 0, 0), p(a / 2 + s, 0, 0), axis),
					Line(p(0, 0, -b / 2 - s), p(0, 0, b / 2 + s), axis),
				)
			)
			refpoints = [
				p(-a / 2, 0, b / 2),
				p(0, 0, b / 2),
				p(a / 2, 0, b / 2),
				p(-a / 2, 0, 0),
				p(a / 2, 0, 0),
				p(-a / 2, 0, -b / 2),
				p(0, 0, -b / 2),
				p(a / 2, 0, -b / 2),
			]

		origin = p(0, 0, 0)
		for index, (record, reference) in enumerate(zip(records, refpoints)):
			for axis_name, field, text_field, policy_field, variants in (
				(
					"x",
					"Fx",
					"Fx_txt",
					"Fx_txt_alttxt",
					{
						"справа +": (1, False),
						"справа -": (1, True),
						"слева +": (-1, True),
						"слева -": (-1, False),
					},
				),
				(
					"y",
					"Fy",
					"Fy_txt",
					"Fy_txt_alttxt",
					{
						"сверху +": (1, False),
						"сверху -": (1, True),
						"снизу +": (-1, True),
						"снизу -": (-1, False),
					},
				),
				(
					"z",
					"Fz",
					"Fz_txt",
					"Fz_txt_alttxt",
					{"+": (1, True), "-": (1, False)},
				),
			):
				variant = _value(record, field, "нет")
				if variant == "нет":
					continue
				sign, reverse = variants[variant]
				if axis_name == "x":
					vector_end = p(sign * settings.force_length, 0, 0)
				elif axis_name == "y":
					vector_end = p(0, 0, sign * settings.force_length)
				else:
					vector_end = p(0, settings.force_length, 0)
				delta = Point(vector_end.x - origin.x, vector_end.y - origin.y)
				outer = reference.translated(delta)
				start_point, end_point = (
					(outer, reference) if reverse else (reference, outer)
				)
				objects.append(
					_force_label(
						start_point,
						end_point,
						text_transform(_value(record, text_field, "")),
						_value(record, policy_field, "1"),
						style,
						text_metrics,
						main,
						double,
						"point/{}/force-{}".format(index, axis_name),
					)
				)
		return Scene(Rect(0, 0, settings.width, settings.height), tuple(objects))
