"""Qt-independent layout for the plate task."""

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
class PlateLayoutSettings:
	width: float
	height: float
	hcenter: float
	base_height: float = 20.0
	fixed_ends: bool = True
	axis: bool = True
	fixed_end_length: float = 30.0
	dimension_start: float = 20.0
	dimension_step: float = 40.0
	arrow_size: float = 13.0
	font_size: float = 12.0
	line_width: float = 2.0


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _polygon(points, stroke, fill=Fill(BLACK), convex=False):
	return Polygon(tuple(points), stroke=stroke, fill=fill, convex=convex)


def _horizontal_dimension(p0, p1, level, stroke, style, text, index):
	center = Point((p0.x + p1.x) / 2, level)
	size = 10
	left_tip = Point(p0.x, level)
	right_tip = Point(p1.x + 0.5, level + 0.5)
	return Group(
		(
			Line(p0, left_tip, stroke),
			Line(p1, Point(p1.x, level), stroke),
			Line(center, left_tip, stroke),
			_polygon(
				(
					left_tip,
					Point(left_tip.x + size, left_tip.y + size / 3),
					Point(left_tip.x + size, left_tip.y - size / 3),
				),
				stroke,
				convex=True,
			),
			Line(center, Point(p1.x, level), stroke),
			_polygon(
				(
					right_tip,
					Point(p1.x - size + 0.5, level + size / 3 + 0.5),
					Point(p1.x - size + 0.5, level - size / 3 + 0.5),
				),
				stroke,
				convex=True,
			),
			Text(
				Point(center.x, level - 5),
				text,
				style,
				TextAnchor.BASELINE_CENTER,
				object_id="dimension/{}/width/text".format(index),
			),
		),
		object_id="dimension/{}/width".format(index),
		metadata=metadata(kind="dimension", index=index, axis="width"),
	)


def _vertical_dimension(up, down, center, stroke, style, text, text_metrics, index):
	size = 10
	height = text_metrics.measure(text, style).height
	x_width = text_metrics.measure("x", style).width
	return Group(
		(
			_polygon(
				(
					Point(up.x, up.y - size),
					Point(up.x + size / 3, up.y - size),
					up,
					Point(up.x - size / 3, up.y - size),
				),
				stroke,
				convex=True,
			),
			_polygon(
				(
					Point(down.x, down.y + size),
					Point(down.x + size / 3, down.y + size),
					down,
					Point(down.x - size / 3, down.y + size),
				),
				stroke,
				convex=True,
			),
			Line(
				Point(up.x, up.y - size * 1.5),
				Point(down.x, down.y + size * 1.5),
				stroke,
			),
			Text(
				Point(down.x + x_width / 2, down.y + height),
				text,
				style,
				TextAnchor.BASELINE_LEFT,
				object_id="dimension/{}/height/text".format(index),
			),
		),
		object_id="dimension/{}/height".format(index),
		metadata=metadata(kind="dimension", index=index, axis="height"),
	)


def _terminator(base, angle, half_width, depth, main):
	normal = angle + math.pi / 2
	first = Point(
		base.x + math.cos(normal) * half_width,
		base.y + math.sin(normal) * half_width,
	)
	second = Point(
		base.x - math.cos(normal) * half_width,
		base.y - math.sin(normal) * half_width,
	)
	offset = Point(math.sin(normal) * depth, -math.cos(normal) * depth)
	points = (first, second, second.translated(offset), first.translated(offset))
	return (
		Polygon(points, stroke=None, fill=Fill(WHITE)),
		Line(first, second, main),
		Polygon(points, stroke=None, fill=Fill(BLACK, "backward-diagonal")),
	)


