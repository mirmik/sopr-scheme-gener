from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.rod_system_1 import (
	RodSystem1LayoutBuilder,
	RodSystem1LayoutSettings,
)
from sopr_scheme_gener.scene import Group, Rect, SceneIndex, TextMeasurement


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(len(text) * 8, 20, 15, 5)


def _task():
	return {
		"sections": [
			{"l": 1.5, "label": "", "label_height": 20, "dims": True},
			{"l": 1, "label": "", "label_height": 20, "dims": True},
			{"l": 1, "label": "", "label_height": 20, "dims": True},
		],
		"betsect": [
			{"l": 0, "A": 1, "F": "нет", "F2": "нет", "sharn": "нет"},
			{"l": 1, "A": 1, "F": "нет", "F2": "нет", "sharn": "нет"},
			{"l": 2, "A": 1, "F": "+", "F2": "нет", "sharn": "нет"},
			{"l": -2, "A": 1, "F": "нет", "F2": "нет", "sharn": "нет"},
		],
	}


def _index(scene):
	return SceneIndex(scene, FixedTextMetrics())


def test_default_rod_system_1_layout_has_stable_semantic_objects():
	scene = RodSystem1LayoutBuilder().build(
		_task(),
		RodSystem1LayoutSettings(400, 250, 125),
		FixedTextMetrics(),
		length_text=lambda value, suffix="l": "{}{}".format(value, suffix),
	)
	index = _index(scene)

	assert scene.viewport == Rect(0, 0, 400, 250)
	assert index.get("base/body") is not None
	assert all(index.get("dimension/{}".format(i)) is not None for i in range(3))
	assert index.get("rod/1").metadata_value("kind") == "rod"
	assert index.get("rod/2/fixed-end") is not None
	assert index.get("rod/3/text/full") is not None
	assert index.get("force/2").metadata_value("direction") == "+"


def test_rod_system_1_layout_covers_configurable_features():
	task = {
		"sections": [
			{"l": 1, "label": "\\alpha", "label_height": 20, "dims": False},
			{"l": 2, "label": "B", "label_height": -30, "dims": True},
		],
		"betsect": [
			{
				"l": 0,
				"A": 1,
				"lbl": "N0",
				"F": "-",
				"Ftxt": "F0",
				"F2": "нет",
				"sharn": "1",
			},
			{
				"l": 1,
				"A": 2,
				"lbl": "R1",
				"F": "+",
				"Ftxt": "F1",
				"F2": "+",
				"F2txt": "Q1",
				"zazor": True,
				"zazor_txt": "\\Delta",
				"sharn": "2",
				"sterzn_text1": "upper",
				"sterzn_text2": "lower",
				"sterzn_text_horizontal": False,
				"sterzn_text_alt": True,
				"sterzn_text_off": 3,
			},
			{
				"l": -1,
				"A": 3,
				"lbl": "R2",
				"F": "-",
				"Ftxt": "F2",
				"F2": "-",
				"F2txt": "Q2",
				"zazor": False,
				"sharn": "нет",
				"sterzn_text_horizontal": True,
				"sterzn_text_alt": False,
			},
		],
	}
	scene = RodSystem1LayoutBuilder().build(
		task,
		RodSystem1LayoutSettings(
			400,
			250,
			125,
			left_support="1",
			right_support="2",
			highlighted_node=1,
		),
		FixedTextMetrics(),
		text_transform=lambda value: value.replace("\\alpha", "α").replace(
			"\\Delta", "Δ"
		),
	)
	index = _index(scene)

	assert index.get("dimension/0") is None
	assert index.get("dimension/1") is not None
	assert index.get("section/0/label") is not None
	assert index.get("node/0/label") is not None
	assert index.get("node/0/support").metadata_value("support_type") == "1"
	assert index.get("node/1/support").metadata_value("support_type") == "2"
	assert index.get("rod/1/gap/text") is not None
	assert index.get("rod/1/text/first") is not None
	assert index.get("rod/1/text/second") is not None
	assert index.get("rod-force/1").metadata_value("direction") == "+"
	assert index.get("rod-force/2").metadata_value("direction") == "-"
	assert index.get("endpoint/left/support") is not None
	assert index.get("endpoint/right/support") is not None
	assert isinstance(index.get("rod/2").item, Group)
	assert index.get("rod/2").item.antialias is False


def test_rod_system_1_layout_rejects_inconsistent_documents():
	task = _task()
	task["betsect"].pop()

	with pytest.raises(ValueError, match="inconsistent"):
		RodSystem1LayoutBuilder().build(
			task,
			RodSystem1LayoutSettings(400, 250, 125),
			FixedTextMetrics(),
		)


def test_rod_system_1_has_no_legacy_subject_painting_path():
	root = Path(__file__).resolve().parents[1]
	layout_source = (
		root / "sopr_scheme_gener" / "layouts" / "rod_system_1.py"
	).read_text(encoding="utf-8")
	widget_source = (root / "tasks" / "sharn_sterhen.py").read_text(
		encoding="utf-8"
	)

	assert "PyQt" not in layout_source
	assert "QPainter" not in layout_source
	assert "paintool" not in layout_source
	for forbidden in (
		"paintool.dimlines",
		"paintool.draw_",
		"paintool.common_arrow",
		"paintool.zadelka",
		"elements.draw_",
		"self.painter.draw",
	):
		assert forbidden not in widget_source
