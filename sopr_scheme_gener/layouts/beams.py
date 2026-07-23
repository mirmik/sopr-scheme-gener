"""Qt-independent layout for the 2D beams task."""

import math
from dataclasses import dataclass

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
class BeamLayoutSettings:
	width: float
	height: float
	hcenter: float
	line_width: float = 2.0
	font_size: float = 12.0
	base_section_height: float = 6.0
	arrow_size: float = 15.0
	left_node: str = "Нет"
	right_node: str = "Нет"
	postfix_enabled: bool = False
	postfix: str = ""
	section: BeamSectionSpec = BeamSectionSpec()


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _length_text(length):
	if abs(float(length) - int(length)) < 0.0001:
		return "{}l".format(int(length + 0.1)) if length != 1 else "l"
	return "{:.3}l".format(length)


def _arrow(start, end, stroke, size, object_id, head_stroke=None):
	return Arrow(
		start,
		end,
		stroke=stroke,
		head_stroke=head_stroke,
		head_length=size,
		head_width=size * 2 / 3,
		object_id=object_id,
	)


def _dimension_arrow(start, end, stroke, size):
	direction = 1 if end.x > start.x else -1
	offset = 0.5 if direction > 0 else 0
	tip = Point(end.x + offset, end.y + offset)
	base_x = end.x - direction * size + offset
	return Group(
		(
			Line(start, end, stroke=stroke),
			Polygon(
				(
					tip,
					Point(base_x, end.y + size / 3 + offset),
					Point(base_x, end.y - size / 3 + offset),
				),
				stroke=stroke,
				fill=Fill(BLACK),
			),
		)
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
		stroke=stroke,
		fill=Fill(BLACK),
	)


def _moment(center, direction, radius, arrow_size, stroke, index):
	if direction == "+":
		line_angle = -(math.pi * 60 / 180)
		tip_angle = -(math.pi * 120 / 180)
		head_angle = -tip_angle + math.pi / 2 - math.pi * 10 / 180
	else:
		line_angle = -(math.pi * 120 / 180)
		tip_angle = -(math.pi * 60 / 180)
		head_angle = -tip_angle - math.pi / 2 + math.pi * 10 / 180
	line_degrees = line_angle * 180 / math.pi
	tip_degrees = tip_angle * 180 / math.pi
	arc_start = -line_degrees
	arc_span = -(tip_degrees - line_degrees)
	line_end = Point(
		center.x + radius * math.cos(line_angle),
		center.y + radius * math.sin(line_angle),
	)
	tip = Point(
		center.x + radius * math.cos(tip_angle),
		center.y + radius * math.sin(tip_angle),
	)
	return Group(
		(
			Line(center, line_end, stroke=stroke),
			Arc(
				Rect(
					center.x - radius,
					center.y - radius,
					radius * 2,
					radius * 2,
				),
				arc_start,
				arc_span,
				stroke=stroke,
			),
			_arrow_head(tip, head_angle, stroke, arrow_size),
		),
		object_id="moment/{}".format(index),
		metadata=metadata(kind="moment", index=index, direction=direction),
	)


def _terminator(center, angle, termx, termy, main, object_id):
	normal = angle + math.pi / 2
	first = Point(
		center.x + math.cos(normal) * termx,
		center.y + math.sin(normal) * termx,
	)
	second = Point(
		center.x - math.cos(normal) * termx,
		center.y - math.sin(normal) * termx,
	)
	offset = Point(math.sin(normal) * termy, -math.cos(normal) * termy)
	third = second.translated(offset)
	fourth = first.translated(offset)
	points = (first, second, third, fourth)
	return (
		Polygon(points, stroke=None, fill=Fill(WHITE)),
		Line(first, second, stroke=main),
		Polygon(
			points,
			stroke=None,
			fill=Fill(BLACK, pattern="backward-diagonal"),
			object_id=object_id,
		),
	)


