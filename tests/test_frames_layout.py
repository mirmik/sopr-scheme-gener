from pathlib import Path

import pytest

from sopr_scheme_gener.layouts.beam_sections import BeamSectionSpec
from sopr_scheme_gener.layouts.frames import FramesLayoutBuilder, FramesLayoutSettings
from sopr_scheme_gener.scene import Point, Rect, SceneIndex, TextMeasurement


class FixedTextMetrics:
	def measure(self, text, style):
		return TextMeasurement(len(text) * 8, 20, 15, 5)


def _member(index, **changes):
	record = {
		"xstrt": "0" if index == 0 else "",
		"ystrt": "0" if index == 0 else "",
		"xfini": str(index + 1),
		"yfini": str(index % 2),
		"lsharn": "нет",
		"rsharn": "нет",
		"txt": "R{}".format(index),
		"alttxt": False,
	}
	record.update(changes)
	return record


def _task(count=3):
	return {
		"sections": [_member(index) for index in range(count)],
		"sectforce": [{"distrib": "clean", "txt": ""} for _ in range(count)],
		"betsect": [
			{
				"fenl": "нет",
				"fenr": "нет",
				"menl": "нет",
				"menr": "нет",
				"fl_txt": "",
				"fr_txt": "",
				"ml_txt": "",
				"mr_txt": "",
				"fl_txt_alt": False,
				"fr_txt_alt": False,
			}
			for _ in range(count)
		],
		"label": [
			{
				"smaker": "",
				"fmaker": "",
				"smaker_pos": "сверху",
				"fmaker_pos": "сверху",
			}
			for _ in range(count)
		],
	}


def _index(scene):
	return SceneIndex(scene, FixedTextMetrics())


def test_default_frames_layout_has_stable_semantic_objects():
	scene = FramesLayoutBuilder().build(
		_task(),
		FramesLayoutSettings(500, 300, 150),
		FixedTextMetrics(),
	)
	index = _index(scene)

	assert scene.viewport == Rect(0, 0, 500, 300)
	assert index.get("member/0").metadata_value("kind") == "member"
	assert index.get("member/0/line") is not None
	assert index.get("member/1/text") is not None
	assert index.get("member/2") is not None


def test_frames_layout_covers_loads_supports_forces_moments_and_labels():
	task = _task(4)
	supports = [
		("слева шарн1", "снизу шарн2"),
		("сверху врез1", "врезанный"),
		("заделка", "справа шарн1"),
		("снизу врез1", "справа шарн2"),
	]
	for section, (left, right) in zip(task["sections"], supports):
		section["lsharn"], section["rsharn"] = left, right
	task["sectforce"][0].update(distrib="+", txt="q0")
	task["sectforce"][1].update(distrib="-", txt="q1")
	for index, node in enumerate(task["betsect"]):
		directions = ("слева", "справа", "сверху", "снизу")
		node.update(
			fenl=directions[index] + " от",
			fenr=directions[index] + " к",
			menl=directions[index] + " +",
			menr=directions[index] + " -",
			fl_txt="FL{}".format(index),
			fr_txt="FR{}".format(index),
			ml_txt="ML{}".format(index),
			mr_txt="MR{}".format(index),
			fl_txt_alt=index % 2 == 0,
			fr_txt_alt=index % 2 == 1,
		)
		task["label"][index].update(
			smaker="S{}".format(index),
			fmaker="F{}".format(index),
			smaker_pos=directions[index],
			fmaker_pos=directions[-index - 1],
		)

	scene = FramesLayoutBuilder().build(
		task,
		FramesLayoutSettings(
			600,
			400,
			200,
			section=BeamSectionSpec(
				section_type="Треугольник",
				arg0=40,
				arg1=60,
				text0="b",
				text1="h",
			),
			highlight_hint="N1",
			highlight_row=2,
		),
		FixedTextMetrics(),
	)
	index = _index(scene)

	assert index.get("section/cross-section").metadata_value("kind") == "cross-section"
	assert index.get("member/0/distributed").metadata_value("direction") == "+"
	assert index.get("member/1/distributed").metadata_value("direction") == "-"
	assert index.get("member/2/distributed") is None
	for member in range(4):
		assert index.get("member/{}/start-support".format(member)) is not None
		assert index.get("member/{}/end-support".format(member)) is not None
		assert index.get("member/{}/start-force".format(member)) is not None
		assert index.get("member/{}/end-force".format(member)) is not None
		assert index.get("member/{}/start-moment".format(member)) is not None
		assert index.get("member/{}/end-moment".format(member)) is not None
		assert index.get("member/{}/start-label".format(member)) is not None
		assert index.get("member/{}/end-label".format(member)) is not None
	assert index.get("highlight/member") is not None
	assert index.get("highlight/node") is not None


def test_frames_layout_exposes_grid_preview_and_hover_metadata():
	scene = FramesLayoutBuilder().build(
		_task(1),
		FramesLayoutSettings(
			400,
			300,
			150,
			grid_enabled=True,
			hovered_grid=Point(0, 0),
			preview_start=Point(0, 0),
			preview_end=Point(1, 1),
		),
		FixedTextMetrics(),
	)
	index = _index(scene)

	grid = index.get("grid/0/0")
	assert grid.metadata_value("kind") == "grid-node"
	assert grid.metadata_value("grid_x") == 0
	assert grid.metadata_value("grid_y") == 0
	assert index.get("preview").metadata_value("kind") == "preview"


def test_frames_layout_rejects_inconsistent_documents():
	task = _task()
	task["label"].pop()

	with pytest.raises(ValueError, match="inconsistent"):
		FramesLayoutBuilder().build(
			task,
			FramesLayoutSettings(400, 300, 150),
			FixedTextMetrics(),
		)


def test_frames_layout_and_widget_have_no_legacy_painting_path():
	root = Path(__file__).resolve().parents[1]
	layout_source = (
		root / "sopr_scheme_gener" / "layouts" / "frames.py"
	).read_text(encoding="utf-8")
	widget_source = (root / "tasks" / "frames.py").read_text(encoding="utf-8")

	assert "PyQt" not in layout_source
	assert "QPainter" not in layout_source
	assert "paintool" not in layout_source
	for forbidden in (
		"elements.draw_",
		"paintool.draw_",
		"paintool.common_arrow",
		"self.painter.draw",
	):
		assert forbidden not in widget_source
