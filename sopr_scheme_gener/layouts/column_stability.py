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
	support_size: float = 24.0


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _hatching(x1, y1, x2, y2, stroke, step=8):
	lines = []
	if abs(y2 - y1) < 0.01:
		x = x1
		while x <= x2:
			lines.append(Line(Point(x, y1), Point(x - 6, y1 + 7), stroke))
			x += step
	else:
		y = y1
		while y <= y2:
			lines.append(Line(Point(x1, y), Point(x1 - 7, y + 6), stroke))
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


def _side_link(point, size, stroke, object_id, side):
	sign = -1 if side == "left" else 1
	radius = max(3.5, size / 6)
	inner = Point(point.x + sign * radius * 1.5, point.y)
	outer = Point(point.x + sign * size * 1.8, point.y)
	wall_x = outer.x + sign * radius
	return Group(
		(
			Ellipse(
				Rect(inner.x - radius, inner.y - radius, radius * 2, radius * 2),
				stroke,
				Fill(WHITE),
			),
			Line(inner, outer, stroke),
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
			*_hatching(left_wall, top, left_wall, bottom, stroke),
			*_hatching(right_wall, top, right_wall, bottom, stroke),
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
		return _side_link(point, settings.support_size, stroke, object_id, "left")
	if support in (SUPPORT_SIDE_RIGHT, "side-link-right"):
		return _side_link(point, settings.support_size, stroke, object_id, "right")
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
		top = max(70.0, settings.support_size + settings.arrow_size + 12)
		bottom = max(top + 100.0, settings.hcenter + 50.0)
		if bottom > settings.height - 35:
			bottom = settings.height - 35
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
						Point(x + 20, center_y),
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
						Point(x + 75, (start.y + end.y) / 2),
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
				if load in (LOAD_DOWN, "down"):
					neighbor_gap = (
						y - node_y[index + 1] if index + 1 < len(node_y) else 70
					)
					load_length = min(48.0, max(24.0, neighbor_gap * 0.65))
					start, end = Point(x, y - load_length), Point(x, y - 5)
				elif load in (LOAD_UP, "up"):
					neighbor_gap = y - node_y[index - 1] if index else -70
					load_length = min(48.0, max(24.0, abs(neighbor_gap) * 0.65))
					start, end = Point(x, y + load_length), Point(x, y + 5)
				else:
					raise ValueError("Unsupported stability load: {!r}".format(load))
				objects.append(
					Arrow(
						start,
						end,
						rod,
						head_length=settings.arrow_size,
						head_width=settings.arrow_size * 0.7,
						object_id="node/{}/load".format(index),
						metadata=metadata(kind="force", index=index, direction=load),
					)
				)
				label = text_transform(str(_value(node, "load_text", "")))
				if label:
					objects.append(
						Text(
							Point(x + 24, (start.y + end.y) / 2),
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
