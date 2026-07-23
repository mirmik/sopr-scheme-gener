"""Qt-independent layout for the shafts-and-pipes task."""

import math
from dataclasses import dataclass

from sopr_scheme_gener.scene import (
	BLACK,
	TRANSPARENT,
	WHITE,
	Arc,
	Ellipse,
	Fill,
	Group,
	Line,
	Point,
	Polygon,
	Polyline,
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
class ShaftsPipesLayoutSettings:
	has_central: bool = False
	external_camera: bool = True
	short_length: bool = False
	hollow: bool = True
	end_type: str = "труба"
	force_direction: str = "нет"
	eccentric_force: bool = True
	force_below: bool = False
	force_text: str = "P"
	torque_direction: str = "нет"
	torque_text: str = "M"
	torque_at_ends: bool = False
	bending_direction: str = "нет"
	bending_text: str = "M"
	bending_style: str = "круговой"
	pressure_text: str = "p"
	inner_pressure_text: str = ""
	thickness_text: str = "h"
	length_text: str = ""
	camera_width: float = 25.0
	tube_width: float = 10.0
	horizontal_border: float = 10.0
	vertical_border: float = 20.0
	note: str = ""
	font_size: float = 12.0
	line_width: float = 2.0


def _value(record, name, default=None):
	if isinstance(record, dict):
		return record.get(name, default)
	return getattr(record, name, default)


def _rotate(angle, point):
	return Point(
		point.x * math.cos(angle) - point.y * math.sin(angle),
		point.y * math.cos(angle) + point.x * math.sin(angle),
	)


def _translated(point, offset):
	return Point(point.x + offset.x, point.y + offset.y)


class _Bounds:
	def __init__(self):
		self.value = None

	def add(self, rect):
		self.value = rect if self.value is None else self.value.union(rect)

	def geometry(self, points, stroke_width=0.0):
		rect = Rect.around(points)
		half = stroke_width / 2
		self.add(
			Rect(
				rect.x - half,
				rect.y - half,
				rect.width + stroke_width,
				rect.height + stroke_width,
			)
		)

	def arrow(self, start, end):
		self.add(
			Rect(
				min(start.x, end.x) - 5,
				min(start.y, end.y) - 5,
				abs(end.x - start.x) + 10,
				abs(end.y - start.y) + 10,
			)
		)

	def legacy_text(self, center, measurement, offset="none", rotation=0.0):
		if offset == "left":
			left = center.x - measurement.width
		elif offset == "right":
			left = center.x
		else:
			left = center.x - measurement.width / 2
		top = center.y - measurement.height / 2
		width = measurement.width + 5
		height = measurement.height
		if rotation:
			cx, cy = left + width / 2, top + height / 2
			corners = (
				Point(left, top),
				Point(left + width, top),
				Point(left, top + height),
				Point(left + width, top + height),
			)
			rotated = []
			for point in corners:
				delta = _rotate(rotation, Point(point.x - cx, point.y - cy))
				rotated.append(Point(cx + delta.x, cy + delta.y))
			self.add(Rect.around(rotated))
		else:
			self.add(Rect(left, top, width, height))


class ShaftsPipesLayoutBuilder:
	def build(self, task, settings, text_metrics, text_transform=None):
		text_transform = text_transform or (lambda value: value)
		sections = tuple(task["sections"])
		expected = 2 if settings.has_central else 1
		if len(sections) != expected:
			raise ValueError(
				"shafts-pipes requires {} section record(s)".format(expected)
			)

		main = Stroke(width=settings.line_width)
		half = Stroke(width=max(1, int(settings.line_width / 2)))
		axis = Stroke(
			width=max(1, int(settings.line_width / 2)),
			line_style="dash-dot",
		)
		style = TextStyle(
			point_size=settings.font_size,
			italic=True,
		)
		objects = []
		bounds = _Bounds()

		def add_line(start, end, stroke=main, object_id=None):
			objects.append(Line(start, end, stroke, object_id=object_id))
			bounds.geometry((start, end), stroke.width)

		def add_rect(x, y, width, height, stroke=main, fill=Fill(), object_id=None):
			left, right = sorted((x, x + width))
			top, bottom = sorted((y, y + height))
			rect = Rect(left, top, right - left, bottom - top)
			objects.append(
				Rectangle(rect, stroke=stroke, fill=fill, object_id=object_id)
			)
			bounds.geometry(
				(Point(rect.left, rect.top), Point(rect.right, rect.bottom)),
				0 if stroke is None else stroke.width,
			)

		def add_polygon(points, stroke=main, fill=Fill(), object_id=None):
			points = tuple(points)
			objects.append(
				Polygon(points, stroke=stroke, fill=fill, object_id=object_id)
			)
			bounds.geometry(points, 0 if stroke is None else stroke.width)

		def add_ellipse(rect, stroke=main, fill=Fill(), object_id=None):
			objects.append(
				Ellipse(rect, stroke=stroke, fill=fill, object_id=object_id)
			)
			bounds.geometry(
				(Point(rect.left, rect.top), Point(rect.right, rect.bottom)),
				0 if stroke is None else stroke.width,
			)

		def add_text(
			value,
			center,
			offset="none",
			rotation=0.0,
			clean=False,
			object_id=None,
		):
			value = text_transform(value)
			measurement = text_metrics.measure(value, style)
			objects.append(
				Text(
					center,
					value,
					style,
					TextAnchor.CENTER,
					rotation_degrees=math.degrees(rotation),
					object_id=object_id,
					metadata=metadata(
						kind="legacy-text",
						offset=offset,
						clean=clean,
					),
				)
			)
			bounds.legacy_text(center, measurement, offset, rotation)

		def add_arrow(
			start,
			end,
			size=(10, 3),
			stroke=main,
			reverse=False,
			double=False,
			object_id=None,
		):
			if reverse:
				start, end = end, start
			dx, dy = end.x - start.x, end.y - start.y
			length = math.hypot(dx, dy)
			ux, uy = dx / length, dy / length
			normal = Point(uy, -ux)
			at_end = Point(end.x - ux * size[0], end.y - uy * size[0])
			children = [
				Line(start, end, stroke),
				Polygon(
					(
						end,
						Point(
							at_end.x + normal.x * size[1],
							at_end.y + normal.y * size[1],
						),
						Point(
							at_end.x - normal.x * size[1],
							at_end.y - normal.y * size[1],
						),
					),
					stroke,
					Fill(BLACK),
				),
			]
			if double:
				at_start = Point(
					start.x + ux * size[0],
					start.y + uy * size[0],
				)
				children.append(
					Polygon(
						(
							start,
							Point(
								at_start.x + normal.x * size[1],
								at_start.y + normal.y * size[1],
							),
							Point(
								at_start.x - normal.x * size[1],
								at_start.y - normal.y * size[1],
							),
						),
						stroke,
						Fill(BLACK),
					)
				)
			objects.append(
				Group(
					children,
					object_id=object_id,
					metadata=metadata(kind="legacy-arrow", double=double),
				)
			)
			bounds.arrow(start, end)

		def draw_tube(
			wmin,
			wmax,
			radius,
			hollow=False,
			text="",
			camera=False,
			notext=False,
			nobody=False,
			text_position=None,
			prefix="tube",
		):
			thickness = settings.tube_width
			if text_position is None:
				text_position = (wmax + wmin) / 2
			if not nobody:
				if not hollow:
					add_rect(
						wmin,
						-radius,
						wmax - wmin,
						2 * radius,
						object_id=prefix + "/body",
					)
				elif camera:
					add_rect(
						wmin,
						-radius,
						wmax - wmin,
						2 * radius,
						fill=Fill(BLACK, "backward-diagonal"),
						object_id=prefix + "/outer",
					)
					add_rect(
						wmin + thickness,
						-radius + thickness,
						wmax - wmin - 2 * thickness,
						2 * radius - 2 * thickness,
						fill=Fill(WHITE),
						object_id=prefix + "/inner",
					)
				else:
					add_rect(
						wmin,
						-radius,
						wmax - wmin,
						thickness,
						fill=Fill(BLACK, "backward-diagonal"),
						object_id=prefix + "/upper-wall",
					)
					add_rect(
						wmin,
						-radius + thickness,
						wmax - wmin,
						2 * radius - 2 * thickness,
						object_id=prefix + "/hollow",
					)
					add_rect(
						wmin,
						radius,
						wmax - wmin,
						-thickness,
						object_id=prefix + "/lower-wall",
					)
				if hollow:
					add_line(
						Point(wmin, -radius + thickness / 2),
						Point(wmax, -radius + thickness / 2),
						axis,
					)
					add_line(
						Point(wmin, radius - thickness / 2),
						Point(wmax, radius - thickness / 2),
						axis,
					)
					if text:
						add_arrow(
							Point(text_position, radius - thickness / 2),
							Point(text_position, -radius + thickness / 2),
							double=True,
						)
				elif text:
					add_arrow(
						Point(text_position, radius),
						Point(text_position, -radius),
						double=True,
					)
			if not notext and text:
				add_text(
					text,
					Point(text_position - 15, 0),
					rotation=math.pi / 2,
					clean=True,
					object_id=prefix + "/diameter-label",
				)

		def draw_camera(wmax, wmin, hmax, hmin, hint):
			backward = Fill(BLACK, "backward-diagonal")
			for sign in (1, -1):
				add_polygon(
					(
						Point(wmax, sign * hmax),
						Point(-wmax, sign * hmax),
						Point(-wmax, sign * hint),
						Point(-wmin, sign * hint),
						Point(-wmin, sign * hmin),
						Point(wmin, sign * hmin),
						Point(wmin, sign * hint),
						Point(wmax, sign * hint),
					),
					fill=backward,
					object_id="camera/{}".format("lower" if sign > 0 else "upper"),
				)
			width = wmax - wmin
			for xsign, ysign, name in (
				(-1, -1, "upper-left"),
				(1, -1, "upper-right"),
				(1, 1, "lower-right"),
				(-1, 1, "lower-left"),
			):
				add_polygon(
					(
						Point(xsign * (wmin + width / 4), ysign * hint),
						Point(
							xsign * (wmin + width / 3),
							ysign * (hint + 15),
						),
						Point(
							xsign * (wmax - width / 3),
							ysign * (hint + 15),
						),
						Point(xsign * (wmax - width / 4), ysign * hint),
					),
					fill=Fill(BLACK, "forward-diagonal"),
					object_id="camera/" + name,
				)

		width = 500.0
		w1, w4 = -width * 0.45, width * 0.45
		if settings.short_length:
			w2, w3 = -width * 0.1, width * 0.1
		else:
			w2, w3 = -width * 0.2, width * 0.2
		w2_camera, w3_camera = -width * 0.2, width * 0.2
		radii = tuple(float(_value(section, "D")) for section in sections)
		ymax, ymin = max(radii), min(radii)
		radius = radii[0]

		add_text(
			settings.pressure_text,
			Point(-(w3 + 3 * w2) / 4 + 15, -ymax - 18),
			object_id="pressure/external",
		)

		if settings.torque_direction != "нет":
			position = (3 * w1 + w2) / 4
			if settings.torque_at_ends:
				position = w1
			min_radius, max_radius = radius, radius + 30
			for x in (position, -position):
				add_line(Point(x, min_radius), Point(x, max_radius))
				add_line(Point(x, -min_radius), Point(x, -max_radius))
			invert = settings.torque_direction == "-"
			for point, crossed in (
				(Point(position, -max_radius), invert),
				(Point(-position, -max_radius), not invert),
				(Point(position, max_radius), not invert),
				(Point(-position, max_radius), invert),
			):
				add_ellipse(
					Rect(point.x - 10, point.y - 10, 20, 20),
					fill=Fill(WHITE),
				)
				if crossed:
					delta = 10 / math.sqrt(2)
					add_line(
						Point(point.x - delta, point.y - delta),
						Point(point.x + delta, point.y + delta),
					)
					add_line(
						Point(point.x + delta, point.y - delta),
						Point(point.x - delta, point.y + delta),
					)
				else:
					add_ellipse(
						Rect(point.x - 2.5, point.y - 2.5, 5, 5),
						fill=Fill(BLACK),
					)
			add_text(
				settings.torque_text,
				Point(position - 15, -max_radius),
				offset="left",
				object_id="torque/left-label",
			)
			add_text(
				settings.torque_text,
				Point(-position + 15, -max_radius),
				offset="right",
				object_id="torque/right-label",
			)

		if settings.bending_direction != "нет":
			if settings.bending_style == "круговой":
				for center, angle, inverse, name in (
					(Point(w1, 0), math.pi, settings.bending_direction == "-", "left"),
					(Point(w4, 0), 0, settings.bending_direction == "+", "right"),
				):
					moment_bounds = Rect(center.x - 50, center.y - 50, 100, 100)
					bounds.add(moment_bounds)
					objects.append(
						Group(
							self._circular_moment(center, angle, inverse, main),
							object_id="bending/" + name,
							metadata=metadata(kind="moment"),
						)
					)
				add_text(
					settings.bending_text,
					Point(w1 - 56, 0),
					offset="left",
				)
				add_text(
					settings.bending_text,
					Point(w4 + 56, 0),
					offset="right",
				)
			else:
				x, y = 35.0, radius + 15
				for center, inverse, name in (
					(Point(w1, 0), settings.bending_direction == "-", "left"),
					(Point(w4, 0), settings.bending_direction == "+", "right"),
				):
					bounds.add(Rect(center.x - x, center.y - y, 2 * x, 2 * y))
					objects.append(
						Group(
							self._square_moment(center, x, y, inverse, main),
							object_id="bending/" + name,
							metadata=metadata(kind="moment"),
						)
					)
				label_y = y - 15
				inverse = settings.bending_direction == "+"
				add_text(
					settings.bending_text,
					Point(w1 - 20, label_y if inverse else -label_y),
					offset="left",
				)
				add_text(
					settings.bending_text,
					Point(w4 + 20, label_y if inverse else -label_y),
					offset="right",
				)

		if settings.force_direction != "нет":
			force_radius = radius if settings.eccentric_force else 0
			if (
				force_radius == radius
				and settings.hollow
				and len(sections) == 1
			):
				force_radius = radius - settings.tube_width / 2
			if settings.force_below:
				force_radius = -force_radius
			reverse = settings.force_direction == "-"
			left_start, left_end = Point(w1 - 5, -force_radius), Point(
				w1 - 50, -force_radius
			)
			right_start, right_end = Point(w4 + 5, -force_radius), Point(
				w4 + 50, -force_radius
			)
			add_arrow(
				right_start,
				right_end,
				size=(15, 5),
				reverse=reverse,
				object_id="force/right",
			)
			add_arrow(
				left_start,
				left_end,
				size=(15, 5),
				reverse=reverse,
				object_id="force/left",
			)
			for start, end, name in (
				(left_start, left_end, "left"),
				(right_start, right_end, "right"),
			):
				add_text(
					settings.force_text,
					Point((start.x + end.x) / 2, -force_radius - 13),
					object_id="force/{}/label".format(name),
				)

		text_position = (
			(w3 * 3 + w4) / 4
			if settings.short_length
			else (w3 * 2 + w4 * 2) / 4
		)
		if settings.has_central:
			draw_tube(
				w1,
				w2,
				radii[0],
				text=_value(sections[0], "Dtext", ""),
				notext=True,
				text_position=-text_position,
				prefix="section/left",
			)
			draw_tube(
				w2,
				w3,
				radii[1],
				hollow=settings.hollow,
				text=_value(sections[1], "Dtext", ""),
				notext=True,
				prefix="section/central",
			)
			draw_tube(
				w3,
				w4,
				radii[0],
				text=_value(sections[0], "Dtext", ""),
				notext=True,
				text_position=text_position,
				prefix="section/right",
			)
		else:
			draw_tube(
				w1,
				w4,
				radii[0],
				hollow=settings.hollow,
				text=_value(sections[0], "Dtext", ""),
				camera=settings.end_type == "камера",
				notext=True,
				prefix="section/main",
			)

		add_line(Point(w1 - 20, 0), Point(w4 + 20, 0), axis, "axis")
		add_text(
			settings.inner_pressure_text,
			Point(-(w3 + 3 * w2) / 4 + 15, -ymin + 25),
			clean=True,
			object_id="pressure/internal",
		)

		if settings.has_central:
			draw_tube(
				w1,
				w2,
				radii[0],
				text=_value(sections[0], "Dtext", ""),
				nobody=True,
				text_position=-text_position,
				prefix="section/left",
			)
			draw_tube(
				w2,
				w3,
				radii[1],
				hollow=settings.hollow,
				text=_value(sections[1], "Dtext", ""),
				nobody=True,
				prefix="section/central",
			)
			draw_tube(
				w3,
				w4,
				radii[0],
				text=_value(sections[0], "Dtext", ""),
				nobody=True,
				text_position=text_position,
				prefix="section/right",
			)
		else:
			draw_tube(
				w1,
				w4,
				radii[0],
				hollow=settings.hollow,
				text=_value(sections[0], "Dtext", ""),
				camera=settings.end_type == "камера",
				nobody=True,
				prefix="section/main",
			)

		if settings.external_camera:
			draw_camera(
				w3_camera + 20 + settings.camera_width,
				w3_camera + 20,
				ymax + 30 + settings.camera_width,
				ymax + 30,
				radii[0],
			)

		if settings.hollow:
			index = 1 if len(sections) == 2 else 0
			height = radii[index]
			add_text(
				settings.thickness_text,
				Point(45, height + 15),
				offset="right",
				object_id="dimension/thickness/label",
			)
			add_arrow(
				Point(40, height + 15),
				Point(40, height),
				object_id="dimension/thickness/outer",
			)
			add_arrow(
				Point(40, height - settings.tube_width - 15),
				Point(40, height - settings.tube_width),
				object_id="dimension/thickness/inner",
			)
			add_line(
				Point(40, height + 15),
				Point(40, height - settings.tube_width - 15),
				half,
			)

		if settings.end_type == "разрез":
			left = (
				Point(w1 + 5, radius),
				Point(w1, radius / 2),
				Point(w1 + 10, -radius / 2),
				Point(w1 + 5, -radius),
			)
			add_polygon(
				left
				+ (
					Point(w1 - 20, -radius - 10),
					Point(w1 - 20, radius + 10),
				),
				stroke=Stroke(WHITE, main.width),
				fill=Fill(WHITE),
			)
			for start, end in zip(left, left[1:]):
				add_line(start, end, Stroke())
			right = (
				Point(w4 - 5, radius),
				Point(w4 - 10, radius / 2),
				Point(w4, -radius / 2),
				Point(w4 - 5, -radius),
			)
			add_polygon(
				right
				+ (
					Point(w4 + 20, -radius - 10),
					Point(w4 + 20, radius + 10),
				),
				stroke=Stroke(WHITE, main.width),
				fill=Fill(WHITE),
			)
			for start, end in zip(right, right[1:]):
				add_line(start, end, Stroke())

		if settings.length_text:
			if settings.external_camera:
				left, right = w2, w3
				dimension_y = ymax + 30 + settings.camera_width + 30
				for x in (left, right):
					add_line(Point(x, 0), Point(x, dimension_y + 3), Stroke())
			else:
				correction = settings.tube_width if settings.end_type == "камера" else 0
				left, right = w1 + correction, w4 - correction
				dimension_y = ymax + 60
				for x in (left, right):
					add_line(Point(x, 0), Point(x, ymax + 63), Stroke())
			add_arrow(
				Point(left, dimension_y),
				Point(right, dimension_y),
				stroke=half,
				double=True,
				object_id="dimension/length",
			)
			add_text(
				settings.length_text,
				Point(0, ymax + 30 + settings.camera_width + 20),
				object_id="dimension/length/label",
			)

		content_bounds = bounds.value
		note_lines = tuple(text_transform(settings.note).splitlines())
		for index, line in enumerate(note_lines):
			objects.append(
				Text(
					Point(
						content_bounds.x,
						content_bounds.bottom
						+ text_metrics.measure(line, style).height * index,
					),
					line,
					style,
					TextAnchor.TOP_LEFT,
					object_id="note/{}".format(index),
					metadata=metadata(kind="qgraphics-text"),
				)
			)

		horizontal_border = settings.horizontal_border
		if settings.force_direction != "нет":
			horizontal_border += 25
		border = Rect(
			-content_bounds.width / 2 - horizontal_border,
			-content_bounds.height / 2 - settings.vertical_border,
			content_bounds.width + horizontal_border * 2,
			content_bounds.height + settings.vertical_border,
		)
		objects.append(
			Rectangle(
				border,
				stroke=Stroke(TRANSPARENT),
				fill=Fill(TRANSPARENT),
				object_id="viewport-border",
			)
		)
		viewport = Rect(
			border.x - 0.5,
			border.y - 0.5,
			border.width + 1,
			border.height + 1,
		)
		if note_lines:
			note_height = text_metrics.measure(note_lines[0], style).height + 8
			note_bottom = (
				content_bounds.bottom
				+ text_metrics.measure(note_lines[-1], style).height
				* (len(note_lines) - 1)
				+ note_height
			)
			if note_bottom > viewport.bottom:
				viewport = Rect(
					viewport.x,
					viewport.y,
					viewport.width,
					note_bottom - viewport.y,
				)
		return Scene(viewport, tuple(objects), content_bounds=content_bounds)

	@staticmethod
	def _circular_moment(center, angle, inverse, stroke):
		radius, arc_angle = 50.0, math.pi / 2
		first = _rotate(angle + arc_angle / 2, Point(radius, 0))
		second = _rotate(angle - arc_angle / 2, Point(radius, 0))
		arrow_angle = math.pi / 2 if not inverse else -math.pi / 2
		side = -arc_angle / 2 if not inverse else arc_angle / 2
		polygon_angle = angle + arrow_angle + side * 3 / 4
		point, other = (first, second) if not inverse else (second, first)
		tip = _translated(center, other)
		return (
			Line(center, _translated(center, point), stroke),
			Arc(
				Rect(center.x - radius, center.y - radius, radius * 2, radius * 2),
				math.degrees(angle - arc_angle / 2),
				math.degrees(arc_angle),
				stroke,
			),
			Polygon(
				(
					tip,
					_translated(
						tip,
						_rotate(polygon_angle, Point(15, 5)),
					),
					_translated(
						tip,
						_rotate(polygon_angle, Point(15, -5)),
					),
				),
				stroke,
				Fill(BLACK),
			),
		)

	@staticmethod
	def _square_moment(center, x, y, inverse, stroke):
		children = [Line(Point(center.x, center.y + y), Point(center.x, center.y - y))]
		if inverse:
			ends = (
				(Point(center.x, center.y - y), Point(center.x - x, center.y - y), 1),
				(Point(center.x, center.y + y), Point(center.x + x, center.y + y), -1),
			)
		else:
			ends = (
				(Point(center.x, center.y - y), Point(center.x + x, center.y - y), -1),
				(Point(center.x, center.y + y), Point(center.x - x, center.y + y), 1),
			)
		for start, tip, direction in ends:
			children.append(Line(start, tip, stroke))
			children.append(
				Polygon(
					(
						tip,
						Point(tip.x + direction * 15, tip.y + 5),
						Point(tip.x + direction * 15, tip.y - 5),
					),
					stroke,
					Fill(BLACK),
				)
			)
		return tuple(children)
