import pytest

from sopr_scheme_gener.scene import (
	Group,
	Point,
	Rect,
	Rectangle,
	Scene,
	SceneIndex,
	Text,
	TextAnchor,
	TextMeasurement,
	TextStyle,
	ViewportMapping,
	metadata,
)


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(
			width=len(text) * 10,
			height=20,
			ascent=15,
			descent=5,
		)


def test_hit_testing_honors_nested_offsets_depth_and_painter_order():
	first = Group(
		(
			Rectangle(
				Rect(0, 0, 30, 30),
				object_id="first/shape",
				metadata=metadata(kind="shape"),
			),
		),
		offset=Point(10, 5),
		object_id="first",
		metadata=metadata(kind="group"),
	)
	second = Rectangle(
		Rect(20, 10, 30, 30),
		object_id="second",
		metadata=metadata(kind="shape"),
	)
	index = SceneIndex(
		Scene(Rect(0, 0, 100, 80), (first, second)),
		FixedTextMetrics(),
	)

	assert index.bounds("first/shape") == Rect(9.5, 4.5, 31, 31)
	assert index.bounds("first") == index.bounds("first/shape")
	assert index.hit_test(Point(12, 8)).object_id == "first/shape"
	assert index.hit_test(Point(25, 15)).object_id == "second"
	assert (
		index.hit_test(Point(25, 15), kinds=("group",)).object_id
		== "first"
	)


def test_text_bounds_and_kind_policy_support_interactive_labels():
	label = Text(
		Point(50, 30),
		"abc",
		style=TextStyle(point_size=12),
		anchor=TextAnchor.CENTER,
		object_id="label/0",
		metadata=metadata(kind="label", index=0),
	)
	index = SceneIndex(
		Scene(Rect(0, 0, 100, 60), (label,)),
		FixedTextMetrics(),
	)

	assert index.bounds("label/0") == Rect(35, 20, 35, 20)
	hit = index.hit_test(Point(68, 29), kinds=("label",))
	assert hit.object_id == "label/0"
	assert hit.metadata_value("index") == 0
	assert index.hit_test(Point(68, 29), kinds=("shape",)) is None


def test_scene_index_rejects_duplicate_object_ids():
	scene = Scene(
		Rect(0, 0, 20, 20),
		(
			Rectangle(Rect(0, 0, 5, 5), object_id="duplicate"),
			Rectangle(Rect(10, 10, 5, 5), object_id="duplicate"),
		),
	)

	with pytest.raises(ValueError, match="Duplicate"):
		SceneIndex(scene, FixedTextMetrics())


def test_viewport_mapping_supports_direct_and_aspect_fit_renderers():
	viewport = Rect(-10, -20, 200, 100)

	direct = ViewportMapping.direct(viewport)
	assert direct.from_device(Point(15, 25)) == Point(5, 5)

	fitted = ViewportMapping.aspect_fit(viewport, 100, 100)
	assert fitted.scale == 0.5
	assert fitted.from_device(Point(15, 25)) == Point(20, 30)
	assert fitted.delta_from_device(Point(5, -10)) == Point(10, -20)
