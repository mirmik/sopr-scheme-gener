import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QComboBox

from sopr_scheme_gener.app import build_parser, create_runtime
from sopr_scheme_gener.devapi import DevBridge
from sopr_scheme_gener.layouts.column_stability import (
	BASE_SUPPORT_TYPES,
	NODE_SUPPORT_TYPES,
)


def test_column_stability_editor_renders_and_round_trips_document(tmp_path):
	context = create_runtime(
		build_parser().parse_args(
			["--type", "column-stability", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		assert len(scheme.task["nodes"]) == len(scheme.task["segments"])
		assert scheme.task["base_support"] == "заделка"
		context.app.processEvents()
		image = context.canvas.make_image()
		assert image.bits().asstring(image.sizeInBytes())
		index = context.canvas.scene_interaction.index
		assert index.get("base/support") is not None
		assert index.get("node/1/support") is not None
		assert index.get("node/0/load") is not None

		path = tmp_path / "stability.sopr.json"
		before = context.storage.to_data()
		context.storage.save(path)
		assert context.storage.load(path) == before
	finally:
		context.window.close()


def test_stability_editor_uses_separate_base_support_and_top_down_rows():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "column-stability", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		conf = scheme.confwidget
		assert len(scheme.task["nodes"]) == len(scheme.task["segments"])
		assert scheme.task["segments"][0].rigidity_text == "EJ_min"
		assert scheme.task["nodes"][0].load_text == "F"
		assert tuple(conf.node_table.columns[0].variant) == NODE_SUPPORT_TYPES

		base_combo = conf.findChild(QComboBox, "column_base_support")
		assert tuple(
			base_combo.itemText(index)
			for index in range(base_combo.count())
		) == BASE_SUPPORT_TYPES
		base_combo.setCurrentText("шарнир")
		assert scheme.task["base_support"] == "шарнир"

		segments_before = list(scheme.task["segments"])
		nodes_before = list(scheme.task["nodes"])
		conf.insert_action_impl(0)
		assert len(scheme.task["nodes"]) == len(scheme.task["segments"]) == 3
		conf.del_action_impl(0)
		assert scheme.task["segments"] == segments_before
		assert scheme.task["nodes"] == nodes_before
	finally:
		context.window.close()


def test_clearing_rod_width_while_editing_does_not_break_render():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "column-stability", "--no-maximize"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		bridge = DevBridge(context)
		assert scheme.rod_width.get() == 5.0

		scheme.rod_width.obj.clear()
		context.app.processEvents()

		assert scheme.rod_width.get() == 5.0
		assert bridge.dispatch("screenshot", {"target": "canvas"})["png_base64"]
		assert bridge.dispatch("errors.list", {}) == []

		scheme.rod_width.obj.setText("7.5")
		context.app.processEvents()
		assert scheme.rod_width.get() == 7.5
		assert bridge.dispatch("errors.list", {}) == []
	finally:
		context.window.close()


def test_documents_without_label_offsets_remain_renderable():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "column-stability", "--no-maximize", "--error"]
		)
	)
	try:
		document = context.storage.to_data()
		payload = document["task"]["payload"]
		for segment in payload["segments"]:
			for field in (
				"length_offset_x",
				"length_offset_y",
				"rigidity_offset_x",
				"rigidity_offset_y",
			):
				segment["fields"].pop(field)
		for node in payload["nodes"]:
			node["fields"].pop("load_offset_x")
			node["fields"].pop("load_offset_y")

		context.storage.load_data(document)
		context.app.processEvents()
		image = context.canvas.make_image()

		assert image.bits().asstring(image.sizeInBytes())
		assert context.canvas.scene_interaction.index.get(
			"segment/0/length-label"
		) is not None
		assert context.canvas.scene_interaction.index.get(
			"node/0/load-label"
		) is not None
	finally:
		context.window.close()
