import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QEvent, QPointF, Qt
from PyQt5.QtGui import QMouseEvent
import pytest

from sopr_scheme_gener.app import build_parser, create_runtime


def _mouse_event(event_type, point, button=Qt.NoButton, buttons=Qt.NoButton):
	return QMouseEvent(
		event_type,
		QPointF(point[0], point[1]),
		button,
		buttons,
		Qt.NoModifier,
	)


def _hover(widget, point):
	widget.mouseMoveEvent(_mouse_event(QEvent.MouseMove, point))


def _drag(widget, start, end):
	widget.mousePressEvent(
		_mouse_event(
			QEvent.MouseButtonPress,
			start,
			button=Qt.LeftButton,
			buttons=Qt.LeftButton,
		)
	)
	widget.mouseMoveEvent(
		_mouse_event(
			QEvent.MouseMove,
			end,
			buttons=Qt.LeftButton,
		)
	)
	widget.mouseReleaseEvent(
		_mouse_event(
			QEvent.MouseButtonRelease,
			end,
			button=Qt.LeftButton,
		)
	)


def _device_center(interaction, object_id):
	bounds = interaction.index.bounds(object_id)
	world_x = bounds.x + bounds.width / 2
	world_y = bounds.y + bounds.height / 2
	mapping = interaction.mapping
	return (
		(world_x - mapping.viewport.x) * mapping.scale,
		(world_y - mapping.viewport.y) * mapping.scale,
	)


def test_beams_hover_and_drag_use_scene_object_id():
	context = create_runtime(
		build_parser().parse_args(["--type", "beams", "--no-maximize", "--error"])
	)
	try:
		scheme = context.controller.current_scheme
		label = scheme.confwidget.label("drag", (0.0, -20.0))
		scheme.task["labels"] = [label]
		context.app.processEvents()
		context.canvas.make_image()

		start = _device_center(context.canvas.scene_interaction, "label/0")
		_hover(context.canvas, start)

		assert context.canvas.selected_label_id == "label/0"
		assert context.canvas.label_items == {}

		before = label.pos
		_drag(context.canvas, start, (start[0] + 12, start[1] + 7))

		assert label.pos[0] > before[0]
		assert label.pos[1] == before[1] + 7
	finally:
		context.window.close()
		context.app.processEvents()


def test_stress_cube_hover_and_drag_use_same_scene_hit_api():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "stress-cube", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		scheme.task["sections"][0].qx = "+"
		scheme.task["labels"][0].text = "drag"
		context.app.processEvents()
		context.canvas.make_image()

		object_id = "cube/0/label/qx"
		start = _device_center(context.canvas.scene_interaction, object_id)
		_hover(context.canvas, start)

		assert context.canvas.selected_object_id == object_id
		assert not hasattr(context.canvas, "hovers")

		label = scheme.task["labels"][0]
		before = (label.x, label.y)
		scale = context.canvas.scene_interaction.mapping.scale
		_drag(
			context.canvas,
			start,
			(start[0] + 10 * scale, start[1] + 6 * scale),
		)

		assert label.x == pytest.approx(before[0] + 10, abs=0.6)
		assert label.y == pytest.approx(before[1] + 6, abs=0.6)
	finally:
		context.window.close()
		context.app.processEvents()


def test_plate_hover_and_drag_reuses_scene_interaction():
	context = create_runtime(
		build_parser().parse_args(["--type", "plate", "--no-maximize", "--error"])
	)
	try:
		scheme = context.controller.current_scheme
		label = scheme.confwidget.label("drag", (0.0, -15.0))
		scheme.task["labels"] = [label]
		context.app.processEvents()
		context.canvas.make_image()

		start = _device_center(context.canvas.scene_interaction, "label/0")
		_hover(context.canvas, start)

		assert context.canvas.selected_label_id == "label/0"
		assert context.canvas.label_items == {}

		before = label.pos
		_drag(context.canvas, start, (start[0] + 9, start[1] + 5))

		assert label.pos[0] > before[0]
		assert label.pos[1] == before[1] + 5
	finally:
		context.window.close()
		context.app.processEvents()
