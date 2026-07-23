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
import traceback
from types import SimpleNamespace

from PyQt5.QtCore import QByteArray, QBuffer, QEventLoop, QIODevice, QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget


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
		self._lock = threading.Lock()

	def add(self, source, message, details=None):
		entry = {
			"source": source,
			"message": message,
			"details": details,
		}
		with self._lock:
			self._entries.append(entry)
			del self._entries[:-self.limit]

	def entries(self):
		with self._lock:
			return list(self._entries)


class _BridgeRequest:
	def __init__(self, method, params):
		self.method = method
		self.params = params
		self.done = threading.Event()
		self.result = None
		self.error = None


class DevBridge(QObject):
	requested = pyqtSignal(object)

	def __init__(self, runtime, allow_unsafe_exec=False):
		super().__init__()
		self.runtime = runtime
		self.allow_unsafe_exec = allow_unsafe_exec
		self.errors = ErrorCollector()
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
		window = self.runtime.window
		central = window.cw
		objects = {
			"app": self.runtime.app,
			"window": window,
			"central": central,
			"task_selector": central.type_list_widget,
			"canvas_container": central.container_paint,
			"canvas": central.container_paint.curwidget,
			"settings_container": central.container_settings,
			"settings": central.container_settings.curwidget,
			"common_settings": central.confview,
		}
		if central.currentno >= 0:
			objects["task"] = central.current_scheme()
		return objects

	def script_context(self):
		objects = self.object_registry()
		return SimpleNamespace(
			**objects,
			objects=objects,
			screenshot=self._screenshot,
			wait_idle=self._wait_idle,
			select_task=self.runtime.window.cw.select_task,
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
			"errors.list": self._errors_list,
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
			"name": self.runtime.app.applicationName(),
			"pid": os.getpid(),
			"task_count": len(self.runtime.window.cw.task_specs),
			"current_task": current,
			"unsafe_exec": self.allow_unsafe_exec,
		}

	def _tasks_list(self):
		central = self.runtime.window.cw
		return [
			{
				"index": index,
				"id": spec.identifier,
				"title": spec.title,
				"active": index == central.currentno,
			}
			for index, spec in enumerate(central.task_specs)
		]

	def _task_current(self):
		central = self.runtime.window.cw
		spec = central.current_task_spec()
		if spec is None:
			return None
		return {
			"index": central.currentno,
			"id": spec.identifier,
			"title": spec.title,
		}

	def _task_select(self, selector):
		spec = self.runtime.window.cw.select_task(selector)
		self._wait_idle()
		return {
			"index": self.runtime.window.cw.currentno,
			"id": spec.identifier,
			"title": spec.title,
		}

	def _wait_idle(self, max_time_ms=100):
		app = QApplication.instance()
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

	def _errors_list(self):
		return self.errors.entries()

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
	runtime,
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
	bridge = DevBridge(runtime, allow_unsafe_exec=allow_unsafe_exec)
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
