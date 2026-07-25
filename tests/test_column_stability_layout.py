from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.column_stability import (
	ColumnStabilityLayoutBuilder,
	ColumnStabilityLayoutSettings,
)
from sopr_scheme_gener.scene import Point, SceneIndex, TextMeasurement


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
				{"length": 1, "length_text": "l", "rigidity_text": "EJ_min"},
				{"length": 1, "length_text": "l", "rigidity_text": ""},
			],
			"nodes": [
				{"support": "none", "load": "down", "load_text": "F"},
				{
					"support": "floating-clamp",
					"load": "none",
					"load_text": "",
				},
			],
			"base_support": "fixed",
		}
	)
	index = SceneIndex(scene, FixedTextMetrics())

	assert index.get("segment/0/body") is not None
	assert index.get("segment/0/rigidity-label") is not None
	assert dict(index.get("node/1/support").item.metadata)["support"] == (
		"floating-clamp"
	)
	assert index.get("node/0/load") is not None
	assert index.get("node/0/load-label") is not None
	assert dict(index.get("segment/0/length-label").item.metadata)["kind"] == "label"
	assert dict(index.get("segment/0/rigidity-label").item.metadata)[
		"label_kind"
	] == "rigidity"


def test_label_offsets_move_length_rigidity_and_load_text():
	base_task = {
		"segments": [
			{
				"length": 1,
				"length_text": "l",
				"rigidity_text": "EJ",
				"length_offset_x": 11,
				"length_offset_y": -7,
				"rigidity_offset_x": -5,
				"rigidity_offset_y": 9,
			}
		],
		"nodes": [
			{
				"support": "нет",
				"load": "вниз",
				"load_text": "F",
				"load_offset_x": 13,
				"load_offset_y": 4,
			},
		],
		"base_support": "заделка",
	}
	moved = SceneIndex(_build(base_task), FixedTextMetrics())
	default = SceneIndex(
		_build(
			{
				"segments": [
					{"length": 1, "length_text": "l", "rigidity_text": "EJ"}
				],
				"nodes": [
					{"support": "нет", "load": "вниз", "load_text": "F"},
				],
				"base_support": "заделка",
			}
		),
		FixedTextMetrics(),
	)

	for object_id, dx, dy in (
		("segment/0/length-label", 11, -7),
		("segment/0/rigidity-label", -5, 9),
		("node/0/load-label", 13, 4),
	):
		moved_position = moved.get(object_id).item.position
		default_position = default.get(object_id).item.position
		assert moved_position.x == default_position.x + dx
		assert moved_position.y == default_position.y + dy


def test_internal_load_uses_crossbar_and_two_slender_arrows():
	scene = _build(
		{
			"segments": [
				{"length": 1, "length_text": "l", "rigidity_text": ""},
				{"length": 1, "length_text": "l", "rigidity_text": ""},
			],
			"nodes": [
				{"support": "нет", "load": "нет", "load_text": ""},
				{"support": "нет", "load": "вниз", "load_text": "3F"},
			],
			"base_support": "заделка",
		}
	)
	index = SceneIndex(scene, FixedTextMetrics())
	load = index.get("node/1/load").item

	assert dict(load.metadata)["style"] == "crossbar"
	assert index.get("node/1/load/bar") is not None
	assert index.get("node/1/load/left").item.stroke.width == 2.0
	assert index.get("node/1/load/right").item.stroke.width == 2.0
	assert index.get("node/1/load/left").item.head_width == 8.0


def test_side_link_hatching_stays_outside_with_same_slope_on_both_sides():
	def support(side):
		scene = _build(
			{
				"segments": [
					{"length": 1, "length_text": "l", "rigidity_text": ""}
				],
				"nodes": [
					{"support": side, "load": "нет", "load_text": ""},
				],
				"base_support": "нет",
			}
		)
		return SceneIndex(scene, FixedTextMetrics()).get("node/0/support").item

	left_hatches = [
		item
		for item in support("боковая тяга слева").children
		if hasattr(item, "start")
		and abs(item.end.x - item.start.x) == 7
		and abs(item.end.y - item.start.y) == 6
	]
	right_hatches = [
		item
		for item in support("боковая тяга справа").children
		if hasattr(item, "start")
		and abs(item.end.x - item.start.x) == 7
		and abs(item.end.y - item.start.y) == 6
	]

	assert any(item.end.x < item.start.x for item in left_hatches)
	assert any(item.end.x > item.start.x for item in right_hatches)
	assert all(
		(item.end.x - item.start.x) * (item.end.y - item.start.y) < 0
		for item in left_hatches + right_hatches
	)


