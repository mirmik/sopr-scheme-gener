"""Qt-independent layout for the axial/torsion rod task."""

import math
from dataclasses import dataclass

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


AXIAL = 0
TORSION_STIFFNESS = 1
TORSION_DIAMETER = 2


@dataclass(frozen=True)
class AxialTorsionLayoutSettings:
	width: float
	height: float
	hcenter: float
	subtype: int = AXIAL
	axis: bool = True
	left_fixed: bool = False
	right_fixed: bool = False
	dimensions: bool = True
	base_section_height: float = 40.0
	arrow_size: float = 20.0
	dimension_offset: float = 40.0
	left_margin: float = 30.0
	right_margin: float = 30.0
	font_size: float = 12.0
	line_width: float = 2.0
	highlighted_section: int = -1
	highlighted_node: int = -1


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _arrow_head(tip, angle, size, stroke, object_id=None, top=False):
	shift = 0.5 if top and abs(math.sin(angle)) < 1e-12 and math.cos(angle) > 0 else 0
	tip = Point(tip.x + shift, tip.y + shift)
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
		object_id=object_id,
		convex=True,
	)


def _horizontal_arrow(start, direction, length, main, half, size, object_id):
	end = Point(start.x + direction * length, start.y)
	return Group(
		(
			Line(start, end, main),
			_arrow_head(
				end,
				0 if direction > 0 else math.pi,
				size,
				half,
				top=direction > 0,
			),
		),
		object_id=object_id,
		metadata=metadata(kind="force-arrow", direction=direction),
	)


def _double_horizontal_arrow(center, direction, length, height, main, half, size, object_id):
	first = Point(center.x, center.y + height / 2)
	second = Point(center.x, center.y - height / 2)
	return Group(
		(
			_horizontal_arrow(first, direction, length, main, half, size, None),
			_horizontal_arrow(second, direction, length, main, half, size, None),
			Line(first, second, half),
		),
		object_id=object_id,
		metadata=metadata(kind="force-arrow", direction=direction, extended=True),
	)


def _dimension(x0, x1, body_bottom, level, text, style, text_metrics, half, index):
	left = Point(int(x0), level)
	right = Point(int(x1), level)
	center = Point((left.x + right.x) / 2, level)
	splashed = x1 - x0 < 20
	left_angle = 0 if splashed else math.pi
	right_angle = math.pi if splashed else 0
	measurement = text_metrics.measure(text, style)
	return Group(
		(
			_arrow_head(left, left_angle, 10, half),
			_arrow_head(right, right_angle, 10, half),
			Line(left, right, half),
			Line(left, right, half),
			Line(Point(int(x0), body_bottom), left, half),
			Line(Point(int(x1), body_bottom), right, half),
			Text(
				Point(
					center.x,
					level - 3 - measurement.height / 4,
				),
				text,
				style,
				TextAnchor.BASELINE_CENTER,
				object_id="section/{}/dimension/text".format(index),
			),
		),
		object_id="section/{}/dimension".format(index),
		metadata=metadata(kind="dimension", index=index),
	)


