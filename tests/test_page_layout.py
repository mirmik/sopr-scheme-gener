import os

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtTest import QTest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime
from sopr_scheme_gener.devapi import DevBridge


def _context():
	return create_runtime(
		build_parser().parse_args(["--type", "beams", "--no-maximize"])
	)


def test_layout_materializes_only_when_grip_is_dragged():
	context = _context()
	try:
		canvas = context.canvas
		layout = canvas.page_layout()
		task = layout.task_frame

		QTest.mouseClick(
			canvas,
			Qt.LeftButton,
			pos=QPoint(int(task.x + task.width / 2), int(task.y + task.height / 2)),
		)
		assert context.controller.current_scheme.page_layout is None

		grip = canvas._layout_grip_rect(canvas._layout_frame_rect("task_frame"))
		QTest.mouseClick(canvas, Qt.LeftButton, pos=grip.center().toPoint())
		assert context.controller.current_scheme.page_layout is None

		start = grip.center().toPoint()
		finish = start + QPoint(12, 9)
		QTest.mousePress(canvas, Qt.LeftButton, pos=start)
		QTest.mouseMove(canvas, finish)
		QTest.mouseRelease(canvas, Qt.LeftButton, pos=finish)

		materialized = context.controller.current_scheme.page_layout
		assert materialized is not None
		assert materialized.task_frame.x == task.x + 12
		assert materialized.task_frame.y == task.y + 9
	finally:
		context.window.close()


def test_resize_handle_changes_frame_and_stays_inside_canvas():
	context = _context()
	try:
		canvas = context.canvas
		task = canvas.page_layout().task_frame
		handle = canvas._layout_handle_rects(
			canvas._layout_frame_rect("task_frame")
		)["se"].center().toPoint()

		QTest.mousePress(canvas, Qt.LeftButton, pos=handle)
		QTest.mouseMove(canvas, QPoint(canvas.width() + 100, canvas.height() + 100))
		QTest.mouseRelease(
			canvas,
			Qt.LeftButton,
			pos=QPoint(canvas.width() + 100, canvas.height() + 100),
		)

		frame = context.controller.current_scheme.page_layout.task_frame
		assert frame.width > task.width
		assert frame.x + frame.width <= canvas.width()
		assert frame.y + frame.height <= canvas.height()
	finally:
		context.window.close()


def test_editor_overlay_is_not_exported():
	context = _context()
	try:
		canvas = context.canvas
		before = canvas.make_image()
		canvas._layout_hover = "task_frame"
		after = canvas.make_image()

		assert before == after
	finally:
		context.window.close()


def test_every_task_renders_with_materialized_frames():
	context = _context()
	try:
		bridge = DevBridge(context)
		for spec in context.task_specs:
			context.controller.select(spec.identifier)
			context.controller.current_scheme.page_layout = (
				context.canvas._derived_page_layout()
			)
			context.canvas.update()
			context.app.processEvents()
			image = context.canvas.make_image()
			assert image.bits().asstring(image.sizeInBytes())
		assert bridge.dispatch("errors.list", {}) == []
	finally:
		context.window.close()


def test_task_frame_resize_recomposes_scene_in_local_dimensions():
	context = _context()
	try:
		context.controller.select("column-stability")
		layout = context.canvas._derived_page_layout()
		layout.task_frame.width = 220
		layout.task_frame.height = 160
		context.controller.current_scheme.page_layout = layout

		context.canvas.make_image()

		assert context.canvas.last_scene.viewport.width == 220
		assert context.canvas.last_scene.viewport.height == 160
	finally:
		context.window.close()


def test_stress_cube_uses_classic_sheet_resize_and_one_to_one_framed_scene():
	context = _context()
	try:
		context.controller.select("stress-cube")
		canvas = context.canvas
		scheme = context.controller.current_scheme
		assert canvas.no_resize is True

		layout = canvas._derived_page_layout()
		scheme.page_layout = layout
		assert canvas.no_resize is False

		canvas.make_image()
		first = canvas.scene_interaction.index.bounds("cube/0")
		assert canvas.scene_interaction.mapping.scale == 1.0

		layout.task_frame.width -= 60
		layout.task_frame.height -= 40
		canvas.make_image()
		second = canvas.scene_interaction.index.bounds("cube/0")

		assert canvas.scene_interaction.mapping.scale == 1.0
		assert second.width == first.width
		assert second.height == first.height
	finally:
		context.window.close()
