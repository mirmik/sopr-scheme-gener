from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Element(QWidget):
	updated = pyqtSignal()

	def __init__(self, label, type, defval):
		super().__init__()
		self.label = QLabel(label)
		self.type = type

		if type == "text":
			self.obj = QLineEdit(defval)
			self.obj.textChanged.connect(self.updated)

		if type == "int":
			self.obj = QLineEdit(defval)
			self.obj.textChanged.connect(self.updated)

		if type == "float":
			self.obj = QLineEdit(defval)
			self.obj.textChanged.connect(self.updated)

		if type == "bool":
			self.obj = QCheckBox()
			self.obj.setChecked(defval)
			self.obj.stateChanged.connect(self.updated)

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
				if (self.type == "text"):
					return self.obj.text()

				if (self.type == "int"):
					try:
						return int(self.obj.text())
					except:
						return 1

				if (self.type == "float"):
					return float(self.obj.text())

				if (self.type == "bool"):
					return bool(self.obj.checkState())

				print("strange type")

			def set(self, val):
				if (self.type == "text"):
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

	def add(self, label, type, defval):
		el = Element(label, type, defval)
		self.layout.addWidget(el)
		el.updated.connect(self.updated)
		return el.getter()