def _leader_text(point, distance, value, style, text_metrics, half, object_id, right=False):
	measurement = text_metrics.measure(value, style)
	width = max(measurement.width, 18)
	shelf_y = point.y - distance
	shelf_left = Point(point.x - width / 2, shelf_y)
	shelf_right = Point(point.x + width / 2, shelf_y)
	leader_end = shelf_left if right else shelf_right
	return Group(
		(
			Line(point, leader_end, half),
			Line(shelf_left, shelf_right, half),
			Text(
				Point(point.x, shelf_y - 3),
				value,
				style,
				TextAnchor.BASELINE_CENTER,
			),
		),
		object_id=object_id,
		metadata=metadata(kind="label"),
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
	dx, dy = end.x - start.x, end.y - start.y
	length = math.hypot(dx, dy)
	ux, uy = dx / length, dy / length
	if alternate:
		ux, uy = -ux, -uy
	nx, ny = -uy, ux
	measurement = text_metrics.measure(value, style)
	center = Point(
		(start.x + end.x) / 2 + nx * (offset + measurement.width / 2),
		(start.y + end.y) / 2 + measurement.height / 4 + ny * offset,
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
						center.x
						+ (-1 if not alternate else 1) * measurement.width / 2,
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


def _circle_symbol(center, diameter, point, main, object_id=None):
	bounds = Rect(
		center.x - diameter / 2,
		center.y - diameter / 2,
		diameter,
		diameter,
	)
	children = [Ellipse(bounds, main, Fill(WHITE))]
	if point:
		inner = diameter / 4
		children.append(
			Ellipse(
				Rect(
					center.x + 0.5 - inner / 2,
					center.y + 0.5 - inner / 2,
					inner + 0.5,
					inner + 0.5,
				),
				main,
				Fill(BLACK),
			)
		)
	else:
		delta = diameter / 2 / math.sqrt(2)
		children.extend(
			(
				Line(
					Point(center.x - delta + 0.5, center.y - delta + 0.5),
					Point(center.x + delta + 0.5, center.y + delta + 0.5),
					main,
				),
				Line(
					Point(center.x - delta + 0.5, center.y + delta + 0.5),
					Point(center.x + delta + 0.5, center.y - delta + 0.5),
					main,
				),
			)
		)
	return Group(children, object_id=object_id)


def _torque_symbol(center, radius, positive, main, half, object_id):
	top = Point(center.x, center.y - radius - 11)
	bottom = Point(center.x, center.y + radius + 11)
	return Group(
		(
			_circle_symbol(top, 22, positive, main),
			_circle_symbol(bottom, 22, not positive, main),
			Line(
				Point(center.x, center.y - radius),
				Point(center.x, center.y + radius),
				half,
			),
		),
		object_id=object_id,
		metadata=metadata(kind="torque", direction="+" if positive else "-"),
	)


def _diameter_dimension(center_x, top, bottom, value, style, text_metrics, main, half, object_id):
	size = 10
	measurement = text_metrics.measure(value, style)
	center_y = (top + bottom) / 2
	text_x = center_x + text_metrics.measure("x", style).width / 2
	return Group(
		(
			Polygon(
				(
					Point(center_x, top),
					Point(center_x + size / 3, top),
					Point(center_x, top + size),
					Point(center_x - size / 3, top),
				),
				half,
				Fill(BLACK),
				convex=True,
			),
			Polygon(
				(
					Point(center_x, bottom - size),
					Point(center_x + size / 3, bottom - size),
					Point(center_x, bottom),
					Point(center_x - size / 3, bottom - size),
				),
				half,
				Fill(BLACK),
				convex=True,
			),
			Line(Point(center_x, top), Point(center_x, bottom), half),
			Rectangle(
				Rect(
					text_x,
					center_y - measurement.height / 2,
					measurement.width,
					measurement.height,
				),
				stroke=None,
				fill=Fill(WHITE),
			),
			Text(
				Point(text_x, center_y + measurement.height / 4),
				value,
				style,
				object_id=object_id + "/text",
			),
		),
		object_id=object_id,
		metadata=metadata(kind="diameter-dimension"),
	)


def _fixed_end(x0, x1, top, bottom, border_x, main, object_id):
	return Group(
		(
			Rectangle(
				Rect(x0, top, x1 - x0, bottom - top),
				stroke=None,
				fill=Fill(BLACK, "backward-diagonal"),
			),
			Line(Point(border_x, top), Point(border_x, bottom), main),
		),
		object_id=object_id,
		metadata=metadata(kind="fixed-end"),
	)


class AxialTorsionLayoutBuilder:
	def build(
		self,
		task,
		settings,
		text_metrics,
		text_transform=None,
		pretty_value=None,
	):
		text_transform = text_transform or (lambda value: value)
		pretty_value = pretty_value or (
			lambda value, suffix="": "{}{}".format(value, suffix)
		)
		sections = task["sections"]
		nodes = task["betsect"]
		loads = task["sectforce"]
		if not sections:
			raise ValueError("axial-torsion requires at least one section")
		if len(nodes) != len(sections) + 1 or len(loads) != len(sections):
			raise ValueError("axial-torsion arrays have inconsistent lengths")
		total_length = sum(float(_value(section, "l", 0)) for section in sections)
		if total_length <= 0:
			raise ValueError("axial-torsion total length must be positive")
		if settings.subtype not in (AXIAL, TORSION_STIFFNESS, TORSION_DIAMETER):
			raise ValueError("unknown axial-torsion subtype")

		main = Stroke(width=settings.line_width)
		half = Stroke(width=max(1, int(settings.line_width / 2)))
		wide_green = Stroke(
			color=Color(0, 255, 0),
			width=max(1, int(settings.line_width * 2)),
		)
		style = TextStyle(point_size=settings.font_size, italic=True)
		hcenter = settings.hcenter
		start_x = settings.left_margin
		end_x = settings.width - settings.right_margin
		arrow_length = 50
		if settings.subtype == AXIAL:
			first, last = nodes[0], nodes[-1]
			if _value(first, "Fstyle", "") != "к узлу" and _value(first, "F") == "-":
				start_x += arrow_length
			if _value(last, "Fstyle", "") != "к узлу" and _value(last, "F") == "+":
				end_x -= arrow_length
			if _value(first, "Fstyle", "") == "к узлу" and _value(first, "F") == "+":
				start_x += arrow_length
			if _value(last, "Fstyle", "") == "к узлу" and _value(last, "F") == "-":
				end_x -= arrow_length

		def coefficient(section):
			if settings.subtype == AXIAL:
				return math.sqrt(float(_value(section, "A", 0)))
			if settings.subtype == TORSION_STIFFNESS:
				return math.sqrt(float(_value(section, "GIk", 0)))
			return float(_value(section, "d", 0))

		max_area = max(float(_value(section, "A", 0)) for section in sections)
		dimension_level = int(
			hcenter
			+ settings.base_section_height * math.sqrt(max_area) / 2
			+ settings.dimension_offset
		)
		if settings.dimensions:
			hcenter -= settings.dimension_offset / 2
		cumulative = [0.0]
		for section in sections:
			cumulative.append(cumulative[-1] + float(_value(section, "l", 0)))

		def x_position(index):
			left_weight = total_length - cumulative[index]
			right_weight = cumulative[index]
			return (end_x * right_weight + start_x * left_weight) // total_length

		def radius(index):
			return coefficient(sections[index]) * settings.base_section_height / 2

		def node_radius(index):
			left = 0 if index == 0 else radius(index - 1)
			right = 0 if index == len(nodes) - 1 else radius(index)
			return max(left, right)

		def torque_radius(index):
			left = 0 if index == 0 else radius(index - 1)
			right = 0 if index == len(nodes) - 1 else radius(index)
			left_load = (
				index > 0 and _value(loads[index - 1], "mkr", "нет") != "нет"
			)
			right_load = (
				index < len(loads)
				and _value(loads[index], "mkr", "нет") != "нет"
			)
			value = max(left, right)
			if (value == left and left_load) or (value == right and right_load):
				value += 20
			return value

		objects = []
		for index, section in enumerate(sections):
			top = int(hcenter - radius(index))
			bottom = int(hcenter + radius(index))
			is_gap = settings.subtype == AXIAL and bool(
				_value(section, "delta", False)
			)
			if not is_gap:
				objects.append(
					Rectangle(
						Rect(
							int(x_position(index)),
							top,
							int(x_position(index + 1) - x_position(index)),
							int(bottom - top),
						),
						wide_green
						if settings.highlighted_section == index
						else main,
						Fill(WHITE),
						object_id="section/{}/body".format(index),
						metadata=metadata(kind="section", index=index),
					)
				)

			if settings.subtype == AXIAL:
				area = float(_value(section, "A", 1))
				modulus = _value(section, "E", 1)
				area_text = (
					"{}A".format(int(area + 0.1))
					if abs(area - int(area)) < 0.0001 and area != 1
					else ("A" if area == 1 else "{}A".format(area))
				)
				modulus_text = pretty_value(modulus, "E")
			else:
				stiffness = float(_value(section, "GIk", 1))
				area_text = (
					"{}GIk".format(int(stiffness + 0.1))
					if abs(stiffness - int(stiffness)) < 0.0001
					and stiffness != 1
					else (
						"GIk"
						if stiffness == 1
						else "{}GIk".format(stiffness)
					)
				)
				modulus_text = ""
			length = float(_value(section, "l", 1))
			length_text = (
				"{}l".format(int(length + 0.1))
				if abs(length - int(length)) < 0.0001 and length != 1
				else ("l" if length == 1 else "{}l".format(length))
			)
			if is_gap:
				dimension_text = ""
			elif _value(section, "text", ""):
				dimension_text = text_transform(_value(section, "text"))
			elif settings.subtype == TORSION_STIFFNESS:
				dimension_text = "{}, {}".format(length_text, area_text)
			elif settings.subtype == AXIAL:
				dimension_text = "{}, {}, {}".format(
					length_text, area_text, modulus_text
				)
			else:
				dimension_text = "{}, G".format(length_text)
			if settings.dimensions:
				objects.append(
					_dimension(
						x_position(index),
						x_position(index + 1),
						bottom,
						dimension_level,
						text_transform(dimension_text),
						style,
						text_metrics,
						half,
						index,
					)
				)

		if settings.axis:
			objects.append(
				Line(
					Point(5, hcenter),
					Point(settings.width - 5, hcenter),
					Stroke(width=1, dash=(10, 3, 1, 3)),
					object_id="axis",
					metadata=metadata(kind="axis"),
				)
			)

		if settings.subtype == AXIAL:
			for index, node in enumerate(nodes):
				force = _value(node, "F", "нет")
				if force == "нет":
					continue
				direction = 1 if force == "+" else -1
				style_name = _value(node, "Fstyle", "от узла")
				base = Point(x_position(index), hcenter)
				if style_name == "к узлу":
					base = Point(base.x - direction * arrow_length, base.y)
				if style_name == "выносн.":
					force_object = _double_horizontal_arrow(
						base,
						direction,
						arrow_length,
						node_radius(index) * 3.2,
						main,
						half,
						15,
						"node/{}/force".format(index),
					)
				else:
					force_object = _horizontal_arrow(
						base,
						direction,
						arrow_length,
						main,
						half,
						15,
						"node/{}/force".format(index),
					)
				objects.append(force_object)
				value = text_transform(_value(node, "T", ""))
				if value:
					displacement = direction * arrow_length / 2
					if style_name == "к узлу":
						displacement = -displacement
					text_point = Point(x_position(index) + displacement, hcenter)
					if style_name == "выносн.":
						measurement = text_metrics.measure(value, style)
						objects.append(
							Text(
								Point(
									text_point.x,
									hcenter - node_radius(index) * 1.6 - 6,
								),
								value,
								style,
								TextAnchor.BASELINE_CENTER,
								object_id="node/{}/force/text".format(index),
							)
						)
					else:
						objects.append(
							_leader_text(
								text_point,
								node_radius(index) + 10,
								value,
								style,
								text_metrics,
								half,
								"node/{}/force/text".format(index),
							)
						)

			for index, load in enumerate(loads):
				direction = _value(load, "Fr", "нет")
				if direction == "нет":
					continue
				x0, x1 = x_position(index), x_position(index + 1)
				objects.append(
					Rectangle(
						Rect(x0 + 2, hcenter - 5, x1 - x0 - 4, 10),
						stroke=None,
						fill=Fill(WHITE),
					)
				)
				count = int(abs(x1 - x0) / 20)
				count = count - count % 2 + 1
				children = []
				if count > 1:
					for arrow_index in range(count - 1):
						point = Point(
							x0 + (x1 - x0) * arrow_index / (count - 1) + 0.5,
							hcenter + 0.5,
						)
						children.append(
							_horizontal_arrow(
								point
								if direction == "+"
								else Point(point.x + 20, point.y),
								1 if direction == "+" else -1,
								20,
								main,
								half,
								12,
								None,
							)
						)
				objects.append(
					Group(
						children,
						object_id="section/{}/distributed-force".format(index),
						metadata=metadata(
							kind="distributed-force", direction=direction
						),
					)
				)
				value = text_transform(_value(load, "mkrT", ""))
				if value:
					objects.append(
						_leader_text(
							Point((x0 + x1) / 2, hcenter),
							radius(index) + 10,
							value,
							style,
							text_metrics,
							half,
							"section/{}/distributed-force/text".format(index),
							right=True,
						)
					)
		else:
			for index, node in enumerate(nodes):
				direction = _value(node, "Mkr", "нет")
				if direction == "нет":
					continue
				objects.append(
					_torque_symbol(
						Point(x_position(index), hcenter),
						torque_radius(index) + 10,
						direction == "+",
						main,
						half,
						"node/{}/torque".format(index),
					)
				)
				value = text_transform(_value(node, "T", ""))
				if value:
					objects.append(
						Text(
							Point(
								x_position(index) + 14,
								hcenter - torque_radius(index) - 14,
							),
							value,
							style,
							object_id="node/{}/torque/text".format(index),
						)
					)

			for index, load in enumerate(loads):
				direction = _value(load, "mkr", "нет")
				if direction == "нет":
					continue
				x0, x1 = x_position(index), x_position(index + 1)
				top, bottom = hcenter - radius(index), hcenter + radius(index)
				count = int(abs(x1 - x0) / 18)
				count = count - count % 2 + 1
				children = []
				if count > 1:
					for arrow_index in range(count):
						x = x0 + (x1 - x0) * arrow_index / (count - 1)
						for y, offset, point_symbol in (
							(top, -15, direction == "+"),
							(bottom, 15, direction != "+"),
						):
							target = Point(x, y + offset)
							children.extend(
								(
									Line(Point(x, y), target, half),
									_circle_symbol(
										target,
										10,
										point_symbol,
										main,
									),
								)
							)
				objects.append(
					Group(
						children,
						object_id="section/{}/distributed-torque".format(index),
						metadata=metadata(
							kind="distributed-torque", direction=direction
						),
					)
				)
				value = text_transform(_value(load, "mkrT", ""))
				if value:
					objects.append(
						Text(
							Point((x0 + x1) / 2, top - 28),
							value,
							style,
							object_id="section/{}/distributed-torque/text".format(
								index
							),
						)
					)

		if settings.subtype == TORSION_DIAMETER:
			for index, section in enumerate(sections):
				value = _value(section, "dtext", "") or pretty_value(
					_value(section, "d", 1), "d"
				)
				objects.append(
					_diameter_dimension(
						(x_position(index) + x_position(index + 1)) / 2,
						hcenter - radius(index),
						hcenter + radius(index),
						text_transform(value),
						style,
						text_metrics,
						main,
						half,
						"section/{}/diameter".format(index),
					)
				)

		for index, node in enumerate(nodes):
			value = text_transform(_value(node, "label", ""))
			if not value:
				continue
			position = _value(node, "label_off", "справа")
			x = x_position(index)
			if position == "справа-сверху":
				start = Point(x, hcenter - node_radius(index))
				end = Point(x, hcenter - node_radius(index) - 40)
				alternate, offset = False, 14
				leader = Point(x, hcenter)
			elif position == "слева-снизу":
				start = Point(x, hcenter + node_radius(index))
				end = Point(x, hcenter + node_radius(index) + 40)
				alternate, offset = True, -24
				leader = Point(x, hcenter)
			else:
				start = Point(x, hcenter + node_radius(index))
				end = Point(x, hcenter - node_radius(index))
				alternate, offset, leader = False, 6, None
			objects.append(
				_text_by_points(
					start,
					end,
					value,
					style,
					text_metrics,
					alternate,
					offset,
					"node/{}/label".format(index),
					leader,
				)
			)

		if 0 <= settings.highlighted_node < len(nodes):
			x = x_position(settings.highlighted_node)
			objects.append(
				Ellipse(
					Rect(x - 5, hcenter - 5, 10, 10),
					main,
					Fill(Color(0, 255, 0)),
					object_id="node/{}/highlight".format(
						settings.highlighted_node
					),
					metadata=metadata(kind="node-highlight"),
				)
			)

		if settings.left_fixed:
			height = radius(0) + 20
			objects.append(
				_fixed_end(
					x_position(0) - 10,
					x_position(0),
					hcenter - height,
					hcenter + height,
					x_position(0),
					main,
					"fixed-end/left",
				)
			)
		if settings.right_fixed:
			height = radius(len(sections) - 1) + 20
			objects.append(
				_fixed_end(
					x_position(len(sections)),
					x_position(len(sections)) + 10,
					hcenter - height,
					hcenter + height,
					x_position(len(sections)),
					main,
					"fixed-end/right",
				)
			)

		for index, section in enumerate(sections):
			value = text_transform(_value(section, "label", ""))
			if not value:
				continue
			if _value(section, "label_height", 20) <= -20:
				value += "  "
			objects.append(
				_text_by_points(
					Point(x_position(index), hcenter - radius(index)),
					Point(x_position(index + 1), hcenter - radius(index)),
					value,
					style,
					text_metrics,
					True,
					14,
					"section/{}/label".format(index),
					Point(
						(x_position(index) + x_position(index + 1)) / 2,
						hcenter,
					),
				)
			)

		return Scene(Rect(0, 0, settings.width, settings.height), tuple(objects))
