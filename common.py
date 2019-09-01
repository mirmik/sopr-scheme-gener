from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import taskconf_menu

APP = None
CONFVIEW = None
SCHEMETYPE = None
HSPLITTER = None
PAINT_CONTAINER = None

#class ELabel(QWidget):
#	def __init__(self, ltext, ftext, lwidth, fwidth):
#		super().__init__()
#
#		self.layout = QHBoxLayout()
#		self.label = QLabel(ltext)
#		self.edit = QLineEdit(ftext)
#
#		self.label.setFixedWidth(lwidth)
#		self.edit.setFixedWidth(fwidth)
#
#		self.layout.addWidget(self.label)
#		self.layout.addWidget(self.edit)
#
#		self.setLayout(self.layout)

class StyleWidget(QWidget):
	def __init__(self):
		super().__init__()

#class DataSettings:
#	def __init__(self):
#		self.width = 400
#		self.height = 200
#		self.font_size = 12

#datasettings = DataSettings()

class SchemeType:
	def __init__(self, name):
		self.name = name
		#self.datasettings = datasettings
	
	def setwidgets(self,confwidget, paintwidget, tablewidget):
		self.paintwidget = paintwidget
		self.confwidget = confwidget
		self.tablewidget = tablewidget
		self.confwidget.shemetype = self
		self.paintwidget.shemetype = self
		self.tablewidget.shemetype = self

		self.width_getter = CONFVIEW.width_getter
		self.height_getter = CONFVIEW.height_getter
		self.arrow_size_getter = CONFVIEW.arrow_size_getter

		self.confwidget.inittask()

	def updateSizeFields(self):
		pass
	#	CONFVIEW.width_getter.set(str(self.width))
	#	CONFVIEW.height_getter.set(str(self.height))

	def redraw(self):
		self.confwidget.redraw()

	def get_size(self):
		return (CONFVIEW.width_getter.get(), CONFVIEW.height_getter.get())

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
	def __init__(self, sheme=None):
		super().__init__()
		if sheme:
			self.shemetype = sheme
			self.shemetype.font_size = CONFVIEW.font_size_getter
			self.shemetype.line_width = CONFVIEW.lwidth_getter

	def sections(self):
		return self.shemetype.task["sections"]

	def bsections(self):
		return self.shemetype.task["betsect"]

	def sectforce(self):
		return self.shemetype.task["sectforce"]

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
		self.layout = QVBoxLayout()

		#self.width_edit = QLineEdit("800")
		#self.height_edit = QLineEdit("600")

		#self.width_label = QLabel("Ширина в px:")
		#self.height_label = QLabel("Высота в px:")

		self.sett = taskconf_menu.TaskConfMenu()
		self.width_getter = self.sett.add("Ширина в px:", "int", "400")
		self.height_getter = self.sett.add("Высота в px:", "int", "200")
		self.font_size_getter = self.sett.add("Размер шрифта:", "int", "12")
		self.lwidth_getter = self.sett.add("Толщина линий:", "int", "2")
		self.arrow_size_getter = self.sett.add("Размер стрелок:", "int", "10")
		self.sett.updated.connect(self.updated)

		#self.width_edit.editingFinished.connect(self.set_size)
		#self.height_edit.editingFinished.connect(self.set_size)

		#self.width_edit.setFixedWidth(100)
		#self.height_edit.setFixedWidth(100)

		#self.width_label.setFixedWidth(100)
		#self.height_label.setFixedWidth(100)

		#self.layout.addWidget(self.width_label,0,0)
		#self.layout.addWidget(self.height_label,1,0)
		#self.layout.addWidget(self.width_edit,0,1)
		#self.layout.addWidget(self.height_edit,1,1)

		self.layout.addWidget(self.sett)

		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		self.setLayout(self.layout)

	def updated(self):
		self.set_size() # И, попутно обновление по новой спецификации
		SCHEMETYPE.redraw()

	def size(self):
		return (self.width_getter.get(), self.height_getter.get())

	def set_size(self):
		sz = self.size()
		
		#SCHEMETYPE.datasettings.width = sz[0]
		#SCHEMETYPE.datasettings.height = sz[1]

		#oldsz = HSPLITTER.sizes()
		#oldszsumm = oldsz[0] + oldsz[1]
		#HSPLITTER.setSizes([sz[0], oldszsumm - sz[0]])
		PAINT_CONTAINER.resize(sz[0], sz[1])

def getLineWidth():
	return CONFVIEW.lwidth_getter.get()