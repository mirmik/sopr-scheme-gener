from pathlib import Path

import pytest

from sopr_scheme_gener.context import DocumentController, EventJournal


class FakeScheme:
	def __init__(self, size):
		self.size = size

	def get_size(self):
		return self.size


class FakeSpec:
	def __init__(self, identifier, title, scheme):
		self.identifier = identifier
		self.title = title
		self.scheme = scheme

	def create(self):
		return self.scheme


class FakeLegacy:
	def __init__(self):
		self.common_settings = None
		self.active_scheme = None
		self.canvas_size = None

	def bind_common_settings(self, settings):
		self.common_settings = settings

	def activate_scheme(self, scheme):
		self.active_scheme = scheme

	def resize_canvas(self, width, height):
		self.canvas_size = (width, height)


class FakeView:
	def __init__(self):
		self.scheme = None
		self.changed = None
		self.selected_index = None
		self.empty = False

	def display_scheme(self, scheme, changed):
		self.scheme = scheme
		self.changed = changed

	def set_selected_index(self, index):
		self.selected_index = index

	def display_empty(self):
		self.empty = True


def make_controller():
	legacy = FakeLegacy()
	context = type(
		"Context",
		(),
		{"legacy": legacy, "events": EventJournal()},
	)()
	specs = (
		FakeSpec("first", "Первый", FakeScheme((400, 250))),
		FakeSpec("second", "Второй", FakeScheme((500, 300))),
	)
	controller = DocumentController(context, specs)
	controller.initialize_tasks(object())
	view = FakeView()
	controller.bind_view(view)
	return controller, legacy, view


def test_document_controller_owns_selection_and_legacy_publication():
	controller, legacy, view = make_controller()

	spec = controller.select("second")

	assert spec.identifier == "second"
	assert controller.current_index == 1
	assert controller.current_spec is spec
	assert controller.current_scheme is view.scheme
	assert legacy.active_scheme is controller.current_scheme
	assert legacy.canvas_size == (500, 300)
	assert view.selected_index == 1
	assert view.changed is True


def test_document_controller_accepts_index_title_and_rejects_unknown_selector():
	controller, _, view = make_controller()

	controller.select(0)
	assert controller.current_spec.identifier == "first"
	controller.select("Первый")
	assert view.changed is False

	with pytest.raises(ValueError, match="Unknown task type"):
		controller.select("missing")


def test_only_legacy_adapter_accesses_common_globals():
	package_dir = Path(__file__).resolve().parents[1] / "sopr_scheme_gener"
	offenders = []
	for path in package_dir.glob("*.py"):
		if path.name == "legacy.py":
			continue
		source = path.read_text(encoding="utf-8")
		if "import common" in source or "from common" in source or "common." in source:
			offenders.append(path.name)
	assert offenders == []
