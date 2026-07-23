"""Trusted development API for inspecting and automating the running Qt app."""

import base64
import contextlib
import io
import json
import os
from pathlib import Path
import secrets
import socketserver
import sys
import tempfile
import threading
import time
import traceback
from types import SimpleNamespace

from PyQt5.QtCore import (
	QByteArray,
	QBuffer,
	QEventLoop,
	QIODevice,
	QObject,
	QTimer,
	Qt,
	pyqtSignal,
)
from PyQt5.QtWidgets import QWidget


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_TIMEOUT = 10.0


def default_info_file():
	return Path(tempfile.gettempdir()) / "sopr-scheme-gener-dev.json"


def _json_value(value):
	if value is None or isinstance(value, (bool, int, float, str)):
		return value
	if isinstance(value, (list, tuple)):
		return [_json_value(item) for item in value]
	if isinstance(value, dict):
		return {str(key): _json_value(item) for key, item in value.items()}
	if hasattr(value, "x") and hasattr(value, "y"):
		result = {"x": value.x(), "y": value.y()}
		if hasattr(value, "width") and hasattr(value, "height"):
			result.update(width=value.width(), height=value.height())
		return result
	return repr(value)


class ErrorCollector:
	def __init__(self, limit=100):
		self.limit = limit
		self._entries = []
		self._sequence = 0
		self._lock = threading.Lock()

	def add(self, source, message, details=None):
		with self._lock:
			self._sequence += 1
			entry = {
				"sequence": self._sequence,
				"time": time.time(),
				"source": source,
				"message": message,
				"details": details,
			}
			self._entries.append(entry)
			del self._entries[:-self.limit]
			return dict(entry)

	def entries(self, since=0, limit=100):
		with self._lock:
			result = [entry for entry in self._entries if entry["sequence"] > since]
			return [dict(entry) for entry in result[-limit:]]

	def clear(self):
		with self._lock:
			self._entries.clear()


class _BridgeRequest:
	def __init__(self, method, params):
		self.method = method
		self.params = params
		self.done = threading.Event()
		self.result = None
		self.error = None


