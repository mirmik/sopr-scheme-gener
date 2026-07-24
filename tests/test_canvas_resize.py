import os

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtTest import QTest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def _context(task_type="beams"):
	return create_runtime(
		build_parser().parse_args(
			["--type", task_type, "--no-maximize"]
		)
	)


def _drag(canvas, start, finish):
	QTest.mouseMove(canvas, start)
	QTest.mousePress(canvas, Qt.LeftButton, pos=start)
	QTest.mouseMove(canvas, finish)
	QTest.mouseRelease(canvas, Qt.LeftButton, pos=finish)


def test_canvas_edges_and_corners_show_resize_cursors():
	context = _context()
	try:
		canvas = context.canvas
		width = canvas.width()
		height = canvas.height()
		cases = (
			(QPoint(2, height // 2), Qt.SizeHorCursor),
			(QPoint(width // 2, 2), Qt.SizeVerCursor),
			(QPoint(2, 2), Qt.SizeFDiagCursor),
			(QPoint(width - 2, 2), Qt.SizeBDiagCursor),
			(QPoint(2, height - 2), Qt.SizeBDiagCursor),
			(QPoint(width - 2, height - 2), Qt.SizeFDiagCursor),
		)
		for point, cursor in cases:
			QTest.mouseMove(canvas, point)
			assert canvas.cursor().shape() == cursor
	finally:
		context.window.close()


def test_canvas_corner_resizes_width_and_height_together():
	context = _context()
	try:
		canvas = context.canvas
		width = canvas.width()
		height = canvas.height()
		start = QPoint(width - 2, height - 2)
		finish = start - QPoint(30, 20)

		_drag(canvas, start, finish)

		assert canvas.width() == width - 30
		assert canvas.height() == height - 20
	finally:
		context.window.close()


def test_auto_size_canvas_resize_is_enabled_only_after_layout_materializes():
	context = _context("shafts-pipes")
	try:
		canvas = context.canvas
		canvas.make_image()
		context.app.processEvents()
		context.app.processEvents()
		context.app.processEvents()
		legacy_size = canvas.size()
		start = QPoint(canvas.width() - 2, canvas.height() - 2)
		_drag(canvas, start, start + QPoint(20, 15))
		assert canvas.size() == legacy_size

		context.controller.current_scheme.page_layout = (
			canvas._derived_page_layout()
		)
		start = QPoint(canvas.width() - 2, canvas.height() - 2)
		_drag(canvas, start, start - QPoint(20, 15))
		assert canvas.width() == legacy_size.width() - 20
		assert canvas.height() == legacy_size.height() - 15
	finally:
		context.window.close()
