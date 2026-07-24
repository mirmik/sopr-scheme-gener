"""Reusable always-on-top palette for document note editors."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
	QDialog,
	QGridLayout,
	QGroupBox,
	QHBoxLayout,
	QLabel,
	QPushButton,
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


class SymbolPaletteDialog(QDialog):
	def __init__(self, editor, parent=None):
		super().__init__(parent)
		self.editor = editor
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
		cursor = self.editor.textCursor()
		cursor.insertText(symbol)
		self.editor.setTextCursor(cursor)
		self.editor.setFocus(Qt.OtherFocusReason)


def add_symbol_text_editor(layout, editor):
	layout.addWidget(editor)
	button = QPushButton("Греческие буквы и символы…")
	button.setObjectName("open_symbol_palette")

	def show_palette():
		dialog = getattr(button, "_symbol_palette_dialog", None)
		if dialog is None:
			dialog = SymbolPaletteDialog(editor, button.window())
			button._symbol_palette_dialog = dialog
		dialog.show()
		dialog.raise_()
		dialog.activateWindow()

	button.clicked.connect(show_palette)
	layout.addWidget(button)
	return button
