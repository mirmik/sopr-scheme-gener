"""PyQt5 adapters for the independent Scene model."""

import math

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import (
	QBrush,
	QColor,
	QFont,
	QFontMetrics,
	QPainter,
	QPen,
	QPolygonF,
)

from .metrics import TextMeasurement
from .model import (
	Arc,
	Arrow,
	Ellipse,
	Group,
	Line,
	Polygon,
	Polyline,
	Rectangle,
	Scene,
	Text,
	TextAnchor,
)


def _color(value):
	return QColor(value.red, value.green, value.blue, value.alpha)


def _font(style):
	font = QFont()
	if style.family:
		font.setFamily(style.family)
	font.setPointSizeF(style.point_size)
	font.setBold(style.bold)
	font.setItalic(style.italic)
	return font


def _pen(stroke):
	pen = QPen(_color(stroke.color))
	pen.setWidthF(stroke.width)
	if stroke.dash:
		pen.setDashPattern(list(stroke.dash))
	return pen


def _polygon(points):
	return QPolygonF([QPointF(point.x, point.y) for point in points])


def _brush(fill):
	brush = QBrush(_color(fill.color))
	if fill.pattern == "backward-diagonal":
		brush.setStyle(Qt.BDiagPattern)
	return brush


class QtTextMetrics:
	def measure(self, text, style):
		metrics = QFontMetrics(_font(style))
		return TextMeasurement(
			width=metrics.horizontalAdvance(text),
			height=metrics.height(),
			ascent=metrics.ascent(),
			descent=metrics.descent(),
		)


class QtPainterRenderer:
	def __init__(self, text_metrics=None):
		self.text_metrics = text_metrics or QtTextMetrics()

	def render(self, scene, painter):
		if not isinstance(scene, Scene):
			raise TypeError("scene must be a Scene")
		if not isinstance(painter, QPainter) or not painter.isActive():
			raise TypeError("painter must be an active QPainter")

		painter.save()
		try:
			painter.fillRect(
				QRectF(0, 0, scene.viewport.width, scene.viewport.height),
				QBrush(_color(scene.background)),
			)
			painter.translate(-scene.viewport.x, -scene.viewport.y)
			for item in scene.objects:
				self._render_object(item, painter)
		finally:
			painter.restore()

	def _render_object(self, item, painter):
		if isinstance(item, Line):
			painter.setPen(_pen(item.stroke))
			painter.setBrush(QBrush())
			painter.drawLine(
				QPointF(item.start.x, item.start.y),
				QPointF(item.end.x, item.end.y),
			)
			return
		if isinstance(item, Polyline):
			painter.setPen(_pen(item.stroke))
			painter.setBrush(QBrush())
			painter.drawPolyline(_polygon(item.points))
			return
		if isinstance(item, Polygon):
			painter.setPen(_pen(item.stroke) if item.stroke is not None else Qt.NoPen)
			painter.setBrush(_brush(item.fill))
			painter.drawPolygon(_polygon(item.points))
			return
		if isinstance(item, Rectangle):
			painter.setPen(_pen(item.stroke) if item.stroke is not None else Qt.NoPen)
			painter.setBrush(_brush(item.fill))
			painter.drawRect(
				QRectF(
					item.bounds.x,
					item.bounds.y,
					item.bounds.width,
					item.bounds.height,
				)
			)
			return
		if isinstance(item, Ellipse):
			painter.setPen(_pen(item.stroke) if item.stroke is not None else Qt.NoPen)
			painter.setBrush(_brush(item.fill))
			painter.drawEllipse(
				QRectF(
					item.bounds.x,
					item.bounds.y,
					item.bounds.width,
					item.bounds.height,
				)
			)
			return
		if isinstance(item, Arc):
			painter.setPen(_pen(item.stroke))
			painter.setBrush(Qt.NoBrush)
			painter.drawArc(
				QRectF(
					item.bounds.x,
					item.bounds.y,
					item.bounds.width,
					item.bounds.height,
				),
				int(item.start_degrees * 16),
				int(item.span_degrees * 16),
			)
			return
		if isinstance(item, Arrow):
			self._render_arrow(item, painter)
			return
		if isinstance(item, Text):
			self._render_text(item, painter)
			return
		if isinstance(item, Group):
			painter.save()
			try:
				painter.translate(item.offset.x, item.offset.y)
				for child in item.children:
					self._render_object(child, painter)
			finally:
				painter.restore()
			return
		raise TypeError("Unsupported scene object: {}".format(type(item).__name__))

	def _render_arrow(self, item, painter):
		dx = item.end.x - item.start.x
		dy = item.end.y - item.start.y
		length = math.hypot(dx, dy)
		ux, uy = dx / length, dy / length
		base_x = item.end.x - ux * item.head_length
		base_y = item.end.y - uy * item.head_length
		angle = math.atan2(-dy, dx)
		half_width = item.head_width / 2
		head = QPolygonF(
			[
				QPointF(item.end.x, item.end.y),
				QPointF(
					item.end.x
					- item.head_length * math.cos(angle)
					+ half_width * math.sin(angle),
					item.end.y
					+ item.head_length * math.sin(angle)
					+ half_width * math.cos(angle),
				),
				QPointF(
					item.end.x
					- item.head_length * math.cos(angle)
					- half_width * math.sin(angle),
					item.end.y
					+ item.head_length * math.sin(angle)
					- half_width * math.cos(angle),
				),
			]
		)
		painter.setPen(_pen(item.stroke))
		painter.setBrush(QBrush(_color(item.stroke.color)))
		painter.drawLine(
			QPointF(item.start.x, item.start.y),
			QPointF(base_x, base_y),
		)
		if item.head_stroke is not None:
			painter.setPen(_pen(item.head_stroke))
		painter.drawConvexPolygon(head)

	def _render_text(self, item, painter):
		measurement = self.text_metrics.measure(item.value, item.style)
		x = item.position.x
		y = item.position.y
		if item.anchor == TextAnchor.TOP_LEFT:
			y += measurement.ascent
		elif item.anchor == TextAnchor.BASELINE_CENTER:
			x -= measurement.width / 2
		elif item.anchor == TextAnchor.BASELINE_RIGHT:
			x -= measurement.width
		elif item.anchor == TextAnchor.CENTER:
			x -= measurement.width / 2
			y += (measurement.ascent - measurement.descent) / 2

		painter.save()
		try:
			painter.translate(item.position.x, item.position.y)
			painter.rotate(item.rotation_degrees)
			painter.translate(-item.position.x, -item.position.y)
			painter.setFont(_font(item.style))
			painter.setPen(QPen(_color(item.style.color)))
			painter.setBrush(QBrush())
			painter.drawText(QPointF(x, y), item.value)
		finally:
			painter.restore()
