"""Qt-independent layout for the 2D beams task."""

import math
from dataclasses import dataclass

from sopr_scheme_gener.scene import (
	BLACK,
	WHITE,
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


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def supports_scene_layout(task, settings, section_type="Нет", extra_text=""):
	"""Return whether the current vertical slice can replace legacy rendering."""
	if section_type != "Нет" or extra_text or task.get("labels"):
		return False
	if settings.left_node != "Нет" or settings.right_node != "Нет":
		return False
	for node in task["betsect"]:
		if _value(node, "F", "Нет") != "Нет" or _value(node, "M", "Нет") != "Нет":
			return False
		if _value(node, "sectname", ""):
			return False
	return all(
		_value(node, "sharn", "Нет") in ("Нет", "1", "2")
		for node in task["betsect"]
	)


def _length_text(length):
	if abs(float(length) - int(length)) < 0.0001:
		return "{}l".format(int(length + 0.1)) if length != 1 else "l"
	return "{:.3}l".format(length)


def _arrow(start, end, stroke, size, object_id):
	return Arrow(
		start,
		end,
		stroke=stroke,
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


def _support_one(center, termrad, main, double, index):
	radius = 5.5
	base = Point(center.x, center.y + termrad)
	second_circle = Point(center.x, center.y + termrad - radius)
	children = [
		Line(center, base, stroke=double),
		*_terminator(base, math.pi / 2, 20, 10, main, None),
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
		object_id="support/{}".format(index),
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
	def build(self, task, settings, text_transform=None):
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
		style = TextStyle(point_size=settings.font_size, italic=True)

		left = 20.0
		right = settings.width - 20.0
		prefix = 30.0
		beam_left = left + prefix
		beam_right = right - prefix
		total = sum(float(_value(section, "l")) for section in sections)
		if total <= 0:
			raise ValueError("total beam length must be positive")
		scale = (beam_right - beam_left) / total
		points = [beam_left]
		for section in sections:
			points.append(points[-1] + float(_value(section, "l")) * scale)

		objects = []
		load_height = 30.0
		load_step = 10.0
		load_arrow_size = settings.arrow_size * 2 / 3
		beam_top = settings.hcenter - settings.base_section_height / 2

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

		for index, node in enumerate(nodes):
			support_type = _value(node, "sharn", "Нет")
			if support_type == "Нет":
				continue
			endpoint = index in (0, len(nodes) - 1)
			center = Point(points[index], settings.hcenter + (0 if endpoint else 8))
			termrad = 33 if endpoint else 25
			if support_type == "1":
				objects.append(_support_one(center, termrad, main, double, index))
			elif support_type == "2":
				objects.append(_support_two(center, termrad, main, index))
			else:
				raise ValueError("Unsupported support type: {!r}".format(support_type))

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
