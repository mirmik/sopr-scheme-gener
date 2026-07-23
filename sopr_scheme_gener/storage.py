"""Versioned, non-executable JSON documents for sopr-scheme-gener."""

from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import tempfile

import numpy

from .document import _getter_map, to_json_value
from .legacy_storage import load_trusted_pickle


FORMAT_NAME = "sopr-scheme-document"
FORMAT_VERSION = 1
MAX_DOCUMENT_BYTES = 10 * 1024 * 1024

# Model classes are nested in each legacy ConfWidget. The JSON file stores only
# these short aliases; it never supplies a module or class to import.
TASK_OBJECT_TYPES = {
	"axial-torsion": ("sect", "betsect", "sectforce"),
	"beams": ("sect", "betsect", "sectforce"),
	"rod-system-1": ("sect", "betsect"),
	"rod-system-2": ("sect",),
	"plate": ("sect", "betsect", "sectforce"),
	"frames": ("sect", "betsect", "sectforce", "label"),
	"oblique-bending": ("sect", "betsect", "sectforce"),
	"eccentric-bending": ("sect",),
	"stress-cube": ("sect", "label"),
	"shafts-pipes": ("sect",),
	"spatial-beams": ("sect", "node", "label"),
}
TASK_SCHEMA_VERSIONS = {task_id: 1 for task_id in TASK_OBJECT_TYPES}
TASK_MIGRATIONS = {task_id: {} for task_id in TASK_OBJECT_TYPES}


class DocumentFormatError(ValueError):
	pass


@dataclass(frozen=True)
class _Reference:
	path: str


def _pointer(path, token):
	token = str(token).replace("~", "~0").replace("/", "~1")
	return "{}/{}".format(path, token)


