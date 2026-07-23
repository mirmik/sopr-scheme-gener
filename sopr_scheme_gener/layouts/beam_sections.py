"""Qt-independent cross-section layouts used by the beams task."""

from dataclasses import dataclass, replace
import math

from sopr_scheme_gener.scene import (
	BLACK,
	WHITE,
	Ellipse,
	Fill,
	Group,
	Line,
	Point,
	Polygon,
	Rect,
	Rectangle,
	Stroke,
	Text,
	TextAnchor,
	metadata,
)


GENERAL_SECTION = "Сечение общего типа"
H_SECTION = "H - профиль"
RECT_MINUS_RECT_SECTION = "Прямоугольник с прямоугольным отверстием"
SUPPORTED_SECTION_TYPES = (
	"Нет",
	GENERAL_SECTION,
	H_SECTION,
	RECT_MINUS_RECT_SECTION,
	"Тонкая труба",
	"Треугольник",
)


@dataclass(frozen=True)
class BeamSectionSpec:
	section_type: str = "Нет"
	arg0: float = 0
	arg1: float = 0
	arg2: float = 0
	arg3: float = 0
	text0: str = ""
	text1: str = ""
	text2: str = ""
	text3: str = ""
	outer_type: str = ""
	inner_type: str = ""
	offset_enabled: bool = False
	offset_value: float = 0
	offset_text: str = ""
	edge: str = "Нет"
	rotated: bool = False


def beam_section_width(spec):
	if spec.section_type == "Нет":
		return 0
	if spec.section_type == "Тонкая труба":
		return spec.arg0 + 120
	if spec.section_type == "Треугольник":
		return spec.arg1 + 120
	if spec.section_type == GENERAL_SECTION:
		return spec.arg0 + 120
	if spec.section_type == RECT_MINUS_RECT_SECTION:
		return spec.arg0 + 120
	if spec.section_type == H_SECTION:
		return spec.arg0 + 120
	raise ValueError("Unsupported beam section: {!r}".format(spec.section_type))


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


def _dimension(
	apnt,
	bpnt,
	offset,
	textoff,
	text,
	arrow_size,
	stroke,
	style,
	text_metrics,
	splashed=False,
	textline_from=None,
):
	aoff = apnt.translated(offset)
	boff = bpnt.translated(offset)
	coff = Point((aoff.x + boff.x) / 2, (aoff.y + boff.y) / 2)
	diff = Point(boff.x - aoff.x, boff.y - aoff.y)
	angle = math.atan2(-diff.y, diff.x)
	aangle = angle if splashed else angle + math.pi
	bangle = angle + math.pi if splashed else angle
	measurement = text_metrics.measure(text, style)
	text_center = Point(
		coff.x + textoff.x,
		coff.y + textoff.y + measurement.height / 4,
	)
	children = [
		_arrow_head(aoff, aangle, stroke, arrow_size),
		_arrow_head(boff, bangle, stroke, arrow_size),
		Line(aoff, boff, stroke=stroke),
		Line(aoff, boff, stroke=stroke),
		Line(apnt, aoff, stroke=stroke),
		Line(bpnt, boff, stroke=stroke),
		Text(
			text_center,
			text,
			style=style,
			anchor=TextAnchor.BASELINE_CENTER,
		),
	]
	if textline_from is not None:
		text_left = Point(
			text_center.x - measurement.width / 2,
			text_center.y + measurement.height / 8,
		)
		text_right = Point(
			text_center.x + measurement.width / 2,
			text_center.y + measurement.height / 8,
		)
		children.append(Line(text_left, text_right, stroke=stroke))
		children.append(
			Line(
				bpnt if textline_from == "bpnt" else apnt,
				text_left,
				stroke=stroke,
			)
		)
	return Group(children)


def _section_group(children, section_type):
	normalized = []
	dimension_index = 0
	for child in children:
		if isinstance(child, Group) and child.object_id is None:
			dimension_id = "section/dimension/{}".format(dimension_index)
			dimension_children = tuple(
				replace(
					item,
					object_id="{}/text".format(dimension_id),
				)
				if isinstance(item, Text) and item.object_id is None
				else item
				for item in child.children
			)
			child = replace(
				child,
				children=dimension_children,
				object_id=dimension_id,
				metadata=metadata(
					kind="section-dimension",
					index=dimension_index,
				),
			)
			dimension_index += 1
		normalized.append(child)
	return Group(
		normalized,
		object_id="section/cross-section",
		metadata=metadata(kind="cross-section", section_type=section_type),
	)