class DevBridge(QObject):
	requested = pyqtSignal(object)

	def __init__(self, context, allow_unsafe_exec=False):
		super().__init__()
		self.context = context
		self.allow_unsafe_exec = allow_unsafe_exec
		self.errors = ErrorCollector()
		self.context.legacy.set_error_reporter(self.errors.add)
		self.context.events.record("devapi.bridge.created")
		self.requested.connect(self._handle_request, Qt.QueuedConnection)

	def submit(self, method, params, timeout=DEFAULT_TIMEOUT):
		request = _BridgeRequest(method, params or {})
		self.requested.emit(request)
		if not request.done.wait(timeout):
			raise TimeoutError("Qt application did not answer within {:.1f}s".format(timeout))
		if request.error is not None:
			raise request.error
		return request.result

	def object_registry(self):
		context = self.context
		objects = {
			"app": context.app,
			"context": context,
			"controller": context.controller,
			"window": context.window,
			"central": context.central,
			"task_selector": context.central.type_list_widget,
			"canvas_container": context.canvas_container,
			"canvas": context.canvas,
			"settings_container": context.settings_container,
			"settings": context.settings,
			"common_settings": context.common_settings,
		}
		if context.controller.current_scheme is not None:
			objects["task"] = context.controller.current_scheme
		return objects

	def script_context(self):
		objects = self.object_registry()
		return SimpleNamespace(
			**objects,
			objects=objects,
			screenshot=self._screenshot,
			wait_idle=self._wait_idle,
			select_task=self.context.controller.select,
		)

	def _handle_request(self, request):
		try:
			request.result = self.dispatch(request.method, request.params)
		except Exception as exc:
			self.errors.add("devapi", str(exc), traceback.format_exc())
			request.error = exc
		finally:
			request.done.set()

	def dispatch(self, method, params):
		handlers = {
			"ping": self._ping,
			"app.info": self._app_info,
			"tasks.list": self._tasks_list,
			"task.current": self._task_current,
			"task.select": self._task_select,
			"wait.idle": self._wait_idle,
			"screenshot": self._screenshot,
			"widgets.tree": self._widgets_tree,
			"objects.list": self._objects_list,
			"object.get": self._object_get,
			"document.snapshot": self._document_snapshot,
			"document.get": self._document_get,
			"document.set": self._document_set,
			"document.patch": self._document_patch,
			"scenario.run": self._scenario_run,
			"events.list": self._events_list,
			"events.clear": self._events_clear,
			"errors.list": self._errors_list,
			"errors.clear": self._errors_clear,
			"python.exec": self._python_exec,
		}
		try:
			handler = handlers[method]
		except KeyError:
			raise ValueError("Unknown development API method: {}".format(method))
		return handler(**params)

	def _ping(self):
		return {"status": "ok"}

	def _app_info(self):
		current = self._task_current()
		return {
			"name": self.context.app.applicationName(),
			"pid": os.getpid(),
			"task_count": len(self.context.controller.task_specs),
			"current_task": current,
			"unsafe_exec": self.allow_unsafe_exec,
		}

	def _tasks_list(self):
		controller = self.context.controller
		return [
			{
				"index": index,
				"id": spec.identifier,
				"title": spec.title,
				"active": index == controller.current_index,
			}
			for index, spec in enumerate(controller.task_specs)
		]

	def _task_current(self):
		controller = self.context.controller
		spec = controller.current_spec
		if spec is None:
			return None
		return {
			"index": controller.current_index,
			"id": spec.identifier,
			"title": spec.title,
		}

	def _task_select(self, selector):
		spec = self.context.controller.select(selector)
		self._wait_idle()
		return {
			"index": self.context.controller.current_index,
			"id": spec.identifier,
			"title": spec.title,
		}

	def _document_snapshot(self):
		return self.context.document.snapshot()

	def _document_get(self, path=""):
		return {
			"path": path,
			"value": self.context.document.get(path),
		}

	def _document_set(self, path, value):
		value = self.context.document.set(path, value)
		self._wait_idle()
		return {"path": path, "value": value}

	def _document_patch(self, changes):
		result = self.context.document.patch(changes)
		self._wait_idle()
		return result

	def _scenario_run(
		self,
		selector=None,
		changes=None,
		wait_ms=0,
		screenshot_target=None,
		include_document=True,
	):
		result = {}
		if selector is not None:
			result["task"] = self._task_select(selector)
		if changes:
			result["patch"] = self.context.document.patch(changes)
		self._wait_duration(wait_ms)
		if include_document:
			result["document"] = self.context.document.snapshot()
		if screenshot_target is not None:
			result["screenshot"] = self._screenshot(screenshot_target)
		self.context.events.record(
			"scenario.completed",
			{
				"selector": selector,
				"change_count": len(changes or []),
				"wait_ms": wait_ms,
				"screenshot_target": screenshot_target,
			},
		)
		return result

	def _wait_duration(self, wait_ms=0):
		if not isinstance(wait_ms, int) or isinstance(wait_ms, bool):
			raise TypeError("wait_ms must be an integer")
		if wait_ms < 0 or wait_ms > 10000:
			raise ValueError("wait_ms must be between 0 and 10000")
		self._wait_idle()
		if wait_ms:
			loop = QEventLoop()
			QTimer.singleShot(wait_ms, loop.quit)
			loop.exec()
			self._wait_idle()
		return {"status": "idle", "wait_ms": wait_ms}

	def _wait_idle(self, max_time_ms=100):
		app = self.context.app
		app.processEvents(QEventLoop.AllEvents, max_time_ms)
		app.sendPostedEvents()
		app.processEvents(QEventLoop.AllEvents, max_time_ms)
		return {"status": "idle"}

	def _target_widget(self, target):
		objects = self.object_registry()
		try:
			widget = objects[target]
		except KeyError:
			raise ValueError("Unknown screenshot target: {}".format(target))
		if not isinstance(widget, QWidget):
			raise ValueError("Object {!r} is not a QWidget".format(target))
		return widget

	def _screenshot(self, target="canvas"):
		self._wait_idle()
		widget = self._target_widget(target)
		pixmap = widget.grab()
		data = QByteArray()
		buffer = QBuffer(data)
		buffer.open(QIODevice.WriteOnly)
		if not pixmap.save(buffer, "PNG"):
			raise RuntimeError("Qt failed to encode screenshot")
		return {
			"target": target,
			"width": pixmap.width(),
			"height": pixmap.height(),
			"format": "png",
			"png_base64": base64.b64encode(bytes(data)).decode("ascii"),
		}

	def _widget_node(self, widget):
		geometry = widget.geometry()
		node = {
			"class": type(widget).__name__,
			"name": widget.objectName(),
			"visible": widget.isVisible(),
			"enabled": widget.isEnabled(),
			"geometry": {
				"x": geometry.x(),
				"y": geometry.y(),
				"width": geometry.width(),
				"height": geometry.height(),
			},
		}
		if hasattr(widget, "text") and callable(widget.text):
			try:
				node["text"] = widget.text()
			except TypeError:
				pass
		node["children"] = [
			self._widget_node(child)
			for child in widget.children()
			if isinstance(child, QWidget)
		]
		return node

	def _widgets_tree(self, target="window"):
		return self._widget_node(self._target_widget(target))

	def _objects_list(self):
		return [
			{
				"name": name,
				"class": type(obj).__name__,
				"object_name": obj.objectName() if isinstance(obj, QObject) else None,
			}
			for name, obj in self.object_registry().items()
		]

	def _object_get(self, name, attribute=None):
		try:
			obj = self.object_registry()[name]
		except KeyError:
			raise ValueError("Unknown object: {}".format(name))

		if attribute is not None:
			if attribute.startswith("_"):
				raise ValueError("Private attributes are not exposed by object.get")
			return _json_value(getattr(obj, attribute))

		result = {
			"class": type(obj).__name__,
			"repr": repr(obj),
		}
		if isinstance(obj, QObject):
			meta = obj.metaObject()
			properties = {}
			for index in range(meta.propertyCount()):
				prop = meta.property(index)
				name = prop.name()
				try:
					properties[name] = _json_value(prop.read(obj))
				except Exception:
					continue
			result["properties"] = properties
		return result

	def _errors_list(self, since=0, limit=100):
		return self.errors.entries(since=since, limit=limit)

	def _errors_clear(self):
		self.errors.clear()
		return {"status": "cleared"}

	def _events_list(self, since=0, limit=100):
		return self.context.events.entries(since=since, limit=limit)

	def _events_clear(self):
		self.context.events.clear()
		return {"status": "cleared"}

	def _python_exec(self, code):
		if not self.allow_unsafe_exec:
			raise PermissionError(
				"Python execution is disabled; restart with --unsafe-dev-exec"
			)

		ctx = self.script_context()
		namespace = {"ctx": ctx}
		stdout = io.StringIO()
		stderr = io.StringIO()
		with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
			try:
				result = eval(compile(code, "<soprctl>", "eval"), namespace, namespace)
			except SyntaxError:
				exec(compile(code, "<soprctl>", "exec"), namespace, namespace)
				result = namespace.get("result")
		self._wait_idle()
		return {
			"result": _json_value(result),
			"stdout": stdout.getvalue(),
			"stderr": stderr.getvalue(),
		}