class TaskPayloadCodec:
	def __init__(self, task_id, scheme):
		try:
			aliases = TASK_OBJECT_TYPES[task_id]
		except KeyError:
			raise DocumentFormatError("No task codec registered for {!r}".format(task_id))
		confwidget = scheme.confwidget
		self.classes = {}
		for alias in aliases:
			model_class = getattr(type(confwidget), alias, None)
			if not isinstance(model_class, type):
				raise DocumentFormatError(
					"Task {!r} does not provide model type {!r}".format(
						task_id,
						alias,
					)
				)
			self.classes[alias] = model_class
		self.aliases = {model_class: alias for alias, model_class in self.classes.items()}

	def encode(self, value):
		return self._encode(value, "", {})

	def _encode(self, value, path, seen):
		if value is None or isinstance(value, (bool, int, str)):
			return value
		if isinstance(value, float):
			if not math.isfinite(value):
				raise DocumentFormatError("Non-finite number at {}".format(path or "/"))
			return value
		if isinstance(value, numpy.generic):
			return self._encode(value.item(), path, seen)

		value_id = id(value)
		previous = seen.get(value_id)
		if previous is not None and previous[0] is value:
			return {"$ref": previous[1]}
		seen[value_id] = (value, path or "/")

		if isinstance(value, numpy.ndarray):
			if value.dtype.kind not in "biuf":
				raise DocumentFormatError(
					"Unsupported NumPy dtype at {}: {}".format(path or "/", value.dtype)
				)
			return {
				"$type": "ndarray",
				"dtype": str(value.dtype),
				"items": [
					self._encode(item, _pointer(_pointer(path, "items"), index), seen)
					for index, item in enumerate(value.tolist())
				],
			}
		if isinstance(value, tuple):
			return {
				"$type": "tuple",
				"items": [
					self._encode(item, _pointer(path, index), seen)
					for index, item in enumerate(value)
				],
			}

		if isinstance(value, list):
			return [
				self._encode(item, _pointer(path, index), seen)
				for index, item in enumerate(value)
			]
		if isinstance(value, dict):
			result = {}
			for key, item in value.items():
				if not isinstance(key, str):
					raise DocumentFormatError(
						"Task object key at {} is not a string".format(path or "/")
					)
				result[key] = self._encode(item, _pointer(path, key), seen)
			return result

		alias = self.aliases.get(type(value))
		if alias is None:
			raise DocumentFormatError(
				"Unsupported task object at {}: {}".format(
					path or "/",
					type(value).__qualname__,
				)
			)
		return {
			"$type": "object",
			"class": alias,
			"fields": {
				key: self._encode(item, _pointer(path, key), seen)
				for key, item in value.__dict__.items()
				if not key.startswith("_")
			},
		}

	def decode(self, payload):
		paths = {}
		value = self._decode(payload, "", paths)
		return self._resolve_references(value, paths, set())

	def _decode(self, value, path, paths):
		if value is None or isinstance(value, (bool, int, str)):
			return value
		if isinstance(value, float):
			if not math.isfinite(value):
				raise DocumentFormatError("Non-finite number at {}".format(path or "/"))
			return value
		if isinstance(value, list):
			result = []
			paths[path or "/"] = result
			for index, item in enumerate(value):
				result.append(self._decode(item, _pointer(path, index), paths))
			return result
		if not isinstance(value, dict):
			raise DocumentFormatError("Invalid task value at {}".format(path or "/"))

		if set(value) == {"$ref"}:
			reference = value["$ref"]
			if not isinstance(reference, str) or not reference.startswith("/"):
				raise DocumentFormatError("Invalid task reference at {}".format(path or "/"))
			return _Reference(reference)

		value_type = value.get("$type")
		if value_type == "tuple":
			if set(value) != {"$type", "items"} or not isinstance(value["items"], list):
				raise DocumentFormatError("Malformed tuple at {}".format(path or "/"))
			result = tuple(
				self._decode(item, _pointer(path, index), paths)
				for index, item in enumerate(value["items"])
			)
			paths[path or "/"] = result
			return result
		if value_type == "ndarray":
			if set(value) != {"$type", "dtype", "items"}:
				raise DocumentFormatError("Malformed ndarray at {}".format(path or "/"))
			try:
				dtype = numpy.dtype(value["dtype"])
			except (TypeError, ValueError):
				raise DocumentFormatError("Invalid ndarray dtype at {}".format(path or "/"))
			if dtype.kind not in "biuf":
				raise DocumentFormatError("Unsupported ndarray dtype at {}".format(path or "/"))
			items = self._decode(value["items"], _pointer(path, "items"), paths)
			result = numpy.asarray(items, dtype=dtype)
			paths[path or "/"] = result
			return result
		if value_type == "object":
			if set(value) != {"$type", "class", "fields"}:
				raise DocumentFormatError("Malformed model object at {}".format(path or "/"))
			try:
				model_class = self.classes[value["class"]]
			except (KeyError, TypeError):
				raise DocumentFormatError(
					"Unknown model class at {}: {!r}".format(
						path or "/",
						value.get("class"),
					)
				)
			if not isinstance(value["fields"], dict):
				raise DocumentFormatError("Model fields must be an object")
			result = model_class.__new__(model_class)
			paths[path or "/"] = result
			for key, item in value["fields"].items():
				if not isinstance(key, str) or key.startswith("_"):
					raise DocumentFormatError("Invalid model field {!r}".format(key))
				setattr(result, key, self._decode(item, _pointer(path, key), paths))
			return result
		if value_type is not None:
			raise DocumentFormatError(
				"Unknown task value type at {}: {!r}".format(path or "/", value_type)
			)

		result = {}
		paths[path or "/"] = result
		for key, item in value.items():
			if not isinstance(key, str):
				raise DocumentFormatError("Task object key is not a string")
			result[key] = self._decode(item, _pointer(path, key), paths)
		return result

	def _resolve_references(self, value, paths, seen):
		if isinstance(value, _Reference):
			try:
				return paths[value.path]
			except KeyError:
				raise DocumentFormatError("Unknown task reference: {}".format(value.path))
		if value is None or isinstance(value, (bool, int, float, str, numpy.ndarray)):
			return value
		value_id = id(value)
		if value_id in seen:
			return value
		seen.add(value_id)
		if isinstance(value, list):
			for index, item in enumerate(value):
				value[index] = self._resolve_references(item, paths, seen)
			return value
		if isinstance(value, tuple):
			return tuple(self._resolve_references(item, paths, seen) for item in value)
		if isinstance(value, dict):
			for key, item in value.items():
				value[key] = self._resolve_references(item, paths, seen)
			return value
		if type(value) in self.aliases:
			for key, item in value.__dict__.items():
				setattr(value, key, self._resolve_references(item, paths, seen))
			return value
		raise DocumentFormatError("Unexpected decoded task object")


