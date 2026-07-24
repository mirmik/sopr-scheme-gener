"""Qt-independent layout for column-stability schemes."""

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


SUPPORT_NONE = "нет"
SUPPORT_FIXED = "заделка"
SUPPORT_HINGE = "шарнир"
SUPPORT_SIDE_LEFT = "боковая тяга слева"
SUPPORT_SIDE_RIGHT = "боковая тяга справа"
SUPPORT_FLOATING = "плавающая заделка"
SUPPORT_FLOATING_LEFT = "плавающая заделка слева"
SUPPORT_FLOATING_RIGHT = "плавающая заделка справа"
SUPPORT_TYPES = (
	SUPPORT_NONE,
	SUPPORT_FIXED,
	SUPPORT_HINGE,
	SUPPORT_SIDE_LEFT,
	SUPPORT_SIDE_RIGHT,
	SUPPORT_FLOATING,
)

LOAD_NONE = "нет"
LOAD_DOWN = "вниз"
LOAD_UP = "вверх"
LOAD_TYPES = (LOAD_NONE, LOAD_DOWN, LOAD_UP)


@dataclass(frozen=True)
class ColumnStabilityLayoutSettings:
	width: float = 400.0
	height: float = 250.0
	hcenter: float = 125.0
	line_width: float = 2.0
	font_size: float = 12.0
	arrow_size: float = 12.0
	rod_width: float = 5.0
	support_size: float = 36.0


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _hatching(x1, y1, x2, y2, stroke, step=8, direction=-1):
	lines = []
	if abs(y2 - y1) < 0.01:
		x = x1
		while x <= x2:
			lines.append(
				Line(Point(x, y1), Point(x + direction * 6, y1 + 7), stroke)
			)
			x += step
	else:
		y = y1
		while y <= y2:
			lines.append(
				Line(Point(x1, y), Point(x1 + direction * 7, y + 6), stroke)
			)
			y += step
	return tuple(lines)


def _fixed_support(point, size, stroke, object_id, at_top=False):
	y = point.y - 2 if at_top else point.y + 2
	surface_y = y - 2 if at_top else y + 2
	return Group(
		(
			Line(Point(point.x - size, surface_y), Point(point.x + size, surface_y), stroke),
			*_hatching(
				point.x - size,
				surface_y,
				point.x + size,
				surface_y,
				stroke,
			),
		),
		object_id=object_id,
		metadata=metadata(kind="support", support="fixed"),
	)


def _hinge_support(point, size, stroke, object_id, at_top=False):
	sign = -1 if at_top else 1
	radius = max(4.0, size / 5)
	base_y = point.y + sign * size
	triangle = Polygon(
		(
			Point(point.x, point.y + sign * radius),
			Point(point.x - size * 0.65, base_y),
			Point(point.x + size * 0.65, base_y),
		),
		stroke,
		Fill(WHITE),
	)
	surface_y = base_y + sign * 3
	return Group(
		(
			Ellipse(
				Rect(point.x - radius, point.y - radius, radius * 2, radius * 2),
				stroke,
				Fill(WHITE),
			),
			triangle,
			Line(
				Point(point.x - size, surface_y),
				Point(point.x + size, surface_y),
				stroke,
			),
			*_hatching(
				point.x - size,
				surface_y,
				point.x + size,
				surface_y,
				stroke,
			),
		),
		object_id=object_id,
		metadata=metadata(kind="support", support="hinge"),
	)


def _side_link(point, size, stroke, object_id, side, at_endpoint=False):
	sign = -1 if side == "left" else 1
	radius = max(3.5, size / 6)
	inner = (
		point
		if at_endpoint
		else Point(point.x + sign * radius * 1.5, point.y)
	)
	outer = Point(point.x + sign * size * 1.8, point.y)
	wall_x = outer.x + sign * radius
	link_start = Point(inner.x + sign * radius, inner.y)
	link_end = Point(outer.x - sign * radius, outer.y)
	return Group(
		(
			Line(link_start, link_end, stroke),
			Ellipse(
				Rect(inner.x - radius, inner.y - radius, radius * 2, radius * 2),
				stroke,
				Fill(WHITE),
			),
			Ellipse(
				Rect(outer.x - radius, outer.y - radius, radius * 2, radius * 2),
				stroke,
				Fill(WHITE),
			),
			Line(
				Point(wall_x, point.y - size),
				Point(wall_x, point.y + size),
				stroke,
			),
			*_hatching(
				wall_x,
				point.y - size,
				wall_x,
				point.y + size,
				stroke,
				direction=sign,
			),
		),
		object_id=object_id,
		metadata=metadata(kind="support", support="side-link", side=side),
	)


