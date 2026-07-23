from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.axial_torsion import (
	AXIAL,
	TORSION_DIAMETER,
	TORSION_STIFFNESS,
	AxialTorsionLayoutBuilder,
	AxialTorsionLayoutSettings,
)
from sopr_scheme_gener.scene import Rect, SceneIndex, TextMeasurement


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(len(text) * 8, 20, 15, 5)


def _section(**changes):
	record = {
		"A": 1,
		"GIk": 1,
		"d": 1,
		"l": 1,
		"E": 1,
		"text": "",
		"dtext": "",
		"delta": False,
		"label": "",
		"label_height": 20,
	}
	record.update(changes)
	return record


def _node(**changes):
	record = {
		"F": "нет",
		"Fstyle": "от узла",
		"Mkr": "нет",
		"T": "",
		"label": "",
		"label_up": False,
		"label_off": "справа",
	}
	record.update(changes)
	return record


def _load(**changes):
	record = {"mkr": "нет", "mkrT": "", "Fr": "нет"}
	record.update(changes)
	return record


def _task():
	return {
		"sections": [_section(), _section(A=2), _section(l=2)],
		"betsect": [_node(), _node(), _node(), _node()],
		"sectforce": [_load(), _load(), _load()],
	}


def _index(scene):
	return SceneIndex(scene, FixedTextMetrics())


def _build(task, subtype=AXIAL, **settings):
	return AxialTorsionLayoutBuilder().build(
		task,
		AxialTorsionLayoutSettings(
			400,
			250,
			125,
			subtype=subtype,
			**settings,
		),
		FixedTextMetrics(),
	)


def test_default_axial_layout_has_stable_semantic_objects():
	scene = _build(_task())
	index = _index(scene)

	assert scene.viewport == Rect(0, 0, 400, 250)
	assert index.get("section/0/body").metadata_value("kind") == "section"
	assert index.get("section/1/dimension").metadata_value("kind") == "dimension"
	assert index.get("section/2/body") is not None
	assert index.get("axis").metadata_value("kind") == "axis"


def test_axial_layout_covers_gaps_forces_loads_labels_fixed_ends_and_highlights():
	task = _task()
	task["sections"][1].update(text="custom", label="S1", label_height=-30)
	task["sections"][2]["delta"] = True
	task["betsect"] = [
		_node(F="+", Fstyle="от узла", T="P0", label="A"),
		_node(F="-", Fstyle="к узлу", T="P1", label="B", label_off="справа-сверху"),
		_node(F="+", Fstyle="выносн.", T="P2", label="C", label_off="слева-снизу"),
		_node(F="-", Fstyle="от узла", T="P3", label="D"),
	]
	task["sectforce"] = [
		_load(Fr="+", mkrT="q0"),
		_load(Fr="-", mkrT="q1"),
		_load(Fr="+", mkrT="q2"),
	]
	scene = _build(
		task,
		left_fixed=True,
		right_fixed=True,
		highlighted_section=1,
		highlighted_node=2,
	)
	index = _index(scene)

	assert index.get("section/2/body") is None
	assert index.get("node/0/force").metadata_value("kind") == "force-arrow"
	assert index.get("node/2/force").metadata_value("extended") is True
	assert index.get("section/0/distributed-force").metadata_value("direction") == "+"
	assert index.get("section/1/distributed-force").metadata_value("direction") == "-"
	assert index.get("node/1/label") is not None
	assert index.get("section/1/label") is not None
	assert index.get("node/2/highlight") is not None
	assert index.get("fixed-end/left") is not None
	assert index.get("fixed-end/right") is not None


def test_torsion_layout_covers_stiffness_torques_and_distributed_torques():
	task = _task()
	task["sections"][1].update(GIk=2.25, text="Gcustom")
	task["betsect"] = [
		_node(Mkr="+", T="M0"),
		_node(Mkr="-", T="M1"),
		_node(Mkr="+", T="M2"),
		_node(Mkr="-", T="M3"),
	]
	task["sectforce"] = [
		_load(mkr="+", mkrT="m0"),
		_load(mkr="-", mkrT="m1"),
		_load(mkr="+", mkrT="m2"),
	]
	scene = _build(task, TORSION_STIFFNESS)
	index = _index(scene)

	assert index.get("node/0/torque").metadata_value("direction") == "+"
	assert index.get("node/1/torque").metadata_value("direction") == "-"
	assert index.get("section/0/distributed-torque").metadata_value("direction") == "+"
	assert index.get("section/1/distributed-torque").metadata_value("direction") == "-"
	assert index.get("section/1/dimension/text") is not None


def test_diameter_torsion_layout_has_dimensions_and_accepts_fractional_geometry():
	task = _task()
	task["sections"] = [
		_section(d=1, l=0.7, dtext="d0"),
		_section(d=1.5, l=1.3, dtext="d1"),
		_section(d=0.8, l=1, dtext="d2"),
	]
	scene = _build(task, TORSION_DIAMETER)
	index = _index(scene)

	for section in range(3):
		assert (
			index.get("section/{}/diameter".format(section)).metadata_value("kind")
			== "diameter-dimension"
		)


def test_axial_torsion_layout_rejects_inconsistent_documents():
	task = _task()
	task["betsect"].pop()

	with pytest.raises(ValueError, match="inconsistent"):
		_build(task)


def test_axial_torsion_layout_and_widget_have_no_legacy_painting_path():
	root = Path(__file__).resolve().parents[1]
	layout_source = (
		root / "sopr_scheme_gener" / "layouts" / "axial_torsion.py"
	).read_text(encoding="utf-8")
	widget_source = (root / "tasks" / "task0.py").read_text(encoding="utf-8")

	assert "PyQt" not in layout_source
	assert "QPainter" not in layout_source
	assert "paintool" not in layout_source
	for forbidden in (
		"paintool.draw_",
		"paintool.raspred_",
		"paintool.zadelka",
		"elements.draw_",
		"self.painter.draw",
	):
		assert forbidden not in widget_source
