from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from sopr_scheme_gener.scene import (
	Arc,
	Arrow,
	Color,
	Ellipse,
	Fill,
	Group,
	Line,
	Point,
	Polygon,
	Polyline,
	Rect,
	Rectangle,
	Scene,
	Stroke,
	Text,
	TextAnchor,
	TextMeasurement,
	TextStyle,
	metadata,
)


def test_scene_values_are_immutable_and_normalize_sequences():
	line = Line(
		Point(1, 2),
		Point(3, 4),
		object_id="beam/0",
		metadata=metadata(kind="beam", index=0),
	)
	group = Group([line], offset=Point(10, 5))
	scene = Scene(Rect(0, 0, 100, 50), [group])

	assert scene.objects == (group,)
	assert group.children == (line,)
	assert list(scene.walk()) == [group, line]
	assert scene.content_bounds == scene.viewport

	with pytest.raises(FrozenInstanceError):
		line.start = Point(0, 0)
	with pytest.raises(FrozenInstanceError):
		scene.objects = ()


def test_geometry_style_and_primitive_validation():
	assert Rect(0, 0, 10, 10).union(Rect(5, -2, 10, 5)) == Rect(0, -2, 15, 12)
	assert Rect.around([Point(-1, 4), Point(3, 2)]) == Rect(-1, 2, 4, 2)
	assert Point(1, 2).translated(Point(3, -1)) == Point(4, 1)

	with pytest.raises(ValueError, match="cannot be negative"):
		Rect(0, 0, -1, 2)
	with pytest.raises(ValueError, match="at least two"):
		Polyline([Point(0, 0)])
	with pytest.raises(ValueError, match="at least three"):
		Polygon([Point(0, 0), Point(1, 1)])
	with pytest.raises(ValueError, match="must differ"):
		Arrow(Point(0, 0), Point(0, 0))
	with pytest.raises(ValueError, match="dash values"):
		Stroke(dash=(2, 0))
	with pytest.raises(ValueError, match="Unsupported line style"):
		Stroke(line_style="dots")
	with pytest.raises(ValueError, match="0 to 255"):
		Color(256, 0, 0)
	with pytest.raises(ValueError, match="Unsupported fill pattern"):
		Fill(pattern="dots")
	with pytest.raises(TypeError, match="bounds must be a Rect"):
		Rectangle("not-a-rect")


def test_minimal_scene_contains_only_generic_primitives():
	style = TextStyle(point_size=11, italic=True)
	scene = Scene(
		viewport=Rect(0, 0, 120, 80),
		content_bounds=Rect(5, 5, 110, 70),
		objects=(
			Line(Point(5, 5), Point(40, 5)),
			Polyline((Point(5, 15), Point(20, 10), Point(40, 15))),
			Polygon(
				(Point(5, 25), Point(25, 25), Point(15, 40)),
				fill=Fill(Color(220, 220, 220)),
			),
			Rectangle(Rect(45, 25, 10, 10)),
			Ellipse(Rect(60, 25, 10, 10)),
			Arc(Rect(75, 25, 10, 10), 0, 180),
			Text(Point(50, 20), "N", style=style, anchor=TextAnchor.CENTER),
			Arrow(Point(50, 50), Point(100, 50)),
		),
	)

	assert len(tuple(scene.walk())) == 8
	assert scene.content_bounds == Rect(5, 5, 110, 70)


def test_text_metrics_contract_is_usable_without_qt():
	class FixedMetrics:
		def measure(self, text, style):
			return TextMeasurement(
				width=len(text) * style.point_size,
				height=style.point_size,
				ascent=style.point_size * 0.8,
				descent=style.point_size * 0.2,
			)

	result = FixedMetrics().measure("abc", TextStyle(point_size=10))
	assert result == TextMeasurement(30, 10, 8, 2)


def test_scene_core_source_does_not_import_qt():
	scene_dir = (
		Path(__file__).resolve().parents[1]
		/ "sopr_scheme_gener"
		/ "scene"
	)
	for name in ("__init__.py", "model.py", "metrics.py"):
		source = (scene_dir / name).read_text(encoding="utf-8")
		assert "PyQt" not in source
		assert "QPainter" not in source
