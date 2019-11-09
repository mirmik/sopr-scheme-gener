
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class TableWidget(QTableWidget):
	updated = pyqtSignal()

	class cellsig(QObject):
		signal = pyqtSignal(int, int)

		def __init__(self, row, column):
			super().__init__()
			self.row = row
			self.column = column

		def emit_signal(self):
			self.signal.emit(self.row, self.column)


	class column:
		def __init__(self, name, type, note, variant):
			self.name = name
			self.type = type
			self.note = note
			self.variant = variant

	def __init__(self, sheme, modelname):
		super().__init__()
		self.shemetype = sheme
		self.modelname = modelname

		self.columns = []

		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		self.cellChanged.connect(self.changed)	
		self.protect = False

	def addColumn(self, name, type, note=None, variant=None):
		if note is None: note = name
		self.columns.append(self.column(name, type, note, variant))

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
					obj.addItems(variant)
					obj.sig = sig
					obj.currentIndexChanged.connect(sig.emit_signal)

					cur = str(getattr(self.shemetype.task[self.modelname][j], self.columns[i].name))
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
	