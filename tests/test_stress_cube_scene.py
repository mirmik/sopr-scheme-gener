from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.stress_cube import (
	Projection,
	StressCubeLayoutBuilder,
	StressCubeLayoutSettings,
)
from sopr_scheme_gener.scene import Group, SceneIndex, Text, TextMeasurement


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(
			width=len(text) * 8,
			height=20,
			ascent=15,
			descent=5,
		)


def _task(second=False):
	sections = [
		{"qx": "+", "qy": "-", "qz": "+", "mx": "-", "my": "+", "mz": "-"}
	]
	if second:
		sections.append(
			{"qx": "-", "qy": "+", "qz": "-", "mx": "+", "my": "-", "mz": "+"}
		)
	return {
		"sections": sections,
		"labels": [
			{
				"text": name,
				"x": index,
				"y": -index,
				"text2": name + "2",
				"x2": -index,
				"y2": index,
			}
			for index, name in enumerate(("qx", "qy", "qz", "mx", "my", "mz"))
		],
	}


def test_projection_preserves_historical_isometric_mapping():
	projection = Projection(
		yaw_degrees=20,
		pitch_degrees=40,
		z_scale=0.6,
		axonom=False,
	)

	point = projection(50, -50, -50)

	assert point.x == pytest.approx(72.98133329356934)
	assert point.y == pytest.approx(30.716371709403823)


def test_layout_exposes_stable_objects_and_interaction_bounds_without_qt():
	scene = StressCubeLayoutBuilder().build(
		_task(second=True),
		StressCubeLayoutSettings(
			second_cube=True,
			note="line 1\nline 2",
		),
		text_metrics=FixedTextMetrics(),
		text_transform=str.upper,
	)
	index = SceneIndex(scene, FixedTextMetrics())
	ids = {item.object_id for item in scene.walk() if item.object_id}
	label_ids = {
		entry.object_id
		for entry in index.entries
		if entry.metadata_value("kind") == "label"
	}

	assert "cube/0" in ids
	assert "cube/1" in ids
	assert "cube/0/stress/qx" in ids
	assert "cube/1/moment/mz/1" in ids
	assert "cube/1/label/mz" in ids
	assert label_ids == {
		"cube/{}/label/{}".format(cube, name)
		for cube in (0, 1)
		for name in ("qx", "qy", "qz", "mx", "my", "mz")
	}
	assert scene.viewport.width > scene.content_bounds.width
	assert scene.viewport.height >= scene.content_bounds.height
	assert sum(isinstance(item, Text) for item in scene.walk()) == 20
	assert all(
		not isinstance(item, Group) or isinstance(item.children, tuple)
		for item in scene.walk()
	)


def test_layout_rejects_inconsistent_documents():
	builder = StressCubeLayoutBuilder()
	task = _task()

	with pytest.raises(ValueError, match="second section"):
		builder.build(
			task,
			StressCubeLayoutSettings(second_cube=True),
			text_metrics=FixedTextMetrics(),
		)

	with pytest.raises(ValueError, match="six labels"):
		builder.build(
			{"sections": task["sections"], "labels": []},
			StressCubeLayoutSettings(),
			text_metrics=FixedTextMetrics(),
		)


def test_stress_cube_layout_source_does_not_import_qt():
	source = (
		Path(__file__).resolve().parents[1]
		/ "sopr_scheme_gener"
		/ "layouts"
		/ "stress_cube.py"
	).read_text(encoding="utf-8")

	assert "PyQt" not in source
	assert "QPainter" not in source
	assert "QGraphicsScene" not in source
