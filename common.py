from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

CONFVIEW = None

class StyleWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.setStyleSheet("border: 1px solid black");
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class SchemeType:
	def __init__(self, name, confwidget, paintwidget, tablewidget):
		self.name = name
		self.paintwidget = paintwidget
		self.confwidget = confwidget
		self.tablewidget = tablewidget

		self.confwidget.shemetype = self
		self.paintwidget.shemetype = self
		self.tablewidget.shemetype = self

		self.task = self.confwidget.inittask()

class StubWidget(StyleWidget):
	def __init__(self, text):
		super().__init__()
		self.text = text
		self.layout = QVBoxLayout()
		self.label = QLabel(text)
		self.layout.addWidget(self.label)
		self.setLayout(self.layout)

class ConfWidget_Stub(StyleWidget):
	def __init__(self):
		super().__init__()
		self.text = "STUB"
		self.layout = QVBoxLayout()
		self.label = QLabel(self.text)
		self.layout.addWidget(self.label)
		self.setLayout(self.layout)

	def inittask(self):
		return {}

class TableWidget(QWidget):
	def __init__(self):
		super().__init__()

class ConfView(QWidget):
	"""Общие настройки"""

	def __init__(self):
		super().__init__()
		self.layout = QGridLayout()

		self.width_edit = QLineEdit("800")
		self.height_edit = QLineEdit("600")

		self.width_label = QLabel("Ширина в px:")
		self.height_label = QLabel("Высота в px:")

		self.width_edit.setFixedWidth(100)
		self.height_edit.setFixedWidth(100)

		self.width_label.setFixedWidth(100)
		self.height_label.setFixedWidth(100)

		self.layout.addWidget(self.width_label,0,0)
		self.layout.addWidget(self.height_label,1,0)
		self.layout.addWidget(self.width_edit,0,1)
		self.layout.addWidget(self.height_edit,1,1)

		#self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		self.setLayout(self.layout)

	def size(self):
		return (int(self.width_edit.text()), int(self.height_edit.text()))