def _support(center, support_type, main, double, index, side):
	radius = 3.5
	term_radius = 20
	base = Point(center.x, center.y + term_radius)
	children = []
	if support_type == "1":
		second_circle = Point(center.x, center.y + term_radius - radius)
		children.extend(
			(
				Line(center, base, double),
				*_terminator(base, math.pi / 2, 15, 10, main),
				Ellipse(
					Rect(
						center.x - radius,
						center.y - radius,
						radius * 2,
						radius * 2,
					),
					main,
					Fill(WHITE),
				),
				Ellipse(
					Rect(
						second_circle.x - radius,
						second_circle.y - radius,
						radius * 2,
						radius * 2,
					),
					main,
					Fill(WHITE),
				),
			)
		)
	else:
		connection = Point(center.x, center.y + term_radius - radius * 2 / 3)
		half = 15 * 2 / 3
		left = Point(base.x - half, base.y)
		right = Point(base.x + half, base.y)
		children.extend(
			(
				*_terminator(base, math.pi / 2, 15, 10, main),
				Line(left, right, main),
				Line(center, right, main),
				Line(center, left, main),
				Ellipse(
					Rect(
						center.x - radius,
						center.y - radius,
						radius * 2,
						radius * 2,
					),
					main,
					Fill(WHITE),
				),
			)
		)
	return Group(
		children,
		object_id="support/{}/{}/{}".format(index, side, support_type),
		metadata=metadata(
			kind="support",
			index=index,
			side=side,
			support_type=support_type,
		),
	)


def _square_moment(center, x_extent, y_extent, inverse, size, index, side):
	stroke = Stroke(width=1)
	if inverse:
		top_end = Point(center.x - x_extent, center.y - y_extent)
		bottom_end = Point(center.x + x_extent, center.y + y_extent)
	else:
		top_end = Point(center.x + x_extent, center.y - y_extent)
		bottom_end = Point(center.x - x_extent, center.y + y_extent)
	children = [
		Line(Point(center.x, center.y + y_extent), Point(center.x, center.y - y_extent), stroke),
		Line(Point(center.x, center.y - y_extent), top_end, stroke),
		Line(Point(center.x, center.y + y_extent), bottom_end, stroke),
	]
	for tip, direction in ((top_end, 1 if not inverse else -1), (bottom_end, -1 if not inverse else 1)):
		children.append(
			Polygon(
				(
					tip,
					Point(tip.x - direction * size, tip.y + 4),
					Point(tip.x - direction * size, tip.y - 4),
				),
				stroke,
				Fill(BLACK),
			)
		)
	return Group(
		children,
		object_id="moment/{}/{}".format(index, side),
		metadata=metadata(kind="moment", index=index, side=side),
	)