def _floating_clamp(point, size, stroke, object_id):
	"""Draw the two cheek plates used in the supplied stability references."""
	gap = max(5.0, size / 4)
	left_plate = point.x - gap
	right_plate = point.x + gap
	left_wall = point.x - size * 1.8
	right_wall = point.x + size * 1.8
	top = point.y - size * 0.55
	bottom = point.y + size * 0.55
	return Group(
		(
			Line(Point(left_plate, top), Point(left_plate, bottom), stroke),
			Line(Point(right_plate, top), Point(right_plate, bottom), stroke),
			Line(Point(left_wall, top), Point(left_plate, top), stroke),
			Line(Point(left_wall, bottom), Point(left_plate, bottom), stroke),
			Line(Point(right_plate, top), Point(right_wall, top), stroke),
			Line(Point(right_plate, bottom), Point(right_wall, bottom), stroke),
			*_hatching(left_wall, top, left_wall, bottom, stroke, direction=-1),
			*_hatching(right_wall, top, right_wall, bottom, stroke, direction=1),
		),
		object_id=object_id,
		metadata=metadata(kind="support", support="floating-clamp"),
	)


def _support(point, support, settings, stroke, object_id, node_index, node_count):
	if support in (None, SUPPORT_NONE, "none"):
		return None
	if support in (SUPPORT_FIXED, "fixed"):
		return _fixed_support(
			point,
			settings.support_size,
			stroke,
			object_id,
			at_top=node_index == node_count - 1,
		)
	if support in (SUPPORT_HINGE, "hinge"):
		return _hinge_support(
			point,
			settings.support_size,
			stroke,
			object_id,
			at_top=node_index == node_count - 1,
		)
	if support in (SUPPORT_SIDE_LEFT, "side-link-left"):
		return _side_link(
			point,
			settings.support_size,
			stroke,
			object_id,
			"left",
			at_endpoint=node_index in (0, node_count - 1),
		)
	if support in (SUPPORT_SIDE_RIGHT, "side-link-right"):
		return _side_link(
			point,
			settings.support_size,
			stroke,
			object_id,
			"right",
			at_endpoint=node_index in (0, node_count - 1),
		)
	if support in (
		SUPPORT_FLOATING,
		SUPPORT_FLOATING_LEFT,
		SUPPORT_FLOATING_RIGHT,
		"floating-clamp",
		"floating-clamp-left",
		"floating-clamp-right",
	):
		return _floating_clamp(point, settings.support_size, stroke, object_id)
	raise ValueError("Unsupported stability support: {!r}".format(support))


