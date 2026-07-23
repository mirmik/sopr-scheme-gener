import base64
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime
from sopr_scheme_gener.devapi import DevBridge


def test_runtime_selects_task_and_renders_canvas():
	args = build_parser().parse_args(["--type", "stress-cube", "--no-maximize"])
	runtime = create_runtime(args)
	try:
		bridge = DevBridge(runtime)
		assert runtime.window.context is runtime
		assert runtime.central.context is runtime
		assert runtime.controller.current_scheme.paintwidget is runtime.canvas
		assert bridge.dispatch("task.current", {})["id"] == "stress-cube"
		screenshot = bridge.dispatch("screenshot", {"target": "canvas"})
		assert screenshot["width"] > 0
		assert screenshot["height"] > 0
		assert base64.b64decode(screenshot["png_base64"]).startswith(b"\x89PNG")
	finally:
		runtime.window.close()