def build_beam_section(
	spec,
	right,
	hcenter,
	arrow_size,
	main,
	half,
	axis,
	text_style,
	text_metrics,
	text_transform,
):
	if spec.section_type == "Нет":
		return ()
	if spec.section_type not in SUPPORTED_SECTION_TYPES:
		raise ValueError("Unsupported beam section: {!r}".format(spec.section_type))

	text0 = text_transform(spec.text0)
	text1 = text_transform(spec.text1)
	text2 = text_transform(spec.text2)
	if spec.section_type == GENERAL_SECTION:
		return _build_general_section(
			spec,
			right,
			hcenter,
			arrow_size,
			main,
			half,
			axis,
			text_style,
			text_metrics,
			text0,
			text1,
			text2,
		)
	if spec.section_type == RECT_MINUS_RECT_SECTION:
		return _build_rect_minus_rect_section(
			spec,
			right,
			hcenter,
			arrow_size,
			main,
			half,
			axis,
			text_style,
			text_metrics,
			text0,
			text1,
			text2,
			text_transform(spec.text3),
			text_transform(spec.offset_text),
		)
	if spec.section_type == H_SECTION:
		return _build_h_section(
			spec,
			right,
			hcenter,
			arrow_size,
			main,
			half,
			axis,
			text_style,
			text_metrics,
			text0,
			text1,
			text2,
			text_transform(spec.text3),
		)
	center = Point(right - 30 - spec.arg0 / 2, hcenter)
	dimension_arrow = arrow_size / 3 * 2

	if spec.section_type == "Тонкая труба":
		outer = spec.arg0
		inner = spec.arg1
		middle = (inner + outer) / 2
		text0_width = text_metrics.measure(text0, text_style).width
		children = [
			Ellipse(
				Rect(
					center.x - outer,
					center.y - outer,
					outer * 2,
					outer * 2,
				),
				stroke=main,
				fill=Fill(BLACK, pattern="backward-diagonal"),
			),
			Ellipse(
				Rect(
					center.x - inner,
					center.y - inner,
					inner * 2,
					inner * 2,
				),
				stroke=main,
				fill=Fill(WHITE),
			),
			Ellipse(
				Rect(
					center.x - middle,
					center.y - middle,
					middle * 2,
					middle * 2,
				),
				stroke=axis,
				fill=Fill(),
			),
			_dimension(
				Point(center.x, center.y - middle),
				Point(center.x, center.y + middle),
				Point(-outer - 20, 0),
				Point(-10 - text0_width / 2, 0),
				text0,
				dimension_arrow,
				half,
				text_style,
				text_metrics,
			),
		]
		diagonal = math.cos(math.pi / 4)
		children.append(
			_dimension(
				Point(center.x + diagonal * inner, center.y + diagonal * inner),
				Point(center.x + diagonal * outer, center.y + diagonal * outer),
				Point(0, 0),
				Point(
					diagonal * (outer - inner) + 15,
					diagonal * (outer - inner),
				),
				text1,
				dimension_arrow,
				half,
				text_style,
				text_metrics,
				splashed=True,
				textline_from="bpnt",
			)
		)
		axis_length = outer + 10
		children.extend(
			(
				Line(
					Point(center.x - axis_length, center.y),
					Point(center.x + axis_length, center.y),
					stroke=axis,
				),
				Line(
					Point(center.x, center.y - axis_length),
					Point(center.x, center.y + axis_length),
					stroke=axis,
				),
			)
		)
	else:
		height = spec.arg0
		half_width = spec.arg1
		children = [
			Polygon(
				(
					Point(center.x - half_width, center.y + height),
					Point(center.x + half_width, center.y + height),
					Point(center.x, center.y - height),
				),
				stroke=main,
				fill=Fill(BLACK, pattern="backward-diagonal"),
			),
			_dimension(
				Point(center.x, center.y + height),
				Point(center.x, center.y - height),
				Point(-20 - height, 0),
				Point(-10, 0),
				text0,
				dimension_arrow,
				half,
				text_style,
				text_metrics,
			),
			_dimension(
				Point(center.x + half_width, center.y + height),
				Point(center.x - half_width, center.y + height),
				Point(0, 25),
				Point(0, -6),
				text1,
				dimension_arrow,
				half,
				text_style,
				text_metrics,
			),
		]
		axis_length = height + 10
		children.extend(
			(
				Line(
					Point(center.x - axis_length, center.y + height / 3),
					Point(center.x + axis_length, center.y + height / 3),
					stroke=axis,
				),
				Line(
					Point(center.x, center.y - axis_length),
					Point(center.x, center.y + axis_length),
					stroke=axis,
				),
			)
		)

	return (_section_group(children, spec.section_type),)