def _support_one(center, angle, termrad, main, double, index, object_id=None):
	radius = 5.5
	base = Point(
		center.x + termrad * math.cos(angle),
		center.y + termrad * math.sin(angle),
	)
	second_circle = Point(
		center.x + (termrad - radius) * math.cos(angle),
		center.y + (termrad - radius) * math.sin(angle),
	)
	children = [
		Line(center, base, stroke=double),
		*_terminator(base, angle, 20, 10, main, None),
		Ellipse(
			Rect(center.x - radius, center.y - radius, radius * 2 + 1, radius * 2 + 1),
			stroke=main,
			fill=Fill(WHITE),
		),
		Ellipse(
			Rect(
				second_circle.x - radius,
				second_circle.y - radius,
				radius * 2 + 1,
				radius * 2 + 1,
			),
			stroke=main,
			fill=Fill(WHITE),
		),
	]
	return Group(
		children,
		object_id=object_id or "support/{}".format(index),
		metadata=metadata(kind="support", index=index, support_type="1"),
	)


def _support_two(center, termrad, main, index):
	radius = 5.5
	base = Point(center.x, center.y + termrad)
	half_width = 20 * 2 / 3
	left = Point(base.x - half_width, base.y)
	right = Point(base.x + half_width, base.y)
	children = [
		*_terminator(base, math.pi / 2, 20, 10, main, None),
		Line(left, right, stroke=main),
		Line(center, right, stroke=main),
		Line(center, left, stroke=main),
		Ellipse(
			Rect(center.x - radius, center.y - radius, radius * 2 + 1, radius * 2 + 1),
			stroke=main,
			fill=Fill(WHITE),
		),
	]
	return Group(
		children,
		object_id="support/{}".format(index),
		metadata=metadata(kind="support", index=index, support_type="2"),
	)


