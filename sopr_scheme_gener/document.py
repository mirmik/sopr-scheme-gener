"""Structured, JSON-compatible access to the active legacy task document."""

import numbers

import numpy


def to_json_value(value, seen=None, path=""):
	if value is None or isinstance(value, (bool, int, float, str)):
		return value
	if isinstance(value, numpy.generic):
		return value.item()
	if isinstance(value, numpy.ndarray):
		return value.tolist()

	if seen is None:
		seen = {}
	value_id = id(value)
	if value_id in seen:
		return {"$ref": seen[value_id]}
	seen[value_id] = path or "/"

	if isinstance(value, dict):
		return {
			str(key): to_json_value(item, seen, _join_pointer(path, str(key)))
			for key, item in value.items()
		}
	if isinstance(value, (list, tuple)):
		return [
			to_json_value(item, seen, _join_pointer(path, str(index)))
			for index, item in enumerate(value)
		]
	if hasattr(value, "__dict__"):
		return {
			key: to_json_value(item, seen, _join_pointer(path, key))
			for key, item in value.__dict__.items()
			if not key.startswith("_")
		}
	return repr(value)


def _escape_pointer(token):
	return token.replace("~", "~0").replace("/", "~1")


def _join_pointer(path, token):
	return "{}/{}".format(path, _escape_pointer(token))


def parse_pointer(path):
	if path == "":
		return []
	if not isinstance(path, str) or not path.startswith("/"):
		raise ValueError("Document path must be an RFC 6901 JSON Pointer")
	return [
		token.replace("~1", "/").replace("~0", "~")
		for token in path[1:].split("/")
	]


def _getter_map(menu):
	result = {}
	for getter in menu.getters:
		key = str(getter.parent.serlbl)
		if key in result:
			raise ValueError("Duplicate serialized setting label: {!r}".format(key))
		result[key] = getter
	return result


def _read_child(container, token):
	if token.startswith("_"):
		raise ValueError("Private document attributes are not exposed")
	if isinstance(container, dict):
		return container[token]
	if isinstance(container, (list, tuple)):
		return container[int(token)]
	return getattr(container, token)


def _write_child(container, token, value):
	if token.startswith("_"):
		raise ValueError("Private document attributes are not writable")
	if isinstance(container, dict):
		current = container[token]
		container[token] = _coerce_value(current, value, widen_numeric=True)
		return current
	if isinstance(container, list):
		index = int(token)
		current = container[index]
		container[index] = _coerce_value(current, value, widen_numeric=True)
		return current
	if isinstance(container, tuple):
		raise ValueError("Tuple elements are not writable")
	current = getattr(container, token)
	setattr(container, token, _coerce_value(current, value, widen_numeric=True))
	return current


def _coerce_value(current, value, widen_numeric=False):
	if isinstance(current, bool):
		if not isinstance(value, bool):
			raise TypeError("Expected a boolean value")
		return value
	if isinstance(current, numbers.Integral) and not isinstance(current, bool):
		expected = numbers.Real if widen_numeric else numbers.Integral
		if not isinstance(value, expected) or isinstance(value, bool):
			raise TypeError("Expected an integer value")
		return (
			float(value)
			if widen_numeric and not isinstance(value, numbers.Integral)
			else int(value)
		)
	if isinstance(current, numbers.Real):
		if not isinstance(value, numbers.Real) or isinstance(value, bool):
			raise TypeError("Expected a numeric value")
		return float(value)
	if isinstance(current, str):
		if not isinstance(value, str):
			raise TypeError("Expected a string value")
		return value
	if isinstance(current, numpy.ndarray):
		return numpy.asarray(value, dtype=current.dtype)
	if value is current:
		return value
	raise TypeError(
		"Replacing structured value of type {} is not supported".format(
			type(current).__name__
		)
	)


