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


@pytest.mark.parametrize(
	("object_id", "record_name", "record_index", "x_field", "y_field"),
	[
		(
			"segment/0/length-label",
			"segments",
			0,
			"length_offset_x",
			"length_offset_y",
		),
		(
			"segment/1/rigidity-label",
			"segments",
			1,
			"rigidity_offset_x",
			"rigidity_offset_y",
		),
		(
			"node/2/load-label",
			"nodes",
			2,
			"load_offset_x",
			"load_offset_y",
		),
	],
)
def test_column_stability_generated_labels_are_draggable_and_persisted(
	object_id,
	record_name,
	record_index,
	x_field,
	y_field,
):
	context = create_runtime(
		build_parser().parse_args(
			["--type", "column-stability", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		context.app.processEvents()
		context.canvas.make_image()
		start = _device_center(context.canvas.scene_interaction, object_id)
		_hover(context.canvas, start)

		assert context.canvas.selected_label_id == object_id
		record = scheme.task[record_name][record_index]
		before = (getattr(record, x_field), getattr(record, y_field))
		_drag(context.canvas, start, (start[0] + 14, start[1] - 8))

		assert getattr(record, x_field) == pytest.approx(before[0] + 14)
		assert getattr(record, y_field) == pytest.approx(before[1] - 8)

		document = context.storage.to_data()
		context.storage.load_data(document)
		restored = context.controller.current_scheme.task[record_name][record_index]
		assert getattr(restored, x_field) == pytest.approx(before[0] + 14)
		assert getattr(restored, y_field) == pytest.approx(before[1] - 8)
	finally:
		context.window.close()
		context.app.processEvents()


@pytest.mark.parametrize(
	("object_id", "record_name", "record_index", "x_field", "y_field"),
	[
		(
			"node/0/force/text",
			"betsect",
			0,
			"action_text_offset_x",
			"action_text_offset_y",
		),
		(
			"section/0/distributed-force/text",
			"sectforce",
			0,
			"load_text_offset_x",
			"load_text_offset_y",
		),
		(
			"node/0/label",
			"betsect",
			0,
			"node_label_offset_x",
			"node_label_offset_y",
		),
		(
			"section/0/label",
			"sections",
			0,
			"section_label_offset_x",
			"section_label_offset_y",
		),
	],
)
def test_axial_torsion_labels_use_shared_drag_controller(
	object_id,
	record_name,
	record_index,
	x_field,
	y_field,
):
	context = create_runtime(
		build_parser().parse_args(
			["--type", "axial-torsion", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		node = scheme.task["betsect"][0]
		load = scheme.task["sectforce"][0]
		if object_id == "node/0/force/text":
			node.F = "+"
			node.T = "P"
		elif object_id == "section/0/distributed-force/text":
			load.Fr = "+"
			load.mkrT = "q"
		elif object_id == "node/0/label":
			node.label = "A"
		else:
			scheme.task["sections"][0].label = "S"
		context.app.processEvents()
		context.canvas.make_image()

		start = _device_center(context.canvas.scene_interaction, object_id)
		_hover(context.canvas, start)
		assert context.canvas.selected_label_id == object_id

		record = scheme.task[record_name][record_index]
		before = (getattr(record, x_field), getattr(record, y_field))
		_drag(context.canvas, start, (start[0] + 10, start[1] + 6))

		assert getattr(record, x_field) == pytest.approx(before[0] + 10)
		assert getattr(record, y_field) == pytest.approx(before[1] + 6)
	finally:
		context.window.close()
		context.app.processEvents()


def test_torsion_action_label_reuses_shared_persisted_offset():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "axial-torsion", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		scheme.task_subtype.set(1)
		node = scheme.task["betsect"][0]
		node.Mkr = "+"
		node.T = "M"
		context.app.processEvents()
		context.canvas.make_image()

		object_id = "node/0/torque/text"
		start = _device_center(context.canvas.scene_interaction, object_id)
		_hover(context.canvas, start)
		_drag(context.canvas, start, (start[0] - 9, start[1] + 5))

		assert node.action_text_offset_x == pytest.approx(-9)
		assert node.action_text_offset_y == pytest.approx(5)
		document = context.storage.to_data()
		context.storage.load_data(document)
		restored = context.controller.current_scheme.task["betsect"][0]
		assert restored.action_text_offset_x == pytest.approx(-9)
		assert restored.action_text_offset_y == pytest.approx(5)
	finally:
		context.window.close()
		context.app.processEvents()


def test_rod_system_1_force_label_uses_shared_drag_controller():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "rod-system-1", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		node = scheme.task["betsect"][0]
		node.F = "+"
		node.Ftxt = "P"
		context.app.processEvents()
		context.canvas.make_image()

		object_id = "force/0/text"
		start = _device_center(context.canvas.scene_interaction, object_id)
		_hover(context.canvas, start)
		assert context.canvas.selected_label_id == object_id
		_drag(context.canvas, start, (start[0] + 11, start[1] - 7))

		assert node.force_text_offset_x == pytest.approx(11)
		assert node.force_text_offset_y == pytest.approx(-7)
		document = context.storage.to_data()
		context.storage.load_data(document)
		restored = context.controller.current_scheme.task["betsect"][0]
		assert restored.force_text_offset_x == pytest.approx(11)
		assert restored.force_text_offset_y == pytest.approx(-7)
	finally:
		context.window.close()
		context.app.processEvents()


def test_oblique_bending_moment_label_uses_shared_drag_controller():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "oblique-bending", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		node = scheme.task["betsect"][0]
		node.xM = "+"
		node.xMtxt = "M"
		context.app.processEvents()
		context.canvas.make_image()

		object_id = "node/0/moment-x/text"
		start = _device_center(context.canvas.scene_interaction, object_id)
		_hover(context.canvas, start)
		assert context.canvas.selected_label_id == object_id
		_drag(context.canvas, start, (start[0] - 8, start[1] + 9))

		assert node.x_moment_text_offset_x == pytest.approx(-8)
		assert node.x_moment_text_offset_y == pytest.approx(9)
	finally:
		context.window.close()
		context.app.processEvents()


def test_eccentric_bending_force_label_uses_shared_drag_controller():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "eccentric-bending", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		record = scheme.task["sections"][0]
		record.Fx = "справа +"
		record.Fx_txt = "F"
		context.app.processEvents()
		context.canvas.make_image()

		object_id = "point/0/force-x/text"
		start = _device_center(context.canvas.scene_interaction, object_id)
		_hover(context.canvas, start)
		assert context.canvas.selected_label_id == object_id
		_drag(context.canvas, start, (start[0] + 7, start[1] + 5))

		assert record.fx_text_offset_x == pytest.approx(7)
		assert record.fx_text_offset_y == pytest.approx(5)
	finally:
		context.window.close()
		context.app.processEvents()


def test_rod_system_2_force_label_drag_does_not_start_member_creation():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "rod-system-2", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		section = scheme.confwidget.sect(force="от", ftxt="P", angle=0)
		scheme.task["sections"].append(section)
		context.app.processEvents()
		context.canvas.make_image()

		object_id = "section/0/force/text"
		start = _device_center(context.canvas.scene_interaction, object_id)
		_hover(context.canvas, start)
		assert context.canvas.selected_label_id == object_id
		_drag(context.canvas, start, (start[0] + 12, start[1] - 6))

		assert section.force_text_offset_x == pytest.approx(12)
		assert section.force_text_offset_y == pytest.approx(-6)
		assert len(scheme.task["sections"]) == 1
	finally:
		context.window.close()
		context.app.processEvents()


def test_frames_member_label_drag_does_not_start_grid_member_creation():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "frames", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		context.app.processEvents()
		context.canvas.make_image()

		section = scheme.task["sections"][0]
		object_id = "member/0/text"
		start = _device_center(context.canvas.scene_interaction, object_id)
		_hover(context.canvas, start)
		assert context.canvas.selected_label_id == object_id
		_drag(context.canvas, start, (start[0] - 9, start[1] + 8))

		assert section.member_text_offset_x == pytest.approx(-9)
		assert section.member_text_offset_y == pytest.approx(8)
		assert len(scheme.task["sections"]) == 3
	finally:
		context.window.close()
		context.app.processEvents()


def test_spatial_beams_label_text_can_be_edited_by_double_click(monkeypatch):
	context = create_runtime(
		build_parser().parse_args(
			["--type", "spatial-beams", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		label = scheme.confwidget.label("before", (10, 20))
		scheme.task["labels"].append(label)
		context.app.processEvents()
		context.canvas.make_image()

		monkeypatch.setattr(
			"tasks.spatial_beams.QInputDialog.getText",
			lambda *args, **kwargs: ("after", True),
		)
		start = _device_center(context.canvas.scene_interaction, "label/0")
		context.canvas.mouseDoubleClickEvent(
			_mouse_event(
				QEvent.MouseButtonDblClick,
				start,
				button=Qt.LeftButton,
				buttons=Qt.LeftButton,
			)
		)

		assert label.text == "after"
		assert context.canvas.selected_label_id == 0
	finally:
		context.window.close()
		context.app.processEvents()


def test_shafts_pipes_force_label_uses_shared_persisted_drag_offset():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "shafts-pipes", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		scheme.uncentered_force.set("-")
		context.app.processEvents()
		context.canvas.make_image()

		record = scheme.task["sections"][0]
		object_id = "force/left/label"
		start = _device_center(context.canvas.scene_interaction, object_id)
		_hover(context.canvas, start)
		assert context.canvas.selected_label_id == object_id
		_drag(context.canvas, start, (start[0] + 8, start[1] - 6))

		assert record.force_left_text_offset_x == pytest.approx(8)
		assert record.force_left_text_offset_y == pytest.approx(-6)
		document = context.storage.to_data()
		context.storage.load_data(document)
		restored = context.controller.current_scheme.task["sections"][0]
		assert restored.force_left_text_offset_x == pytest.approx(8)
		assert restored.force_left_text_offset_y == pytest.approx(-6)
	finally:
		context.window.close()
		context.app.processEvents()
