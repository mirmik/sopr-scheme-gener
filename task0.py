import common
import math

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ForceComboBox(QComboBox):
	def __init__(self, idx, confw):
		super().__init__()

		self.idx = idx 
		self.confw = confw

		self.addItem("0")
		self.addItem("1")
		self.addItem("2")

		self.confw.shemetype.task["betsect"][self.idx]["F"]

		self.activated.connect(self.activated_handler)

	def activated_handler(self):
		n = self.currentIndex() 
		self.confw.shemetype.task["betsect"][self.idx]["F"] = n
		self.confw.redraw()

class TorqueComboBox(QComboBox):
	def __init__(self, idx, confw):
		super().__init__()

		self.idx = idx 
		self.confw = confw

		self.addItem("0")
		self.addItem("1")
		self.addItem("2")

		self.activated.connect(self.activated_handler)

	def activated_handler(self):
		n = self.currentIndex() 
		self.confw.shemetype.task["betsect"][self.idx]["M"] = n
		self.confw.redraw()

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

		self.table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)		
		self.table.resizeColumnsToContents()
		
		self.table2.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.table2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.table2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)		
		self.table2.resizeColumnsToContents()

		self.table.cellChanged.connect(self.changed)
		self.table2.cellChanged.connect(self.changed2)

		self.arrow_size_le = common.ELabel("Размер линии стрелки:", str(common.datasettings.arrow_size), 300, 100)
		self.arrow_head_size_le = common.ELabel("Размер стрелки:", str(common.datasettings.arrow_head_size), 300, 100)

		self.vlayout.addWidget(self.arrow_size_le)
		self.vlayout.addWidget(self.arrow_head_size_le)

		self.arrow_size_le.edit.editingFinished.connect(self.arrows_update)
		self.arrow_head_size_le.edit.editingFinished.connect(self.arrows_update)

		self.setLayout(self.vlayout)

	def arrows_update(self):
		arrow_size = int(self.arrow_size_le.edit.text())
		arrow_head_size = int(self.arrow_head_size_le.edit.text())

		self.shemetype.datasettings.arrow_size = arrow_size
		self.shemetype.datasettings.arrow_head_size = arrow_head_size

		self.redraw()


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

		self.shemetype.task["sections"][row][field] = float(self.table.item(row,column).text())

		self.redraw()

	def changed2(self, row, column):
		field = None

		if column == 0: field = 'F'
		if column == 1: field = 'M'

		self.shemetype.task["betsect"][row][field] = float(self.table2.item(row,column).text())

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

		self.table.setFixedSize(
				self.table.horizontalHeader().length() + self.table.verticalHeader().width(), 
				self.table.verticalHeader().length() + self.table.horizontalHeader().height())

		self.table.repaint()

	def updateTable2(self):
		self.table2.clear()

		self.table2.setColumnCount(2)
		self.table2.setRowCount(len(self.shemetype.task["betsect"]))
		self.table2.setHorizontalHeaderItem(0, QTableWidgetItem("F")) 
		self.table2.setHorizontalHeaderItem(1, QTableWidgetItem("M")) 

		for i in range(len(self.shemetype.task["betsect"])):
			#it = QTableWidgetItem(str(self.shemetype.task["betsect"][i]["F"]))

			it = ForceComboBox(i, self)
			self.table2.setCellWidget(i,0,it)

			it = TorqueComboBox(i, self)
			self.table2.setCellWidget(i,1,it)

		self.table2.setFixedSize(
				self.table2.horizontalHeader().length() + self.table2.verticalHeader().width(), 
				self.table2.verticalHeader().length() + self.table2.horizontalHeader().height())

		self.table2.repaint()

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

	def resizeEvent(self, ev):
		print("resizeEvent")

		self.shemetype.datasettings.width = self.width()
		self.shemetype.datasettings.height = self.height()

		self.shemetype.updateDataSettingsVM()

	def paintEvent(self, ev):
		"""Рисуем сцену согласно объекта задания"""

		arrow_size = self.shemetype.datasettings.arrow_size
		arrow_head_size = self.shemetype.datasettings.arrow_head_size

		task = self.shemetype.task
		size = self.size()

		width = size.width()
		height = size.height()

		height_zone = 40

		strt_width = 10
		fini_width = width-10

		if task["betsect"][0]["F"] == 1:
			strt_width += arrow_size + 2*arrow_head_size

		if task["betsect"][-1]["F"] == 2:
			fini_width -= arrow_size + 2*arrow_head_size

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

			A = task["sections"][i]["A"]
			l = task["sections"][i]["l"]

			if abs(float(A) - int(A)) < 0.0001:
				text_A = "{}A".format(int(task["sections"][i]["A"]+0.1)) if task["sections"][i]["A"] != 1 else "A"
			else:
				text_A = str(float(A)) + "A"

			if abs(float(l) - int(l)) < 0.0001:
				text_l = "{}l".format(int(task["sections"][i]["l"]+0.1)) if task["sections"][i]["l"] != 1 else "l"
			else:
				text_l = str(float(l)) + "l"
			
			painter.drawRect(wsect(i), strt_height, wsect(i+1)-wsect(i), fini_height-strt_height)
			painter.drawText( QPoint((wsect(i)+wsect(i+1))/2, strt_height - 5), text_A)
			painter.drawText( QPoint((wsect(i)+wsect(i+1))/2, fini_height + 15), text_l)

		#Отрисовка граничных эффектов
		for i in range(len(task["betsect"])):
			if task["betsect"][i]["F"] == 1:
				self.leftArrow(painter, QPoint(wsect(i), height/2))

			if task["betsect"][i]["F"] == 2:
				self.rightArrow(painter, QPoint(wsect(i), height/2))

	def leftArrow(self, painter, basepoint):
		arrow_size = self.shemetype.datasettings.arrow_size
		arrow_head_size = self.shemetype.datasettings.arrow_head_size		

		painter.drawLine(basepoint, QPoint(basepoint.x() - arrow_size, basepoint.y()))

		points = [
			(basepoint.x() - arrow_size - 2 * arrow_head_size, basepoint.y()), 
			(basepoint.x() - arrow_size, basepoint.y() - arrow_head_size), 
			(basepoint.x() - arrow_size, basepoint.y() + arrow_head_size)
		]
		qpoints = [QPointF(x, y) for (x, y) in points]
		polygon = QPolygonF(qpoints)

		painter.drawConvexPolygon(polygon)

	def rightArrow(self, painter, basepoint):
		arrow_size = self.shemetype.datasettings.arrow_size
		arrow_head_size = self.shemetype.datasettings.arrow_head_size

		painter.drawLine(basepoint, QPoint(basepoint.x() + arrow_size, basepoint.y()))

		points = [
			(basepoint.x() + arrow_size + 2 * arrow_head_size, basepoint.y()), 
			(basepoint.x() + arrow_size, basepoint.y() - arrow_head_size), 
			(basepoint.x() + arrow_size, basepoint.y() + arrow_head_size)
		]
		qpoints = [QPointF(x, y) for (x, y) in points]
		polygon = QPolygonF(qpoints)

		painter.drawConvexPolygon(polygon)
