from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.eccentric_bending import (
	EccentricBendingLayoutBuilder,
	EccentricBendingLayoutSettings,
)
from sopr_scheme_gener.scene import Rect, SceneIndex, TextMeasurement


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(len(text) * 8, 20, 15, 5)


def _record(**changes):
	record = {
		"Fx": "нет",
		"Fy": "нет",
		"Fz": "нет",
		"Fx_txt": "",
		"Fy_txt": "",
		"Fz_txt": "",
		"Fx_txt_alttxt": "1",
		"Fy_txt_alttxt": "1",
		"Fz_txt_alttxt": "1",
	}
	record.update(changes)
	return record


def _task():
	return {"sections": [_record() for _ in range(8)]}


def _build(task, **changes):
	return EccentricBendingLayoutBuilder().build(
		task,
		EccentricBendingLayoutSettings(400, 250, 125, **changes),
		FixedTextMetrics(),
	)


def test_default_eccentric_bending_has_stable_pipe_scene():
	scene = _build(_task())
	index = SceneIndex(scene, FixedTextMetrics())

	assert scene.viewport == Rect(0, 0, 400, 250)
	assert index.get("section/outer").metadata_value("kind") == "section"
	assert index.get("section/inner") is not None
	assert index.get("section/midline") is not None
	assert index.get("dimension/thickness").metadata_value("kind") == "dimension"
	assert index.get("dimension/length") is not None


@pytest.mark.parametrize("section_type", ["прямоугольник", "ромб", "круг", "труба"])
def test_eccentric_bending_renders_every_section_type(section_type):
	scene = _build(_task(), section_type=section_type, axonometric=True)
	index = SceneIndex(scene, FixedTextMetrics())

	assert index.get("section/outer") is not None
	if section_type == "труба":
		assert index.get("section/inner") is not None


def test_eccentric_bending_covers_force_axes_directions_and_text_policies():
	task = _task()
	task["sections"][0] = _record(
		Fx="справа +",
		Fx_txt="Fx0",
		Fx_txt_alttxt="1",
		Fy="сверху -",
		Fy_txt="Fy0",
		Fy_txt_alttxt="5",
		Fz="+",
		Fz_txt="Fz0",
		Fz_txt_alttxt="6",
	)
	task["sections"][1] = _record(
		Fx="слева -",
		Fx_txt="Fx1",
		Fx_txt_alttxt="4",
		Fy="снизу +",
		Fy_txt="Fy1",
		Fy_txt_alttxt="2",
		Fz="-",
		Fz_txt="Fz1",
		Fz_txt_alttxt="3",
	)
	scene = _build(task)
	index = SceneIndex(scene, FixedTextMetrics())

	for point in (0, 1):
		for axis in ("x", "y", "z"):
			assert index.get("point/{}/force-{}".format(point, axis)) is not None
	assert index.get("point/0/force-y").metadata_value("policy") == "5"
	assert index.get("point/0/force-z").metadata_value("policy") == "6"


def test_eccentric_bending_rejects_wrong_force_point_count():
	with pytest.raises(ValueError, match="eight"):
		_build({"sections": [_record()]})


def test_eccentric_bending_widget_has_no_subject_legacy_painting():
	root = Path(__file__).resolve().parents[1]
	layout = (
		root / "sopr_scheme_gener" / "layouts" / "eccentric_bending.py"
	).read_text(encoding="utf-8")
	widget = (root / "tasks" / "eccentric_bending.py").read_text(
		encoding="utf-8"
	)

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
