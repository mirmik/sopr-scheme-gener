from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pickle

class Element(QWidget):
	updated = pyqtSignal()

	def __init__(self, 
		         label, 
		         type, 
		         defval=None, 
		         variant=None,
		         vars=None,
		         serlbl=None):
		super().__init__()
		self.label = QLabel(label)
		self.type = type
		self.vars = vars
		self.variant = variant
		self.serlbl = serlbl

		self.label.setFixedWidth(200)
		self.layout = QHBoxLayout()
		self.layout.addWidget(self.label)
		
		if isinstance(type, tuple):
			self.obj = []
			for i in range(len(type)):
				self.obj.append(self.add_object(type[i], defval[i], variant[i] if variant else None))
		else:
			self.obj = self.add_object(type, defval, variant) 

		self.layout.setContentsMargins(0,0,0,0)
		self.setLayout(self.layout)


	def add_object(self, type, defval, variant):
		if type == "text" or type == "str":
			obj = QLineEdit(defval)
			obj.textChanged.connect(self.updated)

		elif type == "int":
			obj = QLineEdit(defval)
			obj.textChanged.connect(self.updated)

		elif type == "float":
			obj = QLineEdit(defval)
			obj.textChanged.connect(self.updated)

		elif type == "bool":
			obj = QCheckBox()
			obj.setChecked(defval)
			obj.stateChanged.connect(self.updated)

		elif type == "list":
			obj = QComboBox()
			obj.addItems(variant)
			obj.setCurrentIndex(defval),
			obj.currentIndexChanged.connect(self.updated)

		self.layout.addWidget(obj)
		return obj		

	def getter(self):
		class getcls:
			def __init__(self, obj, type, parent):
				self.obj = obj
				self.type = type
				self.parent = parent

			def element(self):
				return self.parent

			def label(self):
				return self.parent.label

			def _get(self, type, obj):
				if (type == "text" or type == "str"):
					return obj.text()

				elif (type == "int"):
					try:
						return int(obj.text())
					except:
						return 1

				elif (type == "float"):
					return float(obj.text())

				elif (type == "bool"):
					return bool(obj.checkState())

				elif type == "list":
					idx = obj.currentIndex()
					return  self.parent.vars[idx] #str(obj.itemText(idx))

				print("strange type")

			def get(self):
				if isinstance(self.type, tuple):
					ret = []
					for i in range(len(self.type)):
						ret.append(self._get(self.type[i], self.obj[i]))
					return ret
				else:
					return self._get(self.type, self.obj)
				
			def _set(self, type, obj, val):
				if (type == "text" or type=="str"):
					obj.setText(val)
					return 

				if (type == "int"):
					obj.setText(str(val))
					return 

				if (type == "list"):
					idx=val
					if isinstance(val, str):
						for i in range(len(self.parent.vars)):
							if val == self.parent.vars[i]:
								idx = i
								break						
					obj.setCurrentIndex(idx)
					return 

				if (type == "float"):
					obj.setText(str(val))
					return 

				if (type == "bool"):

					obj.setCheckState(Qt.Checked if val else Qt.Unchecked)
					return 

				print("strange type", type, val)


			def set(self, val):
				if isinstance(self.type, tuple):
					for i in range(len(self.type)):
						self._set(self.type[i], self.obj[i], val[i])

				else:
					self._set(self.type, self.obj, val)

		return getcls(self.obj, self.type, parent=self)

class TaskConfMenu(QWidget):
	updated = pyqtSignal()	

	def __init__(self):
		super().__init__()
		self.getters = []
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

	def add(self, label, type, defval=None, variant=None, vars=None,
			handler=None, serlbl=None):
		if serlbl is None:
			serlbl = label

		if vars is None:
			vars = variant

		el = Element(
			label=label, 
			type=type, 
			defval=defval, 
			variant=variant,
			vars=vars,
			serlbl=serlbl)
		
		self.layout.addWidget(el)
		el.updated.connect(self.updated)

		if handler is not None:
			el.updated.connect(handler)

		g = el.getter()
		self.getters.append(g)
		return g

	def add_delimiter(self):
		hFrame = QFrame()
		hFrame.setFrameShape(QFrame.HLine);
		hFrame.setFixedHeight(10)
		self.layout.addWidget(hFrame)

	def add_widget(self, wdg):
		self.layout.addWidget(wdg)
		return wdg

	def serialize(self):
		return pickle.dumps({ g.label().text() : g.get() for g in self.getters })
		
		# old style saving:
		#return pickle.dumps([ g.get() for g in self.getters ])

	def deserialize(self, ppp):
		ppp = pickle.loads(ppp)
		print(ppp)

		if (isinstance(ppp, list)):
			for i in range(len(self.getters)):
				self.getters[i].set(ppp[i])

		elif isinstance(ppp, dict):
			for i in range(len(self.getters)):
				for k,v in ppp.items():
					if self.getters[i].parent.serlbl == k:
						self.getters[i].set(v)
		else:
			util.error_msgbox("unresolved deserializated type")