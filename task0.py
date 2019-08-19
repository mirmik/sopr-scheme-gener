import common
import paintwdg
import math

import paintool
import taskconf_menu

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ShemeTypeT0(common.SchemeType):
	def __init__(self):
		super().__init__("Тип0 (Растяжение/сжатие/кручение стержня переменного сечения)")
		self.setwidgets(ConfWidget_T0(self), PaintWidget_T0(), common.TableWidget())

class TorqueComboBox(QComboBox):
	def __init__(self, idx, confw, f):
		super().__init__()

		self.idx = idx 
		self.confw = confw
		self.f = f

		self.addItem("0")
		self.addItem("+")
		self.addItem("-")

		self.activated.connect(self.activated_handler)

	def activated_handler(self):
		n = self.currentIndex() 
		self.confw.shemetype.task["betsect"][self.idx][self.f] = n
		self.confw.redraw()

class TTLineEdit(QLineEdit):
	def __init__(self, idx, confw):
		super().__init__()

		self.idx = idx 
		self.confw = confw
		self.textChanged.connect(self.handler)

	def handler(self): 
		self.confw.shemetype.task["betsect"][self.idx]["T"] = self.text() 
		self.confw.redraw()

class TableCheckBox(QCheckBox):
	def __init__(self, idx, confw, f):
		super().__init__()

		self.idx = idx 
		self.confw = confw
		self.stateChanged.connect(self.handler)
		self.f = f

	def handler(self): 
		self.confw.shemetype.task["sections"][self.idx][self.f] = self.checkState()
		self.confw.redraw()