class BeamLayoutBuilder:
	def build(self, task, settings, text_transform=None, text_metrics=None):
		text_transform = text_transform or (lambda text: text)
		sections = task["sections"]
		nodes = task["betsect"]
		loads = task["sectforce"]
		if not sections:
			raise ValueError("beams task requires at least one section")
		if len(nodes) != len(sections) + 1 or len(loads) != len(sections):
			raise ValueError("beams task arrays have inconsistent lengths")

		main = Stroke(width=settings.line_width)
		half = Stroke(width=max(1, int(settings.line_width / 2)))
		double = Stroke(width=max(1, int(settings.line_width * 2)))
		axis = Stroke(
			width=max(1, int(settings.line_width / 2)),
			line_style="dash-dot",
		)
		style = TextStyle(point_size=settings.font_size, italic=True)

		left = 20.0
		right = settings.width - 20.0
		cross_section_width = beam_section_width(settings.section)
		body_right = right - cross_section_width
		prefix = 30.0
		beam_left = left + prefix
		beam_right = body_right - prefix
		total = sum(float(_value(section, "l")) for section in sections)
		if total <= 0:
			raise ValueError("total beam length must be positive")
		scale = (beam_right - beam_left) / total
		points = [beam_left]
		for section in sections:
			points.append(points[-1] + float(_value(section, "l")) * scale)

		if settings.section.section_type != "Нет" and text_metrics is None:
			raise ValueError("text_metrics is required for cross-section layout")
		objects = list(
			build_beam_section(
				settings.section,
				right,
				settings.hcenter,
				settings.arrow_size,
				main,
				half,
				axis,
				style,
				text_metrics,
				text_transform,
			)
		)
		load_height = 30.0
		load_step = 10.0
		load_arrow_size = settings.arrow_size * 2 / 3
		beam_top = settings.hcenter - settings.base_section_height / 2

		current_stroke = main
		for index, node in enumerate(nodes):
			x = points[index]
			moment_direction = _value(node, "M", "Нет")
			force_direction = _value(node, "F", "Нет")
			has_moment = moment_direction != "Нет"
			if has_moment:
				objects.append(
					_moment(
						Point(x, settings.hcenter),
						moment_direction,
						60,
						settings.arrow_size,
						half,
						index,
					)
				)
				current_stroke = half

			if force_direction in ("+", "-"):
				half_height = settings.base_section_height / 2
				if has_moment:
					top = Point(x, settings.hcenter + half_height)
					bottom = Point(x, settings.hcenter + 60 + half_height)
				else:
					top = Point(x, settings.hcenter - 60 - half_height)
					bottom = Point(x, settings.hcenter - half_height)
				start, end = (
					(bottom, top) if force_direction == "+" else (top, bottom)
				)
				objects.append(
					_arrow(
						start,
						end,
						current_stroke,
						settings.arrow_size,
						"force/{}".format(index),
						head_stroke=half,
					)
				)
			elif force_direction in ("влево", "вправо"):
				center = Point(x, settings.hcenter)
				sign = -1 if force_direction == "влево" else 1
				if index == 0:
					left_point = Point(x - 40, settings.hcenter)
					start, end = (
						(center, left_point)
						if sign < 0
						else (left_point, center)
					)
					children = (
						_arrow(
							start,
							end,
							current_stroke,
							settings.arrow_size,
							None,
							head_stroke=half,
						),
					)
				elif index == len(nodes) - 1:
					right_point = Point(x + 40, settings.hcenter)
					start, end = (
						(right_point, center)
						if sign < 0
						else (center, right_point)
					)
					children = (
						_arrow(
							start,
							end,
							current_stroke,
							settings.arrow_size,
							None,
							head_stroke=half,
						),
					)
				else:
					upper = Point(x, settings.hcenter - 25)
					lower = Point(x, settings.hcenter + 25)
					offset = Point(sign * 30, 0)
					children = (
						_arrow(
							lower,
							lower.translated(offset),
							current_stroke,
							settings.arrow_size,
							None,
							head_stroke=half,
						),
						_arrow(
							upper,
							upper.translated(offset),
							half,
							settings.arrow_size,
							None,
							head_stroke=half,
						),
						Line(lower, upper, stroke=half),
					)
				objects.append(
					Group(
						children,
						object_id="force/{}".format(index),
						metadata=metadata(
							kind="force",
							index=index,
							direction=force_direction,
						),
					)
				)
				current_stroke = half

			if has_moment:
				objects.append(
					Text(
						Point(x, settings.hcenter - 65),
						text_transform(_value(node, "MT", "")),
						style=style,
						anchor=TextAnchor.BASELINE_CENTER,
						object_id="moment/{}/text".format(index),
					)
				)
			if force_direction != "Нет":
				if force_direction in ("влево", "вправо"):
					text_position = Point(x, settings.hcenter - 30)
				elif has_moment:
					text_position = Point(x + 10, settings.hcenter + 25)
				else:
					text_position = Point(x + 10, settings.hcenter - 60)
				objects.append(
					Text(
						text_position,
						text_transform(_value(node, "FT", "")),
						style=style,
						object_id="force/{}/text".format(index),
					)
				)

			section_name = _value(node, "sectname", "")
			if section_name:
				offset = 11 if _value(node, "sharn", "") != "" else 5
				objects.append(
					Text(
						Point(x - offset, settings.hcenter + 21),
						section_name,
						style=style,
						anchor=TextAnchor.BASELINE_RIGHT,
						object_id="node/{}/name".format(index),
						metadata=metadata(kind="node-name", index=index),
					)
				)

		for index, load in enumerate(loads):
			direction = _value(load, "Fr", "Нет")
			if direction == "Нет":
				continue
			start = Point(points[index], beam_top)
			end = Point(points[index + 1], beam_top)
			top_start = Point(start.x, start.y - load_height)
			top_end = Point(end.x, end.y - load_height)
			distance = end.x - start.x
			count = int(distance / load_step)
			count = count - count % 2 + 1
			children = [Line(start, end, half), Line(top_start, top_end, half)]
			for arrow_index in range(count):
				coefficient = arrow_index / (count - 1)
				x = coefficient * end.x + (1 - coefficient) * start.x + 0.5
				y = (
					coefficient * end.y
					+ (1 - coefficient) * start.y
					+ 0.5
				)
				bottom = Point(x, y)
				top = Point(x, y - load_height)
				arrow_start, arrow_end = (
					(bottom, top) if direction == "+" else (top, bottom)
				)
				children.append(
					_arrow(
						arrow_start,
						arrow_end,
						half,
						load_arrow_size,
						"load/{}/arrow/{}".format(index, arrow_index),
					)
				)
			children.append(
				Text(
					Point((start.x + end.x) / 2, start.y - load_height - 5),
					text_transform(_value(load, "FrT", "")),
					style=style,
					anchor=TextAnchor.BASELINE_CENTER,
					object_id="load/{}/text".format(index),
				)
			)
			objects.append(
				Group(
					children,
					object_id="load/{}".format(index),
					metadata=metadata(kind="distributed-load", index=index),
				)
			)

		objects.append(
			Rectangle(
				Rect(
					beam_left,
					beam_top,
					beam_right - beam_left,
					settings.base_section_height,
				),
				stroke=main,
				fill=Fill(WHITE),
				object_id="beam/body",
				metadata=metadata(kind="beam"),
			)
		)

		dimension_level = settings.hcenter + 80
		for index, section in enumerate(sections):
			start = Point(points[index], settings.hcenter)
			end = Point(points[index + 1], settings.hcenter)
			center = Point((start.x + end.x) / 2, dimension_level)
			text = _length_text(float(_value(section, "l")))
			if settings.postfix_enabled:
				text += settings.postfix
			objects.append(
				Group(
					(
						Line(start, Point(start.x, dimension_level), half),
						Line(end, Point(end.x, dimension_level), half),
						_dimension_arrow(
							center,
							Point(start.x, dimension_level),
							half,
							10,
						),
						_dimension_arrow(
							center,
							Point(end.x, dimension_level),
							half,
							10,
						),
						Text(
							Point(center.x, dimension_level - 5),
							text,
							style=style,
							anchor=TextAnchor.BASELINE_CENTER,
							object_id="dimension/{}/text".format(index),
						),
					),
					object_id="dimension/{}".format(index),
					metadata=metadata(kind="dimension", index=index),
				)
			)

		if settings.left_node == "Шарнир":
			objects.append(
				_support_one(
					Point(points[0], settings.hcenter),
					math.pi,
					25,
					main,
					double,
					0,
					object_id="endpoint/left",
				)
			)
		elif settings.left_node == "Заделка":
			objects.append(
				Group(
					_terminator(
						Point(points[0] + 0.5, settings.hcenter),
						math.pi,
						25,
						15,
						main,
						None,
					),
					object_id="endpoint/left",
					metadata=metadata(kind="fixed-end", side="left"),
				)
			)

		if settings.right_node == "Шарнир":
			objects.append(
				_support_one(
					Point(points[-1], settings.hcenter),
					0,
					25,
					main,
					double,
					len(nodes) - 1,
					object_id="endpoint/right",
				)
			)
		elif settings.right_node == "Заделка":
			objects.append(
				Group(
					_terminator(
						Point(points[-1] + 0.5, settings.hcenter),
						0,
						25,
						15,
						main,
						None,
					),
					object_id="endpoint/right",
					metadata=metadata(kind="fixed-end", side="right"),
				)
			)

		for index, node in enumerate(nodes):
			support_type = _value(node, "sharn", "Нет")
			if support_type == "Нет":
				continue
			endpoint = index in (0, len(nodes) - 1)
			center = Point(points[index], settings.hcenter + (0 if endpoint else 8))
			termrad = 33 if endpoint else 25
			if support_type == "1":
				objects.append(
					_support_one(
						center,
						math.pi / 2,
						termrad,
						main,
						double,
						index,
					)
				)
			elif support_type == "2":
				objects.append(_support_two(center, termrad, main, index))
			else:
				raise ValueError("Unsupported support type: {!r}".format(support_type))

		label_center = Point((20 + body_right) / 2, settings.hcenter)
		label_scale = settings.width - 40 - cross_section_width
		for index, label in enumerate(task.get("labels", ())):
			position = _value(label, "pos")
			objects.append(
				Text(
					Point(
						label_center.x + float(position[0]) * label_scale,
						label_center.y + float(position[1]),
					),
					text_transform(_value(label, "text", "")),
					style=style,
					anchor=TextAnchor.CENTER,
					object_id="label/{}".format(index),
					metadata=metadata(kind="label", index=index),
				)
			)

		return Scene(
			viewport=Rect(0, 0, settings.width, settings.height),
			content_bounds=Rect(
				beam_left,
				beam_top - load_height,
				beam_right - beam_left,
				113,
			),
			objects=objects,
		)
