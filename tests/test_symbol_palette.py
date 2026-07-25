import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QPushButton

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
