from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

APP = None
CONFVIEW = None
SCHEMETYPE = None
HSPLITTER = None
PAINT_CONTAINER = None

class ELabel(QWidget):
	def __init__(self, ltext, ftext, lwidth, fwidth):
		super().__init__()

		self.layout = QHBoxLayout()
		self.label = QLabel(ltext)
		self.edit = QLineEdit(ftext)

		self.label.setFixedWidth(lwidth)
		self.edit.setFixedWidth(fwidth)

		self.layout.addWidget(self.label)
		self.layout.addWidget(self.edit)

		self.setLayout(self.layout)

class StyleWidget(QWidget):
	def __init__(self):
		super().__init__()

class DataSettings:
	def __init__(self):
		self.width = 400
		self.height = 200

datasettings = DataSettings()

class SchemeType:
	def __init__(self, name):
		self.name = name
		self.datasettings = datasettings
	
	def setwidgets(self,confwidget, paintwidget, tablewidget):
		self.paintwidget = paintwidget
		self.confwidget = confwidget
		self.tablewidget = tablewidget
		self.confwidget.shemetype = self
		self.paintwidget.shemetype = self
		self.tablewidget.shemetype = self
		self.confwidget.inittask()

	def updateDataSettingsVM(self):
		CONFVIEW.width_edit.setText(str(self.datasettings.width))
		CONFVIEW.height_edit.setText(str(self.datasettings.height))

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


class ConfWidget(StyleWidget):
	def redraw(self):
		self.shemetype.paintwidget.repaint()

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

		self.width_edit.editingFinished.connect(self.set_size)
		self.height_edit.editingFinished.connect(self.set_size)

		self.width_edit.setFixedWidth(100)
		self.height_edit.setFixedWidth(100)

		self.width_label.setFixedWidth(100)
		self.height_label.setFixedWidth(100)

		self.layout.addWidget(self.width_label,0,0)
		self.layout.addWidget(self.height_label,1,0)
		self.layout.addWidget(self.width_edit,0,1)
		self.layout.addWidget(self.height_edit,1,1)

		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		self.setLayout(self.layout)

	def size(self):
		return (int(self.width_edit.text()), int(self.height_edit.text()))

	def set_size(self):
		sz = self.size()
		
		SCHEMETYPE.datasettings.width = sz[0]
		SCHEMETYPE.datasettings.height = sz[1]

		oldsz = HSPLITTER.sizes()
		oldszsumm = oldsz[0] + oldsz[1]
		#HSPLITTER.setSizes([sz[0], oldszsumm - sz[0]])
		PAINT_CONTAINER.resize(sz[0], sz[1])