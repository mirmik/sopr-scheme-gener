from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import taskconf_menu

APP = None
CONFVIEW = None
SCHEMETYPE = None
HSPLITTER = None
PAINT_CONTAINER = None

def angle(strt, fini):
	return math.atan2(fini.y()-strt.y(), fini.x()-strt.x())

class StyleWidget(QWidget):
	def __init__(self):
		super().__init__()

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
	def create_task_structure(self):
		raise NotImplementedError()

	def init_sections_buttons(self):
		self.add_button = QPushButton("Добавить секцию")
		self.del_button = QPushButton("Убрать секцию")

		self.butlayout = QHBoxLayout()

		self.butlayout.addWidget(self.add_button)
		self.butlayout.addWidget(self.del_button)

		self.add_button.clicked.connect(self.add_action)
		self.del_button.clicked.connect(self.del_action)

		self.vlayout.addLayout(self.butlayout)

	def __init__(self, sheme=None):
		super().__init__()

		self.shemetype = sheme

		if sheme:
			self.vlayout = QVBoxLayout()

			self.shemetype = sheme
			self.shemetype.font_size = CONFVIEW.font_size_getter
			self.shemetype.line_width = CONFVIEW.lwidth_getter

			self.create_task_structure()
			self.init_sections_buttons()

	def sections(self):
		return self.shemetype.task["sections"]

	def bsections(self):
		return self.shemetype.task["betsect"]

	def sectforces(self):
		return self.shemetype.task["sectforce"]

	def redraw(self):
		self.shemetype.paintwidget.repaint()

class TableWidget(QWidget):
	def __init__(self):
		super().__init__()

class ConfView(QWidget):
	"""Общие настройки"""
	def __init__(self, sheme=None):
		super().__init__()
		self.layout = QGridLayout()
		self.layout = QVBoxLayout()

		self.sett = taskconf_menu.TaskConfMenu()
		self.width_getter = self.sett.add("Ширина в px:", "int", "400")
		self.height_getter = self.sett.add("Высота в px:", "int", "200")
		self.font_size_getter = self.sett.add("Размер шрифта:", "int", "12")
		self.lwidth_getter = self.sett.add("Толщина линий:", "int", "2")
		self.arrow_size_getter = self.sett.add("Размер стрелок:", "int", "10")
		self.sett.updated.connect(self.updated)

		#self.layout.addWidget(self.sett)

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

def pretty_str(f, t):
	if (f == 1):
		return t
	else:
		if abs(float(f) - int(f)) < 0.0001:
			return str(int(f)) + t
		else:
			return str(f) + t
