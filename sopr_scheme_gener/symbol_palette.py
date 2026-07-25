"""Reusable always-on-top palette for document note editors."""

from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import (
	QApplication,
	QDialog,
	QGridLayout,
	QGroupBox,
	QHBoxLayout,
	QLabel,
	QLineEdit,
	QPlainTextEdit,
	QPushButton,
	QTableWidget,
	QTextEdit,
	QVBoxLayout,
)


SYMBOL_GROUPS = (
	(
		"Греческие строчные",
		(
			("alpha", "𝛼", "альфа"),
			("beta", "β", "бета"),
			("gamma", "γ", "гамма"),
			("delta", "δ", "дельта"),
			("epsilon", "ε", "эпсилон"),
			("zeta", "ζ", "дзета"),
			("eta", "η", "эта"),
			("theta", "θ", "тета"),
			("iota", "ι", "йота"),
			("kappa", "κ", "каппа"),
			("lambda", "λ", "лямбда"),
			("mu", "μ", "мю"),
			("nu", "ν", "ню"),
			("xi", "ξ", "кси"),
			("omicron", "ο", "омикрон"),
			("pi", "𝜋", "пи"),
			("rho", "ρ", "ро"),
			("sigma", "σ", "сигма"),
			("tau", "𝜏", "тау"),
			("upsilon", "υ", "ипсилон"),
			("phi", "φ", "фи"),
			("chi", "χ", "хи"),
			("psi", "ψ", "пси"),
			("omega", "ω", "омега"),
		),
	),
	(
		"Греческие прописные",
		(
			("Alpha", "Α", "альфа"),
			("Beta", "Β", "бета"),
			("Gamma", "Γ", "гамма"),
			("Delta", "Δ", "дельта"),
			("Epsilon", "Ε", "эпсилон"),
			("Zeta", "Ζ", "дзета"),
			("Eta", "Η", "эта"),
			("Theta", "Θ", "тета"),
			("Iota", "Ι", "йота"),
			("Kappa", "Κ", "каппа"),
			("Lambda", "Λ", "лямбда"),
			("Mu", "Μ", "мю"),
			("Nu", "Ν", "ню"),
			("Xi", "Ξ", "кси"),
			("Omicron", "Ο", "омикрон"),
			("Pi", "Π", "пи"),
			("Rho", "Ρ", "ро"),
			("Sigma", "Σ", "сигма"),
			("Tau", "Τ", "тау"),
			("Upsilon", "Υ", "ипсилон"),
			("Phi", "Φ", "фи"),
			("Chi", "Χ", "хи"),
			("Psi", "Ψ", "пси"),
			("Omega", "Ω", "омега"),
		),
	),
	(
		"Дополнительные символы",
		(
			("diameter", "⌀", "диаметр"),
			("degree", "°", "градус"),
			("squared", "²", "квадрат"),
			("cubed", "³", "куб"),
			("fourth_power", "⁴", "четвёртая степень"),
			("sqrt", "√", "корень"),
			("plus_minus", "±", "плюс-минус"),
			("multiply", "×", "умножение"),
			("middle_dot", "·", "средняя точка"),
			("not_equal", "≠", "не равно"),
			("less_equal", "≤", "меньше или равно"),
			("greater_equal", "≥", "больше или равно"),
			("infinity", "∞", "бесконечность"),
			("approximately", "≈", "приблизительно"),
			("arrow_right", "→", "стрелка вправо"),
		),
	),
)


def _is_descendant(widget, ancestor):
	while widget is not None:
		if widget is ancestor:
			return True
		widget = widget.parentWidget()
	return False


def _configuration_widget(button):
	widget = button.parentWidget()
	while widget is not None:
		if hasattr(widget, "shemetype"):
			return widget
		widget = widget.parentWidget()
	return None


def _ancestor_table(widget):
	while widget is not None:
		if isinstance(widget, QTableWidget):
			return widget
		widget = widget.parentWidget()
	return None


def _table_column_accepts_symbols(table, column):
	columns = getattr(table, "columns", ())
	return 0 <= column < len(columns) and columns[column].type == "str"


class _TableTextTarget:
	def __init__(
		self,
		table,
		row,
		column,
		position=None,
		selection_start=-1,
		selection_length=0,
	):
		self.table = table
		self.row = row
		self.column = column
		self.position = position
		self.selection_start = selection_start
		self.selection_length = selection_length

	def insert(self, symbol):
		item = self.table.item(self.row, self.column)
		if item is None:
			return
		text = item.text()
		position = len(text) if self.position is None else self.position
		position = max(0, min(position, len(text)))
		if self.selection_start >= 0 and self.selection_length:
			start = max(0, min(self.selection_start, len(text)))
			end = max(start, min(start + self.selection_length, len(text)))
			text = text[:start] + symbol + text[end:]
			position = start + len(symbol)
		else:
			text = text[:position] + symbol + text[position:]
			position += len(symbol)
		self.table.setCurrentCell(self.row, self.column)
		item.setText(text)
		self.position = position
		self.selection_start = -1
		self.selection_length = 0


