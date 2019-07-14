import common
import paintwdg
import math

import tablewidget
import paintool
import taskconf_menu

from paintool import deg

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ShemeTypeT2(common.SchemeType):
	def __init__(self):
		super().__init__("Тип2 (Горизонтальный стержень на шарнирах)")
		self.setwidgets(ConfWidget_T2(self), PaintWidget_T2(), common.TableWidget())

class ConfWidget_T2(common.ConfWidget):
	class sect:
		def __init__(self, 
			l=1, 
		):
			self.l = l

	class betsect:
		def __init__(self, 
			l=1, 
		):
			self.l = l

	"""Виджет настроек задачи T0"""
	def __init__(self, sheme):
		super().__init__()
		self.shemetype = sheme

		self.shemetype.task = {
			"sections": 
			[
				self.sect(l=1.5),
				self.sect(l=1),
				self.sect(l=1)
			],

			"betsect": 
			[
				self.betsect(l=0),
				self.betsect(l=1),
				self.betsect(l=3),
				self.betsect(l=-5)
			],
		}

		self.add_button = QPushButton("Добавить секцию")
		self.del_button = QPushButton("Убрать секцию")

		self.vlayout = QVBoxLayout()
		self.butlayout = QHBoxLayout()

		self.butlayout.addWidget(self.add_button)
		self.butlayout.addWidget(self.del_button)

		self.add_button.clicked.connect(self.add_action)
		self.del_button.clicked.connect(self.del_action)

		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.base_height = self.sett.add("Базовая толщина:", "int", "10")
		#self.shemetype.base_height = self.sett.add("Базовая высота стержня:", "int", "10")
		self.sett.updated.connect(self.redraw)

		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter

		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("l", "float", "Длина секции")
		self.table.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("l", "float", "Длина опоры")
		self.table2.updateTable()
		
		self.vlayout.addLayout(self.butlayout)
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)

		self.setLayout(self.vlayout)

	def add_action(self):
		self.shemetype.task["sections"].append(self.sect())
		self.shemetype.task["betsect"].append(self.betsect())
		self.redraw()
		self.updateTables()

	def del_action(self):
		if len(self.shemetype.task["sections"]) == 1: return
		del self.shemetype.task["sections"][-1]
		del self.shemetype.task["betsect"][-1]
		self.redraw()
		self.updateTables()

	def inittask(self):
		#compat
		return {}

	def updateTables(self):
		self.table.updateTable()
		self.table2.updateTable()

class PaintWidget_T2(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()

	def paintEventImplementation(self, ev):
		sects = self.shemetype.task["sections"]
		bsects = self.shemetype.task["betsect"]

		assert len(sects) + 1 == len(bsects)

		width = self.width()
		height = self.height()

		center = QPoint(width/2, height/2)

		font_size = self.shemetype.font_size.get()
		lwidth = self.shemetype.line_width.get()

		base_height = self.shemetype.base_height.get()

		painter = QPainter(self)
		font = painter.font()
		font.setItalic(True)
		font.setPointSize(font_size)
		painter.setFont(font)

		br = QPen()
		br.setWidth(lwidth)
		painter.setPen(br)

		br = QBrush(Qt.SolidPattern)
		br.setColor(Qt.white)
		painter.setBrush(br)

		left_span = 60
		right_span = 50
		up_span = 50
		down_span = 50

		smax = 0
		smin = 0
		for b in bsects:
			if b.l > smax: smax = b.l
			if b.l < smin: smin = b.l

		fheight = height - up_span - down_span
		#hsum = 0
		#for s in bsects: hsum += s.l 
		hkoeff = float(fheight) / (smax - smin)
		hbase = hkoeff * smax + up_span

		lu = QPoint(left_span, hbase)
		ru = QPoint(width - right_span, hbase)
		ld = QPoint(left_span + base_height, hbase+base_height)
		rd = QPoint(width - right_span - base_height, hbase+base_height)

		fsize = width - right_span - left_span
		lsum = 0
		for s in sects: lsum += s.l 
		lkoeff = float(fsize) / lsum

		painter.drawLine(lu, ru)
		painter.drawLine(lu, ld)
		painter.drawLine(ld, rd)
		painter.drawLine(rd, ru)

		def xnode(n):
			x = 0
			for i in range(n): x += sects[i].l * lkoeff
			return left_span + x

		for i in range(len(bsects)):
			if bsects[i].l != 0:
				painter.drawLine(QPoint(xnode(i), hbase), QPoint(xnode(i), hbase - bsects[i].l*hkoeff))
				#painter.drawEllipse(paintool.radrect(QPoint(xnode(i), hbase - bsects[i].l*hkoeff), 10))
				painter.drawEllipse(paintool.radrect(QPoint(xnode(i), hbase), 5))
	
				
				if (bsects[i].l < 0):
					angle = deg(90)
				else:
					angle = deg(-90)
	
				paintool.zadelka_sharnir(painter, QPoint(xnode(i), hbase - bsects[i].l*hkoeff), angle, 30, 10, 5)

		paintool.zadelka_sharnir_type2(painter, QPoint(xnode(0), hbase), deg(0), 30, 10, 5)
			