class ConfWidget_T0(common.ConfWidget):
	"""Виджет настроек задачи T0"""
	def __init__(self, sheme):
		super().__init__(sheme)

		self.add_button = QPushButton("Добавить секцию")
		self.del_button = QPushButton("Убрать секцию")

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
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(self.table2)
		#self.vlayout.addLayout(self.hhlayout)

		self.table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)	
		
		self.table2.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.table2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.table2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)	

		self.table.cellChanged.connect(self.changed)
		self.table2.cellChanged.connect(self.changed2)

		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.axis = self.sett.add("Нарисовать ось:", "bool", True)
		self.shemetype.zleft = self.sett.add("Заделка слева:", "bool", False)
		self.shemetype.zright = self.sett.add("Заделка справа:", "bool", False)
		#self.shemetype.lwidth = self.sett.add("Ширина линий:", "int", "2")
		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.base_section_height = self.sett.add("Базовая высота секции:", "int", "40")
		self.shemetype.arrow_line_size = self.sett.add("Размер линии стрелки:", "int", "20")
		self.shemetype.dimlines_start_step = self.sett.add("Отступ размерных линий:", "int", "40")
		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "10")
		#self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.left_zone = self.sett.add("Отступ слева:", "int", "20")
		self.shemetype.right_zone = self.sett.add("Отступ справа:", "int", "20")
		
		self.sett.updated.connect(self.redraw)

		#self.arrow_size_le = common.ELabel("Размер линии стрелки:", str(common.datasettings.arrow_size), 300, 100)
		#self.arrow_head_size_le = common.ELabel("Размер стрелки:", str(common.datasettings.arrow_head_size), 300, 100)

		self.vlayout.addWidget(self.sett)
		#self.vlayout.addWidget(self.arrow_size_le)
		#self.vlayout.addWidget(self.arrow_head_size_le)

		#self.arrow_size_le.edit.editingFinished.connect(self.arrows_update)
		#self.arrow_head_size_le.edit.editingFinished.connect(self.arrows_update)

		self.setLayout(self.vlayout)

	def add_action(self):
		self.sections().append(self.sect())
		self.shemetype.task["betsect"].append(self.betsect())
		self.redraw()
		self.updateTable1()
		self.updateTable2()

	def del_action(self):
		if len(self.sections()) == 1:
			return

		del self.sections()[-1]
		del self.shemetype.task["betsect"][-1]
		self.redraw()
		self.updateTable1()
		self.updateTable2()

	def changed(self, row, column):
		field = None

		if column == 0: field = 'A'
		if column == 1: field = 'l'
		if column == 2: field = 'Atext'
		if column == 3: field = 'ltext'
		if column == 4: field = 'delta'

		if field == "A" or field == "l":
			self.sections()[row].field = float(self.table.item(row,column).text())
		elif field == "Atext" or field == "ltext":
			self.sections()[row].field = self.table.item(row,column).text()
		else:
			self.sections()[row].field = self.table.item(row,column).checkedState()

		self.redraw()

	def changed2(self, row, column):
		field = None

		if column == 0: field = 'F'
		if column == 1: field = 'M'
		if column == 1: field = 'Mкр'
		if column == 2: field = 'T'

		if field != "T":
			self.shemetype.task["betsect"][row][field] = float(self.table2.item(row,column).text())
		else:
			self.shemetype.task["betsect"][row][field] = self.table2.item(row,column).text()

		self.redraw()

	def updateTable1(self):
		self.table.setColumnCount(5)
		self.table.setRowCount(len(self.sections()))
		self.table.setHorizontalHeaderItem(0, QTableWidgetItem("A")) 
		self.table.setHorizontalHeaderItem(1, QTableWidgetItem("l")) 
		self.table.setHorizontalHeaderItem(2, QTableWidgetItem("A текст")) 
		self.table.setHorizontalHeaderItem(3, QTableWidgetItem("l текст")) 
		self.table.setHorizontalHeaderItem(4, QTableWidgetItem("Разрыв")) 

		for i in range(len(self.sections())):
			it = QTableWidgetItem(str(self.sections()[i].A))
			self.table.setItem(i,0,it)

			it = QTableWidgetItem(str(self.sections()[i].l))
			self.table.setItem(i,1,it)

			it = QTableWidgetItem(str(self.sections()[i].Atext))
			self.table.setItem(i,2,it)

			it = QTableWidgetItem(str(self.sections()[i].ltext))
			self.table.setItem(i,3,it)

			it = TableCheckBox(i, self, "delta")
			self.table.setCellWidget(i,4,it)

		self.table.resizeColumnsToContents()
		self.table.setFixedSize(
				self.table.horizontalHeader().length() + self.table.verticalHeader().width() + 15, 
				self.table.verticalHeader().length() + self.table.horizontalHeader().height() + 5)

		self.table.repaint()

	def updateTable2(self):
		self.table2.clear()

		self.table2.setColumnCount(4)
		self.table2.setRowCount(len(self.shemetype.task["betsect"]))
		self.table2.setHorizontalHeaderItem(0, QTableWidgetItem("F")) 
		self.table2.setHorizontalHeaderItem(1, QTableWidgetItem("M"))  
		self.table2.setHorizontalHeaderItem(2, QTableWidgetItem("Mкр"))  
		self.table2.setHorizontalHeaderItem(3, QTableWidgetItem("T"))

		for i in range(len(self.shemetype.task["betsect"])):
			#it = QTableWidgetItem(str(self.shemetype.task["betsect"][i].F))

			it = TorqueComboBox(i, self, "F")
			self.table2.setCellWidget(i,0,it)

			it = TorqueComboBox(i, self, "M")
			self.table2.setCellWidget(i,1,it)

			it = TorqueComboBox(i, self, "Mкр")
			self.table2.setCellWidget(i,2,it)

			it = TTLineEdit(i, self)
			self.table2.setCellWidget(i,3,it)

		self.table2.resizeColumnsToContents()
		self.table2.setFixedSize(
				self.table2.horizontalHeader().length() + self.table2.verticalHeader().width() + 15, 
				self.table2.verticalHeader().length() + self.table2.horizontalHeader().height() + 5)

		self.table2.repaint()


	class sect:
		def __init__(self, A=1, l=1, Atext="", ltext="", delta=False):
			self.A=A
			self.l=l
			self.Atext=Atext
			self.ltext = ltext
			self.delta=delta

	class betsect:
		def __init__(self, F=0, M=0, Mkr=0, T=""):
			self.F = F 
			self.M = M
			self.Mkr = Mkr 
			self.T = T

	def inittask(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(A=1, l=1),
				self.sect(A=2, l=1),
				self.sect(A=1, l=2),
			],
			"betsect":[self.betsect(),self.betsect(),self.betsect(),self.betsect()]
		}

		self.updateTable1()
		self.updateTable2()
		self.updateTable1()
		self.updateTable2()

		return self.shemetype.task

