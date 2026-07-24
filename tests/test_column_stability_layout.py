from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.column_stability import (
	ColumnStabilityLayoutBuilder,
	ColumnStabilityLayoutSettings,
)
from sopr_scheme_gener.scene import SceneIndex, TextMeasurement


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(len(text) * 8, 20, 15, 5)


def _build(task):
	return ColumnStabilityLayoutBuilder().build(
		task,
		ColumnStabilityLayoutSettings(),
		FixedTextMetrics(),
	)


def test_reference_like_scene_has_segments_loads_labels_and_floating_clamp():
	scene = _build(
		{
			"segments": [
				{"length": 1, "length_text": "l", "rigidity_text": ""},
				{"length": 1, "length_text": "l", "rigidity_text": "EJ_min"},
			],
			"nodes": [
				{"support": "fixed", "load": "none", "load_text": ""},
				{
					"support": "floating-clamp",
					"load": "none",
					"load_text": "",
				},
				{"support": "none", "load": "down", "load_text": "F"},
			],
		}
	)
	index = SceneIndex(scene, FixedTextMetrics())

	assert index.get("segment/0/body") is not None
	assert index.get("segment/1/rigidity-label") is not None
	assert dict(index.get("node/1/support").item.metadata)["support"] == (
		"floating-clamp"
	)
	assert index.get("node/2/load") is not None
	assert index.get("node/2/load-label") is not None


@pytest.mark.parametrize(
	"support",
	[
		"заделка",
		"шарнир",
		"боковая тяга слева",
		"боковая тяга справа",
		"плавающая заделка",
	],
)
def test_all_editor_support_types_render(support):
	scene = _build(
		{
			"segments": [{"length": 1, "length_text": "l", "rigidity_text": ""}],
			"nodes": [
				{"support": "нет", "load": "нет", "load_text": ""},
				{"support": support, "load": "нет", "load_text": ""},
			],
		}
	)
	assert SceneIndex(scene, FixedTextMetrics()).get("node/1/support") is not None


def test_layout_rejects_broken_composition():
	with pytest.raises(ValueError, match="one more node"):
		_build(
			{
				"segments": [{"length": 1}],
				"nodes": [{"support": "нет"}],
			}
		)
	with pytest.raises(ValueError, match="positive"):
		_build(
			{
				"segments": [{"length": 0}],
				"nodes": [{"support": "нет"}, {"support": "нет"}],
			}
		)


def test_layout_and_widget_have_no_subject_legacy_painting():
	root = Path(__file__).resolve().parents[1]
	layout = (root / "sopr_scheme_gener/layouts/column_stability.py").read_text(
		encoding="utf-8"
	)
	widget = (root / "tasks/column_stability.py").read_text(encoding="utf-8")

	assert "PyQt" not in layout
	assert "QPainter" not in layout
	for forbidden in ("self.painter.draw", "paintool.draw", "items."):
		assert forbidden not in widget