def _single_support(support_name):
	return _build(
		{
			"segments": [
				{"length": 1, "length_text": "l", "rigidity_text": ""}
			],
			"nodes": [
				{
					"support": support_name,
					"load": "нет",
					"load_text": "",
				},
			],
			"base_support": "нет",
		}
	)


def _walk_scene_items(item):
	yield item
	for child in getattr(item, "children", ()):
		yield from _walk_scene_items(child)


@pytest.mark.parametrize("support_name", ["заделка", "плавающая заделка"])
def test_support_hatching_is_thinner_than_geometry(support_name):
	scene = _single_support(support_name)
	support = SceneIndex(scene, FixedTextMetrics()).get("node/0/support").item
	lines = [
		item
		for item in _walk_scene_items(support)
		if hasattr(item, "start") and hasattr(item, "end")
	]
	hatches = [
		item
		for item in lines
		if item.start.x != item.end.x and item.start.y != item.end.y
	]
	geometry = [
		item
		for item in lines
		if item.start.x == item.end.x or item.start.y == item.end.y
	]

	assert hatches
	assert geometry
	assert {item.stroke.width for item in hatches} == {1.0}
	assert {item.stroke.width for item in geometry} == {2.0}
	assert all(item.stroke.width < geometry[0].stroke.width for item in hatches)


def _assert_block_hatching_is_clipped(block):
	border = block.children[0].bounds
	hatches = [
		item
		for item in block.children[1:]
		if hasattr(item, "start")
		and (item.end.x - item.start.x) * (item.end.y - item.start.y) < 0
	]
	assert hatches
	for hatch in hatches:
		for point in (hatch.start, hatch.end):
			assert border.left <= point.x <= border.right
			assert border.top <= point.y <= border.bottom
		assert (hatch.end.x - hatch.start.x) * (
			hatch.end.y - hatch.start.y
		) < 0


def _vertical_lines_at(block, x):
	return [
		item
		for item in block.children
		if hasattr(item, "start")
		and item.start.x == item.end.x == x
		and item.start.y != item.end.y
	]


def _horizontal_lines_at(block, y):
	return [
		item
		for item in block.children
		if hasattr(item, "start")
		and item.start.y == item.end.y == y
		and item.start.x != item.end.x
	]


def test_node_fixed_clamp_has_two_short_hatched_blocks_next_to_rod():
	index = SceneIndex(_single_support("заделка"), FixedTextMetrics())
	support = index.get("node/0/support").item
	left = index.get("node/0/support/left-block").item
	right = index.get("node/0/support/right-block").item
	rod_x = index.get("segment/0/body").item.start.x

	assert dict(support.metadata)["support"] == "node-fixed-clamp"
	left_bounds = left.children[0].bounds
	right_bounds = right.children[0].bounds
	assert right_bounds.left - left_bounds.right > 12
	assert rod_x - left_bounds.right == right_bounds.left - rod_x
	assert left_bounds.width < 30
	assert right_bounds.width < 30
	assert not _vertical_lines_at(left, left_bounds.left)
	assert _vertical_lines_at(left, left_bounds.right)
	assert _vertical_lines_at(right, right_bounds.left)
	assert not _vertical_lines_at(right, right_bounds.right)
	_assert_block_hatching_is_clipped(left)
	_assert_block_hatching_is_clipped(right)


def test_floating_clamp_has_guides_cheeks_and_four_hatched_outer_blocks():
	index = SceneIndex(_single_support("плавающая заделка"), FixedTextMetrics())
	support = index.get("node/0/support").item
	left_guide = index.get("node/0/support/left-guide").item
	right_guide = index.get("node/0/support/right-guide").item
	left_cheek = index.get("node/0/support/left-cheek").item
	right_cheek = index.get("node/0/support/right-cheek").item
	blocks = {
		(side, level): index.get(
			"node/0/support/{}-{}-block".format(side, level)
		).item
		for side in ("left", "right")
		for level in ("upper", "lower")
	}

	assert dict(support.metadata)["support"] == "floating-clamp"
	assert left_guide.end.x == left_cheek.start.x
	assert right_guide.start.x == right_cheek.start.x
	assert left_cheek.start.x < right_cheek.start.x
	assert right_guide.end.x - left_guide.start.x < 100
	left_upper = blocks[("left", "upper")].children[0].bounds
	left_lower = blocks[("left", "lower")].children[0].bounds
	assert left_lower.top - left_upper.bottom > 12
	for (side, level), block in blocks.items():
		bounds = block.children[0].bounds
		inner_x = bounds.right if side == "left" else bounds.left
		facing_y = bounds.bottom if level == "upper" else bounds.top
		assert len(_vertical_lines_at(block, inner_x)) == 1
		assert len(_horizontal_lines_at(block, facing_y)) == 1
		assert sum(
			1
			for item in block.children
			if hasattr(item, "start")
			and (
				item.start.x == item.end.x
				or item.start.y == item.end.y
			)
		) == 2
		_assert_block_hatching_is_clipped(block)