def _build_general_section(
	spec,
	right,
	hcenter,
	arrow_size,
	main,
	half,
	axis,
	text_style,
	text_metrics,
	width_text,
	height_text,
	inner_text,
):
	width = spec.arg0
	height = spec.arg1
	inner_width = spec.arg2
	center = Point(right - 30 - width, hcenter)
	dimension_arrow = arrow_size / 3 * 2
	children = []
	axis_width = width
	axis_height = width

	if spec.outer_type == "Прямоугольник":
		children.append(
			Rectangle(
				Rect(
					center.x - width,
					center.y - height,
					width * 2,
					height * 2,
				),
				stroke=main,
				fill=Fill(BLACK, pattern="backward-diagonal"),
			)
		)
		children.extend(
			(
				_dimension(
					Point(center.x - width, center.y + height),
					Point(center.x - width, center.y - height),
					Point(-18, 0),
					Point(-10, 0),
					height_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
				),
				_dimension(
					Point(center.x + width, center.y + height),
					Point(center.x - width, center.y + height),
					Point(0, 30),
					Point(0, -11),
					width_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
				),
			)
		)
		axis_height = height
	elif spec.outer_type == "Квадрат":
		children.append(
			Rectangle(
				Rect(
					center.x - width,
					center.y - width,
					width * 2,
					width * 2,
				),
				stroke=main,
				fill=Fill(BLACK, pattern="backward-diagonal"),
			)
		)
		children.append(
			_dimension(
				Point(center.x + width, center.y + width),
				Point(center.x - width, center.y + width),
				Point(0, 30),
				Point(0, -11),
				width_text,
				dimension_arrow,
				half,
				text_style,
				text_metrics,
			)
		)
	elif spec.outer_type == "Квадрат повёрнутый 45 град":
		children.append(
			Polygon(
				(
					Point(center.x - width, center.y),
					Point(center.x, center.y + width),
					Point(center.x + width, center.y),
					Point(center.x, center.y - width),
				),
				stroke=main,
				fill=Fill(BLACK, pattern="backward-diagonal"),
			)
		)
		children.extend(
			(
				_dimension(
					Point(center.x, center.y - width),
					Point(center.x - width, center.y),
					Point(-15, -15),
					Point(-10, -10),
					width_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
				),
				_dimension(
					Point(center.x, center.y + width),
					Point(center.x - width, center.y),
					Point(-15, 15),
					Point(-10, 10),
					width_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
				),
			)
		)
	elif spec.outer_type == "Круг":
		children.append(
			Ellipse(
				Rect(
					center.x - width,
					center.y - width,
					width * 2,
					width * 2,
				),
				stroke=main,
				fill=Fill(BLACK, pattern="backward-diagonal"),
			)
		)
		children.append(
			_dimension(
				Point(center.x + width, center.y),
				Point(center.x - width, center.y),
				Point(0, 23 + width),
				Point(0, -7),
				width_text,
				dimension_arrow,
				half,
				text_style,
				text_metrics,
			)
		)
	else:
		raise ValueError("Unsupported outer section: {!r}".format(spec.outer_type))

	if spec.inner_type == "Квадрат":
		children.append(
			Rectangle(
				Rect(
					center.x - inner_width,
					center.y - inner_width,
					inner_width * 2,
					inner_width * 2,
				),
				stroke=main,
				fill=Fill(WHITE),
			)
		)
		children.append(
			_dimension(
				Point(center.x + inner_width, center.y + inner_width),
				Point(center.x + inner_width, center.y - inner_width),
				Point(width - inner_width + 15, 0),
				Point(8, 0),
				inner_text,
				dimension_arrow,
				half,
				text_style,
				text_metrics,
			)
		)
	elif spec.inner_type == "Квадрат повёрнутый 45 град":
		children.append(
			Polygon(
				(
					Point(center.x - inner_width, center.y),
					Point(center.x, center.y + inner_width),
					Point(center.x + inner_width, center.y),
					Point(center.x, center.y - inner_width),
				),
				stroke=main,
				fill=Fill(WHITE),
			)
		)
		if spec.outer_type == "Квадрат повёрнутый 45 град":
			delta = (width - inner_width) / 2
			upper_offset = Point(delta + 15, delta + 15)
			lower_offset = Point(delta + 15, -delta - 15)
		else:
			upper_offset = Point(10, 10)
			lower_offset = Point(10, -10)
		children.extend(
			(
				_dimension(
					Point(center.x, center.y + inner_width),
					Point(center.x + inner_width, center.y),
					upper_offset,
					Point(10, 10),
					inner_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
				),
				_dimension(
					Point(center.x, center.y - inner_width),
					Point(center.x + inner_width, center.y),
					lower_offset,
					Point(10, -10),
					inner_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
				),
			)
		)
	elif spec.inner_type == "Круг":
		children.append(
			Ellipse(
				Rect(
					center.x - inner_width,
					center.y - inner_width,
					inner_width * 2,
					inner_width * 2,
				),
				stroke=main,
				fill=Fill(WHITE),
			)
		)
		diagonal = math.cos(math.pi / 4) * inner_width
		children.append(
			_dimension(
				Point(center.x + diagonal, center.y + diagonal),
				Point(center.x - diagonal, center.y - diagonal),
				Point(0, 0),
				Point(8, -8),
				inner_text,
				dimension_arrow,
				half,
				text_style,
				text_metrics,
			)
		)
	elif spec.inner_type != "Нет":
		raise ValueError("Unsupported inner section: {!r}".format(spec.inner_type))

	axis_width += 10
	axis_height += 10
	children.extend(
		(
			Line(
				Point(center.x + axis_width, center.y),
				Point(center.x - axis_width, center.y),
				stroke=axis,
			),
			Line(
				Point(center.x, center.y - axis_height),
				Point(center.x, center.y + axis_height),
				stroke=axis,
			),
		)
	)
	return (_section_group(children, spec.section_type),)


