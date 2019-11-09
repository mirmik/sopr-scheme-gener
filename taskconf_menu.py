from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Element(QWidget):
	updated = pyqtSignal()

	def __init__(self, label, type, defval=None, variant=None):
		super().__init__()
		self.label = QLabel(label)
		self.type = type

		if type == "text" or type == "str":
			self.obj = QLineEdit(defval)
			self.obj.textChanged.connect(self.updated)

		elif type == "int":
			self.obj = QLineEdit(defval)
			self.obj.textChanged.connect(self.updated)

		elif type == "float":
			self.obj = QLineEdit(defval)
			self.obj.textChanged.connect(self.updated)

		elif type == "bool":
			self.obj = QCheckBox()
			self.obj.setChecked(defval)
			self.obj.stateChanged.connect(self.updated)

		elif type == "list":
			self.obj = QComboBox()
			self.obj.addItems(variant)
			self.obj.setCurrentIndex(defval),
			self.obj.currentIndexChanged.connect(self.updated)

			#cur = str(getattr(self.shemetype.task[self.modelname][j], self.columns[i].name))
			#no = variant.index(cur)
			#self.obj.setCurrentIndex(no)

		self.label.setFixedWidth(200)

		self.layout = QHBoxLayout()
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.obj)
		self.layout.setContentsMargins(0,0,0,0)

		self.setLayout(self.layout)

	def getter(self):
		class getcls:
			def __init__(self, obj, type):
				self.obj = obj
				self.type = type

			def get(self):
				if (self.type == "text" or self.type == "str"):
					return self.obj.text()

				elif (self.type == "int"):
					try:
						return int(self.obj.text())
					except:
						return 1

				elif (self.type == "float"):
					return float(self.obj.text())

				elif (self.type == "bool"):
					return bool(self.obj.checkState())

				elif self.type == "list":
					idx = self.obj.currentIndex()
					return str(self.obj.itemText(idx))

				print("strange type")

			def set(self, val):
				if (self.type == "text" or self.type=="str"):
					self.obj.setText(val)
					return 

				if (self.type == "int"):
					self.obj.setText(str(val))
					return 

				if (self.type == "float"):
					self.obj.setText(str(val))
					return 

				if (self.type == "bool"):
					self.obj.setCheckState(val)
					return 

				print("strange type")


		return getcls(self.obj, self.type)

class TaskConfMenu(QWidget):
	updated = pyqtSignal()	

	def __init__(self):
		super().__init__()
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

	def add(self, label, type, defval=None, variant=None):
		el = Element(label, type, defval, variant)
		self.layout.addWidget(el)
		el.updated.connect(self.updated)
		return el.getter()