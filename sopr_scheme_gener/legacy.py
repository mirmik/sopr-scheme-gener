"""Narrow compatibility boundary for the legacy global application contract."""

import common
import paintwdg


class LegacyAdapter:
	"""Own all writes to globals still consumed by legacy task modules."""

	def configure(self, app, debug=False, exit_on_render_error=False):
		common.DEBUG = debug
		common.APP = app
		if exit_on_render_error:
			paintwdg.set_EXIT_ON_ERROR()

	def set_error_reporter(self, reporter):
		paintwdg.set_ERROR_REPORTER(reporter)

	def create_common_settings(self):
		return common.ConfView()

	def create_stub(self, text):
		return common.StubWidget(text)

	def create_paint_widget_setter(self, canvas_container):
		return paintwdg.PaintWidgetSetter(canvas_container)

	def bind_common_settings(self, confview):
		common.CONFVIEW = confview

	def bind_splitter(self, splitter):
		common.HSPLITTER = splitter

	def bind_canvas_container(self, canvas_container):
		common.PAINT_CONTAINER = canvas_container

	def activate_scheme(self, scheme):
		common.SCHEMETYPE = scheme

	def resize_canvas(self, width, height):
		common.PAINT_CONTAINER.resize(width, height)
