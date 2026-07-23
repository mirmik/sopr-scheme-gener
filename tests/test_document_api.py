import json
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime
from sopr_scheme_gener.devapi import DevBridge


def test_every_task_has_a_json_document_snapshot():
	args = build_parser().parse_args(["--no-maximize"])
	context = create_runtime(args)
	try:
		for spec in context.task_specs:
			context.controller.select(spec.identifier)
			snapshot = context.document.snapshot()
			assert snapshot["task_type"]["id"] == spec.identifier
			json.dumps(snapshot, ensure_ascii=False)
	finally:
		context.window.close()


def test_structured_document_get_set_patch_and_scenario():
	args = build_parser().parse_args(["--type", "stress-cube", "--no-maximize"])
	context = create_runtime(args)
	try:
		bridge = DevBridge(context)
		snapshot = bridge.dispatch("document.snapshot", {})
		assert snapshot["task_type"]["id"] == "stress-cube"
		assert snapshot["task"]["sections"][0]["qx"] == "нет"

		changed = bridge.dispatch(
			"document.set",
			{"path": "/task/sections/0/qx", "value": "+"},
		)
		assert changed == {"path": "/task/sections/0/qx", "value": "+"}

		with pytest.raises(TypeError, match="Expected a string"):
			context.document.patch(
				[
					{"path": "/task/sections/0/qx", "value": "-"},
					{"path": "/task/sections/0/qy", "value": 123},
				]
			)
		assert context.document.get("/task/sections/0/qx") == "+"

		result = bridge.dispatch(
			"scenario.run",
			{
				"selector": "beams",
				"changes": [{"path": "/task/sections/0/l", "value": 2.0}],
				"wait_ms": 1,
				"screenshot_target": "canvas",
			},
		)
		assert result["task"]["id"] == "beams"
		assert result["document"]["task"]["sections"][0]["l"] == 2.0
		assert result["screenshot"]["png_base64"]
		assert context.canvas.last_scene.viewport.width == context.canvas.width()
		assert "beam/body" in {
			item.object_id
			for item in context.canvas.last_scene.walk()
			if item.object_id
		}
		assert any(
			entry["event"] == "scenario.completed"
			for entry in bridge.dispatch("events.list", {})
		)
		assert bridge.dispatch("events.clear", {}) == {"status": "cleared"}
		assert bridge.dispatch("events.list", {}) == []
	finally:
		context.window.close()


def test_render_errors_are_reported_without_opening_a_modal():
	args = build_parser().parse_args(["--type", "beams", "--no-maximize"])
	context = create_runtime(args)
	try:
		bridge = DevBridge(context)
		canvas = context.canvas
		original = canvas.paintEventImplementation

		def broken_render(_event):
			raise RuntimeError("synthetic render failure")

		canvas.paintEventImplementation = broken_render
		bridge.dispatch("screenshot", {"target": "canvas"})
		errors = bridge.dispatch("errors.list", {})
		assert errors[-1]["source"] == "render"
		assert errors[-1]["message"] == "synthetic render failure"
		assert "RuntimeError" in errors[-1]["details"]
		assert bridge.dispatch("errors.clear", {}) == {"status": "cleared"}
		assert bridge.dispatch("errors.list", {}) == []
		canvas.paintEventImplementation = original
	finally:
		context.window.close()
