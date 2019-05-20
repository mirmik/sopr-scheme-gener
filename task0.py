import common
import math

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ConfWidget_T0(common.StyleWidget):
	"""Виджет настроек задачи T0"""
	def __init__(self):
		super().__init__()

		self.add_button = QPushButton("add")
		self.del_button = QPushButton("del")

		self.vlayout = QVBoxLayout()
		self.butlayout = QHBoxLayout()
		self.hhlayout = QHBoxLayout()

		self.butlayout.addWidget(self.add_button)
		self.butlayout.addWidget(self.del_button)

		self.add_button.clicked.connect(self.add_action)
		self.del_button.clicked.connect(self.del_action)
		self.vlayout.addLayout(self.butlayout)

		self.table = QTableWidget()
		self.table2 = QTableWidget()
		self.hhlayout.addWidget(self.table)
		self.hhlayout.addWidget(self.table2)
		self.vlayout.addLayout(self.hhlayout)

		self.setLayout(self.vlayout)

	def redraw(self):
		self.shemetype.paintwidget.repaint()

	def add_action(self):
		self.shemetype.task["sections"].append({"A":1,"l":1})
		self.shemetype.task["betsect"].append(self.betsect())
		self.redraw()
		self.updateTable1()
		self.updateTable2()

	def del_action(self):
		if len(self.shemetype.task["sections"]) == 1:
			return

		del self.shemetype.task["sections"][-1]
		del self.shemetype.task["betsect"][-1]
		self.redraw()
		self.updateTable1()
		self.updateTable2()

	def changed(self, row, column):
		field = None

		if column == 0: field = 'A'
		if column == 1: field = 'l'

		self.shemetype.task["sections"][row][field] = int(self.table.item(row,column).text())

		self.redraw()

	def changed2(self, row, column):
		field = None

		if column == 0: field = 'F'
		if column == 1: field = 'M'

		self.shemetype.task["betsect"][row][field] = int(self.table2.item(row,column).text())

		self.redraw()

	def updateTable1(self):
		self.table.setColumnCount(2)
		self.table.setRowCount(len(self.shemetype.task["sections"]))
		self.table.setHorizontalHeaderItem(0, QTableWidgetItem("A")) 
		self.table.setHorizontalHeaderItem(1, QTableWidgetItem("l")) 

		for i in range(len(self.shemetype.task["sections"])):
			it = QTableWidgetItem(str(self.shemetype.task["sections"][i]["A"]))
			self.table.setItem(i,0,it)

			it = QTableWidgetItem(str(self.shemetype.task["sections"][i]["l"]))
			self.table.setItem(i,1,it)

		self.table.repaint()
		self.table.cellChanged.connect(self.changed)

	def updateTable2(self):
		self.table2.setColumnCount(2)
		self.table2.setRowCount(len(self.shemetype.task["betsect"]))
		self.table2.setHorizontalHeaderItem(0, QTableWidgetItem("F")) 
		self.table2.setHorizontalHeaderItem(1, QTableWidgetItem("M")) 

		for i in range(len(self.shemetype.task["betsect"])):
			it = QTableWidgetItem(str(self.shemetype.task["betsect"][i]["F"]))
			self.table2.setItem(i,0,it)

			it = QTableWidgetItem(str(self.shemetype.task["betsect"][i]["M"]))
			self.table2.setItem(i,1,it)

		self.table2.repaint()
		self.table2.cellChanged.connect(self.changed2)

	def betsect(self, F=0, M=0):
		return {"F":F, "M":M}

	def inittask(self):
		self.shemetype.task = {
			"sections": 
			[
				{
					"A" : 1,
					"l" : 1
				},
				{
					"A" : 2,
					"l" : 2
				},
				{
					"A" : 1,
					"l" : 3
				},
			],
			"betsect":[self.betsect(),self.betsect(),self.betsect(),self.betsect()]
		}

		self.updateTable1()
		self.updateTable2()

		return self.shemetype.task

class PaintWidget_T0(QWidget):
	def __init__(self):
		super().__init__()

	def paintEvent(self, ev):
		"""Рисуем сцену согласно объекта задания"""

		task = self.shemetype.task
		size = self.size()

		width = size.width()
		height = size.height()

		height_zone = 40
		strt_width = 10
		fini_width = width-10

		painter = QPainter(self)
		font = painter.font()
		font.setItalic(True)
		painter.setFont(font)

		#size = common.CONFVIEW.size()

		painter.drawRect(0,0,width-1,height-1);

		# Длины и дистанции
		summary_length = 0
		ll = [0]
		for i in range(len(task["sections"])):
			summary_length += task["sections"][i]["l"]
			ll.append(ll[i] + task["sections"][i]["l"])
		def wsect(i):
			l = len(task["sections"])
			k0 = summary_length - ll[i]
			k1 = ll[i]
			return (fini_width * k1 + strt_width * k0) // summary_length

		# Отрисовка секций
		for i in range(len(task["sections"])):
			hkoeff = math.sqrt(task["sections"][i]["A"])

			strt_height = height/2 - height_zone*hkoeff/2
			fini_height = height/2 + height_zone*hkoeff/2

			text_A = "{}A".format(task["sections"][i]["A"]) if task["sections"][i]["A"] != 1 else "A"
			text_l = "{}l".format(task["sections"][i]["l"]) if task["sections"][i]["l"] != 1 else "l"
			
			painter.drawRect(wsect(i), strt_height, wsect(i+1)-wsect(i), fini_height-strt_height);
			painter.drawText( QPoint((wsect(i)+wsect(i+1))/2, strt_height - 5), text_A);
			painter.drawText( QPoint((wsect(i)+wsect(i+1))/2, fini_height + 15), text_l);