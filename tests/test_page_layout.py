import os

from PyQt5.QtCore import QPoint, QRectF, Qt
from PyQt5.QtTest import QTest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime
from sopr_scheme_gener.devapi import DevBridge


def _context():
	return create_runtime(
		build_parser().parse_args(["--type", "beams", "--no-maximize"])
	)


def test_layout_activates_only_from_explicit_button_and_cannot_be_disabled():
	context = _context()
	try:
		canvas = context.canvas
		scheme = context.controller.current_scheme
		layout = canvas._derived_page_layout()
		task = layout.task_frame
		transient_grip = canvas._layout_grip_rect(
			QRectF(task.x, task.y, task.width, task.height)
		)
		QTest.mouseMove(canvas, transient_grip.center().toPoint())
		assert scheme.page_layout is None
		assert canvas._layout_hover is None

		button = context.central.page_layout_button
		assert button.isEnabled()
		button.click()

		assert scheme.page_layout is not None
		assert not button.isEnabled()
		assert button.text() == "Свободное расположение включено"

		materialized = scheme.page_layout
		button.click()
		assert scheme.page_layout is materialized

		context.controller.select("stress-cube")
		assert button.isEnabled()
		assert button.text() == "Свободное расположение"
		context.controller.select("beams")
		assert not button.isEnabled()
	finally:
		context.window.close()


def test_page_layout_button_tracks_loaded_legacy_and_framed_documents():
	context = _context()
	try:
		legacy = context.storage.to_data()
		context.central.activate_page_layout()
		framed = context.storage.to_data()
		assert not context.central.page_layout_button.isEnabled()

		context.storage.load_data(legacy)
		assert context.central.page_layout_button.isEnabled()

		context.storage.load_data(framed)
		assert not context.central.page_layout_button.isEnabled()
	finally:
		context.window.close()


def test_resize_handle_changes_frame_and_stays_inside_canvas():
	context = _context()
	try:
		canvas = context.canvas
		context.central.activate_page_layout()
		task = canvas.page_layout().task_frame
		initial_width = task.width
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
		assert frame.width > initial_width
		assert frame.x + frame.width <= canvas.width()
		assert frame.y + frame.height <= canvas.height()
	finally:
		context.window.close()


def test_editor_overlay_is_not_exported():
	context = _context()
	try:
		canvas = context.canvas
		context.central.activate_page_layout()
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


def test_spatial_beams_keep_one_to_one_scale_when_task_frame_resizes():
	context = _context()
	try:
		context.controller.select("spatial-beams")
		canvas = context.canvas
		scheme = context.controller.current_scheme
		layout = canvas._derived_page_layout()
		scheme.page_layout = layout

		canvas.make_image()
		first = canvas.scene_interaction.index.bounds("section/0/hit")
		assert canvas.scene_interaction.mapping.scale == 1.0

		layout.task_frame.width -= 60
		layout.task_frame.height -= 40
		canvas.make_image()
		second = canvas.scene_interaction.index.bounds("section/0/hit")

		assert canvas.scene_interaction.mapping.scale == 1.0
		assert second.width == first.width
		assert second.height == first.height
	finally:
		context.window.close()


def test_page_layout_task_scene_is_independent_from_note_text_for_every_task():
	context = _context()
	try:
		for spec in context.task_specs:
			context.controller.select(spec.identifier)
			scheme = context.controller.current_scheme
			scheme.texteditor.setPlainText("")
			scheme.page_layout = context.canvas._derived_page_layout()
			empty_note_image = context.canvas.make_image()
			empty_note_scene = context.canvas.last_scene

			scheme.texteditor.setPlainText(
				"Первая строка\nВторая строка\nТретья строка"
			)
			long_note_image = context.canvas.make_image()
			long_note_scene = context.canvas.last_scene

			assert long_note_scene == empty_note_scene, spec.identifier
			assert long_note_image != empty_note_image, spec.identifier
	finally:
		context.window.close()


def test_legacy_layout_keeps_historic_note_dependent_task_position():
	context = _context()
	try:
		scheme = context.controller.current_scheme
		assert scheme.page_layout is None
		scheme.texteditor.setPlainText("")
		context.canvas.make_image()
		empty_note_scene = context.canvas.last_scene

		scheme.texteditor.setPlainText("Первая строка\nВторая строка")
		context.canvas.make_image()

		assert context.canvas.last_scene != empty_note_scene
	finally:
		context.window.close()
