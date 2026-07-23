"""Command-line client for the running application's development API."""

import argparse
import base64
import json
from pathlib import Path
import socket
import sys

from .devapi import DEFAULT_TIMEOUT, default_info_file


class DevAPIError(RuntimeError):
	pass


def _connection_settings(args):
	info = {}
	info_path = Path(args.info_file) if args.info_file else default_info_file()
	if info_path.exists():
		info = json.loads(info_path.read_text(encoding="utf-8"))

	host = args.host or info.get("host")
	port = args.port or info.get("port")
	token = args.token or info.get("token")
	if not host or not port or not token:
		raise DevAPIError(
			"No complete connection settings found; start the app with --dev-api "
			"or pass --host, --port and --token"
		)
	return host, int(port), token


def request(args, method, params=None):
	host, port, token = _connection_settings(args)
	payload = {
		"id": 1,
		"method": method,
		"params": params or {},
		"token": token,
		"timeout": args.timeout,
	}
	with socket.create_connection((host, port), timeout=args.timeout) as sock:
		sock.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
		response_file = sock.makefile("rb")
		line = response_file.readline(4 * 1024 * 1024)
	if not line:
		raise DevAPIError("Development API closed the connection without a response")
	response = json.loads(line.decode("utf-8"))
	if "error" in response:
		error = response["error"]
		raise DevAPIError("{}: {}".format(error["type"], error["message"]))
	return response["result"]


def _selector(value):
	return int(value) if value.lstrip("-").isdigit() else value


def _json_value(value):
	try:
		return json.loads(value)
	except json.JSONDecodeError:
		return value


def _json_source(args):
	if args.json_text is not None:
		return json.loads(args.json_text)
	return json.loads(args.file.read_text(encoding="utf-8"))


def build_parser():
	parser = argparse.ArgumentParser(prog="soprctl")
	parser.add_argument("--host")
	parser.add_argument("--port", type=int)
	parser.add_argument("--token")
	parser.add_argument("--info-file")
	parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
	parser.add_argument("--compact", action="store_true")
	subparsers = parser.add_subparsers(dest="command", required=True)

	subparsers.add_parser("ping")
	subparsers.add_parser("info")
	subparsers.add_parser("tasks")

	select = subparsers.add_parser("select")
	select.add_argument("selector", type=_selector)

	screenshot = subparsers.add_parser("screenshot")
	screenshot.add_argument("output", type=Path)
	screenshot.add_argument(
		"--target",
		default="canvas",
		choices=("window", "central", "canvas_container", "canvas", "settings"),
	)

	tree = subparsers.add_parser("tree")
	tree.add_argument("--target", default="window")

	subparsers.add_parser("objects")

	get_object = subparsers.add_parser("get")
	get_object.add_argument("name")
	get_object.add_argument("attribute", nargs="?")

	subparsers.add_parser("document")

	doc_get = subparsers.add_parser("doc-get")
	doc_get.add_argument("path", nargs="?", default="")

	doc_set = subparsers.add_parser("doc-set")
	doc_set.add_argument("path")
	doc_set.add_argument("value", type=_json_value)

	patch = subparsers.add_parser("patch")
	patch_source = patch.add_mutually_exclusive_group(required=True)
	patch_source.add_argument("--json", dest="json_text")
	patch_source.add_argument("--file", type=Path)

	scenario = subparsers.add_parser("scenario")
	scenario_source = scenario.add_mutually_exclusive_group(required=True)
	scenario_source.add_argument("--json", dest="json_text")
	scenario_source.add_argument("--file", type=Path)
	scenario.add_argument("--screenshot-output", type=Path)

	events = subparsers.add_parser("events")
	events.add_argument("--since", type=int, default=0)
	events.add_argument("--limit", type=int, default=100)
	events.add_argument("--clear", action="store_true")

	errors = subparsers.add_parser("errors")
	errors.add_argument("--since", type=int, default=0)
	errors.add_argument("--limit", type=int, default=100)
	errors.add_argument("--clear", action="store_true")

	execute = subparsers.add_parser("exec")
	source = execute.add_mutually_exclusive_group(required=True)
	source.add_argument("--code")
	source.add_argument("--file", type=Path)

	raw = subparsers.add_parser("raw")
	raw.add_argument("method")
	raw.add_argument("--params", default="{}")
	return parser


def run_command(args):
	if args.command == "ping":
		return request(args, "ping")
	if args.command == "info":
		return request(args, "app.info")
	if args.command == "tasks":
		return request(args, "tasks.list")
	if args.command == "select":
		return request(args, "task.select", {"selector": args.selector})
	if args.command == "screenshot":
		result = request(args, "screenshot", {"target": args.target})
		args.output.parent.mkdir(parents=True, exist_ok=True)
		args.output.write_bytes(base64.b64decode(result.pop("png_base64")))
		result["output"] = str(args.output)
		return result
	if args.command == "tree":
		return request(args, "widgets.tree", {"target": args.target})
	if args.command == "objects":
		return request(args, "objects.list")
	if args.command == "get":
		params = {"name": args.name}
		if args.attribute is not None:
			params["attribute"] = args.attribute
		return request(args, "object.get", params)
	if args.command == "document":
		return request(args, "document.snapshot")
	if args.command == "doc-get":
		return request(args, "document.get", {"path": args.path})
	if args.command == "doc-set":
		return request(
			args,
			"document.set",
			{"path": args.path, "value": args.value},
		)
	if args.command == "patch":
		changes = _json_source(args)
		return request(args, "document.patch", {"changes": changes})
	if args.command == "scenario":
		scenario = _json_source(args)
		result = request(args, "scenario.run", scenario)
		screenshot = result.get("screenshot")
		if screenshot is not None and args.screenshot_output is not None:
			args.screenshot_output.parent.mkdir(parents=True, exist_ok=True)
			args.screenshot_output.write_bytes(
				base64.b64decode(screenshot.pop("png_base64"))
			)
			screenshot["output"] = str(args.screenshot_output)
		return result
	if args.command == "events":
		if args.clear:
			return request(args, "events.clear")
		return request(
			args,
			"events.list",
			{"since": args.since, "limit": args.limit},
		)
	if args.command == "errors":
		if args.clear:
			return request(args, "errors.clear")
		return request(
			args,
			"errors.list",
			{"since": args.since, "limit": args.limit},
		)
	if args.command == "exec":
		code = args.code if args.code is not None else args.file.read_text(encoding="utf-8")
		return request(args, "python.exec", {"code": code})
	if args.command == "raw":
		return request(args, args.method, json.loads(args.params))
	raise AssertionError("Unhandled command: {}".format(args.command))


def main(argv=None):
	args = build_parser().parse_args(argv)
	try:
		result = run_command(args)
	except (DevAPIError, OSError, ValueError, json.JSONDecodeError) as exc:
		print("soprctl: {}".format(exc), file=sys.stderr)
		return 1
	indent = None if args.compact else 2
	print(json.dumps(result, ensure_ascii=False, indent=indent))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
