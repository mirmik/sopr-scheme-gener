from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.rod_system_2 import (
	RodSystem2LayoutBuilder,
	RodSystem2LayoutSettings,
)
from sopr_scheme_gener.scene import Group, Point, Rect, SceneIndex, TextMeasurement


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(len(text) * 8, 20, 15, 5)


def _section(**changes):
	record = {
		"start_from": -1,
		"l": 1,
		"A": 1,
		"angle": 0,
		"sharn": "шарн+заделка",
		"body": True,
		"force": "нет",
		"ftxt": "",
		"alttxt": False,
		"addangle": 0,
		"wide": False,
	}
	record.update(changes)
	return record


def _index(scene):
	return SceneIndex(scene, FixedTextMetrics())


def test_empty_rod_system_2_layout_has_stable_root_node():
	scene = RodSystem2LayoutBuilder().build(
		{"sections": []},
		RodSystem2LayoutSettings(400, 250, 125),
		FixedTextMetrics(),
	)
	index = _index(scene)

	assert scene.viewport == Rect(0, 0, 400, 250)
	assert index.get("node/0").metadata_value("kind") == "node"
	assert index.get("node/0/visible") is not None
	assert index.get("section/0/body") is None


def test_rod_system_2_layout_covers_branching_feature_matrix():
	task = {
		"sections": [
			_section(force="от", ftxt="F0", addangle=30),
			_section(
				start_from=0,
				l=1.2,
				A=2,
				angle=60,
				sharn="шарн",
				force="к",
				ftxt="F1",
				alttxt=True,
				addangle=-30,
			),
			_section(
				start_from=0,
				l=0.8,
				A=3,
				angle=-45,
				sharn="нет",
				force="вдоль",
				ftxt="q",
				wide=True,
			),
			_section(
				start_from=1,
				angle=120,
				sharn="нет",
				body=False,
				force="от",
				ftxt="P",
			),
		]
	}
	scene = RodSystem2LayoutBuilder().build(
		task,
		RodSystem2LayoutSettings(
			400,
			250,
			125,
			highlighted_section=1,
			hovered_node=2,
		),
		FixedTextMetrics(),
		text_transform=lambda value: value.replace("\\degree", "°"),
	)
	index = _index(scene)

	assert index.get("section/0/angle") is not None
	assert index.get("section/1/body").metadata_value("kind") == "section"
	assert index.get("section/0/fixed-end") is not None
	assert index.get("section/1/end-joint") is not None
	assert index.get("section/2/body").item.children[1:]
	assert index.get("section/0/force").metadata_value("direction") == "от"
	assert index.get("section/1/force").metadata_value("direction") == "к"
	assert index.get("section/2/force").metadata_value("direction") == "вдоль"
	assert index.get("section/3/body") is None
	assert index.get("section/3/force") is not None
	assert index.get("node/2/hover") is not None
	assert index.get("node/4").metadata_value("kind") == "geometry-node"
	assert isinstance(index.get("section/2/body").item, Group)
	assert index.get("section/2/body").item.antialias is False


def test_rod_system_2_layout_includes_scene_preview():
	scene = RodSystem2LayoutBuilder().build(
		{"sections": [_section()]},
		RodSystem2LayoutSettings(
			400,
			250,
			125,
			preview_start_node=1,
			preview_target=Point(300, 100),
		),
		FixedTextMetrics(),
	)
	index = _index(scene)

	assert index.get("preview").metadata_value("kind") == "preview"
	assert index.get("preview/length") is not None
	assert index.get("preview/angle/text") is not None


def test_rod_system_2_layout_rejects_invalid_graphs():
	with pytest.raises(ValueError, match="invalid start_from"):
		RodSystem2LayoutBuilder().build(
			{"sections": [_section(start_from=0)]},
			RodSystem2LayoutSettings(400, 250, 125),
			FixedTextMetrics(),
		)


def test_rod_system_2_has_no_legacy_subject_painting_path():
	root = Path(__file__).resolve().parents[1]
	layout_source = (
		root / "sopr_scheme_gener" / "layouts" / "rod_system_2.py"
	).read_text(encoding="utf-8")
	widget_source = (root / "tasks" / "rod_system_2.py").read_text(
		encoding="utf-8"
	)

	assert "PyQt" not in layout_source
	assert "QPainter" not in layout_source
	assert "paintool" not in layout_source
	for forbidden in (
		"paintool.common_arrow",
		"paintool.draw_",
		"paintool.zadelka",
		"elements.draw_",
		"self.painter.draw",
	):
		assert forbidden not in widget_source