def _build_rect_minus_rect_section(
	spec,
	right,
	hcenter,
	arrow_size,
	main,
	half,
	axis,
	text_style,
	text_metrics,
	width_text,
	height_text,
	hole_width_text,
	hole_height_text,
	offset_text,
):
	width = spec.arg0
	height = spec.arg1
	hole_width = spec.arg2
	hole_height = spec.arg3
	offset_value = spec.offset_value
	edge = spec.edge
	edge_aligned = edge != "Нет"
	if edge == "Верх":
		offset_value = height - hole_height
	elif edge == "Низ":
		offset_value = 0
	elif spec.offset_enabled:
		offset_value = (height - hole_height) / 2

	center = Point(right - 30 - width, hcenter)
	dimension_arrow = arrow_size / 3 * 2
	hole_bottom = center.y + height - offset_value * 2
	hole_top = hole_bottom - hole_height * 2
	children = [
		Rectangle(
			Rect(
				center.x - width,
				center.y - height,
				width * 2,
				height * 2,
			),
			stroke=main,
			fill=Fill(BLACK, pattern="backward-diagonal"),
		)
	]

	if edge_aligned:
		children.append(
			Rectangle(
				Rect(
					center.x - hole_width,
					hole_top - (3 if edge == "Верх" else 0),
					hole_width * 2,
					hole_height * 2 + 3,
				),
				stroke=Stroke(WHITE),
				fill=Fill(WHITE),
			)
		)
		if edge == "Верх":
			children.extend(
				(
					Line(
						Point(center.x - hole_width, hole_top),
						Point(center.x - hole_width, hole_bottom),
						stroke=main,
					),
					Line(
						Point(center.x + hole_width, hole_bottom),
						Point(center.x - hole_width, hole_bottom),
						stroke=main,
					),
					Line(
						Point(center.x + hole_width, hole_top),
						Point(center.x + hole_width, hole_bottom),
						stroke=main,
					),
				)
			)
		else:
			children.extend(
				(
					Line(
						Point(center.x - hole_width, hole_top),
						Point(center.x - hole_width, hole_bottom),
						stroke=main,
					),
					Line(
						Point(center.x + hole_width, hole_top),
						Point(center.x - hole_width, hole_top),
						stroke=main,
					),
					Line(
						Point(center.x + hole_width, hole_top),
						Point(center.x + hole_width, hole_bottom),
						stroke=main,
					),
				)
			)
	else:
		children.append(
			Rectangle(
				Rect(
					center.x - hole_width,
					hole_top,
					hole_width * 2,
					hole_height * 2,
				),
				stroke=main,
				fill=Fill(WHITE),
			)
		)

	children.append(
		_dimension(
			Point(center.x - width, center.y + height),
			Point(center.x - width, center.y - height),
			Point(-18, 0),
			Point(-10, 0),
			height_text,
			dimension_arrow,
			half,
			text_style,
			text_metrics,
		)
	)
	if edge == "Низ":
		outer_width_y = hole_top
		outer_width_offset = Point(
			0,
			-height * 2
			+ hole_height * 2
			+ offset_value * 2
			- 16,
		)
	else:
		outer_width_y = center.y + height
		outer_width_offset = Point(0, 23)
	children.append(
		_dimension(
			Point(center.x + width, outer_width_y),
			Point(center.x - width, outer_width_y),
			outer_width_offset,
			Point(0, -7),
			width_text,
			dimension_arrow,
			half,
			text_style,
			text_metrics,
		)
	)
	children.append(
		_dimension(
			Point(center.x + hole_width, hole_top),
			Point(center.x + hole_width, hole_bottom),
			Point(width - hole_width + 18, 0),
			Point(10, 0),
			hole_height_text,
			dimension_arrow,
			half,
			text_style,
			text_metrics,
		)
	)
	if edge == "Низ":
		hole_width_y = center.y + height
		hole_width_offset = Point(0, 23)
	else:
		hole_width_y = hole_top
		hole_width_offset = Point(
			0,
			-height * 2
			+ hole_height * 2
			+ offset_value * 2
			- 16,
		)
	children.append(
		_dimension(
			Point(center.x + hole_width, hole_width_y),
			Point(center.x - hole_width, hole_width_y),
			hole_width_offset,
			Point(0, -7),
			hole_width_text,
			dimension_arrow,
			half,
			text_style,
			text_metrics,
		)
	)
	if offset_value != (height - hole_height) / 2 and not edge_aligned:
		children.append(
			_dimension(
				Point(center.x + hole_width, center.y + height),
				Point(center.x + hole_width, hole_bottom),
				Point(width - hole_width + 18, 0),
				Point(10, 0),
				offset_text,
				dimension_arrow,
				half,
				text_style,
				text_metrics,
			)
		)

	if offset_value == (height - hole_height) / 2 and not edge_aligned:
		children.append(
			Line(
				Point(center.x - width - 10, center.y),
				Point(center.x + width + 10, center.y),
				stroke=axis,
			)
		)
	children.append(
		Line(
			Point(center.x, center.y - height - 10),
			Point(center.x, center.y + height + 10),
			stroke=axis,
		)
	)
	return (_section_group(children, spec.section_type),)


