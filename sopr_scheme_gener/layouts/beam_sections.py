"""Qt-independent cross-section layouts used by the beams task."""

from dataclasses import dataclass
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
	Text,
	TextAnchor,
	metadata,
)


SUPPORTED_SECTION_TYPES = ("Нет", "Тонкая труба", "Треугольник")


@dataclass(frozen=True)
class BeamSectionSpec:
	section_type: str = "Нет"
	arg0: float = 0
	arg1: float = 0
	arg2: float = 0
	text0: str = ""
	text1: str = ""
	text2: str = ""


def beam_section_width(spec):
	if spec.section_type == "Нет":
		return 0
	if spec.section_type == "Тонкая труба":
		return spec.arg0 + 120
	if spec.section_type == "Треугольник":
		return spec.arg1 + 120
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

	return (
		Group(
			children,
			object_id="section/cross-section",
			metadata=metadata(kind="cross-section", section_type=spec.section_type),
		),
	)
