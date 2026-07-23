"""Qt-independent layout for the first rod-system task."""

import math
from dataclasses import dataclass

from sopr_scheme_gener.scene import (
	BLACK,
	WHITE,
	Arrow,
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
class RodSystem1LayoutSettings:
	width: float
	height: float
	hcenter: float
	text_height: float = 0.0
	base_height: float = 22.0
	dimension_level: float = 80.0
	right_margin: float = 60.0
	rod_force_offset: float = 28.0
	arrow_size: float = 14.0
	font_size: float = 12.0
	line_width: float = 2.0
	left_support: str = "нет"
	right_support: str = "нет"
	highlighted_node: int = -1


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _ellipse(center, radius, stroke, fill=Fill(WHITE), object_id=None):
	return Ellipse(
		Rect(center.x - radius, center.y - radius, radius * 2 + 1, radius * 2 + 1),
		stroke,
		fill,
		object_id=object_id,
	)


def _arrow(start, end, stroke, size, object_id, head_stroke=None):
	return Arrow(
		start,
		end,
		stroke,
		head_length=size,
		head_width=size * 2 / 3,
		head_stroke=head_stroke or stroke,
		object_id=object_id,
	)


def _dimension(p0, p1, level, stroke, style, text, text_metrics, index):
	center = Point((p0.x + p1.x) / 2, level)
	size = 10
	left_tip = Point(p0.x, level)
	right_tip = Point(p1.x + 0.5, level + 0.5)
	measurement = text_metrics.measure(text, style)
	return Group(
		(
			Line(p0, left_tip, stroke),
			Line(p1, Point(p1.x, level), stroke),
			Line(center, left_tip, stroke),
			Polygon(
				(
					left_tip,
					Point(left_tip.x + size, left_tip.y + size / 3),
					Point(left_tip.x + size, left_tip.y - size / 3),
				),
				stroke,
				Fill(BLACK),
				convex=True,
			),
			Line(center, Point(p1.x, level), stroke),
			Polygon(
				(
					right_tip,
					Point(p1.x - size + 0.5, level + size / 3 + 0.5),
					Point(p1.x - size + 0.5, level - size / 3 + 0.5),
				),
				stroke,
				Fill(BLACK),
				convex=True,
			),
			Text(
				Point(
					center.x,
					level + measurement.height / 4 - 8,
				),
				text,
				style,
				TextAnchor.BASELINE_CENTER,
				object_id="dimension/{}/text".format(index),
			),
		),
		object_id="dimension/{}".format(index),
		metadata=metadata(kind="dimension", index=index),
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
	leader=None,
):
	if start == end:
		return Group((), object_id=object_id)
	dx = end.x - start.x
	dy = end.y - start.y
	length = math.hypot(dx, dy)
	ux, uy = dx / length, dy / length
	if alternate:
		ux, uy = -ux, -uy
	nx, ny = -uy, ux
	measurement = text_metrics.measure(value, style)
	center = Point(
		(start.x + end.x) / 2
		+ nx * (offset + measurement.width / 2),
		(start.y + end.y) / 2
		+ measurement.height / 4
		+ ny * offset,
	)
	children = [
		Text(
			center,
			value,
			style,
			TextAnchor.BASELINE_CENTER,
			object_id=object_id + "/text",
		)
	]
	if leader is not None:
		shelf_y = center.y + measurement.height / 8
		children.extend(
			(
				Line(
					Point(center.x - measurement.width / 2, shelf_y),
					Point(center.x + measurement.width / 2, shelf_y),
					Stroke(width=1),
				),
				Line(
					leader,
					Point(
						center.x + (-1 if not alternate else 1) * measurement.width / 2,
						shelf_y,
					),
					Stroke(width=1),
				),
			)
		)
	return Group(
		children,
		object_id=object_id,
		metadata=metadata(kind="label"),
	)


def _angled_text(start, end, value, style, text_metrics, alternate, offset, object_id):
	if alternate:
		start, end = end, start
	if start == end:
		return Group((), object_id=object_id)
	dx = end.x - start.x
	dy = end.y - start.y
	angle = math.atan2(dy, dx)
	sector = angle / (2 * math.pi) - math.floor(angle / (2 * math.pi))
	rotation = 180 if 0.25 < sector < 0.75 else 0
	if rotation:
		offset = -10
	rotation += angle * 180 / math.pi
	measurement = text_metrics.measure(value, style)
	baseline_offset = measurement.height / 4 - offset + 1
	radians = rotation * math.pi / 180
	center = Point((start.x + end.x) / 2, (start.y + end.y) / 2)
	position = Point(
		center.x - math.sin(radians) * baseline_offset,
		center.y + math.cos(radians) * baseline_offset,
	)
	return Text(
		position,
		value,
		style,
		TextAnchor.BASELINE_CENTER,
		rotation_degrees=rotation,
		object_id=object_id,
	)


def _fixed_rod_end(center, positive, main, index):
	width = 30
	depth = 10
	radius = 5
	angle = -math.pi / 2 if positive else math.pi / 2
	def rotate(point):
		return Point(
			center.x + point.x * math.cos(angle) - point.y * math.sin(angle),
			center.y + point.y * math.cos(angle) + point.x * math.sin(angle),
		)
	points = (
		rotate(Point(0, width)),
		rotate(Point(0, -width)),
		rotate(Point(depth, -width)),
		rotate(Point(depth, width)),
	)
	return Group(
		(
			Polygon(
				points,
				stroke=None,
				fill=Fill(BLACK, "backward-diagonal"),
				convex=True,
			),
			Line(points[0], points[1], main),
			_ellipse(center, radius, main),
		),
		object_id="rod/{}/fixed-end".format(index),
		metadata=metadata(kind="fixed-end", index=index),
	)


def _terminator(center, angle, half_width, depth, main):
	normal = angle + math.pi / 2
	first = Point(
		center.x + math.cos(normal) * half_width,
		center.y + math.sin(normal) * half_width,
	)
	second = Point(
		center.x - math.cos(normal) * half_width,
		center.y - math.sin(normal) * half_width,
	)
	offset = Point(math.sin(normal) * depth, -math.cos(normal) * depth)
	points = (first, second, second.translated(offset), first.translated(offset))
	return (
		Polygon(points, stroke=None, fill=Fill(WHITE)),
		Line(first, second, main),
		Polygon(points, stroke=None, fill=Fill(BLACK, "backward-diagonal")),
	)


def _support(center, support_type, side, main, double, object_id, index):
	angle = {
		"left": math.pi,
		"right": 0,
		"down": math.pi / 2,
	}[side]
	radius = 4
	term_radius = 25
	base = Point(
		center.x + term_radius * math.cos(angle),
		center.y + term_radius * math.sin(angle),
	)
	children = []
	if support_type == "1":
		children.extend(
			(
				Line(center, base, double),
				*_terminator(base, angle, 25, 10, main),
				_ellipse(center, radius, main),
				_ellipse(
					Point(
						center.x + (term_radius - radius) * math.cos(angle),
						center.y + (term_radius - radius) * math.sin(angle),
					),
					radius,
					main,
				),
			)
		)
	else:
		half_width = 25 * 2 / 3
		normal = angle + math.pi / 2
		left = Point(
			base.x + math.cos(normal) * half_width,
			base.y + math.sin(normal) * half_width,
		)
		right = Point(
			base.x - math.cos(normal) * half_width,
			base.y - math.sin(normal) * half_width,
		)
		children.extend(
			(
				*_terminator(base, angle, 25, 10, main),
				Line(left, right, main),
				Line(center, left, main),
				Line(center, right, main),
				_ellipse(center, radius, main),
			)
		)
	return Group(
		children,
		object_id=object_id,
		metadata=metadata(
			kind="support",
			index=index,
			side=side,
			support_type=support_type,
		),
	)


def _with_antialias(group, enabled):
	return Group(
		group.children,
		offset=group.offset,
		object_id=group.object_id,
		metadata=group.metadata,
		antialias=enabled,
	)


class RodSystem1LayoutBuilder:
	def build(self, task, settings, text_metrics, text_transform=None, length_text=None):
		text_transform = text_transform or (lambda value: value)
		length_text = length_text or (lambda value, suffix="": str(value) + suffix)
		sections = task["sections"]
		nodes = task["betsect"]
		if not sections:
			raise ValueError("rod-system-1 requires at least one section")
		if len(nodes) != len(sections) + 1:
			raise ValueError("rod-system-1 arrays have inconsistent lengths")
		if sum(_value(section, "l", 0) for section in sections) == 0:
			raise ValueError("rod-system-1 total section length must be non-zero")

		main = Stroke(width=settings.line_width)
		half = Stroke(width=max(1, int(settings.line_width / 2)))
		double = Stroke(width=max(1, int(settings.line_width * 2)))
		green = Stroke(Color(0, 255, 0), width=settings.line_width)
		wide_green = Stroke(Color(0, 255, 0), width=max(1, int(settings.line_width * 2)))
		style = TextStyle(point_size=settings.font_size, italic=True)

		has_negative = any(_value(node, "l", 0) < 0 for node in nodes)
		has_right = _value(nodes[-1], "l", 0) != 0
		left_span = 60.0
		right_span = 30.0 if not has_right else 10.0 + settings.right_margin
		up_span = 30.0
		down_span = (
			30.0 if has_negative else 10.0 + settings.dimension_level
		) + settings.text_height
		minimum = min(0, *(_value(node, "l", 0) for node in nodes))
		maximum = max(0, *(_value(node, "l", 0) for node in nodes))
		free_height = settings.height - up_span - down_span
		height_scale = (
			free_height / (maximum - minimum)
			if maximum != minimum
			else free_height
		)
		base_y = height_scale * maximum + up_span
		right = settings.width - right_span
		base_bottom = base_y + settings.base_height
		length_scale = (
			(right - left_span)
			/ sum(_value(section, "l", 0) for section in sections)
		)
		x_positions = [left_span]
		for section in sections:
			x_positions.append(
				x_positions[-1] + _value(section, "l", 0) * length_scale
			)

		objects = []
		for index, section in enumerate(sections):
			if _value(section, "dims", True):
				objects.append(
					_dimension(
						Point(x_positions[index], base_y),
						Point(x_positions[index + 1], base_y),
						base_y + settings.dimension_level,
						half,
						style,
						length_text(_value(section, "l"), "a"),
						text_metrics,
						index,
					)
				)

		objects.append(
			Group(
				(
					Line(Point(left_span, base_y), Point(right, base_y), main),
					Line(Point(left_span, base_y), Point(left_span, base_bottom), main),
					Line(Point(left_span, base_bottom), Point(right, base_bottom), main),
					Line(Point(right, base_bottom), Point(right, base_y), main),
				),
				object_id="base/body",
				metadata=metadata(kind="body"),
			)
		)

		for index, section in enumerate(sections):
			label = _value(section, "label", "")
			if label:
				label_height = _value(section, "label_height", 20)
				objects.append(
					_text_by_points(
						Point(x_positions[index], base_y - label_height),
						Point(x_positions[index + 1], base_y - label_height),
						text_transform(label) + ("" if label_height > -20 else "  "),
						style,
						text_metrics,
						True,
						14,
						"section/{}/label".format(index),
						Point(
							(x_positions[index] + x_positions[index + 1]) / 2,
							base_y + settings.base_height / 2,
						),
					)
				)

		rendered_rod_text = False
		for index, node in enumerate(nodes):
			x = x_positions[index]
			length = _value(node, "l", 0)
			node_highlighted = settings.highlighted_node == index
			support = _value(node, "sharn", "нет")
			if support != "нет":
				objects.append(
					_support(
						Point(x, base_bottom),
						support,
						"down",
						main,
						double,
						"node/{}/support".format(index),
						index,
					)
				)
				if rendered_rod_text:
					objects[-1] = _with_antialias(objects[-1], False)
			if not length:
				label = _value(node, "lbl", "")
				if label:
					objects.append(
						_text_by_points(
							Point(x, base_y),
							Point(x, base_y - 60),
							text_transform(label),
							style,
							text_metrics,
							False,
							14,
							"node/{}/label".format(index),
							Point(x, base_y),
						)
					)
				if node_highlighted:
					objects.append(
						_ellipse(
							Point(x, base_y),
							4,
							green,
							object_id="node/{}/highlight".format(index),
						)
					)
				continue

			positive = length > 0
			start = Point(x, base_y if positive else base_bottom)
			gap_start = Point(x, start.y - 20 if positive else start.y + 20)
			end = Point(x, base_y - length * height_scale)
			has_gap = bool(_value(node, "zazor", False))
			rod_start = gap_start if has_gap else start
			rod_stroke = wide_green if node_highlighted else double
			children = [
				Line(rod_start, end, rod_stroke, object_id="rod/{}/line".format(index))
			]
			if not has_gap:
				children.append(
					_ellipse(
						start,
						4,
						green if node_highlighted else main,
						object_id="rod/{}/joint".format(index),
					)
				)
			else:
				gap_text = text_transform(_value(node, "zazor_txt", "\\Delta"))
				gap_measure = text_metrics.measure(gap_text, style)
				x_dimension = x - 20
				children.extend(
					(
						_arrow(
							Point(x_dimension, (start.y + gap_start.y) / 2),
							Point(x_dimension, start.y),
							half,
							10,
							None,
						),
						_arrow(
							Point(x_dimension, (start.y + gap_start.y) / 2),
							Point(x_dimension, gap_start.y),
							half,
							10,
							None,
						),
						Line(Point(x, start.y), Point(x_dimension, start.y), half),
						Line(Point(x, gap_start.y), Point(x_dimension, gap_start.y), half),
						Text(
							Point(
								x_dimension - 10 - gap_measure.width,
								(start.y + gap_start.y) / 2
								+ gap_measure.height / 4,
							),
							gap_text,
							style,
							object_id="rod/{}/gap/text".format(index),
						),
					)
				)
			children.append(_fixed_rod_end(end, positive, main, index))
			objects.append(
				Group(
					children,
					object_id="rod/{}".format(index),
					metadata=metadata(kind="rod", index=index),
					antialias=False if rendered_rod_text else None,
				)
			)

			ap = -length * height_scale if not positive else 0
			bp = 0 if not positive else -length * height_scale
			if not positive:
				ap += settings.base_height
			middle = (ap + bp) / 2
			area_text = length_text(abs(_value(node, "A", 1)), "A") + ",E"
			full_text = "{},{}".format(length_text(abs(length)), area_text)
			half_text = "{},{}".format(length_text(abs(length / 2)), area_text)
			first_text = _value(node, "sterzn_text1", "") or full_text
			first_half_text = _value(node, "sterzn_text1", "") or half_text
			second_half_text = _value(node, "sterzn_text2", "") or half_text
			text_offset = _value(node, "sterzn_text_off", 0)
			horizontal = _value(node, "sterzn_text_horizontal", True)
			alternate = _value(node, "sterzn_text_alt", False)

			def text_segment(a, b, value, suffix, include_offset):
				offset = -text_offset if include_offset else 0
				if horizontal:
					measure = text_metrics.measure(value, style)
					if alternate:
						start_x = x - measure.width - 10
						end_x = x
					else:
						start_x = x
						end_x = x + measure.width + 10
					y = base_y + (a + b) / 2 + measure.height / 2 + offset
					start_point = Point(start_x, y)
					end_point = Point(end_x, y)
					alt_text = False
				else:
					start_point = Point(x, base_y + a + offset)
					end_point = Point(x, base_y + b + offset)
					alt_text = not alternate
				return _angled_text(
					start_point,
					end_point,
					value,
					style,
					text_metrics,
					alt_text,
					15,
					"rod/{}/text/{}".format(index, suffix),
				)

			if _value(node, "F2", "нет") == "нет":
				objects.append(text_segment(ap, bp, first_text, "full", True))
			else:
				objects.extend(
					(
						text_segment(ap, middle, first_half_text, "first", False),
						text_segment(middle, bp, second_half_text, "second", False),
					)
				)
			rendered_rod_text = True

			label = _value(node, "lbl", "")
			if label:
				if bp == 0:
					label_start, label_end, leader = (
						Point(x, base_y + ap / 2),
						Point(x, base_y),
						Point(x, base_y + ap / 4 + 5),
					)
				else:
					label_start, label_end, leader = (
						Point(x, base_y),
						Point(x, base_y + bp / 2),
						Point(x, base_y + bp / 4 + 5),
					)
				objects.append(
					_text_by_points(
						label_start,
						label_end,
						text_transform(label),
						style,
						text_metrics,
						False,
						14,
						"rod/{}/label".format(index),
						leader,
					)
				)

		for index, node in enumerate(nodes):
			force = _value(node, "F", "нет")
			x = x_positions[index]
			length = _value(node, "l", 0)
			if force != "нет":
				if length > 0:
					base = Point(x, base_bottom)
					arrow_length = (
						settings.dimension_level - settings.base_height
					) * 2 / 3
					start = Point(x, base.y + arrow_length)
					end = base
				else:
					base = Point(x, base_y)
					arrow_length = settings.dimension_level * 2 / 3
					start = Point(x, base.y - arrow_length)
					end = base
				if force == "-":
					start, end = end, start
				children = [
					_arrow(
						start,
						end,
						main,
						settings.arrow_size,
						None,
						head_stroke=half,
					)
				]
				force_text = text_transform(_value(node, "Ftxt", ""))
				if force_text:
					measure = text_metrics.measure(force_text, style)
					middle_y = (start.y + end.y) / 2
					children.append(
						Text(
							Point(x + 7, middle_y + measure.height / 4),
							force_text,
							style,
							object_id="force/{}/text".format(index),
						)
					)
				objects.append(
					Group(
						children,
						object_id="force/{}".format(index),
						metadata=metadata(kind="force", index=index, direction=force),
						antialias=False if rendered_rod_text else None,
					)
				)

			rod_force = _value(node, "F2", "нет")
			if rod_force != "нет" and length:
				center_y = base_y - length * height_scale / 2
				delta = -28 if rod_force == "+" else 28
				left = Point(x - settings.rod_force_offset, center_y)
				right_point = Point(x + settings.rod_force_offset, center_y)
				children = [
					_arrow(
						left,
						Point(left.x, left.y + delta),
						main,
						settings.arrow_size,
						None,
						head_stroke=half,
					),
					_arrow(
						right_point,
						Point(right_point.x, right_point.y + delta),
						main,
						settings.arrow_size,
						None,
						head_stroke=half,
					),
					Line(left, right_point, half),
				]
				rod_force_text = _value(node, "F2txt", "")
				if rod_force_text:
					children.append(
						_text_by_points(
							Point(left.x, center_y - settings.dimension_level / 5),
							Point(left.x, center_y + settings.dimension_level / 5),
							rod_force_text,
							style,
							text_metrics,
							False,
							10,
							"rod-force/{}/text".format(index),
						)
					)
				objects.append(
					Group(
						children,
						object_id="rod-force/{}".format(index),
						metadata=metadata(kind="rod-force", index=index, direction=rod_force),
						antialias=False if rendered_rod_text else None,
					)
				)

		for side, support_type, x in (
			("left", settings.left_support, x_positions[0]),
			("right", settings.right_support, x_positions[-1]),
		):
			if support_type != "нет":
				objects.append(
					_support(
						Point(x, base_y + settings.base_height / 2),
						support_type,
						side,
						main,
						double,
						"endpoint/{}/support".format(side),
						0 if side == "left" else len(nodes) - 1,
					)
				)
				if rendered_rod_text:
					objects[-1] = _with_antialias(objects[-1], False)

		return Scene(
			Rect(0, 0, settings.width, settings.height),
			tuple(objects),
		)
