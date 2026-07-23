"""Qt-independent layout for the 2D frames task."""

import math
from dataclasses import dataclass
from typing import Optional

from sopr_scheme_gener.layouts.beam_sections import (
	BeamSectionSpec,
	beam_section_width,
	build_beam_section,
)
from sopr_scheme_gener.scene import (
	BLACK,
	WHITE,
	Arc,
	Arrow,
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
class FramesLayoutSettings:
	width: float
	height: float
	hcenter: float
	base_length: float = 100.0
	arrow_size: float = 12.0
	postfix: str = ",EIx"
	font_size: float = 12.0
	line_width: float = 2.0
	section: BeamSectionSpec = BeamSectionSpec()
	grid_enabled: bool = False
	hovered_grid: Optional[Point] = None
	preview_start: Optional[Point] = None
	preview_end: Optional[Point] = None
	highlight_hint: str = ""
	highlight_row: int = -1


_DIRECTION_ANGLES = {
	"слева": math.pi,
	"справа": 0,
	"сверху": math.pi / 2,
	"снизу": math.pi * 3 / 2,
	"слева сверху": math.pi * 3 / 4,
	"справа сверху": math.pi / 4,
	"слева снизу": math.pi * 5 / 4,
	"справа снизу": math.pi * 7 / 4,
}


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _ellipse(center, radius, stroke, fill=Fill(WHITE), plus_one=True, object_id=None):
	diameter = radius * 2 + (1 if plus_one else 0)
	return Ellipse(
		Rect(center.x - radius, center.y - radius, diameter, diameter),
		stroke,
		fill,
		object_id=object_id,
	)


def _arrow(start, end, stroke, size, object_id=None, head_stroke=None):
	return Arrow(
		start,
		end,
		stroke,
		head_length=size,
		head_width=size * 2 / 3,
		head_stroke=head_stroke or stroke,
		object_id=object_id,
	)


def _arrow_head(tip, angle, stroke, size):
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
	dx = end.x - start.x
	dy = end.y - start.y
	length = math.hypot(dx, dy)
	ux, uy = dx / length, dy / length
	if alternate:
		ux, uy = -ux, -uy
	nx, ny = -uy, ux
	measurement = text_metrics.measure(value, style)
	position = Point(
		(start.x + end.x) / 2
		+ nx * (offset + measurement.width / 2),
		(start.y + end.y) / 2
		+ measurement.height / 4
		+ ny * offset,
	)
	return Text(
		position,
		value,
		style,
		TextAnchor.BASELINE_CENTER,
		object_id=object_id,
	)


def _label(center, value, direction, style, text_metrics, object_id):
	angle = _DIRECTION_ANGLES[direction]
	measurement = text_metrics.measure(value, style)
	return Text(
		Point(
			center.x + math.cos(angle) * 17,
			center.y - math.sin(angle) * 17 + measurement.height / 4,
		),
		value,
		style,
		TextAnchor.BASELINE_CENTER,
		object_id=object_id,
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


def _support(center, support_type, member_angle, main, double, object_id):
	if support_type in ("нет", "clean"):
		return None
	if support_type == "заделка":
		return Group(
			_terminator(center, member_angle, 15, 10, main),
			object_id=object_id,
			metadata=metadata(kind="support", support_type=support_type),
		)
	if support_type == "врезанный":
		return Group(
			(_ellipse(center, 5, main, plus_one=False),),
			object_id=object_id,
			metadata=metadata(kind="support", support_type=support_type),
		)

	angle = None
	for direction, direction_angle in _DIRECTION_ANGLES.items():
		if direction in support_type:
			angle = direction_angle
			break
	if angle is None:
		return None
	radius = 4
	term_radius = 25 if "шарн1" in support_type else 15
	base = Point(
		center.x + term_radius * math.cos(angle),
		center.y + term_radius * math.sin(angle),
	)
	children = []
	if "врез1" in support_type or "шарн1" in support_type:
		center_offset = 6 if "шарн1" in support_type else 0
		first_circle = Point(
			center.x + center_offset * math.cos(angle),
			center.y + center_offset * math.sin(angle),
		)
		second_circle = Point(
			center.x + (term_radius - radius) * math.cos(angle),
			center.y + (term_radius - radius) * math.sin(angle),
		)
		children.extend(
			(
				Line(center, base, main),
				*_terminator(base, angle, 15, 10, main),
				_ellipse(
					first_circle,
					radius,
					main,
					plus_one="шарн1" not in support_type,
				),
				_ellipse(second_circle, radius, main),
			)
		)
	elif "шарн2" in support_type:
		normal = angle + math.pi / 2
		half_width = 15 * 2 / 3
		first = Point(
			base.x + math.cos(normal) * half_width,
			base.y + math.sin(normal) * half_width,
		)
		second = Point(
			base.x - math.cos(normal) * half_width,
			base.y - math.sin(normal) * half_width,
		)
		children.extend(
			(
				*_terminator(base, angle, 15, 10, main),
				Line(first, second, main),
				Line(center, first, main),
				Line(center, second, main),
				_ellipse(center, radius, main),
			)
		)
	return Group(
		children,
		object_id=object_id,
		metadata=metadata(kind="support", support_type=support_type),
	)


def _distributed_load(
	start,
	end,
	direction,
	value,
	style,
	text_metrics,
	half,
	arrow_size,
	index,
):
	if direction not in ("+", "-"):
		return None
	text = _text_by_points(
		start,
		end,
		value,
		style,
		text_metrics,
		direction == "-",
		30,
		"member/{}/distributed/text".format(index),
	)
	load_start, load_end = (start, end) if direction == "+" else (end, start)
	dx = load_end.x - load_start.x
	dy = load_end.y - load_start.y
	distance = math.hypot(dx, dy)
	children = [text]
	if distance >= 20:
		count = int(distance / 10)
		count = count - count % 2 + 1
		normal = Point(-dy / distance * 20, dx / distance * 20)
		offset_start = load_start.translated(normal)
		offset_end = load_end.translated(normal)
		children.append(Line(offset_start, offset_end, half))
		for arrow_index in range(count):
			ratio = arrow_index / (count - 1)
			base = Point(
				load_end.x * ratio + load_start.x * (1 - ratio),
				load_end.y * ratio + load_start.y * (1 - ratio),
			)
			children.append(
				_arrow(
					base.translated(normal),
					base,
					half,
					arrow_size,
					object_id="member/{}/distributed/arrow/{}".format(
						index, arrow_index
					),
				)
			)
	return Group(
		children,
		object_id="member/{}/distributed".format(index),
		metadata=metadata(kind="distributed-load", index=index, direction=direction),
	)


def _force(center, force_type, value, alternate, style, text_metrics, half, size, object_id):
	if force_type == "нет":
		return None
	direction_name = force_type.split()[0]
	angle = _DIRECTION_ANGLES[direction_name]
	outer = Point(
		center.x + 40 * math.cos(angle),
		center.y - 40 * math.sin(angle),
	)
	start, end = center, outer
	if "от" not in force_type:
		start, end = outer, center
	children = [_arrow(start, end, half, size, head_stroke=half)]
	if value:
		measurement = text_metrics.measure(value, style)
		middle = Point((start.x + end.x) / 2, (start.y + end.y) / 2)
		if direction_name in ("слева", "справа"):
			position = Point(
				middle.x,
				middle.y + (-7 if alternate else measurement.height - 2),
			)
			anchor = TextAnchor.BASELINE_CENTER
		else:
			position = Point(
				middle.x + (7 if alternate else -measurement.width - 7),
				middle.y + measurement.height / 4,
			)
			anchor = TextAnchor.BASELINE_LEFT
		children.append(
			Text(
				position,
				value,
				style,
				anchor,
				object_id=object_id + "/text",
			)
		)
	return Group(
		children,
		object_id=object_id,
		metadata=metadata(kind="force", direction=force_type),
	)


def _moment(center, moment_type, value, style, text_metrics, half, size, object_id):
	if moment_type == "нет":
		return None
	direction_name, sign = moment_type.split()
	base_angle = _DIRECTION_ANGLES[direction_name]
	delta = math.pi / 6
	angle = base_angle - delta if sign == "+" else base_angle + delta
	angle2 = base_angle + delta if sign == "+" else base_angle - delta
	line_angle = -angle
	tip_angle = -angle2
	line_end = Point(
		center.x + 40 * math.cos(line_angle),
		center.y + 40 * math.sin(line_angle),
	)
	tip = Point(
		center.x + 40 * math.cos(tip_angle),
		center.y + 40 * math.sin(tip_angle),
	)
	if line_angle > tip_angle:
		head_angle = -tip_angle + math.pi / 2 - math.pi / 18
	else:
		head_angle = -tip_angle - math.pi / 2 + math.pi / 18
	children = [
		Line(center, line_end, half),
		Arc(
			Rect(center.x - 40, center.y - 40, 80, 80),
			-math.degrees(line_angle),
			-math.degrees(tip_angle - line_angle),
			half,
		),
		_arrow_head(tip, head_angle, half, size),
	]
	if value:
		measurement = text_metrics.measure(value, style)
		if direction_name == "слева":
			position = Point(tip.x - 10, tip.y + measurement.height / 4)
			anchor = TextAnchor.BASELINE_RIGHT
		elif direction_name == "справа":
			position = Point(tip.x + 15, tip.y + measurement.height / 4)
			anchor = TextAnchor.BASELINE_CENTER
		elif direction_name == "сверху":
			position = Point(tip.x, tip.y - 10)
			anchor = TextAnchor.BASELINE_CENTER
		else:
			position = Point(tip.x, tip.y + measurement.height)
			anchor = TextAnchor.BASELINE_CENTER
		children.append(
			Text(
				position,
				value,
				style,
				anchor,
				object_id=object_id + "/text",
			)
		)
	return Group(
		children,
		object_id=object_id,
		metadata=metadata(kind="moment", direction=moment_type),
	)


class FramesLayoutBuilder:
	def build(self, task, settings, text_metrics, text_transform=None, length_text=None):
		text_transform = text_transform or (lambda value: value)
		length_text = length_text or (lambda value, suffix="": str(value) + suffix)
		sections = task["sections"]
		loads = task["sectforce"]
		nodes = task["betsect"]
		labels = task["label"]
		if not (
			len(sections) == len(loads) == len(nodes) == len(labels)
		):
			raise ValueError("frames task arrays have inconsistent lengths")
		if settings.base_length <= 0:
			raise ValueError("frames base length must be positive")

		raw = []
		previous_end = None
		xmin = ymin = xmax = ymax = 0.0
		for index, section in enumerate(sections):
			x_start_value = _value(section, "xstrt", "")
			y_start_value = _value(section, "ystrt", "")
			if index == 0:
				x_start_value = 0 if x_start_value == "" else x_start_value
				y_start_value = 0 if y_start_value == "" else y_start_value
			if x_start_value == "" or y_start_value == "":
				if previous_end is None:
					raise ValueError("frames first member requires a start point")
				x_start = (
					previous_end.x if x_start_value == "" else float(x_start_value)
				)
				y_start = (
					previous_end.y if y_start_value == "" else float(y_start_value)
				)
			else:
				x_start = float(x_start_value)
				y_start = float(y_start_value)
			end = Point(
				float(_value(section, "xfini")),
				float(_value(section, "yfini")),
			)
			start = Point(x_start, y_start)
			raw.append((start, end))
			previous_end = end
			xmin, xmax = min(xmin, start.x, end.x), max(xmax, start.x, end.x)
			ymin, ymax = min(ymin, start.y, end.y), max(ymax, start.y, end.y)

		main = Stroke(width=settings.line_width)
		half = Stroke(width=max(1, int(settings.line_width / 2)))
		double = Stroke(width=max(1, int(settings.line_width * 2)))
		axis = Stroke(
			width=max(1, int(settings.line_width / 2)),
			line_style="dash-dot",
		)
		style = TextStyle(point_size=settings.font_size, italic=True)
		# Keep the legacy reservation rule exactly: draw_section_routine()
		# returned the section width and the frame renderer subtracted 10 from
		# it even when there was no section (0 - 10).  The resulting +5 px
		# shift is part of the established output geometry.
		section_width = beam_section_width(settings.section) - 10
		x_shift = -(xmin + xmax) / 2 * settings.base_length - section_width / 2
		y_shift = (ymin + ymax) / 2 * settings.base_length
		center = Point(settings.width / 2, settings.hcenter)
		origin = Point(center.x + x_shift, center.y + y_shift)

		def screen(point):
			return Point(
				point.x * settings.base_length + origin.x,
				-point.y * settings.base_length + origin.y,
			)

		coordinates = tuple((screen(start), screen(end)) for start, end in raw)
		objects = list(
			build_beam_section(
				settings.section,
				settings.width - 10,
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

		for index, ((start, end), (raw_start, raw_end)) in enumerate(
			zip(coordinates, raw)
		):
			section = sections[index]
			value = _value(section, "txt", "")
			if not value:
				distance = math.hypot(
					raw_end.x - raw_start.x,
					raw_end.y - raw_start.y,
				)
				value = length_text(distance) + settings.postfix
			children = [
				Line(start, end, double, object_id="member/{}/line".format(index)),
				_text_by_points(
					start,
					end,
					value,
					style,
					text_metrics,
					_value(section, "alttxt", False),
					14,
					"member/{}/text".format(index),
				),
			]
			label = labels[index]
			start_label = text_transform(_value(label, "smaker", ""))
			end_label = text_transform(_value(label, "fmaker", ""))
			if start_label:
				children.append(
					_label(
						start,
						start_label,
						_value(label, "smaker_pos", "сверху"),
						style,
						text_metrics,
						"member/{}/start-label".format(index),
					)
				)
			if end_label:
				children.append(
					_label(
						end,
						end_label,
						_value(label, "fmaker_pos", "сверху"),
						style,
						text_metrics,
						"member/{}/end-label".format(index),
					)
				)
			objects.append(
				Group(
					children,
					object_id="member/{}".format(index),
					metadata=metadata(kind="member", index=index),
				)
			)

		for index, (start, end) in enumerate(coordinates):
			load = _distributed_load(
				start,
				end,
				_value(loads[index], "distrib", "clean"),
				text_transform(_value(loads[index], "txt", "")),
				style,
				text_metrics,
				half,
				settings.arrow_size / 3 * 2,
				index,
			)
			if load is not None:
				objects.append(load)

		for index, (start, end) in enumerate(coordinates):
			section = sections[index]
			angle = math.atan2(end.y - start.y, end.x - start.x)
			left = _support(
				start,
				_value(section, "lsharn", "нет"),
				angle + math.pi,
				main,
				double,
				"member/{}/start-support".format(index),
			)
			right = _support(
				end,
				_value(section, "rsharn", "нет"),
				angle,
				main,
				double,
				"member/{}/end-support".format(index),
			)
			if left is not None:
				objects.append(left)
			if right is not None:
				objects.append(right)

		for index, (start, end) in enumerate(coordinates):
			node = nodes[index]
			for item in (
				_moment(
					start,
					_value(node, "menl", "нет"),
					text_transform(_value(node, "ml_txt", "")),
					style,
					text_metrics,
					half,
					settings.arrow_size,
					"member/{}/start-moment".format(index),
				),
				_moment(
					end,
					_value(node, "menr", "нет"),
					text_transform(_value(node, "mr_txt", "")),
					style,
					text_metrics,
					half,
					settings.arrow_size,
					"member/{}/end-moment".format(index),
				),
				_force(
					start,
					_value(node, "fenl", "нет"),
					text_transform(_value(node, "fl_txt", "")),
					_value(node, "fl_txt_alt", False),
					style,
					text_metrics,
					half,
					settings.arrow_size,
					"member/{}/start-force".format(index),
				),
				_force(
					end,
					_value(node, "fenr", "нет"),
					text_transform(_value(node, "fr_txt", "")),
					_value(node, "fr_txt_alt", False),
					style,
					text_metrics,
					half,
					settings.arrow_size,
					"member/{}/end-force".format(index),
				),
			):
				if item is not None:
					objects.append(item)

		if settings.grid_enabled:
			min_grid_x = math.ceil((0 - origin.x) / settings.base_length)
			max_grid_x = math.floor((settings.width - origin.x) / settings.base_length)
			min_grid_y = math.ceil(
				(origin.y - settings.height) / settings.base_length
			)
			max_grid_y = math.floor(origin.y / settings.base_length)
			for grid_x in range(min_grid_x, max_grid_x + 1):
				for grid_y in range(min_grid_y, max_grid_y + 1):
					point = Point(
						origin.x + grid_x * settings.base_length,
						origin.y - grid_y * settings.base_length,
					)
					hovered = (
						settings.hovered_grid is not None
						and settings.hovered_grid == Point(grid_x, grid_y)
					)
					color = Color(255, 0, 0) if hovered else Color(0, 255, 0)
					radius = 4 if hovered else 2
					objects.append(
						Group(
							(
								_ellipse(
									point,
									radius,
									half,
									Fill(color),
									plus_one=False,
								),
								Rectangle(
									Rect(
										point.x - settings.base_length / 2,
										point.y - settings.base_length / 2,
										settings.base_length,
										settings.base_length,
									),
									stroke=None,
									fill=Fill(Color(0, 0, 0, 0)),
								),
							),
							object_id="grid/{}/{}".format(grid_x, grid_y),
							metadata=metadata(
								kind="grid-node",
								grid_x=grid_x,
								grid_y=grid_y,
							),
						)
					)

		if settings.preview_start is not None and settings.preview_end is not None:
			preview_start = Point(
				origin.x + settings.preview_start.x * settings.base_length,
				origin.y - settings.preview_start.y * settings.base_length,
			)
			preview_end = Point(
				origin.x + settings.preview_end.x * settings.base_length,
				origin.y - settings.preview_end.y * settings.base_length,
			)
			objects.append(
				Line(
					preview_start,
					preview_end,
					half,
					object_id="preview",
					metadata=metadata(kind="preview"),
				)
			)

		if (
			settings.highlight_row >= 0
			and settings.highlight_row < len(coordinates)
		):
			start, end = coordinates[settings.highlight_row]
			if settings.highlight_hint in ("N0", "N1"):
				objects.extend(
					(
						Line(
							start,
							end,
							Stroke(Color(0, 0, 255), 5),
							object_id="highlight/member",
						),
						_ellipse(
							start if settings.highlight_hint == "N0" else end,
							5,
							main,
							Fill(Color(0, 255, 0)),
							plus_one=False,
							object_id="highlight/node",
						),
					)
				)
			elif settings.highlight_hint == "S":
				objects.append(
					Line(
						start,
						end,
						Stroke(Color(0, 255, 0), 5),
						object_id="highlight/member",
					)
				)

		return Scene(Rect(0, 0, settings.width, settings.height), tuple(objects))
