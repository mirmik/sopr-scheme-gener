from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import util
import math
import taskconf_menu
import pickle

APP = None
CONFVIEW = None
SCHEMETYPE = None
HSPLITTER = None
PAINT_CONTAINER = None

def angle(strt, fini):
	return math.atan2(fini.y()-strt.y(), fini.x()-strt.x())

def do_serialize(obj):
	if obj.__class__ == QTextEdit:
		return obj.toPlainText()

	if hasattr(obj, "serialize"):
		return obj.serialize()
	else:
		return pickle.dumps(obj)

def do_deserialize(obj, info):
	if obj.__class__ == QTextEdit:
		return obj.setText(info)

	if hasattr(obj, "deserialize"):
		return obj.deserialize(info)
	else:
		p = pickle.loads(info)
		for k in obj.keys():
			obj[k] = p[k]

class StyleWidget(QWidget):
	def __init__(self):
		super().__init__()

class SchemeType:
	def __init__(self, name):
		self.name = name
	
	def serialize(self, marchpath):
		slst = self.confwidget.serialize_list()
		lst = [ (k, do_serialize(v)) for k,v in slst ]
		lst = [ ("name", self.name) ] + lst

		pickle.dump(lst, open(marchpath,"wb"))

	def deserialize(self, dct):
		slst = self.confwidget.serialize_list()

		for k, v in slst:
			for kd, vd in dct:
				if k == kd:
					do_deserialize(v, vd)
					self.confwidget.clean_and_update_interface()
	
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
		self.add_button = QPushButton("Добавить последней")
		self.del_button = QPushButton("Убрать последнюю")

		self.add_button.clicked.connect(self.add_action)
		self.del_button.clicked.connect(self.del_action)

		self.add_button2 = QPushButton("Вставить секцию")
		self.del_button2 = QPushButton("Убрать секцию")

		self.add_button2.clicked.connect(self.insert_action)
		self.del_button2.clicked.connect(self.del2_action)

	def add_buttons_to_layout(self, vlayout):
		butlayout1 = QHBoxLayout()
		butlayout2 = QHBoxLayout()

		butlayout1.addWidget(self.add_button)
		butlayout1.addWidget(self.del_button)
		butlayout2.addWidget(self.add_button2)
		butlayout2.addWidget(self.del_button2)

		self.vlayout.addLayout(butlayout1)
		self.vlayout.addLayout(butlayout2)

	def add_action(self):
		self.add_action_impl()

	def del_action(self):
		self.del_action_impl(-1)

	def insert_action(self):
		idx, sts = QInputDialog.getInt(self, 
			"Укажите номер", 
			"Укажите номер:")
		
		if idx <= 0:
			return 

		self.insert_action_impl(idx-1)
	
	def del2_action(self):
		idx, sts = QInputDialog.getInt(self, 
			"Укажите номер", 
			"Укажите номер:")
		
		if idx <= 0:
			return 

		self.del_action_impl(idx-1)
	
	def __init__(self, sheme=None, noinitbuttons=False):
		super().__init__()
		self.shemetype = sheme

		if sheme:
			self.vlayout = QVBoxLayout()

			self.shemetype = sheme
			self.shemetype.font_size = CONFVIEW.font_size_getter
			self.shemetype.line_width = CONFVIEW.lwidth_getter

			self.create_task_structure()
			self.init_sections_buttons()

			if not noinitbuttons:
				self.add_buttons_to_layout(self.vlayout)

	def sections(self):
		return self.shemetype.task["sections"]

	def bsections(self):
		return self.shemetype.task["betsect"]

	def sectforces(self):
		return self.shemetype.task["sectforce"]

	def redraw(self):
		self.shemetype.paintwidget.repaint()

	def update_interface(self):
		print("update interface is not reimplemented")

	def clean_and_update_interface(self):
		util.clear_layout(self.vlayout)
		self.update_interface() 
		self.redraw()

	def serialize_list(self):
		return [
			("task", self.shemetype.task),
			("sett", self.sett),
			("texteditor", self.shemetype.texteditor)
		]

class TableWidget(QWidget):
	def __init__(self):
		super().__init__()

class ConfView(QWidget):
	update_after = pyqtSignal()

	"""Общие настройки"""
	def __init__(self, sheme=None):
		super().__init__()
		self.update_after.connect(self.updated, Qt.QueuedConnection)
		self.layout = QGridLayout()
		self.layout = QVBoxLayout()

		self.sett = taskconf_menu.TaskConfMenu()
		self.width_getter = self.sett.add("Ширина в px:", "int", "400")
		self.height_getter = self.sett.add("Высота в px:", "int", "250")
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
