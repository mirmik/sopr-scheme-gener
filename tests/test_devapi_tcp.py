import json
import os
import threading
import time
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime
from sopr_scheme_gener.ctl import request
from sopr_scheme_gener.devapi import start_dev_server


def test_soprctl_protocol_edits_document_and_returns_screenshot(tmp_path):
	args = build_parser().parse_args(["--type", "beams", "--no-maximize"])
	context = create_runtime(args)
	info_file = tmp_path / "dev-api.json"
	server = start_dev_server(
		context,
		port=0,
		token="test-token",
		info_file=info_file,
	)
	client_args = SimpleNamespace(
		host=None,
		port=None,
		token=None,
		info_file=str(info_file),
		timeout=3.0,
	)
	outcome = {}

	def call_scenario():
		try:
			outcome["result"] = request(
				client_args,
				"scenario.run",
				{
					"changes": [
						{"path": "/task/sections/0/l", "value": 2.5},
						{"path": "/canvas/width", "value": 640},
					],
					"wait_ms": 1,
					"screenshot_target": "canvas",
				},
			)
		except Exception as exc:
			outcome["error"] = exc

	thread = threading.Thread(target=call_scenario)
	thread.start()
	deadline = time.monotonic() + 5
	while thread.is_alive() and time.monotonic() < deadline:
		context.app.processEvents()
		thread.join(0.01)

	try:
		assert not thread.is_alive()
		assert "error" not in outcome
		result = outcome["result"]
		assert result["document"]["task"]["sections"][0]["l"] == 2.5
		assert result["document"]["canvas"]["width"] == 640
		assert result["screenshot"]["format"] == "png"
		assert result["screenshot"]["png_base64"]
		assert json.loads(info_file.read_text(encoding="utf-8"))["port"] > 0
	finally:
		server.close()
		context.window.close()