class _SymbolTargetTracker(QObject):
	def __init__(self, button, editor):
		super().__init__(button)
		self.button = button
		self.editor = editor
		self.target = editor
		QApplication.instance().focusChanged.connect(self.remember_target)

	def remember_target(self, old, new):
		container = _configuration_widget(self.button)
		if container is None:
			return
		for widget in (new, old):
			if widget is None or not _is_descendant(widget, container):
				continue
			target = _target_from_widget(widget)
			if target is not None:
				self.target = target
				return
			if (
				isinstance(widget, QLineEdit)
				and widget.property("symbol_palette_text") is False
			):
				self.target = self.editor
				return

	def current_target(self):
		container = _configuration_widget(self.button)
		if isinstance(self.target, _TableTextTarget):
			if container is not None and _is_descendant(
				self.target.table,
				container,
			):
				return self.target
			return self.editor
		if container is not None and _is_descendant(self.target, container):
			return self.target
		return self.editor


def _target_from_widget(widget):
	if isinstance(widget, (QTextEdit, QPlainTextEdit)):
		return widget
	if isinstance(widget, QLineEdit):
		table = _ancestor_table(widget)
		if table is not None:
			row = table.currentRow()
			column = table.currentColumn()
			if _table_column_accepts_symbols(table, column):
				return _TableTextTarget(
					table,
					row,
					column,
					position=widget.cursorPosition(),
					selection_start=widget.selectionStart(),
					selection_length=len(widget.selectedText()),
				)
			return None
		if widget.property("symbol_palette_text") is True:
			return widget
	if isinstance(widget, QTableWidget):
		row = widget.currentRow()
		column = widget.currentColumn()
		if row >= 0 and _table_column_accepts_symbols(widget, column):
			return _TableTextTarget(widget, row, column)
	return None


def _insert_symbol(target, symbol):
	if isinstance(target, _TableTextTarget):
		target.insert(symbol)
		return
	if isinstance(target, QLineEdit):
		target.insert(symbol)
		target.setFocus(Qt.OtherFocusReason)
		return
	cursor = target.textCursor()
	cursor.insertText(symbol)
	target.setTextCursor(cursor)
	target.setFocus(Qt.OtherFocusReason)


class SymbolPaletteDialog(QDialog):
	def __init__(self, target_provider, parent=None):
		super().__init__(parent)
		self.target_provider = (
			target_provider
			if callable(target_provider)
			else lambda: target_provider
		)
		self.setObjectName("symbol_palette_dialog")
		self.setWindowTitle("Греческие буквы и специальные символы")
		self.setWindowFlags(
			self.windowFlags() | Qt.Tool | Qt.WindowStaysOnTopHint
		)

		main_layout = QVBoxLayout()
		main_layout.addWidget(
			QLabel("Нажмите символ, чтобы вставить его в позицию курсора.")
		)
		for title, symbols in SYMBOL_GROUPS:
			group = QGroupBox(title)
			grid = QGridLayout()
			for index, (name, symbol, description) in enumerate(symbols):
				button = QPushButton(symbol)
				button.setObjectName("symbol_{}".format(name))
				button.setToolTip(description)
				button.setFixedSize(36, 30)
				button.clicked.connect(
					lambda _checked=False, value=symbol: self.insert_symbol(value)
				)
				grid.addWidget(button, index // 12, index % 12)
			group.setLayout(grid)
			main_layout.addWidget(group)

		close_row = QHBoxLayout()
		close_row.addStretch()
		close_button = QPushButton("Закрыть")
		close_button.clicked.connect(self.hide)
		close_row.addWidget(close_button)
		main_layout.addLayout(close_row)
		self.setLayout(main_layout)

	def insert_symbol(self, symbol):
		target = self.target_provider()
		if target is not None:
			_insert_symbol(target, symbol)


def add_symbol_text_editor(layout, editor):
	layout.addWidget(editor)
	button = QPushButton("Греческие буквы и символы…")
	button.setObjectName("open_symbol_palette")
	tracker = _SymbolTargetTracker(button, editor)
	button._symbol_target_tracker = tracker

	def show_palette():
		dialog = getattr(button, "_symbol_palette_dialog", None)
		if dialog is None:
			dialog = SymbolPaletteDialog(tracker.current_target, button.window())
			button._symbol_palette_dialog = dialog
		dialog.show()
		dialog.raise_()
		dialog.activateWindow()

	button.clicked.connect(show_palette)
	layout.addWidget(button)
	return button
