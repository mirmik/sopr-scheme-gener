"""Qt-independent layout for the branching rod-system task."""

import math
from dataclasses import dataclass
from typing import Optional

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
	Scene,
	Stroke,
	Text,
	TextAnchor,
	TextStyle,
	metadata,
)


@dataclass(frozen=True)
class RodSystem2LayoutSettings:
	width: float
	height: float
	hcenter: float
	base_length: float = 80.0
	joint_radius: float = 4.0
	font_size: float = 12.0
	line_width: float = 2.0
	highlighted_section: int = -1
	hovered_node: int = -1
	preview_start_node: int = -1
	preview_target: Optional[Point] = None


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
	center = Point(
		(start.x + end.x) / 2
		+ nx * (offset + measurement.width / 2),
		(start.y + end.y) / 2
		+ measurement.height / 4
		+ ny * offset,
	)
	return Text(
		center,
		value,
		style,
		TextAnchor.BASELINE_CENTER,
		object_id=object_id,
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


def _fixed_end(center, angle, radius, main, object_id):
	width = 30
	depth = 10

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
	sector = angle / (math.pi * 2) - math.floor(angle / (math.pi * 2))
	pattern = (
		"forward-diagonal"
		if (0 < sector < 0.25) or (0.5 < sector < 0.75)
		else "backward-diagonal"
	)
	return Group(
		(
			Polygon(points, stroke=None, fill=Fill(BLACK, pattern), convex=True),
			Line(points[0], points[1], main),
			_ellipse(center, radius, main),
		),
		object_id=object_id,
		metadata=metadata(kind="fixed-end"),
	)


class RodSystem2LayoutBuilder:
	def build(self, task, settings, text_metrics, text_transform=None, length_text=None):
		text_transform = text_transform or (lambda value: value)
		length_text = length_text or (lambda value, suffix="": str(value) + suffix)
		sections = task["sections"]
		if settings.base_length <= 0:
			raise ValueError("rod-system-2 base length must be positive")

		model_starts = []
		model_ends = []
		for index, section in enumerate(sections):
			parent = int(_value(section, "start_from", -1))
			if parent < -1 or parent >= index:
				raise ValueError(
					"rod-system-2 section {} has invalid start_from".format(index)
				)
			start = Point(0, 0) if parent == -1 else model_ends[parent]
			angle = math.radians(_value(section, "angle", 0))
			end = Point(
				start.x + _value(section, "l", 0) * math.cos(angle),
				start.y + _value(section, "l", 0) * math.sin(angle),
			)
			model_starts.append(start)
			model_ends.append(end)

		xmin = ymin = xmax = ymax = 0.0
		for index, section in enumerate(sections):
			if _value(section, "body", True):
				length = _value(section, "l", 0)
			elif _value(section, "force", "нет") in ("к", "от"):
				length = 40 / settings.base_length
			else:
				continue
			angle = math.radians(_value(section, "angle", 0))
			point = Point(
				model_starts[index].x + math.cos(angle) * length,
				model_starts[index].y + math.sin(angle) * length,
			)
			xmin, xmax = min(xmin, point.x), max(xmax, point.x)
			ymin, ymax = min(ymin, point.y), max(ymax, point.y)

		center = Point(
			settings.width / 2 - (xmax + xmin) * settings.base_length / 2,
			settings.hcenter + (ymax + ymin) * settings.base_length / 2,
		)

		def screen(model_point):
			return Point(
				center.x + model_point.x * settings.base_length,
				center.y - model_point.y * settings.base_length,
			)

		starts = tuple(screen(point) for point in model_starts)
		ends = tuple(screen(point) for point in model_ends)
		node_points = [center, *ends]
		node_sources = [-1, *range(len(sections))]
		hit_node_indexes = {0}
		hit_node_indexes.update(
			index + 1
			for index, section in enumerate(sections)
			if _value(section, "body", True)
		)
		visible_node_points = [center]
		visible_node_points.extend(
			ends[index]
			for index, section in enumerate(sections)
			if _value(section, "body", True)
			and _value(section, "sharn", "нет") != "нет"
		)

		def has_node(point):
			return any(
				math.hypot(point.x - node.x, point.y - node.y) < 0.1
				for node in visible_node_points
			)

		main = Stroke(width=settings.line_width)
		half = Stroke(width=max(1, int(settings.line_width / 2)))
		double = Stroke(width=max(1, int(settings.line_width * 2)))
		green = Stroke(Color(0, 255, 0), width=settings.line_width)
		half_green = Stroke(
			Color(0, 255, 0),
			width=max(1, int(settings.line_width / 2)),
		)
		wide_green = Stroke(
			Color(0, 255, 0),
			width=max(1, int(settings.line_width * 2)),
		)
		dash = Stroke(width=2, line_style="dash-dot")
		dash_green = Stroke(Color(0, 255, 0), width=4, line_style="dash-dot")
		style = TextStyle(point_size=settings.font_size, italic=True)
		objects = []

		for index, section in enumerate(sections):
			add_angle = _value(section, "addangle", 0)
			if not add_angle:
				continue
			angle = _value(section, "angle", 0)
			target_angle = angle + add_angle
			start = starts[index]
			is_highlighted = settings.highlighted_section == index
			guide_stroke = dash_green if is_highlighted else dash
			arc_stroke = half_green if is_highlighted else half
			radius = 50
			first = Point(
				start.x + 60 * math.cos(math.radians(angle)),
				start.y - 60 * math.sin(math.radians(angle)),
			)
			second = Point(
				start.x + 60 * math.cos(math.radians(target_angle)),
				start.y - 60 * math.sin(math.radians(target_angle)),
			)
			text_point = Point(
				start.x
				+ 70 * math.cos(math.radians((target_angle + angle) / 2)),
				start.y
				- 70 * math.sin(math.radians((target_angle + angle) / 2)),
			)
			angle_text = text_transform("{}\\degree".format(abs(add_angle)))
			objects.append(
				Group(
					(
						Line(start, first, guide_stroke),
						Line(start, second, guide_stroke),
						Arc(
							Rect(
								start.x - radius,
								start.y - radius,
								radius * 2 + 1,
								radius * 2 + 1,
							),
							angle,
							add_angle,
							arc_stroke,
						),
						Text(
							Point(
								text_point.x,
								text_point.y
								+ text_metrics.measure(angle_text, style).height / 4,
							),
							angle_text,
							style,
							TextAnchor.BASELINE_CENTER,
							object_id="section/{}/angle/text".format(index),
						),
					),
					object_id="section/{}/angle".format(index),
					metadata=metadata(kind="angle", index=index),
				)
			)

		rendered_body_text = False
		for index, section in enumerate(sections):
			if not _value(section, "body", True):
				continue
			is_highlighted = settings.highlighted_section == index
			body_stroke = wide_green if is_highlighted else double
			joint_stroke = green if is_highlighted else main
			start = starts[index]
			end = ends[index]
			children = [Line(start, end, body_stroke)]
			if _value(section, "wide", False):
				offset = Point(0, 8)
				children.extend(
					(
						Line(start.translated(offset), end.translated(offset), body_stroke),
						Line(start, start.translated(offset), body_stroke),
						Line(end, end.translated(offset), body_stroke),
					)
				)
			support = _value(section, "sharn", "шарн+заделка")
			angle = math.radians(_value(section, "angle", 0))
			if support == "шарн+заделка":
				children.append(
					_fixed_end(
						end,
						-angle,
						settings.joint_radius,
						main,
						"section/{}/fixed-end".format(index),
					)
				)
			elif support == "шарн":
				children.append(
					_ellipse(
						end,
						settings.joint_radius,
						joint_stroke,
						object_id="section/{}/end-joint".format(index),
					)
				)
			parent = int(_value(section, "start_from", -1))
			if parent != -1 and _value(sections[parent], "sharn", "нет") != "нет":
				children.append(
					_ellipse(
						start,
						settings.joint_radius,
						joint_stroke,
						object_id="section/{}/start-joint".format(index),
					)
				)
			body = Group(
				children,
				object_id="section/{}/body".format(index),
				metadata=metadata(kind="section", index=index),
				antialias=False if rendered_body_text else None,
			)
			objects.append(body)
			length = length_text(_value(section, "l", 0), suffix="l")
			area = length_text(_value(section, "A", 1), suffix="A")
			objects.append(
				_angled_text(
					start,
					end,
					"{},{},E".format(length, area),
					style,
					text_metrics,
					_value(section, "alttxt", False),
					14,
					"section/{}/body/text".format(index),
				)
			)
			rendered_body_text = True

		for index, section in enumerate(sections):
			force = _value(section, "force", "нет")
			if force == "нет":
				continue
			is_highlighted = settings.highlighted_section == index
			force_stroke = green if is_highlighted else main
			head_stroke = force_stroke if is_highlighted else half
			start = starts[index]
			angle = math.radians(_value(section, "angle", 0))
			node_radius = 6 if has_node(start) else 0
			near = Point(
				start.x + math.cos(angle) * node_radius,
				start.y - math.sin(angle) * node_radius,
			)
			far = Point(
				start.x + math.cos(angle) * 50,
				start.y - math.sin(angle) * 50,
			)
			middle = Point(
				start.x + math.cos(angle) * 25,
				start.y - math.sin(angle) * 25,
			)
			children = []
			if force == "к":
				children.append(
					_arrow(
						far,
						near,
						force_stroke,
						15,
						head_stroke=head_stroke,
					)
				)
			elif force == "от":
				children.append(
					_arrow(
						near,
						far,
						force_stroke,
						15,
						head_stroke=head_stroke,
					)
				)
			elif force == "вдоль":
				vector = Point(math.cos(angle) * 20, -math.sin(angle) * 20)
				normal = Point(vector.y, -vector.x)
				first_start = start.translated(normal)
				second_start = Point(start.x - normal.x, start.y - normal.y)
				first_end = first_start.translated(vector)
				second_end = second_start.translated(vector)
				if is_highlighted:
					first_line = green
					first_head = half
					second_line = green
					second_head = green
					connector = green
				else:
					first_line = main
					first_head = half
					second_line = half
					second_head = half
					connector = half
				children.extend(
					(
						_arrow(
							first_start,
							first_end,
							first_line,
							10,
							head_stroke=first_head,
						),
						_arrow(
							second_start,
							second_end,
							second_line,
							10,
							head_stroke=second_head,
						),
						Line(first_start, second_start, connector),
					)
				)
				middle = start
				far = start.translated(vector)
			else:
				raise ValueError(
					"Unsupported rod-system-2 force: {!r}".format(force)
				)
			force_text = text_transform(_value(section, "ftxt", ""))
			if force_text:
				children.append(
					_text_by_points(
						middle,
						far,
						force_text,
						style,
						text_metrics,
						_value(section, "alttxt", False),
						27 if force == "вдоль" else 12,
						"section/{}/force/text".format(index),
					)
				)
			objects.append(
				Group(
					children,
					object_id="section/{}/force".format(index),
					metadata=metadata(kind="force", index=index, direction=force),
					antialias=False if rendered_body_text else None,
				)
			)

		root = _ellipse(
			center,
			settings.joint_radius,
			main,
			plus_one=False,
			object_id="node/0/visible",
		)
		if rendered_body_text:
			objects.append(
				Group((root,), object_id="node/0/joint", antialias=False)
			)
		else:
			objects.append(root)

		for node_index, point in enumerate(node_points):
			if (
				node_index in hit_node_indexes
				and settings.hovered_node == node_index
			):
				objects.append(
					_ellipse(
						point,
						5,
						green,
						Fill(Color(0, 255, 0)),
						plus_one=False,
						object_id="node/{}/hover".format(node_index),
					)
				)
			objects.append(
				Ellipse(
					Rect(point.x - 8, point.y - 8, 16, 16),
					stroke=None,
					fill=Fill(Color(0, 0, 0, 0)),
					object_id="node/{}".format(node_index),
					metadata=metadata(
						kind=(
							"node"
							if node_index in hit_node_indexes
							else "geometry-node"
						),
						index=node_index,
						source_section=node_sources[node_index],
					),
				)
			)

		if (
			settings.preview_start_node >= 0
			and settings.preview_start_node < len(node_points)
			and settings.preview_target is not None
		):
			start = node_points[settings.preview_start_node]
			target = settings.preview_target
			dx = target.x - start.x
			dy = target.y - start.y
			angle = math.degrees(math.atan2(-dy, dx))
			angle = round(angle / 15) * 15
			length = math.hypot(dx, dy) / settings.base_length
			length = round(length / 0.5) * 0.5
			radians = math.radians(angle)
			end = Point(
				start.x + math.cos(radians) * length * settings.base_length,
				start.y - math.sin(radians) * length * settings.base_length,
			)
			angle_text = text_transform("{}\\degree".format(abs(angle)))
			text_point = Point(
				start.x + 70 * math.cos(radians / 2),
				start.y - 70 * math.sin(radians / 2),
			)
			objects.append(
				Group(
					(
						Line(start, end, main),
						_angled_text(
							start,
							end,
							"{}l".format(length),
							style,
							text_metrics,
							False,
							14,
							"preview/length",
						),
						Arc(
							Rect(start.x - 50, start.y - 50, 101, 101),
							0,
							angle,
							main,
						),
						Text(
							Point(
								text_point.x,
								text_point.y
								+ text_metrics.measure(angle_text, style).height / 4,
							),
							angle_text,
							style,
							TextAnchor.BASELINE_CENTER,
							object_id="preview/angle/text",
						),
					),
					object_id="preview",
					metadata=metadata(kind="preview"),
				)
			)

		return Scene(Rect(0, 0, settings.width, settings.height), tuple(objects))