@pytest.mark.parametrize(
	("support_name", "direction"),
	[
		("боковая тяга слева", -1),
		("боковая тяга справа", 1),
	],
)
def test_endpoint_side_link_centers_joint_and_keeps_link_out_of_circles(
	support_name,
	direction,
):
	scene = _build(
		{
			"segments": [{"length": 1, "length_text": "l", "rigidity_text": ""}],
			"nodes": [
				{"support": support_name, "load": "нет", "load_text": ""},
			],
			"base_support": "заделка",
		}
	)
	index = SceneIndex(scene, FixedTextMetrics())
	support = index.get("node/0/support").item
	body = index.get("segment/0/body").item
	link, inner_joint, outer_joint = support.children[:3]
	inner_center_x = inner_joint.bounds.x + inner_joint.bounds.width / 2
	outer_center_x = outer_joint.bounds.x + outer_joint.bounds.width / 2
	radius = inner_joint.bounds.width / 2

	assert inner_center_x == body.end.x
	assert link.start.x == inner_center_x + direction * radius
	assert link.end.x == outer_center_x - direction * radius
	assert support.children.index(link) < support.children.index(inner_joint)
	assert support.children.index(link) < support.children.index(outer_joint)


def test_internal_side_link_keeps_joint_beside_rod():
	scene = _build(
		{
			"segments": [
				{"length": 1, "length_text": "l", "rigidity_text": ""},
				{"length": 1, "length_text": "l", "rigidity_text": ""},
			],
			"nodes": [
				{"support": "нет", "load": "нет", "load_text": ""},
				{"support": "боковая тяга справа", "load": "нет", "load_text": ""},
			],
			"base_support": "заделка",
		}
	)
	index = SceneIndex(scene, FixedTextMetrics())
	support = index.get("node/1/support").item
	body = index.get("segment/0/body").item
	inner_joint = support.children[1]
	inner_center_x = inner_joint.bounds.x + inner_joint.bounds.width / 2

	assert inner_center_x > body.start.x


def test_base_hinge_triangle_grows_from_support_line_and_joint_covers_apex():
	scene = _build(
		{
			"segments": [{"length": 1, "length_text": "l", "rigidity_text": ""}],
			"nodes": [{"support": "нет", "load": "нет", "load_text": ""}],
			"base_support": "шарнир",
		}
	)
	index = SceneIndex(scene, FixedTextMetrics())
	support = index.get("base/support").item
	triangle = support.children[0]
	surface = support.children[1]
	joint = support.children[-1]
	joint_center_x = joint.bounds.x + joint.bounds.width / 2
	joint_center_y = joint.bounds.y + joint.bounds.height / 2

	assert triangle.points[0] == Point(joint_center_x, joint_center_y)
	assert triangle.points[1].y == surface.start.y
	assert triangle.points[2].y == surface.start.y
	assert support.children.index(joint) > support.children.index(triangle)

	hatches = [
		item
		for item in support.children[2:-1]
		if hasattr(item, "start") and item.end.y != item.start.y
	]
	assert hatches
	assert all(
		item.end.y - item.start.y > 0
		for item in hatches
	)


@pytest.mark.parametrize(
	"support",
	[
		"боковая тяга слева",
		"боковая тяга справа",
		"плавающая заделка",
	],
)
def test_all_node_support_types_render(support):
	scene = _build(
		{
			"segments": [{"length": 1, "length_text": "l", "rigidity_text": ""}],
			"nodes": [
				{"support": support, "load": "нет", "load_text": ""},
			],
			"base_support": "нет",
		}
	)
	assert SceneIndex(scene, FixedTextMetrics()).get("node/0/support") is not None


@pytest.mark.parametrize("support", ["заделка", "шарнир"])
def test_all_base_support_types_render(support):
	scene = _build(
		{
			"segments": [{"length": 1}],
			"nodes": [{"support": "нет"}],
			"base_support": support,
		}
	)
	assert SceneIndex(scene, FixedTextMetrics()).get("base/support") is not None


def test_layout_rejects_broken_composition():
	with pytest.raises(ValueError, match="one upper node"):
		_build(
			{
				"segments": [{"length": 1}, {"length": 1}],
				"nodes": [{"support": "нет"}],
				"base_support": "нет",
			}
		)
	with pytest.raises(ValueError, match="positive"):
		_build(
			{
				"segments": [{"length": 0}],
				"nodes": [{"support": "нет"}],
				"base_support": "нет",
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
