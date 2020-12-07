
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class TableWidget(QTableWidget):
	updated = pyqtSignal()
	hover_hint = pyqtSignal(int,int,str) 
	unhover = pyqtSignal() 

	class cellsig(QObject):
		signal = pyqtSignal(int, int)

		def __init__(self, row, column):
			super().__init__()
			self.row = row
			self.column = column

		def emit_signal(self):
			self.signal.emit(self.row, self.column)


	class column:
		def __init__(self, name, type, note, variant, hint=None):
			self.name = name
			self.type = type
			self.note = note
			self.variant = variant
			self.hint = hint

	def __init__(self, sheme, modelname):
		super().__init__()
		self.setMouseTracking(True)
		self.shemetype = sheme
		self.modelname = modelname
		self.installEventFilter(self)

		self.columns = []

		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		self.cellChanged.connect(self.changed)	
		self.protect = False

	def onMouse(self):
		pos = self.mapFromGlobal(QCursor.pos())
		pos = pos - QPoint(self.verticalHeader().width(), self.horizontalHeader().height())
		index = self.indexAt(pos)
		row = index.row()
		column = index.column()
		if (row != -1 and column != -1):
			self.hover_hint.emit(row,column,self.columns[column].hint)

	def mouseMoveEvent(self,ev):
		self.onMouse()

	def eventFilter(self, obj, ev):
		if (ev.type()==QEvent.MouseMove or ev.type()==QEvent.HoverMove):
			self.onMouse()
		return False

	def leaveEvent(self, ev):
		self.unhover.emit()
		super().leaveEvent(ev)

	def addColumn(self, name, type, note=None, variant=None, hint=None):
		if note is None: note = name
		self.columns.append(self.column(name, type, note, variant, hint))

	def updateTable(self):
		self.protect = True
		self.setColumnCount(len(self.columns))
		self.setRowCount(len(self.shemetype.task[self.modelname]))

		for i in range(len(self.columns)):
			self.setHorizontalHeaderItem(i, QTableWidgetItem(self.columns[i].note))

			for j in range(len(self.shemetype.task[self.modelname])):
				if self.columns[i].type == "int":
					it = QTableWidgetItem(str(getattr(self.shemetype.task[self.modelname][j], self.columns[i].name)))
					self.setItem(j,i,it)

				elif self.columns[i].type == "float":
					it = QTableWidgetItem(str(getattr(self.shemetype.task[self.modelname][j], self.columns[i].name)))
					self.setItem(j,i,it)

				elif self.columns[i].type == "str":
					it = QTableWidgetItem(str(getattr(self.shemetype.task[self.modelname][j], self.columns[i].name)))
					self.setItem(j,i,it)

				elif self.columns[i].type == "list":
					sig = self.cellsig(j,i)
					sig.signal.connect(self.changed)
					variant = self.columns[i].variant

					obj = QComboBox()
					obj.installEventFilter(self)
					#obj.setFixedWidth(0)
					obj.addItems(variant)
					obj.sig = sig
					obj.currentIndexChanged.connect(sig.emit_signal)

					cur = str(getattr(self.shemetype.task[self.modelname][j], self.columns[i].name))
					print(variant)
					print(cur)
					if isinstance(variant, list) and isinstance(cur, bool): 
						cur = "1" if cur else "2"

					no = variant.index(cur)
					obj.setCurrentIndex(no)

					self.setCellWidget(j,i,obj)

				elif self.columns[i].type == "bool":
					sig = self.cellsig(j,i)
					sig.signal.connect(self.changed)

					obj = QCheckBox()
					obj.sig = sig
					obj.setChecked(getattr(self.shemetype.task[self.modelname][j], self.columns[i].name))
					obj.stateChanged.connect(sig.emit_signal)
					self.setCellWidget(j,i,obj)

				else:
					raise Exception("unregistred type")

		self.resizeColumnsToContents()
		self.setFixedHeight(
				#self.horizontalHeader().length() + self.verticalHeader().width() + 15, 
				self.verticalHeader().length() + self.horizontalHeader().height() + 5)
		self.protect = False

	def changed(self, row, column):
		try:
			if column == -1 or self.protect:
				return

			field = self.columns[column].name
			
			val = None
			if self.columns[column].type == "int":
				val = int(self.item(row,column).text())
	
			elif self.columns[column].type == "float":
				val = float(self.item(row,column).text())
	
			elif self.columns[column].type == "str":
				val = self.item(row,column).text()
	
			elif self.columns[column].type == "bool":
				val = bool(self.cellWidget(row,column).checkState())
	
			elif self.columns[column].type == "list":
				val = str(self.cellWidget(row,column).currentText())
			
			else:
				raise Exception("unregistred type")
	
			setattr(self.shemetype.task[self.modelname][row], field, val)
			self.updated.emit()
		except:
			pass
	