def _menu_values(menu):
	return {
		key: to_json_value(getter.get())
		for key, getter in _getter_map(menu).items()
	}


def _section_values(section):
	return {
		"section_type": section.section_type.get(),
		"base_section_widget": _menu_values(section.base_section_widget),
		"rect_minus_rect": _menu_values(section.rect_minus_rect),
		"main_section_0": _menu_values(section.main_section_0),
		"hrect": _menu_values(section.hrect),
	}


def _validated_getter_value(getter, value, name):
	def validate(value_type, candidate, suffix=""):
		location = "{}{}".format(name, suffix)
		if value_type in ("text", "str"):
			if not isinstance(candidate, str):
				raise DocumentFormatError("{} must be a string".format(location))
		elif value_type == "int":
			if not isinstance(candidate, int) or isinstance(candidate, bool):
				raise DocumentFormatError("{} must be an integer".format(location))
		elif value_type == "float":
			if (
				not isinstance(candidate, (int, float))
				or isinstance(candidate, bool)
				or not math.isfinite(candidate)
			):
				raise DocumentFormatError("{} must be a finite number".format(location))
		elif value_type == "bool":
			if not isinstance(candidate, bool):
				raise DocumentFormatError("{} must be a boolean".format(location))
		elif value_type == "list":
			if candidate not in getter.parent.vars:
				raise DocumentFormatError(
					"{} is not one of the supported values".format(location)
				)
		else:
			raise DocumentFormatError(
				"{} uses unsupported setting type {!r}".format(location, value_type)
			)

	if isinstance(getter.type, tuple):
		if not isinstance(value, list) or len(value) != len(getter.type):
			raise DocumentFormatError("{} must be a fixed-size array".format(name))
		for index, (value_type, item) in enumerate(zip(getter.type, value)):
			validate(value_type, item, "[{}]".format(index))
	else:
		validate(getter.type, value)
	return value


def _validated_menu_values(menu, values, name):
	if not isinstance(values, dict):
		raise DocumentFormatError("{} must be a JSON object".format(name))
	getters = _getter_map(menu)
	if set(values) != set(getters):
		raise DocumentFormatError(
			"{} keys do not match this application version".format(name)
		)
	return [
		(
			getters[key],
			_validated_getter_value(
				getters[key],
				values[key],
				"{}/{}".format(name, key),
			),
		)
		for key in getters
	]


def _validated_section_values(section, values):
	if not isinstance(values, dict):
		raise DocumentFormatError("extensions.section must be a JSON object")
	expected = {
		"section_type",
		"base_section_widget",
		"rect_minus_rect",
		"main_section_0",
		"hrect",
	}
	if set(values) != expected:
		raise DocumentFormatError("extensions.section has an invalid schema")
	return {
		"section_type": _validated_getter_value(
			section.section_type,
			values["section_type"],
			"extensions.section/section_type",
		),
		"menus": [
			_validated_menu_values(
				section.base_section_widget,
				values["base_section_widget"],
				"extensions.section.base_section_widget",
			),
			_validated_menu_values(
				section.rect_minus_rect,
				values["rect_minus_rect"],
				"extensions.section.rect_minus_rect",
			),
			_validated_menu_values(
				section.main_section_0,
				values["main_section_0"],
				"extensions.section.main_section_0",
			),
			_validated_menu_values(
				section.hrect,
				values["hrect"],
				"extensions.section.hrect",
			),
		],
	}