class ColumnStabilityLayoutBuilder:
	def build(self, task, settings, text_metrics, text_transform=None):
		text_transform = text_transform or (lambda value: value)
		segments = task.get("segments", ())
		nodes = task.get("nodes", ())
		if not segments:
			raise ValueError("column-stability requires at least one segment")
		if len(nodes) != len(segments) + 1:
			raise ValueError("column-stability requires one more node than segment")

		lengths = [float(_value(segment, "length", 1.0)) for segment in segments]
		if any(length <= 0 for length in lengths):
			raise ValueError("column-stability segment lengths must be positive")

		main = Stroke(width=settings.line_width)
		rod = Stroke(width=max(settings.line_width, settings.rod_width))
		half = Stroke(width=max(1.0, settings.line_width / 2))
		style = TextStyle(point_size=settings.font_size, italic=True)
		x = settings.width * 0.43
		top = max(55.0, settings.support_size + 10)
		bottom = max(top + 150.0, settings.hcenter + 90.0)
		lower_support = _value(nodes[0], "support", SUPPORT_NONE)
		if lower_support in (SUPPORT_HINGE, "hinge"):
			bottom_limit = settings.height - settings.support_size - 10
		else:
			bottom_limit = settings.height - 20
		bottom = min(bottom, bottom_limit)
		available = bottom - top
		total = sum(lengths)
		node_y = [bottom]
		for length in lengths:
			node_y.append(node_y[-1] - available * length / total)

		objects = []
		for index, segment in enumerate(segments):
			start = Point(x, node_y[index])
			end = Point(x, node_y[index + 1])
			objects.append(
				Line(
					start,
					end,
					rod,
					object_id="segment/{}/body".format(index),
					metadata=metadata(kind="segment", index=index),
				)
			)
			length_text = text_transform(str(_value(segment, "length_text", "")))
			if length_text:
				center_y = (start.y + end.y) / 2
				objects.append(
					Text(
						Point(x + 30, center_y),
						length_text,
						style,
						TextAnchor.CENTER,
						object_id="segment/{}/length-label".format(index),
						metadata=metadata(kind="length-label", index=index),
					)
				)
			rigidity = text_transform(str(_value(segment, "rigidity_text", "")))
			if rigidity:
				objects.append(
					Text(
						Point(x + 105, (start.y + end.y) / 2),
						rigidity,
						style,
						TextAnchor.CENTER,
						object_id="segment/{}/rigidity-label".format(index),
						metadata=metadata(kind="rigidity-label", index=index),
					)
				)

		for index, (node, y) in enumerate(zip(nodes, node_y)):
			point = Point(x, y)
			support = _support(
				point,
				_value(node, "support", SUPPORT_NONE),
				settings,
				main,
				"node/{}/support".format(index),
				index,
				len(nodes),
			)
			if support is not None:
				objects.append(support)

			load = _value(node, "load", LOAD_NONE)
			if load not in (LOAD_NONE, "none", None):
				is_internal = 0 < index < len(nodes) - 1
				if load in (LOAD_DOWN, "down"):
					neighbor_gap = (
						y - node_y[index + 1] if index + 1 < len(node_y) else 70
					)
					load_length = min(52.0, max(28.0, neighbor_gap * 0.65))
					start_y, end_y = y - load_length, y
				elif load in (LOAD_UP, "up"):
					neighbor_gap = y - node_y[index - 1] if index else -70
					load_length = min(52.0, max(28.0, abs(neighbor_gap) * 0.65))
					start_y, end_y = y + load_length, y
				else:
					raise ValueError("Unsupported stability load: {!r}".format(load))
				if is_internal:
					bar_half_width = settings.support_size * 0.9
					arrow_offset = bar_half_width * 0.65
					left_start = Point(x - arrow_offset, start_y)
					right_start = Point(x + arrow_offset, start_y)
					left_end = Point(x - arrow_offset, end_y)
					right_end = Point(x + arrow_offset, end_y)
					objects.append(
						Group(
							(
								Line(
									Point(x - bar_half_width, y),
									Point(x + bar_half_width, y),
									main,
									object_id="node/{}/load/bar".format(index),
								),
								Arrow(
									left_start,
									left_end,
									main,
									head_length=settings.arrow_size,
									head_width=settings.arrow_size * 2 / 3,
									head_stroke=half,
									object_id="node/{}/load/left".format(index),
								),
								Arrow(
									right_start,
									right_end,
									main,
									head_length=settings.arrow_size,
									head_width=settings.arrow_size * 2 / 3,
									head_stroke=half,
									object_id="node/{}/load/right".format(index),
								),
							),
							object_id="node/{}/load".format(index),
							metadata=metadata(
								kind="force",
								index=index,
								direction=load,
								style="crossbar",
							),
						)
					)
					label_x = x + bar_half_width + 18
				else:
					start = Point(x, start_y)
					end = Point(x, end_y)
					objects.append(
						Arrow(
							start,
							end,
							main,
							head_length=settings.arrow_size,
							head_width=settings.arrow_size * 2 / 3,
							head_stroke=half,
							object_id="node/{}/load".format(index),
							metadata=metadata(
								kind="force", index=index, direction=load, style="single"
							),
						)
					)
					label_x = x + 24
				label = text_transform(str(_value(node, "load_text", "")))
				if label:
					objects.append(
						Text(
							Point(label_x, (start_y + end_y) / 2),
							label,
							style,
							TextAnchor.CENTER,
							object_id="node/{}/load-label".format(index),
							metadata=metadata(kind="force-label", index=index),
						)
					)

		objects.append(
			Rectangle(
				Rect(0, 0, settings.width, settings.height),
				stroke=Stroke(BLACK, 1),
				fill=Fill(),
				object_id="viewport-border",
				metadata=metadata(kind="viewport"),
			)
		)
		return Scene(
			Rect(0, 0, settings.width, settings.height),
			tuple(objects),
		)
