from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.shafts_pipes import (
	ShaftsPipesLayoutBuilder,
	ShaftsPipesLayoutSettings,
)
from sopr_scheme_gener.scene import SceneIndex, TextMeasurement


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(len(text) * 8, 20, 15, 5)


def _section(diameter=40, text="d"):
	return {"D": diameter, "Dtext": text}


def _build(sections=None, **changes):
	return ShaftsPipesLayoutBuilder().build(
		{"sections": sections or [_section()]},
		ShaftsPipesLayoutSettings(**changes),
		FixedTextMetrics(),
	)


def test_default_shafts_scene_exposes_pipe_camera_and_dimensions():
	scene = _build()
	index = SceneIndex(scene, FixedTextMetrics())

	assert scene.viewport.width == 512
	assert scene.viewport.height == 213
	assert index.get("section/main/upper-wall") is not None
	assert index.get("section/main/diameter-label") is not None
	assert index.get("camera/upper") is not None
	assert index.get("dimension/thickness/label") is not None
	assert index.get("viewport-border") is not None


def test_central_shaft_uses_three_sections_and_validates_record_count():
	scene = _build(
		[_section(40, "d"), _section(30, "d_1")],
		has_central=True,
	)
	index = SceneIndex(scene, FixedTextMetrics())

	assert index.get("section/left/body") is not None
	assert index.get("section/central/upper-wall") is not None
	assert index.get("section/right/body") is not None

	with pytest.raises(ValueError, match="2 section"):
		_build([_section()], has_central=True)


@pytest.mark.parametrize("end_type", ["труба", "камера", "разрез"])
def test_shafts_support_every_end_type(end_type):
	scene = _build(end_type=end_type)
	assert scene.objects


@pytest.mark.parametrize("bending_style", ["круговой", "угловой"])
def test_shafts_feature_scene_contains_forces_and_moments(bending_style):
	scene = _build(
		force_direction="-",
		torque_direction="+",
		bending_direction="-",
		bending_style=bending_style,
		length_text="L",
	)
	index = SceneIndex(scene, FixedTextMetrics())

	assert index.get("force/left") is not None
	assert index.get("force/right") is not None
	assert index.get("torque/left-label") is not None
	assert index.get("bending/left") is not None
	assert index.get("dimension/length") is not None


def test_shafts_widget_has_no_subject_legacy_painting():
	root = Path(__file__).resolve().parents[1]
	layout = (
		root / "sopr_scheme_gener" / "layouts" / "shafts_pipes.py"
	).read_text(encoding="utf-8")
	widget = (root / "tasks" / "vali.py").read_text(encoding="utf-8")

	assert "PyQt" not in layout
	assert "QPainter" not in layout
	assert "QGraphicsScene" not in layout
	for forbidden in (
		"self.scene.add",
		"self.painter.draw",
		"items.arrow",
		"items.circmoment",
		"items.squaremoment",
	):
		assert forbidden not in widget
