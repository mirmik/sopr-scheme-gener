from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.plate import PlateLayoutBuilder, PlateLayoutSettings
from sopr_scheme_gener.scene import Group, Rect, SceneIndex, TextMeasurement


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(len(text) * 8, 20, 15, 5)


def _task():
	return {
		"sections": [
			{"d": 1.5, "h": 2, "shtrih": False, "intgran": True, "dtext": "", "htext": "", "dtext_en": True, "htext_en": True},
			{"d": 3, "h": 2, "shtrih": True, "intgran": False, "dtext": "", "htext": "", "dtext_en": True, "htext_en": True},
			{"d": 4.5, "h": 1, "shtrih": True, "intgran": True, "dtext": "", "htext": "", "dtext_en": True, "htext_en": True},
		],
		"sectforce": [{"distrib": False}, {"distrib": False}, {"distrib": False}],
		"betsect": [
			{"fen": "нет", "men": "нет", "sharn": "нет"},
			{"fen": "нет", "men": "нет", "sharn": "нет"},
			{"fen": "нет", "men": "нет", "sharn": "нет"},
		],
		"labels": [],
	}


def test_default_plate_layout_has_stable_semantic_objects():
	scene = PlateLayoutBuilder().build(
		_task(),
		PlateLayoutSettings(400, 250, 125),
		FixedTextMetrics(),
		text_transform=lambda text: text.replace("\\diam", "ø"),
	)
	index = SceneIndex(scene, FixedTextMetrics())

	assert scene.viewport == Rect(0, 0, 400, 250)
	assert index.get("plate/section/0") is not None
	assert index.get("plate/section/1/hatch") is not None
	assert index.get("fixed-end/left") is not None
	assert index.get("fixed-end/right") is not None
	assert index.get("plate/axis") is not None
	assert all(
		index.get("dimension/{}/width".format(i)) is not None
		and index.get("dimension/{}/height".format(i)) is not None
		for i in range(3)
	)


def test_plate_layout_covers_load_moment_support_and_labels():
	task = _task()
	for load in task["sectforce"]:
		load["distrib"] = True
	for index, node in enumerate(task["betsect"]):
		node.update(
			{
				"fen": "+" if index % 2 else "-",
				"men": "-" if index % 2 else "+",
				"sharn": "1" if index % 2 else "2",
			}
		)
	task["labels"] = [{"text": "L", "pos": (0.1, -15)}]
	scene = PlateLayoutBuilder().build(
		task,
		PlateLayoutSettings(
			400,
			250,
			125,
			fixed_ends=False,
			axis=False,
		),
		FixedTextMetrics(),
	)
	index = SceneIndex(scene, FixedTextMetrics())

	assert index.get("load/1/right") is not None
	assert index.get("force/0") is not None
	assert index.get("moment/1/left") is not None
	assert index.get("support/0/right/2") is not None
	assert index.get("support/1/left/1") is not None
	assert index.get("label/0").metadata_value("kind") == "label"
	assert isinstance(index.get("moment/0/right").item, Group)


def test_plate_layout_rejects_inconsistent_documents():
	task = _task()
	task["betsect"].pop()

	with pytest.raises(ValueError, match="inconsistent"):
		PlateLayoutBuilder().build(
			task,
			PlateLayoutSettings(400, 250, 125),
			FixedTextMetrics(),
		)


def test_plate_layout_and_widget_have_no_legacy_painting_path():
	root = Path(__file__).resolve().parents[1]
	layout_source = (
		root / "sopr_scheme_gener" / "layouts" / "plate.py"
	).read_text(encoding="utf-8")
	widget_source = (root / "tasks" / "plate.py").read_text(encoding="utf-8")

	assert "PyQt" not in layout_source
	assert "QPainter" not in layout_source
	assert "paintool" not in layout_source
	for forbidden in (
		"paintool.dimlines",
		"paintool.draw_",
		"paintool.common_arrow",
		"SquareMomentItem",
		"self.draw_labels()",
	):
		assert forbidden not in widget_source
