"""Application ownership and document-selection coordination."""

from dataclasses import dataclass, field

from .legacy import LegacyAdapter
from .task_registry import TASK_SPECS


class DocumentController:
	"""Own the active task document while legacy models are being migrated."""

	TITLE_ALIASES = {
		"Косой изгиб (Тип 2)": "Косой изгиб",
	}

	def __init__(self, context, task_specs):
		self.context = context
		self.task_specs = tuple(task_specs)
		self.scheme_types = []
		self.current_index = -1
		self.view = None

	def initialize_tasks(self, common_settings):
		if self.scheme_types:
			raise RuntimeError("Task instances have already been initialized")
		self.context.legacy.bind_common_settings(common_settings)
		self.scheme_types = [spec.create() for spec in self.task_specs]
		return self.scheme_types

	def bind_view(self, view):
		if self.view is not None and self.view is not view:
			raise RuntimeError("Document controller is already bound to a view")
		self.view = view

	@property
	def current_scheme(self):
		if self.current_index < 0:
			return None
		return self.scheme_types[self.current_index]

	@property
	def current_spec(self):
		if self.current_index < 0:
			return None
		return self.task_specs[self.current_index]

	def resolve_index(self, selector):
		if isinstance(selector, int):
			index = selector
		else:
			index = next(
				(
					i
					for i, spec in enumerate(self.task_specs)
					if selector in (spec.identifier, spec.title)
				),
				None,
			)
			if index is None:
				raise ValueError("Unknown task type: {}".format(selector))

		if index < 0 or index >= len(self.scheme_types):
			raise ValueError("Task index is out of range: {}".format(index))
		return index

	def select(self, selector):
		if self.view is None:
			raise RuntimeError("Document controller is not bound to a view")
		index = self.resolve_index(selector)
		scheme = self.scheme_types[index]
		changed = self.current_index != index

		# Legacy widgets may repaint while they are being attached, so publish
		# the active scheme before changing the widget hierarchy.
		self.context.legacy.activate_scheme(scheme)
		self.view.display_scheme(scheme, changed=changed)
		self.current_index = index
		self.context.legacy.activate_scheme(scheme)
		self.context.legacy.resize_canvas(*scheme.get_size())
		self.view.set_selected_index(index)
		return self.current_spec

	def select_by_title(self, title):
		return self.select(self.TITLE_ALIASES.get(title, title))

	def clear(self):
		if self.view is None:
			raise RuntimeError("Document controller is not bound to a view")
		self.current_index = -1
		self.view.display_empty()
		self.view.set_selected_index(-1)


@dataclass
class AppContext:
	app: object
	task_specs: tuple = TASK_SPECS
	legacy: LegacyAdapter = field(default_factory=LegacyAdapter)
	window: object = None
	central: object = None
	dev_server: object = None

	def __post_init__(self):
		self.task_specs = tuple(self.task_specs)
		self.controller = DocumentController(self, self.task_specs)

	def attach_window(self, window):
		if self.window is not None and self.window is not window:
			raise RuntimeError("Application context already owns a window")
		self.window = window

	def attach_central(self, central):
		if self.central is not None and self.central is not central:
			raise RuntimeError("Application context already owns a central widget")
		self.central = central

	@property
	def canvas_container(self):
		return self.central.container_paint

	@property
	def canvas(self):
		return self.canvas_container.curwidget

	@property
	def settings_container(self):
		return self.central.container_settings

	@property
	def settings(self):
		return self.settings_container.curwidget

	@property
	def common_settings(self):
		return self.central.confview