class _RequestHandler(socketserver.StreamRequestHandler):
	def handle(self):
		line = self.rfile.readline(4 * 1024 * 1024)
		if not line:
			return
		request_id = None
		try:
			request = json.loads(line.decode("utf-8"))
			request_id = request.get("id")
			token = request.get("token", "")
			if not secrets.compare_digest(token, self.server.api_token):
				raise PermissionError("Invalid development API token")
			result = self.server.bridge.submit(
				request["method"],
				request.get("params", {}),
				timeout=float(request.get("timeout", DEFAULT_TIMEOUT)),
			)
			response = {"id": request_id, "result": result}
		except Exception as exc:
			response = {
				"id": request_id,
				"error": {
					"type": type(exc).__name__,
					"message": str(exc),
				},
			}
		self.wfile.write((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))


class _TCPServer(socketserver.ThreadingTCPServer):
	allow_reuse_address = True
	daemon_threads = True


class RunningDevServer:
	def __init__(self, server, thread, info_file):
		self.server = server
		self.thread = thread
		self.info_file = info_file
		self._closed = False

	@property
	def address(self):
		return self.server.server_address

	def close(self):
		if self._closed:
			return
		self._closed = True
		self.server.shutdown()
		self.server.server_close()
		if threading.current_thread() is not self.thread:
			self.thread.join(timeout=2)
		try:
			info = json.loads(self.info_file.read_text(encoding="utf-8"))
			if info.get("pid") == os.getpid():
				self.info_file.unlink()
		except (FileNotFoundError, json.JSONDecodeError, OSError):
			pass


def start_dev_server(
	context,
	host=DEFAULT_HOST,
	port=DEFAULT_PORT,
	token=None,
	info_file=None,
	allow_unsafe_exec=False,
):
	token = token or secrets.token_hex(24)
	if host not in ("127.0.0.1", "::1", "localhost"):
		print(
			"WARNING: development API traffic is not encrypted; "
			"use a trusted network, VPN, or tunnel",
			file=sys.stderr,
			flush=True,
		)
	bridge = DevBridge(context, allow_unsafe_exec=allow_unsafe_exec)
	server = _TCPServer((host, port), _RequestHandler)
	server.bridge = bridge
	server.api_token = token
	thread = threading.Thread(
		target=server.serve_forever,
		name="sopr-dev-api",
		daemon=True,
	)
	thread.start()

	info_path = Path(info_file) if info_file else default_info_file()
	info_path.parent.mkdir(parents=True, exist_ok=True)
	info = {
		"host": server.server_address[0],
		"port": server.server_address[1],
		"token": token,
		"pid": os.getpid(),
		"unsafe_exec": allow_unsafe_exec,
	}
	info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
	try:
		info_path.chmod(0o600)
	except OSError:
		pass

	print(
		"Development API: {}:{} (discovery: {})".format(
			info["host"],
			info["port"],
			info_path,
		),
		flush=True,
	)
	return RunningDevServer(server, thread, info_path)
