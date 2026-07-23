from pathlib import Path

from sopr_scheme_gener.layouts.beams import (
	BeamLayoutBuilder,
	BeamLayoutSettings,
	supports_scene_layout,
)
from sopr_scheme_gener.scene import Group, Rect, Rectangle, Text


def _task():
	return {
		"sections": [{"l": 1}, {"l": 1}, {"l": 2}],
		"betsect": [
			{"sharn": "1"},
			{"sharn": "Нет"},
			{"sharn": "2"},
			{"sharn": "Нет"},
		],
		"sectforce": [
			{"Fr": "Нет"},
			{"Fr": "Нет"},
			{"Fr": "+", "FrT": "ql"},
		],
		"labels": [],
	}


def test_default_beam_layout_has_stable_semantic_objects():
	settings = BeamLayoutSettings(width=400, height=250, hcenter=125)
	scene = BeamLayoutBuilder().build(_task(), settings)
	by_id = {item.object_id: item for item in scene.walk() if item.object_id}

	assert scene.viewport == Rect(0, 0, 400, 250)
	assert isinstance(by_id["beam/body"], Rectangle)
	assert isinstance(by_id["load/2"], Group)
	assert isinstance(by_id["load/2/text"], Text)
	assert isinstance(by_id["support/0"], Group)
	assert isinstance(by_id["support/2"], Group)
	assert all("dimension/{}".format(index) in by_id for index in range(3))
	assert len(by_id) == len(set(by_id))


def test_beam_layout_rejects_inconsistent_arrays():
	task = _task()
	task["sectforce"] = task["sectforce"][:-1]
	settings = BeamLayoutSettings(width=400, height=250, hcenter=125)

	try:
		BeamLayoutBuilder().build(task, settings)
	except ValueError as error:
		assert "inconsistent lengths" in str(error)
	else:
		raise AssertionError("inconsistent task must fail")


def test_scene_support_predicate_keeps_unmigrated_features_on_legacy_path():
	settings = BeamLayoutSettings(width=400, height=250, hcenter=125)
	assert supports_scene_layout(_task(), settings)

	with_force = _task()
	with_force["betsect"][1]["F"] = "+"
	assert supports_scene_layout(with_force, settings)
	assert not supports_scene_layout(_task(), settings, section_type="Прямоугольник")
	assert supports_scene_layout(_task(), settings, extra_text="note")
	with_label = _task()
	with_label["labels"] = [{"text": "A", "pos": (0.1, -20)}]
	assert supports_scene_layout(with_label, settings)


def test_beam_layout_covers_local_actions_names_and_endpoint_nodes():
	task = _task()
	task["betsect"][0].update({"F": "влево", "FT": "H"})
	task["betsect"][1].update({"F": "+", "FT": "F", "M": "+", "MT": "M"})
	task["betsect"][2]["sectname"] = "B"
	settings = BeamLayoutSettings(
		width=400,
		height=250,
		hcenter=125,
		left_node="Заделка",
		right_node="Шарнир",
	)

	scene = BeamLayoutBuilder().build(task, settings)
	by_id = {item.object_id: item for item in scene.walk() if item.object_id}

	assert "force/0" in by_id
	assert "force/1" in by_id
	assert "moment/1" in by_id
	assert "moment/1/text" in by_id
	assert "node/2/name" in by_id
	assert "endpoint/left" in by_id
	assert "endpoint/right" in by_id


def test_beam_layout_includes_interactive_labels_in_scene():
	task = _task()
	task["labels"] = [{"text": "A", "pos": (0.1, -20)}]
	settings = BeamLayoutSettings(width=400, height=250, hcenter=125)

	scene = BeamLayoutBuilder().build(task, settings)
	by_id = {item.object_id: item for item in scene.walk() if item.object_id}

	assert by_id["label/0"].position.x == 236
	assert by_id["label/0"].position.y == 105


def test_beam_layout_source_does_not_import_qt_or_legacy_painting():
	source = (
		Path(__file__).resolve().parents[1]
		/ "sopr_scheme_gener"
		/ "layouts"
		/ "beams.py"
	).read_text(encoding="utf-8")

	assert "PyQt" not in source
	assert "QPainter" not in source
	assert "paintool" not in source