def _build_h_section(
	spec,
	right,
	hcenter,
	arrow_size,
	main,
	half,
	axis,
	text_style,
	text_metrics,
	width_text,
	height_text,
	web_text,
	flange_text,
):
	width = spec.arg0
	height = spec.arg1
	web_half = spec.arg2
	flange_half = spec.arg3
	center = Point(right - 30 - width, hcenter)
	dimension_arrow = arrow_size / 3 * 2
	axis_width = width + 10
	axis_height = height + 10

	if not spec.rotated:
		points = (
			Point(center.x - width, center.y + height),
			Point(center.x - width + flange_half * 2, center.y + height),
			Point(center.x - width + flange_half * 2, center.y + web_half),
			Point(center.x + width - flange_half * 2, center.y + web_half),
			Point(center.x + width - flange_half * 2, center.y + height),
			Point(center.x + width, center.y + height),
			Point(center.x + width, center.y - height),
			Point(center.x + width - flange_half * 2, center.y - height),
			Point(center.x + width - flange_half * 2, center.y - web_half),
			Point(center.x - width + flange_half * 2, center.y - web_half),
			Point(center.x - width + flange_half * 2, center.y - height),
			Point(center.x - width, center.y - height),
		)
		children = [
			Polygon(
				points,
				stroke=main,
				fill=Fill(BLACK, pattern="backward-diagonal"),
			),
			Line(
				Point(center.x + axis_width, center.y),
				Point(center.x - axis_width, center.y),
				stroke=axis,
			),
			Line(
				Point(
					center.x + width - flange_half,
					center.y + axis_height,
				),
				Point(
					center.x + width - flange_half,
					center.y - axis_height,
				),
				stroke=axis,
			),
			Line(
				Point(
					center.x - width + flange_half,
					center.y + axis_height,
				),
				Point(
					center.x - width + flange_half,
					center.y - axis_height,
				),
				stroke=axis,
			),
		]
		children.extend(
			(
				_dimension(
					Point(center.x - width, center.y - height),
					Point(center.x - width, center.y + height),
					Point(-20, 0),
					Point(-10, 0),
					height_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
				),
				_dimension(
					Point(center.x + width, center.y + height),
					Point(center.x - width, center.y + height),
					Point(0, 25),
					Point(0, -10),
					width_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
				),
				_dimension(
					Point(center.x - width, center.y - height),
					Point(
						center.x - width + flange_half * 2,
						center.y - height,
					),
					Point(0, -20),
					Point(0, -10),
					flange_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
					splashed=True,
				),
				_dimension(
					Point(
						center.x + width - flange_half * 2,
						center.y - height,
					),
					Point(center.x + width, center.y - height),
					Point(0, -20),
					Point(0, -10),
					flange_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
					splashed=True,
				),
				_dimension(
					Point(center.x, center.y - web_half),
					Point(center.x, center.y + web_half),
					Point(width + 20, 0),
					Point(10, 0),
					web_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
					splashed=True,
				),
			)
		)
	else:
		points = (
			Point(center.x + width, center.y - height),
			Point(center.x + width, center.y - height + flange_half * 2),
			Point(center.x + web_half, center.y - height + flange_half * 2),
			Point(center.x + web_half, center.y + height - flange_half * 2),
			Point(center.x + width, center.y + height - flange_half * 2),
			Point(center.x + width, center.y + height),
			Point(center.x - width, center.y + height),
			Point(center.x - width, center.y + height - flange_half * 2),
			Point(center.x - web_half, center.y + height - flange_half * 2),
			Point(center.x - web_half, center.y - height + flange_half * 2),
			Point(center.x - width, center.y - height + flange_half * 2),
			Point(center.x - width, center.y - height),
		)
		children = [
			Polygon(
				points,
				stroke=main,
				fill=Fill(BLACK, pattern="backward-diagonal"),
			),
			Line(
				Point(center.x, center.y + axis_height - 2),
				Point(center.x, center.y - axis_height),
				stroke=axis,
			),
			Line(
				Point(center.x + axis_width, center.y + height - flange_half),
				Point(center.x - axis_width, center.y + height - flange_half),
				stroke=axis,
			),
			Line(
				Point(center.x + axis_width, center.y - height + flange_half),
				Point(center.x - axis_width, center.y - height + flange_half),
				stroke=axis,
			),
		]
		children.extend(
			(
				_dimension(
					Point(center.x - width, center.y - height),
					Point(center.x - width, center.y + height),
					Point(-20, 0),
					Point(-10, 0),
					height_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
				),
				_dimension(
					Point(center.x + width, center.y + height),
					Point(center.x - width, center.y + height),
					Point(0, 25),
					Point(0, -10),
					width_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
				),
				_dimension(
					Point(center.x + width, center.y + height),
					Point(
						center.x + width,
						center.y + height - flange_half * 2,
					),
					Point(20, 0),
					Point(10, 0),
					flange_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
					splashed=True,
				),
				_dimension(
					Point(
						center.x + width,
						center.y - height + flange_half * 2,
					),
					Point(center.x + width, center.y - height),
					Point(20, 0),
					Point(10, 0),
					flange_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
					splashed=True,
				),
				_dimension(
					Point(center.x - web_half, center.y),
					Point(center.x + web_half, center.y),
					Point(0, -20 - height),
					Point(0, -10),
					web_text,
					dimension_arrow,
					half,
					text_style,
					text_metrics,
					splashed=True,
				),
			)
		)

	return (_section_group(children, spec.section_type),)