class DocumentStore:
	def __init__(self, context):
		self.context = context

	def to_data(self):
		controller = self.context.controller
		scheme = controller.current_scheme
		if scheme is None:
			raise RuntimeError("No task type is currently selected")
		spec = controller.current_spec
		snapshot = self.context.document.snapshot()
		extensions = {}
		if hasattr(scheme, "section_container"):
			extensions["section"] = _section_values(scheme.section_container)
		return {
			"format": FORMAT_NAME,
			"version": FORMAT_VERSION,
			"task_type": spec.identifier,
			"canvas": snapshot["canvas"],
			"common": snapshot["common"],
			"settings": snapshot["settings"],
			"text": snapshot["text"],
			"task": {
				"version": TASK_SCHEMA_VERSIONS[spec.identifier],
				"payload": TaskPayloadCodec(spec.identifier, scheme).encode(scheme.task),
			},
			"extensions": extensions,
		}

	def save(self, path):
		path = Path(path)
		data = json.dumps(
			self.to_data(),
			ensure_ascii=False,
			indent=2,
			allow_nan=False,
		) + "\n"
		path.parent.mkdir(parents=True, exist_ok=True)
		with tempfile.NamedTemporaryFile(
			"w",
			encoding="utf-8",
			dir=str(path.parent),
			prefix=".{}.".format(path.name),
			suffix=".tmp",
			delete=False,
		) as stream:
			temp_path = Path(stream.name)
			stream.write(data)
			stream.flush()
			os.fsync(stream.fileno())
		try:
			os.replace(str(temp_path), str(path))
		finally:
			if temp_path.exists():
				temp_path.unlink()
		self.context.events.record("document.saved", {"path": str(path)})
		return path

	def load(self, path):
		path = Path(path)
		if path.stat().st_size > MAX_DOCUMENT_BYTES:
			raise DocumentFormatError("Document exceeds the 10 MiB size limit")
		try:
			data = json.loads(
				path.read_text(encoding="utf-8"),
				parse_constant=lambda value: (_ for _ in ()).throw(
					DocumentFormatError("Invalid JSON number: {}".format(value))
				),
			)
		except (UnicodeDecodeError, json.JSONDecodeError) as exc:
			raise DocumentFormatError("Invalid JSON document: {}".format(exc))
		result = self.load_data(data)
		self.context.events.record("document.opened", {"path": str(path)})
		return result

	def load_data(self, data):
		prepared = self._prepare(data)
		self._apply(prepared)
		return self.to_data()

	def _prepare(self, data):
		if not isinstance(data, dict):
			raise DocumentFormatError("Document root must be a JSON object")
		required = {
			"format",
			"version",
			"task_type",
			"canvas",
			"common",
			"settings",
			"text",
			"task",
			"extensions",
		}
		if set(data) != required:
			raise DocumentFormatError("Document root has an invalid schema")
		if data["format"] != FORMAT_NAME:
			raise DocumentFormatError("Unknown document format")
		if data["version"] != FORMAT_VERSION:
			raise DocumentFormatError(
				"Unsupported document version: {!r}".format(data["version"])
			)
		task_id = data["task_type"]
		if not isinstance(task_id, str):
			raise DocumentFormatError("task_type must be a string")
		try:
			index = self.context.controller.resolve_index(task_id)
		except ValueError:
			raise DocumentFormatError("Unknown task type: {!r}".format(task_id))
		scheme = self.context.controller.scheme_types[index]

		canvas = data["canvas"]
		if (
			not isinstance(canvas, dict)
			or set(canvas) != {"width", "height"}
			or any(
				not isinstance(canvas[key], int)
				or isinstance(canvas[key], bool)
				or canvas[key] <= 0
				or canvas[key] > 10000
				for key in ("width", "height")
			)
		):
			raise DocumentFormatError(
				"canvas must contain integer dimensions between 1 and 10000"
			)
		common = _validated_menu_values(
			self.context.common_settings.sett,
			data["common"],
			"common",
		)
		settings = _validated_menu_values(
			scheme.confwidget.sett,
			data["settings"],
			"settings",
		)
		if data["text"] is not None and not isinstance(data["text"], str):
			raise DocumentFormatError("text must be a string or null")
		if not isinstance(data["extensions"], dict):
			raise DocumentFormatError("extensions must be a JSON object")
		section = None
		has_section = hasattr(scheme, "section_container")
		if set(data["extensions"]) != ({"section"} if has_section else set()):
			raise DocumentFormatError("extensions do not match this task type")
		if has_section:
			section = _validated_section_values(
				scheme.section_container,
				data["extensions"]["section"],
			)
		task_data = data["task"]
		if not isinstance(task_data, dict) or set(task_data) != {"version", "payload"}:
			raise DocumentFormatError("task must contain version and payload")
		task_version = task_data["version"]
		if not isinstance(task_version, int) or isinstance(task_version, bool):
			raise DocumentFormatError("task.version must be an integer")
		current_task_version = TASK_SCHEMA_VERSIONS[task_id]
		payload = task_data["payload"]
		while task_version < current_task_version:
			try:
				migration = TASK_MIGRATIONS[task_id][task_version]
			except KeyError:
				raise DocumentFormatError(
					"No migration for task {!r} version {}".format(
						task_id,
						task_version,
					)
				)
			payload = migration(payload)
			task_version += 1
		if task_version != current_task_version:
			raise DocumentFormatError(
				"Unsupported task schema version for {!r}: {}".format(
					task_id,
					task_version,
				)
			)
		task = TaskPayloadCodec(task_id, scheme).decode(payload)
		if not isinstance(task, dict):
			raise DocumentFormatError("task payload must decode to an object")
		return {
			"task_id": task_id,
			"scheme": scheme,
			"canvas": canvas,
			"common": common,
			"settings": settings,
			"text": data["text"],
			"section": section,
			"task": task,
		}

	def _apply(self, prepared):
		self.context.controller.select(prepared["task_id"])
		scheme = prepared["scheme"]
		scheme.paintwidget.prevent_errors = True
		scheme.confwidget.prevent_errors = True
		try:
			for getter, value in prepared["common"]:
				getter.set(value)
			for getter, value in prepared["settings"]:
				getter.set(value)
			if prepared["section"] is not None:
				section = scheme.section_container
				section.section_type.set(prepared["section"]["section_type"])
				for menu_values in prepared["section"]["menus"]:
					for getter, value in menu_values:
						getter.set(value)
			if hasattr(scheme, "texteditor") and prepared["text"] is not None:
				scheme.texteditor.setPlainText(prepared["text"])
			scheme.task = prepared["task"]
			scheme.confwidget.clean_and_update_interface()
			self.context.legacy.resize_canvas(
				prepared["canvas"]["width"],
				prepared["canvas"]["height"],
			)
		finally:
			scheme.paintwidget.prevent_errors = False
			scheme.confwidget.prevent_errors = False
		scheme.redraw()
		self.context.events.record(
			"document.loaded",
			{"task_type": prepared["task_id"]},
		)

	def import_trusted_legacy(self, path):
		document = load_trusted_pickle(path)
		if (
			not isinstance(document, list)
			or not document
			or not isinstance(document[0], (list, tuple))
			or len(document[0]) != 2
			or document[0][0] != "name"
		):
			raise DocumentFormatError("Malformed trusted legacy document")
		title = document[0][1]
		self.context.controller.select_by_title(title)
		self.context.controller.current_scheme.deserialize(document)
		self.context.events.record(
			"document.legacy_imported",
			{"path": str(Path(path))},
		)
		return self.to_data()
