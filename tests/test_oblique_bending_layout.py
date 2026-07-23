from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.oblique_bending import (
	ObliqueBendingLayoutBuilder,
	ObliqueBendingLayoutSettings,
)
from sopr_scheme_gener.scene import Rect, SceneIndex, TextMeasurement


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(len(text) * 8, 20, 15, 5)


def _section(length=1):
	return {"l": length}


def _node(**changes):
	record = {
		"xF": "нет",
		"xFtxt": "",
		"yF": "нет",
		"yFtxt": "",
		"xM": "нет",
		"xMtxt": "",
		"yM": "нет",
		"yMtxt": "",
		"xS": "нет",
		"yS": "нет",
		"zS": "нет",
	}
	record.update(changes)
	return record


def _load(**changes):
	record = {"xF": "нет", "xFtxt": "", "yF": "нет", "yFtxt": ""}
	record.update(changes)
	return record


def _task():
	return {
		"sections": [_section(1), _section(2)],
		"betsect": [_node(), _node(), _node()],
		"sectforce": [_load(), _load()],
	}


def _build(task, **changes):
	return ObliqueBendingLayoutBuilder().build(
		task,
		ObliqueBendingLayoutSettings(400, 250, **changes),
		FixedTextMetrics(),
	)


def test_default_oblique_bending_has_stable_scene_objects():
	scene = _build(_task())
	index = SceneIndex(scene, FixedTextMetrics())

	assert scene.viewport == Rect(0, 0, 400, 250)
	assert index.get("console").metadata_value("kind") == "console"
	assert index.get("section/0/dimension").metadata_value("kind") == "dimension"
	assert index.get("section/1/dimension/text") is not None
	assert index.get("rod/axis").metadata_value("kind") == "rod"


def test_oblique_bending_covers_forces_moments_loads_supports_and_projection_modes():
	task = _task()
	task["betsect"] = [
		_node(
			xF="+1",
			xFtxt="Fx0",
			yF="-2",
			yFtxt="Fy0",
			xM="+",
			xMtxt="Mx0",
			yM="-",
			yMtxt="My0",
			xS="+1",
			yS="-2",
			zS="+1",
		),
		_node(
			xF="-1",
			yF="+2",
			xM="-",
			yM="+",
			xS="-2",
			yS="+1",
			zS="-2",
		),
		_node(xF="+2", yF="-1", xS="+2", yS="+2", zS="+2"),
	]
	task["sectforce"] = [
		_load(xF="+", xFtxt="qx", yF="-", yFtxt="qy"),
		_load(xF="-", yF="+"),
	]
	scene = _build(
		task,
		axonometric=True,
		forty_five_degrees=True,
		console_enabled=False,
	)
	index = SceneIndex(scene, FixedTextMetrics())

	assert index.get("console") is None
	assert index.get("node/0/force-x").metadata_value("kind") == "force"
	assert index.get("node/0/force-y").metadata_value("axis") == "y"
	assert index.get("node/0/moment-x").metadata_value("kind") == "moment"
	assert index.get("node/1/moment-y").metadata_value("direction") == "+"
	assert index.get("section/0/distributed-x").metadata_value("direction") == "+"
	assert index.get("section/0/distributed-y").metadata_value("direction") == "-"
	for axis in ("x", "y", "z"):
		assert index.get("node/0/support-{}".format(axis)) is not None


def test_oblique_bending_rejects_inconsistent_documents():
	task = _task()
	task["betsect"].pop()
	with pytest.raises(ValueError, match="inconsistent"):
		_build(task)


def test_oblique_bending_widget_has_no_subject_legacy_painting():
	root = Path(__file__).resolve().parents[1]
	layout = (
		root / "sopr_scheme_gener" / "layouts" / "oblique_bending.py"
	).read_text(encoding="utf-8")
	widget = (root / "tasks" / "ar3d2.py").read_text(encoding="utf-8")

	assert "PyQt" not in layout
	assert "QPainter" not in layout
	assert "paintool" not in layout
	for forbidden in (
		"self.painter.draw",
		"paintool.common_arrow",
		"paintool.draw_dimlines",
		"elements.draw_",
	):
		assert forbidden not in widget