class PlateLayoutBuilder:
	def build(self, task, settings, text_metrics, text_transform=None):
		text_transform = text_transform or (lambda value: value)
		sections = task["sections"]
		loads = task["sectforce"]
		nodes = task["betsect"]
		if not sections:
			raise ValueError("plate task requires at least one section")
		if len(sections) != len(loads) or len(sections) != len(nodes):
			raise ValueError("plate task arrays have inconsistent lengths")
		if text_metrics is None:
			raise ValueError("text_metrics is required for plate layout")

		main = Stroke(width=settings.line_width)
		half = Stroke(width=max(1, int(settings.line_width / 2)))
		double = Stroke(width=max(1, int(settings.line_width * 2)))
		axis_stroke = Stroke(width=settings.line_width, line_style="dash-dot")
		style = TextStyle(point_size=settings.font_size, italic=True)
		objects = []

		left_span = 50.0
		right_span = 50.0
		up_span = 100.0
		down_span = (
			100.0
			+ len(sections) * settings.dimension_step
			+ settings.dimension_start
		)
		if settings.fixed_ends:
			left_span += settings.base_height + settings.fixed_end_length
			right_span += settings.base_height + settings.fixed_end_length
		center = Point(
			settings.width / 2 + left_span - right_span,
			settings.hcenter + (up_span - down_span) / 2,
		)
		max_width = max(float(_value(section, "d")) for section in sections)
		max_height = max(float(_value(section, "h")) for section in sections)
		scale = (settings.width - left_span - right_span) / max_width

		previous = None
		for reverse_index, section in enumerate(reversed(sections)):
			index = len(sections) - reverse_index - 1
			width = float(_value(section, "d")) * scale
			height = float(_value(section, "h")) * settings.base_height
			rect = Rect(
				center.x - width / 2,
				center.y - height / 2,
				width,
				height,
			)
			if _value(section, "intgran", True):
				objects.append(
					Rectangle(
						rect,
						main,
						Fill(WHITE),
						object_id="plate/section/{}".format(index),
						metadata=metadata(kind="section", index=index),
					)
				)
			else:
				full_height = max_height * settings.base_height
				objects.append(
					Rectangle(
						Rect(
							center.x - width / 2,
							center.y - full_height / 2,
							width,
							full_height,
						),
						Stroke(WHITE, settings.line_width),
						Fill(WHITE),
					)
				)
				lines = [
					Line(Point(rect.left, rect.top), Point(rect.right, rect.top), main),
					Line(Point(rect.left, rect.bottom), Point(rect.right, rect.bottom), main),
				]
				if previous is not None:
					previous_height = float(_value(previous, "h")) * settings.base_height
					for x in (rect.left, rect.right):
						lines.extend(
							(
								Line(Point(x, rect.top), Point(x, center.y - previous_height / 2), main),
								Line(Point(x, rect.bottom), Point(x, center.y + previous_height / 2), main),
							)
						)
				objects.append(
					Group(
						lines,
						object_id="plate/section/{}".format(index),
						metadata=metadata(kind="section", index=index),
					)
				)
			if _value(section, "shtrih", False):
				objects.append(
					Rectangle(
						Rect(
							rect.x - settings.line_width / 2,
							rect.y - settings.line_width / 2,
							rect.width + settings.line_width,
							rect.height + settings.line_width,
						),
						None,
						Fill(BLACK, "backward-diagonal"),
						object_id="plate/section/{}/hatch".format(index),
					)
				)
			previous = section

		if settings.fixed_ends:
			section = sections[-1]
			height = float(_value(section, "h")) * settings.base_height
			plate_width = float(_value(section, "d")) * scale
			length = settings.fixed_end_length
			clearance = settings.base_height
			left_inner = center.x - plate_width / 2
			left_outer = left_inner - length
			right_inner = center.x + plate_width / 2
			right_outer = right_inner + length
			top = center.y - height / 2
			bottom = center.y + height / 2
			for side, outer in (("left", left_outer), ("right", right_inner)):
				objects.append(
					Rectangle(
						Rect(outer - (clearance if side == "left" else 0), top - clearance, length + clearance, height + 2 * clearance),
						None,
						Fill(BLACK, "forward-diagonal"),
					)
				)
				inner_rect = Rect(
					outer - settings.line_width / 2,
					top - settings.line_width / 2,
					length + settings.line_width,
					height + settings.line_width,
				)
				objects.extend(
					(
						Rectangle(inner_rect, None, Fill(WHITE)),
						Rectangle(
							inner_rect,
							None,
							Fill(BLACK, "backward-diagonal"),
							object_id="fixed-end/{}".format(side),
							metadata=metadata(kind="fixed-end", side=side),
						),
					)
				)
			objects.extend(
				(
					Line(Point(left_outer, top), Point(left_inner, top), main),
					Line(Point(left_outer, top), Point(left_outer, bottom), main),
					Line(Point(left_outer, bottom), Point(left_inner, bottom), main),
					Line(Point(right_inner, top), Point(right_outer, top), main),
					Line(Point(right_outer, top), Point(right_outer, bottom), main),
					Line(Point(right_inner, bottom), Point(right_outer, bottom), main),
				)
			)

		if settings.axis:
			objects.append(
				Line(
					Point(center.x, center.y + max_height * settings.base_height / 2 + 10),
					Point(center.x, center.y - max_height * settings.base_height / 2 - 10),
					axis_stroke,
					object_id="plate/axis",
					metadata=metadata(kind="axis"),
				)
			)

		previous_width = 0.0
		for index, section in enumerate(sections):
			width = float(_value(section, "d")) * scale
			height = float(_value(section, "h")) * settings.base_height
			if _value(section, "dtext_en", True):
				p0 = Point(center.x - width / 2, center.y + height / 2)
				p1 = Point(center.x + width / 2, center.y + height / 2)
				level = (
					center.y
					+ max_height * settings.base_height / 2
					+ settings.dimension_start
					+ settings.dimension_step * (index + 1)
				)
				text = _value(section, "dtext", "")
				if not text:
					value = _value(section, "d")
					text = "\\diam{}d".format(value if value != 1 else "")
				objects.append(
					_horizontal_dimension(
						p0,
						p1,
						level,
						half,
						style,
						text_transform(text),
						index,
					)
				)
			if _value(section, "htext_en", True):
				text = _value(section, "htext", "")
				if not text:
					value = _value(section, "h")
					text = "{}h".format(value if value != 1 else "")
				x = center.x + (
					previous_width / 2 + (width - previous_width) / 4
				)
				objects.append(
					_vertical_dimension(
						Point(x, center.y - height / 2),
						Point(x, center.y + height / 2),
						center,
						half,
						style,
						text_transform(text),
						text_metrics,
						index,
					)
				)
			previous_width = width

		previous_width = 0.0
		for index, (section, load) in enumerate(zip(sections, loads)):
			width = float(_value(section, "d")) * scale
			height = float(_value(section, "h")) * settings.base_height
			if _value(load, "distrib", False):
				top = center.y - height / 2 - settings.line_width
				for start_x, end_x in (
					(center.x + width / 2, center.x + previous_width / 2),
					(center.x - previous_width / 2, center.x - width / 2),
				):
					distance = abs(end_x - start_x)
					if distance < 20:
						continue
					count = int(distance / 10)
					count = count - count % 2 + 1
					line_y = top - 20
					children = [Line(Point(start_x, line_y), Point(end_x, line_y), half)]
					for arrow_index in range(count):
						ratio = arrow_index / (count - 1)
						x = ratio * end_x + (1 - ratio) * start_x
						children.append(
							Arrow(
								Point(x, line_y),
								Point(x, top),
								half,
								settings.arrow_size * 2 / 3,
								settings.arrow_size * 4 / 9,
								head_stroke=half,
							)
						)
					objects.append(
						Group(
							children,
							object_id="load/{}/{}".format(index, "right" if start_x > center.x else "left"),
							metadata=metadata(kind="distributed-load", index=index),
						)
					)
				objects.append(
					Line(
						Point(center.x + previous_width / 2, top - 20),
						Point(center.x - previous_width / 2, top - 20),
						half,
					)
				)
			previous_width = width

		for index, (section, node) in enumerate(zip(sections, nodes)):
			width = float(_value(section, "d")) * scale
			height = float(_value(section, "h")) * settings.base_height
			top = center.y - height / 2 - settings.line_width
			force = _value(node, "fen", "нет")
			if force != "нет":
				arrow_top = top - 40
				children = []
				for x in (center.x + width / 2, center.x - width / 2):
					start = Point(x, arrow_top) if force == "-" else Point(x, top)
					end = Point(x, top) if force == "-" else Point(x, arrow_top)
					children.append(
						Arrow(
							start,
							end,
							half,
							settings.arrow_size,
							settings.arrow_size * 2 / 3,
							head_stroke=half,
						)
					)
				children.append(
					Line(
						Point(center.x + width / 2, arrow_top),
						Point(center.x - width / 2, arrow_top),
						half,
					)
				)
				objects.append(
					Group(
						children,
						object_id="force/{}".format(index),
						metadata=metadata(kind="force", index=index, direction=force),
					)
				)
			moment = _value(node, "men", "нет")
			if moment != "нет":
				direction = moment == "+"
				for side, x, inverse in (
					("right", center.x + width / 2, not direction),
					("left", center.x - width / 2, direction),
				):
					objects.append(
						_square_moment(
							Point(x, center.y),
							20,
							height / 2 + 32,
							inverse,
							settings.arrow_size,
							index,
							side,
						)
					)
			support_type = _value(node, "sharn", "нет")
			if support_type != "нет":
				for side, x in (
					("right", center.x + width / 2),
					("left", center.x - width / 2),
				):
					objects.append(
						_support(
							Point(x, center.y + height / 2 + 3),
							support_type,
							main,
							double,
							index,
							side,
						)
					)

		for index, label in enumerate(task.get("labels", ())):
			position = _value(label, "pos")
			objects.append(
				Text(
					Point(
						center.x + float(position[0]) * scale,
						center.y + float(position[1]),
					),
					text_transform(_value(label, "text", "")),
					style,
					TextAnchor.CENTER,
					object_id="label/{}".format(index),
					metadata=metadata(kind="label", index=index),
				)
			)

		return Scene(
			Rect(0, 0, settings.width, settings.height),
			objects,
			content_bounds=Rect(
				center.x - max_width * scale / 2,
				center.y - max_height * settings.base_height / 2,
				max_width * scale,
				max_height * settings.base_height,
			),
		)
