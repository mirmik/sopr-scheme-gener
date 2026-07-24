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


def test_each_task_type_keeps_its_own_canvas_size():
	context = _context("beams")
	try:
		context.legacy.resize_canvas(520, 330)
		context.app.processEvents()
		assert context.controller.current_scheme.canvas_size == (520, 330)

		context.controller.select("plate")
		assert (context.canvas.width(), context.canvas.height()) == (400, 250)
		context.legacy.resize_canvas(610, 360)
		context.app.processEvents()
		assert context.controller.current_scheme.canvas_size == (610, 360)

		context.controller.select("beams")
		assert (context.canvas.width(), context.canvas.height()) == (520, 330)
		assert context.common_settings.width_getter.get() == 520
		assert context.common_settings.height_getter.get() == 330

		context.controller.select("plate")
		assert (context.canvas.width(), context.canvas.height()) == (610, 360)
		assert context.common_settings.width_getter.get() == 610
		assert context.common_settings.height_getter.get() == 360
	finally:
		context.window.close()


def test_loaded_canvas_size_is_restored_after_switching_task_types():
	context = _context("beams")
	try:
		document = context.storage.to_data()
		document["canvas"] = {"width": 570, "height": 340}
		document["common"]["Ширина в px:"] = 570
		document["common"]["Высота в px:"] = 340
		context.storage.load_data(document)
		assert context.controller.current_scheme.canvas_size == (570, 340)

		context.controller.select("plate")
		context.controller.select("beams")
		assert (context.canvas.width(), context.canvas.height()) == (570, 340)
	finally:
		context.window.close()


def test_auto_sized_task_restores_its_computed_canvas_size():
	context = _context("shafts-pipes")
	try:
		context.canvas.make_image()
		context.app.processEvents()
		context.app.processEvents()
		auto_size = context.canvas.size()
		assert context.controller.current_scheme.canvas_size == (
			auto_size.width(),
			auto_size.height(),
		)

		context.controller.select("beams")
		context.controller.select("shafts-pipes")
		assert context.canvas.size() == auto_size
	finally:
		context.window.close()
