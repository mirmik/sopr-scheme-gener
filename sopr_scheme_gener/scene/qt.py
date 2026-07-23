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
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene

from .metrics import TextMeasurement
from .hit import SceneIndex, ViewportMapping
from .model import (
	Arc,
	Arrow,
	Ellipse,
	Group,
	Line,
	Point,
	Polygon,
	Polyline,
	Rectangle,
	Scene,
	Text,
	TextAnchor,
)


class _GraphicsArrowItem(QGraphicsItem):
	def __init__(self, line, head):
		super().__init__()
		self.line = line
		self.head = head

	def boundingRect(self):
		left = min(self.line.start.x, self.line.end.x) - 5
		top = min(self.line.start.y, self.line.end.y) - 5
		right = max(self.line.start.x, self.line.end.x) + 5
		bottom = max(self.line.start.y, self.line.end.y) + 5
		return QRectF(left, top, right - left, bottom - top)

	def paint(self, painter, option, widget=None):
		painter.setPen(_pen(self.line.stroke))
		painter.setBrush(_brush(self.head.fill))
		painter.drawLine(
			QPointF(self.line.start.x, self.line.start.y),
			QPointF(self.line.end.x, self.line.end.y),
		)
		painter.drawPolygon(_polygon(self.head.points))


class _GraphicsTextItem(QGraphicsItem):
	def __init__(self, item, text_metrics):
		super().__init__()
		self.item = item
		self.measurement = text_metrics.measure(item.value, item.style)

	def boundingRect(self):
		item = self.item
		if item.anchor == TextAnchor.CENTER:
			return QRectF(
				item.position.x - self.measurement.width / 2,
				item.position.y - self.measurement.height / 2,
				self.measurement.width + 5,
				self.measurement.height,
			)
		return QRectF(
			item.position.x,
			item.position.y - self.measurement.ascent,
			self.measurement.width + 5,
			self.measurement.height,
		)

	def paint(self, painter, option, widget=None):
		painter.setPen(QPen(_color(self.item.style.color)))
		painter.setFont(_font(self.item.style))
		if self.item.anchor == TextAnchor.CENTER:
			painter.drawText(self.boundingRect(), self.item.value)
		else:
			painter.drawText(
				QPointF(self.item.position.x, self.item.position.y),
				self.item.value,
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
	if stroke.line_style == "dash-dot":
		pen.setStyle(Qt.DashDotLine)
	elif stroke.dash:
		pen.setDashPattern(list(stroke.dash))
	return pen


def _polygon(points):
	return QPolygonF([QPointF(point.x, point.y) for point in points])


def _brush(fill):
	brush = QBrush(_color(fill.color))
	if fill.pattern == "backward-diagonal":
		brush.setStyle(Qt.BDiagPattern)
	elif fill.pattern == "forward-diagonal":
		brush.setStyle(Qt.FDiagPattern)
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


class QtSceneInteraction:
	"""Translate Qt device coordinates and query the shared Scene index."""

	def __init__(
		self,
		scene,
		text_metrics=None,
		device_width=None,
		device_height=None,
		aspect_fit=False,
	):
		self.text_metrics = text_metrics or QtTextMetrics()
		self.index = SceneIndex(scene, self.text_metrics)
		if aspect_fit:
			if device_width is None or device_height is None:
				raise ValueError("device dimensions are required for aspect fit")
			self.mapping = ViewportMapping.aspect_fit(
				scene.viewport,
				device_width,
				device_height,
			)
		else:
			self.mapping = ViewportMapping.direct(scene.viewport)

	def point(self, qt_point):
		point = self.mapping.from_device(Point(qt_point.x(), qt_point.y()))
		return QPointF(point.x, point.y)

	def delta(self, current_qt_point, previous_qt_point):
		delta = self.mapping.delta_from_device(
			Point(
				current_qt_point.x() - previous_qt_point.x(),
				current_qt_point.y() - previous_qt_point.y(),
			)
		)
		return QPointF(delta.x, delta.y)

	def hit_test(self, qt_point, kinds=None, predicate=None):
		point = self.mapping.from_device(Point(qt_point.x(), qt_point.y()))
		return self.index.hit_test(point, kinds=kinds, predicate=predicate)


class QtGraphicsSceneRenderer:
	"""Compatibility renderer for documents whose raster is a Qt scene contract."""

	def __init__(self, text_metrics=None):
		self.text_metrics = text_metrics or QtTextMetrics()

	def render(self, scene, painter):
		if not isinstance(scene, Scene):
			raise TypeError("scene must be a Scene")
		if not isinstance(painter, QPainter) or not painter.isActive():
			raise TypeError("painter must be an active QPainter")
		graphics_scene = QGraphicsScene()
		for item in scene.objects:
			self._add(item, graphics_scene)
		graphics_scene.setSceneRect(
			QRectF(
				scene.viewport.x,
				scene.viewport.y,
				scene.viewport.width,
				scene.viewport.height,
			)
		)
		graphics_scene.render(painter)

	def _add(self, item, graphics_scene, offset_x=0.0, offset_y=0.0):
		if isinstance(item, Group):
			if ("kind", "arrow") in item.metadata:
				graphics_item = _GraphicsArrowItem(item.children[0], item.children[1])
				graphics_item.setPos(offset_x + item.offset.x, offset_y + item.offset.y)
				graphics_scene.addItem(graphics_item)
				return
			for child in item.children:
				self._add(
					child,
					graphics_scene,
					offset_x + item.offset.x,
					offset_y + item.offset.y,
				)
			return
		if isinstance(item, Line):
			graphics_item = graphics_scene.addLine(
				item.start.x,
				item.start.y,
				item.end.x,
				item.end.y,
				_pen(item.stroke),
			)
		elif isinstance(item, Polygon):
			graphics_item = graphics_scene.addPolygon(
				_polygon(item.points),
				_pen(item.stroke) if item.stroke is not None else QPen(Qt.NoPen),
				_brush(item.fill),
			)
		elif isinstance(item, Rectangle):
			graphics_item = graphics_scene.addRect(
				QRectF(
					item.bounds.x,
					item.bounds.y,
					item.bounds.width,
					item.bounds.height,
				),
				_pen(item.stroke) if item.stroke is not None else QPen(Qt.NoPen),
				_brush(item.fill),
			)
		elif isinstance(item, Text):
			graphics_item = _GraphicsTextItem(item, self.text_metrics)
			graphics_scene.addItem(graphics_item)
		else:
			raise TypeError(
				"QtGraphicsSceneRenderer does not support {}".format(
					type(item).__name__
				)
			)
		graphics_item.setPos(offset_x, offset_y)


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
			if item.convex:
				painter.drawConvexPolygon(_polygon(item.points))
			else:
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
				if item.antialias is not None:
					painter.setRenderHint(QPainter.Antialiasing, item.antialias)
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