class StructuredDocument:
	def __init__(self, context):
		self.context = context

	@property
	def controller(self):
		return self.context.controller

	def _require_scheme(self):
		scheme = self.controller.current_scheme
		if scheme is None:
			raise RuntimeError("No task type is currently selected")
		return scheme

	def _setting_getters(self):
		scheme = self._require_scheme()
		menu = getattr(scheme.confwidget, "sett", None)
		return _getter_map(menu) if menu is not None else {}

	def _common_getters(self):
		return _getter_map(self.context.common_settings.sett)

	def snapshot(self):
		scheme = self._require_scheme()
		spec = self.controller.current_spec
		text = (
			scheme.texteditor.toPlainText()
			if hasattr(scheme, "texteditor")
			else None
		)
		return {
			"task_type": {
				"index": self.controller.current_index,
				"id": spec.identifier,
				"title": spec.title,
			},
			"canvas": {
				"width": self.context.canvas.width(),
				"height": self.context.canvas.height(),
			},
			"common": {
				key: to_json_value(getter.get())
				for key, getter in self._common_getters().items()
			},
			"settings": {
				key: to_json_value(getter.get())
				for key, getter in self._setting_getters().items()
			},
			"text": text,
			"task": to_json_value(scheme.task, path="/task"),
		}

	def get(self, path=""):
		value = self.snapshot()
		for token in parse_pointer(path):
			value = _read_child(value, token)
		return value

	def _resolve_live(self, tokens):
		if not tokens:
			raise ValueError("The document root is not writable")
		root = tokens[0]
		scheme = self._require_scheme()

		if root == "task":
			value = scheme.task
			for token in tokens[1:-1]:
				value = _read_child(value, token)
			if len(tokens) == 1:
				raise ValueError("The task root is not replaceable")
			return ("child", value, tokens[-1])

		if root == "settings":
			if len(tokens) != 2:
				raise ValueError("Settings paths must address one serialized label")
			return ("getter", self._setting_getters()[tokens[1]], None)

		if root == "common":
			if len(tokens) != 2:
				raise ValueError("Common settings paths must address one serialized label")
			return ("getter", self._common_getters()[tokens[1]], None)

		if root == "text":
			if len(tokens) != 1 or not hasattr(scheme, "texteditor"):
				raise ValueError("This task does not expose editable document text")
			return ("text", scheme.texteditor, None)

		if root == "canvas":
			if len(tokens) != 2 or tokens[1] not in ("width", "height"):
				raise ValueError("Canvas path must be /canvas/width or /canvas/height")
			return ("canvas", tokens[1], None)

		raise ValueError("Document root {!r} is read-only or unknown".format(root))

	def _read_live(self, target):
		kind, owner, token = target
		if kind == "child":
			return _read_child(owner, token)
		if kind == "getter":
			return owner.get()
		if kind == "text":
			return owner.toPlainText()
		if kind == "canvas":
			return getattr(self.context.canvas, owner)()
		raise AssertionError("Unknown live target kind: {}".format(kind))

	def _write_live(self, target, value):
		kind, owner, token = target
		if kind == "child":
			_write_child(owner, token, value)
			return
		if kind == "getter":
			owner.set(_coerce_value(owner.get(), value))
			return
		if kind == "text":
			owner.setPlainText(_coerce_value(owner.toPlainText(), value))
			return
		if kind == "canvas":
			width = self.context.canvas.width()
			height = self.context.canvas.height()
			if owner == "width":
				width = _coerce_value(width, value)
			else:
				height = _coerce_value(height, value)
			self.context.legacy.resize_canvas(width, height)
			return
		raise AssertionError("Unknown live target kind: {}".format(kind))

	def set(self, path, value):
		result = self.patch([{"path": path, "value": value}])
		return result["values"][0]

	def patch(self, changes):
		if not isinstance(changes, list) or not changes:
			raise ValueError("Patch must contain at least one change")
		prepared = []
		for change in changes:
			if not isinstance(change, dict) or set(change) != {"path", "value"}:
				raise ValueError("Each patch change must contain only path and value")
			target = self._resolve_live(parse_pointer(change["path"]))
			prepared.append((change["path"], target, self._read_live(target), change["value"]))

		applied = []
		try:
			for path, target, old_value, new_value in prepared:
				self._write_live(target, new_value)
				applied.append((target, old_value))
		except Exception:
			for target, old_value in reversed(applied):
				self._write_live(target, old_value)
			raise

		self._require_scheme().redraw()
		values = [self.get(path) for path, _, _, _ in prepared]
		self.context.events.record(
			"document.patch",
			{
				"changes": [
					{"path": path, "value": value}
					for (path, _, _, _), value in zip(prepared, values)
				]
			},
		)
		return {"values": values}
