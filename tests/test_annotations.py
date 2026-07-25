import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5.QtCore import QEvent, QPointF, Qt
from PyQt5.QtGui import QMouseEvent

import paintwdg
from sopr_scheme_gener.app import build_parser, create_runtime


@pytest.fixture
def context():
	runtime = create_runtime(build_parser().parse_args(["--no-maximize"]))
	try:
		yield runtime
	finally:
		runtime.window.close()


def test_free_annotations_round_trip_and_render_for_every_new_canvas(context):
	covered = []
	for spec in context.task_specs:
		context.controller.select(spec.identifier)
		canvas = context.canvas
		if canvas._uses_legacy_free_labels():
			continue

		before = canvas.make_image()
		canvas.create_annotation(QPointF(120, 80), "{} label".format(spec.identifier))
		assert context.controller.current_scheme.task["annotations"] == [
			{
				"text": "{} label".format(spec.identifier),
				"pos": [120.0, 80.0],
			}
		]

		document = context.storage.to_data()
		context.storage.load_data(document)
		context.app.processEvents()

		assert context.controller.current_scheme.task["annotations"] == [
			{
				"text": "{} label".format(spec.identifier),
				"pos": [120.0, 80.0],
			}
		]
		after = context.canvas.make_image()
		assert not after.isNull()
		assert after != before
		covered.append(spec.identifier)

	assert set(covered) == {
		"axial-torsion",
		"rod-system-1",
		"rod-system-2",
		"frames",
		"oblique-bending",
		"eccentric-bending",
		"stress-cube",
		"shafts-pipes",
		"column-stability",
	}


def test_right_click_create_action_reaches_every_new_canvas(context, monkeypatch):
	def trigger_first_action(menu, global_pos):
		menu.actions()[0].trigger()

	monkeypatch.setattr(paintwdg.QMenu, "popup", trigger_first_action)
	covered = []
	for spec in context.task_specs:
		context.controller.select(spec.identifier)
		canvas = context.canvas
		if canvas._uses_legacy_free_labels():
			continue
		event = QMouseEvent(
			QEvent.MouseButtonPress,
			QPointF(120, 80),
			Qt.RightButton,
			Qt.RightButton,
			Qt.NoModifier,
		)

		assert canvas.eventFilter(canvas, event)
		assert context.controller.current_scheme.task["annotations"] == [
			{"text": "Text", "pos": [120.0, 80.0]}
		]
		covered.append(spec.identifier)

	assert len(covered) == 9


def test_annotation_drag_clone_delete_and_page_layout_coordinates(context):
	context.controller.select("axial-torsion")
	canvas = context.canvas
	layout = canvas.activate_page_layout()
	device_point = QPointF(
		layout.task_frame.x + 100,
		layout.task_frame.y + 70,
	)

	canvas.create_annotation(QPointF(100, 70), "A")
	assert canvas._annotation_press(device_point)
	assert canvas._annotation_move(device_point + QPointF(15, -5))
	assert canvas._annotation_release()
	assert context.controller.current_scheme.task["annotations"][0]["pos"] == [
		115.0,
		65.0,
	]

	canvas.clone_annotation(QPointF(200, 100), 0)
	assert context.controller.current_scheme.task["annotations"][1] == {
		"text": "A",
		"pos": [230.0, 100.0],
	}

	canvas.delete_annotation(0)
	assert context.controller.current_scheme.task["annotations"] == [
		{"text": "A", "pos": [230.0, 100.0]}
	]


@pytest.mark.parametrize("task_id", ["beams", "plate"])
def test_existing_free_labels_are_json_serializable(context, task_id):
	context.controller.select(task_id)
	scheme = context.controller.current_scheme
	scheme.task["labels"].append(scheme.confwidget.label("legacy", (0.25, 10)))

	document = context.storage.to_data()
	context.storage.load_data(document)
	label = context.controller.current_scheme.task["labels"][0]

	assert label.text == "legacy"
	assert label.pos == (0.25, 10)
