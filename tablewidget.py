
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class TableWidget(QTableWidget):
	updated = pyqtSignal()

	class column:
		def __init__(self, name, type, note):
			self.name = name
			self.type = type
			self.note = note

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

	def addColumn(self, name, type, note =None):
		if note is None: note = name
		self.columns.append(self.column(name, type, note))

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

				if self.columns[i].type == "float":
					it = QTableWidgetItem(str(getattr(self.shemetype.task[self.modelname][j], self.columns[i].name)))
					self.setItem(j,i,it)

		self.resizeColumnsToContents()
		self.setFixedSize(
				self.horizontalHeader().length() + self.verticalHeader().width() + 15, 
				self.verticalHeader().length() + self.horizontalHeader().height() + 5)
		self.protect = False

	def changed(self, row, column):
		if column == -1 or self.protect:
			return

		field = self.columns[column].name
		
		val = None
		if self.columns[column].type == "int":
			val = int(self.item(row,column).text())

		if self.columns[column].type == "float":
			val = float(self.item(row,column).text())

		setattr(self.shemetype.task[self.modelname][row], field, val)
		self.updated.emit()
