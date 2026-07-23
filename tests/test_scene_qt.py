import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QApplication

from sopr_scheme_gener.scene import (
	Arc,
	Arrow,
	Color,
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
)
from sopr_scheme_gener.scene.qt import QtPainterRenderer, QtTextMetrics


def _smoke_scene():
	return Scene(
		Rect(0, 0, 160, 100),
		(
			Line(Point(5, 5), Point(70, 5), stroke=Stroke(width=2)),
			Polyline(
				(Point(5, 15), Point(35, 8), Point(70, 15)),
				stroke=Stroke(Color(0, 80, 180), 2),
			),
			Polygon(
				(Point(5, 30), Point(40, 30), Point(20, 55)),
				fill=Fill(Color(220, 220, 220)),
			),
			Rectangle(
				Rect(75, 8, 20, 15),
				fill=Fill(Color(240, 240, 240), pattern="backward-diagonal"),
			),
			Ellipse(Rect(105, 8, 20, 15)),
			Arc(Rect(130, 8, 20, 20), 0, 180),
			Arrow(
				Point(55, 45),
				Point(130, 45),
				stroke=Stroke(Color(180, 0, 0), 2),
			),
			Group(
				(
					Text(
						Point(0, 0),
						"Scene",
						style=TextStyle(point_size=11, italic=True),
						anchor=TextAnchor.TOP_LEFT,
					),
				),
				offset=Point(75, 65),
			),
		),
	)


def _render(scene):
	image = QImage(
		int(scene.viewport.width),
		int(scene.viewport.height),
		QImage.Format_ARGB32,
	)
	painter = QPainter(image)
	painter.setRenderHint(QPainter.Antialiasing, False)
	QtPainterRenderer().render(scene, painter)
	painter.end()
	return image


def _image_bytes(image):
	bits = image.bits()
	return bits.asstring(image.sizeInBytes())


def test_qt_renderer_draws_deterministic_smoke_scene():
	_app = QApplication.instance() or QApplication(["scene-test"])
	scene = _smoke_scene()

	first = _render(scene)
	second = _render(scene)

	assert _image_bytes(first) == _image_bytes(second)
	non_white = sum(
		(
			first.pixelColor(x, y).red(),
			first.pixelColor(x, y).green(),
			first.pixelColor(x, y).blue(),
			first.pixelColor(x, y).alpha(),
		)
		!= (255, 255, 255, 255)
		for y in range(first.height())
		for x in range(first.width())
	)
	assert non_white > 300


def test_qt_text_metrics_returns_positive_dimensions():
	_app = QApplication.instance() or QApplication(["scene-metrics-test"])
	measurement = QtTextMetrics().measure("beam", TextStyle(point_size=12))

	assert measurement.width > 0
	assert measurement.height > 0
	assert measurement.ascent > measurement.descent >= 0
