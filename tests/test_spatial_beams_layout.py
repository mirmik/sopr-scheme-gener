from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.spatial_beams import (
	SpatialBeamsLayoutBuilder,
	SpatialBeamsLayoutSettings,
)
from sopr_scheme_gener.scene import SceneIndex, TextMeasurement


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(len(text) * 8, 20, 15, 5)


def _node(x, y, z, **changes):
	node = {
		"x": x,
		"y": y,
		"z": z,
		"sharn": "нет",
		"sharn_vec": (0, 0, 0),
		"sharn_vec2": (0, 0, 0),
		"force_x": None,
		"force_y": None,
		"force_z": None,
		"torque": None,
	}
	node.update(changes)
	return node


def _section(ax, ay, az, bx, by, bz, distrib=None):
	return {
		"ax": ax,
		"ay": ay,
		"az": az,
		"bx": bx,
		"by": by,
		"bz": bz,
		"distrib": distrib,
	}


def _task():
	return {
		"sections": [
			_section(0, 0, 0, 0, -1, 0),
			_section(0, -1, 0, 1, -1, 0),
			_section(1, -1, 0, 1, -1, 1),
		],
		"nodes": [
			_node(0, 0, 0),
			_node(0, -1, 0),
			_node(1, -1, 0),
			_node(1, -1, 1),
		],
		"labels": [],
	}


def _build(task=None, **changes):
	return SpatialBeamsLayoutBuilder().build(
		task or _task(),
		SpatialBeamsLayoutSettings(**changes),
		FixedTextMetrics(),
	)


def test_default_spatial_beams_preserves_legacy_viewport_and_semantics():
	scene = _build()
	index = SceneIndex(scene, FixedTextMetrics())

	assert scene.viewport.width == pytest.approx(215.82133784004458)
	assert scene.viewport.height == pytest.approx(195.89604803732345)
	for section in range(3):
		assert index.get("section/{}/beam".format(section)) is not None
		assert index.get("section/{}/hit".format(section)).metadata_value(
			"kind"
		) == "section"
	for node in range(4):
		assert index.get("node/{}/hit".format(node)).metadata_value("kind") == "node"


def test_spatial_beams_builds_supports_loads_moments_and_labels():
	task = _task()
	task["sections"][0]["distrib"] = (0, 0, 1)
	task["nodes"][0].update(
		sharn="sharn",
		sharn_vec=(1, 0, 0),
		sharn_vec2=(0, 1, 0),
		force_x=((-0.1, 0, 0), (-1, 0, 0)),
		torque=((0, 1, 0), (0, 0, 1)),
	)
	task["labels"].append({"text": "F_x", "pos": (10, 20)})
	scene = _build(task)
	index = SceneIndex(scene, FixedTextMetrics())

	assert index.get("section/0/distributed") is not None
	assert index.get("node/0/support").metadata_value("kind") == "support"
	assert index.get("node/0/force-x") is not None
	assert index.get("node/0/torque").metadata_value("kind") == "moment"
	assert index.get("label/0").metadata_value("kind") == "label"


@pytest.mark.parametrize("support", ["врез", "sharn", "zadelka"])
def test_spatial_beams_supports_every_restraint_family(support):
	task = _task()
	task["nodes"][0].update(
		sharn=support,
		sharn_vec=(1, 0, 0),
		sharn_vec2=(0, 1, 0),
	)
	scene = _build(task)
	assert SceneIndex(scene, FixedTextMetrics()).get("node/0/support") is not None


def test_spatial_beams_exposes_candidates_for_interactive_construction():
	scene = _build(hovered_node=0, pressed=True)
	index = SceneIndex(scene, FixedTextMetrics())
	candidates = [
		entry
		for entry in index.entries
		if entry.metadata_value("kind") == "candidate"
	]

	assert len(candidates) == 5
	assert all(entry.metadata_value("x") is not None for entry in candidates)


def test_spatial_beams_widget_has_no_subject_legacy_painting():
	root = Path(__file__).resolve().parents[1]
	layout = (
		root / "sopr_scheme_gener" / "layouts" / "spatial_beams.py"
	).read_text(encoding="utf-8")
	widget = (root / "tasks" / "balki3d.py").read_text(encoding="utf-8")

	assert "PyQt" not in layout
	assert "QPainter" not in layout
	assert "QGraphicsScene" not in layout
	for forbidden in (
		"self.scene.add",
		"self.painter.draw",
		"Projector",
		"Sharn3dItem",
		"Torque3dItem",
		"DistribArrowsItem",
		"SectionItem",
	):
		assert forbidden not in widget