class PaintWidget_T0(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()

	def paintEventImplementation(self, ev):
		"""Рисуем сцену согласно объекта задания"""

		lwidth = self.shemetype.lwidth.get()

		axis = self.shemetype.axis.get()
		zleft = self.shemetype.zleft.get()
		zright = self.shemetype.zright.get()

		base_section_height = self.shemetype.base_section_height.get()
		arrow_size = self.shemetype.arrow_line_size.get()
		arrow_head_size = self.shemetype.arrow_size.get()
		font_size = self.shemetype.font_size.get()

		task = self.shemetype.task
		size = self.size()

		width = size.width()
		height = size.height()

		height_zone = base_section_height

		strt_width = self.shemetype.left_zone.get()
		fini_width = width-self.shemetype.right_zone.get()

		painter = QPainter(self)
		font = painter.font()
		font.setItalic(True)
		font.setPointSize(font_size)
		painter.setFont(font)

		br = QPen()
		br.setWidth(lwidth)
		painter.setPen(br)


		maxl = 0
		maxA = 0
		for s in self.sections():
			if s.l > maxl: maxl = s.l
			if s.A > maxA: maxA = s.A

		dimlines_level = height/2 + base_section_height*math.sqrt(maxA)/2 + self.shemetype.dimlines_start_step.get()

		# Длины и дистанции
		summary_length = 0
		ll = [0]
		for i in range(len(task["sections"])):
			summary_length += task["sections"][i].l
			ll.append(ll[i] + task["sections"][i].l)
		def wsect(i):
			l = len(task["sections"])
			k0 = summary_length - ll[i]
			k1 = ll[i]
			return (fini_width * k1 + strt_width * k0) // summary_length

		def sectrad(i):
			return math.sqrt(task["sections"][i].A) * height_zone / 2

		def msectrad(i):
			leftA = 0 if i == 0 else math.sqrt(task["sections"][i-1].A)
			rightA = 0 if i == -1 + len(task["betsect"]) else math.sqrt(task["sections"][i].A)
			return max(leftA, rightA) * height_zone / 2


		# Отрисовка секций
		for i in range(len(task["sections"])):
			hkoeff = math.sqrt(task["sections"][i].A)

			strt_height = height/2 - height_zone*hkoeff/2
			fini_height = height/2 + height_zone*hkoeff/2

			A = task["sections"][i].A
			l = task["sections"][i].l

			if not task["sections"][i].delta:
				if abs(float(A) - int(A)) < 0.0001:
					text_A = "{}A".format(int(task["sections"][i].A+0.1)) if task["sections"][i].A != 1 else "A"
				else:
					text_A = str(float(A)) + "A"
	
				if abs(float(l) - int(l)) < 0.0001:
					text_l = "{}l".format(int(task["sections"][i].l+0.1)) if task["sections"][i].l != 1 else "l"
				else:
					text_l = str(float(l)) + "l"
			else: 
				text_l = ""
				text_A = ""

			if task["sections"][i].ltext != "":
				text_l = task["sections"][i].ltext 

			if task["sections"][i].Atext != "":
				text_A = task["sections"][i].Atext
			
			text_l = paintool.greek(text_l)
			text_A = paintool.greek(text_A)

			if not task["sections"][i].delta:
				painter.drawRect(wsect(i), strt_height, wsect(i+1)-wsect(i), fini_height-strt_height)

			lW = QFontMetrics(font).width(text_l)
			AW = QFontMetrics(font).width(text_A)

			painter.drawText( QPoint((wsect(i)+wsect(i+1))/2 - AW/2, strt_height - 5), text_A)
			painter.drawText( QPoint((wsect(i)+wsect(i+1))/2 - lW/2, fini_height + 15), text_l)

			paintool.dimlines(painter, QPoint(wsect(i), fini_height), QPoint(wsect(i+1), fini_height), dimlines_level)
			painter.setBrush(self.default_brush)
			painter.setPen(self.default_pen)
		
		#Отрисовка граничных эффектов
		for i in range(len(task["betsect"])):
			if task["betsect"][i].F == 1:
				paintool.right_arrow(painter, QPoint(wsect(i), height/2), arrow_size, arrow_head_size)

			if task["betsect"][i].F == 2:
				paintool.left_arrow(painter, QPoint(wsect(i), height/2), arrow_size, arrow_head_size)

			if task["betsect"][i].M == 1:
				paintool.circular_arrow_base(painter, paintool.radrect(QPoint(wsect(i), height/2), 20), False)

			if task["betsect"][i].M == 2:
				paintool.circular_arrow_base(painter, paintool.radrect(QPoint(wsect(i), height/2), 20), True)

			if task["betsect"][i].Mkr == 1:
				paintool.kr_arrow(painter, QPoint(wsect(i), height/2), msectrad(i)+10, 11, False)

			if task["betsect"][i].Mkr == 2:
				paintool.kr_arrow(painter, QPoint(wsect(i), height/2), msectrad(i)+10, 11, True)

			if task["betsect"][i].T != "":
				leftA = 0 if i == 0 else math.sqrt(task["sections"][i-1].A)
				rightA = 0 if i == -1 + len(task["betsect"]) else math.sqrt(task["sections"][i].A)
				
				size = QFontMetrics(font).width(task["betsect"][i].T)
				text = task["betsect"][i].T


				if not task["betsect"][i].Mkr:
					paintool.placedtext(painter,
						QPoint(wsect(i), height/2), 
						max(leftA, rightA) * height_zone / 2 + 10, 
						size, 
						text,
						right = task["betsect"][i].M == 2)

				else:
					painter.drawText(QPoint(wsect(i) - size/2, height/2 - msectrad(i) - 10 - 11*2 - 5), text)

		if zleft:
			y = math.sqrt(task["sections"][0].A) * height_zone
			paintool.zadelka(painter, wsect(0) - 10, wsect(0), height/2-y, height/2+y, left_border=False, right_border=True)

		if zright:
			y = math.sqrt(task["sections"][-1].A) * height_zone
			paintool.zadelka(painter, wsect(-1), wsect(-1) + 10, height/2-y, height/2+y, left_border=True, right_border=False)


		if axis:
			pen = QPen(Qt.CustomDashLine)
			pen.setDashPattern([10,3,1,3])
			painter.setPen(pen)
			painter.drawLine(QPoint(5, height/2), QPoint(width - 5, height/2))
			pen = QPen()
			painter.setPen(pen)

	#def leftArrow(self, painter, basepoint):
	#	arrow_size = self.shemetype.datasettings.arrow_size
	#	arrow_head_size = self.shemetype.datasettings.arrow_head_size		
#
	#	painter.drawLine(basepoint, QPoint(basepoint.x() - arrow_size, basepoint.y()))
#
	#	points = [
	#		(basepoint.x() - arrow_size - 2 * arrow_head_size, basepoint.y()), 
	#		(basepoint.x() - arrow_size, basepoint.y() - arrow_head_size), 
	#		(basepoint.x() - arrow_size, basepoint.y() + arrow_head_size)
	#	]
	#	qpoints = [QPointF(x, y) for (x, y) in points]
	#	polygon = QPolygonF(qpoints)
#
	#	painter.drawConvexPolygon(polygon)
#
	#def rightArrow(self, painter, basepoint):
	#	arrow_size = self.shemetype.datasettings.arrow_size
	#	arrow_head_size = self.shemetype.datasettings.arrow_head_size
#
	#	painter.drawLine(basepoint, QPoint(basepoint.x() + arrow_size, basepoint.y()))
#
	#	points = [
	#		(basepoint.x() + arrow_size + 2 * arrow_head_size, basepoint.y()), 
	#		(basepoint.x() + arrow_size, basepoint.y() - arrow_head_size), 
	#		(basepoint.x() + arrow_size, basepoint.y() + arrow_head_size)
	#	]
	#	qpoints = [QPointF(x, y) for (x, y) in points]
	#	polygon = QPolygonF(qpoints)
#
	#	painter.drawConvexPolygon(polygon)
