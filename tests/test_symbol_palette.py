import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QLineEdit, QPushButton

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def _context():
	return create_runtime(
		build_parser().parse_args(["--type", "beams", "--no-maximize"])
	)


def test_every_task_note_editor_has_a_symbol_palette_button():
	context = _context()
	try:
		for spec in context.task_specs:
			context.controller.select(spec.identifier)
			button = context.controller.current_scheme.confwidget.findChild(
				QPushButton,
				"open_symbol_palette",
			)
			assert button is not None, spec.identifier
	finally:
		context.window.close()


def test_symbol_palette_is_always_on_top_and_inserts_at_cursor():
	context = _context()
	try:
		scheme = context.controller.current_scheme
		editor = scheme.texteditor
		editor.setPlainText("F=")
		cursor = editor.textCursor()
		cursor.movePosition(QTextCursor.End)
		editor.setTextCursor(cursor)

		open_button = scheme.confwidget.findChild(
			QPushButton,
			"open_symbol_palette",
		)
		open_button.click()
		context.app.processEvents()
		dialog = open_button._symbol_palette_dialog

		assert dialog.isVisible()
		assert dialog.windowFlags() & Qt.WindowStaysOnTopHint

		dialog.findChild(QPushButton, "symbol_alpha").click()
		dialog.findChild(QPushButton, "symbol_squared").click()
		dialog.findChild(QPushButton, "symbol_fourth_power").click()
		assert editor.toPlainText() == "F=𝛼²⁴"
	finally:
		context.window.close()


def test_symbol_palette_inserts_into_active_table_text_cell():
	context = _context()
	try:
		context.controller.select("column-stability")
		scheme = context.controller.current_scheme
		conf = scheme.confwidget
		table = conf.node_table
		item = table.item(0, 2)
		table.setCurrentCell(0, 2)
		table.editItem(item)
		context.app.processEvents()
		cell_editor = context.app.focusWidget()
		assert isinstance(cell_editor, QLineEdit)
		cell_editor.setCursorPosition(len(cell_editor.text()))

		open_button = conf.findChild(QPushButton, "open_symbol_palette")
		open_button.click()
		context.app.processEvents()
		dialog = open_button._symbol_palette_dialog
		dialog.findChild(QPushButton, "symbol_alpha").click()

		assert item.text() == "F𝛼"
		assert scheme.task["nodes"][0].load_text == "F𝛼"
	finally:
		context.window.close()


def test_symbol_palette_inserts_into_string_setting_and_marks_numeric_fields():
	context = _context()
	try:
		context.controller.select("frames")
		scheme = context.controller.current_scheme
		conf = scheme.confwidget
		open_button = conf.findChild(QPushButton, "open_symbol_palette")
		string_editor = next(
			editor
			for editor in conf.findChildren(QLineEdit)
			if editor.property("symbol_palette_text") is True
		)
		numeric_editor = next(
			editor
			for editor in conf.findChildren(QLineEdit)
			if editor.property("symbol_palette_text") is False
		)

		string_editor.setFocus()
		string_editor.setCursorPosition(len(string_editor.text()))
		context.app.processEvents()
		open_button.click()
		context.app.processEvents()
		dialog = open_button._symbol_palette_dialog
		dialog.findChild(QPushButton, "symbol_fourth_power").click()
		assert string_editor.text().endswith("⁴")
		assert numeric_editor.property("symbol_palette_text") is False
	finally:
		context.window.close()
