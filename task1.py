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

class ShemeTypeT1(common.SchemeType):
	def __init__(self):
		super().__init__("Тип1 (Соедиение звезда)")
		self.setwidgets(ConfWidget_T1(self), PaintWidget_T1(), common.TableWidget())

class ConfWidget_T1(common.ConfWidget):
	class sect:
		def __init__(self, l=1, angle=30, ztype=0, text="", display_angle=False, force=0):
			self.l = l
			self.angle = angle
			self.ztype = ztype 
			self.text = text
			self.display_angle = False
			self.force = 0

	"""Виджет настроек задачи T0"""
	def __init__(self, sheme):
		super().__init__()
		self.shemetype = sheme

		self.shemetype.task = {
			"sections": 
			[
				self.sect(l=1.5, angle=135),
				self.sect(l=1, angle=90),
				self.sect(l=1, angle=0)
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
		self.shemetype.first_dir = self.sett.add("Положение первого стержня (верт/гор):", "bool", True)
		self.shemetype.base_length = self.sett.add("Базовая длина:", "int", "80")
		
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter

		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("l", "float")
		self.table.addColumn("angle", "float")
		self.table.updateTable()

		self.vlayout.addLayout(self.butlayout)
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)

		self.setLayout(self.vlayout)

	def add_action(self):
		self.shemetype.task["sections"].append(self.sect())
		self.redraw()
		self.updateTables()

	def del_action(self):
		if len(self.shemetype.task["sections"]) == 1: return
		del self.shemetype.task["sections"][-1]
		self.redraw()
		self.updateTables()

	def inittask(self):
		#compat
		return {}

	def updateTables(self):
		self.table.updateTable()



class PaintWidget_T1(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()

	def paintEventImplementation(self, ev):
		sects = self.shemetype.task["sections"]

		angle = deg(180)

		width = self.width()
		height = self.height()

		center = QPoint(width/2, height/2)

		font_size = self.shemetype.font_size.get()
		lwidth = self.shemetype.line_width.get()

		base_length = self.shemetype.base_length.get()


		painter = QPainter(self)
		font = painter.font()
		font.setItalic(True)
		font.setPointSize(font_size)
		painter.setFont(font)

		br = QPen()
		br.setWidth(lwidth)
		painter.setPen(br)


		ster = []
		for s in sects:
			if s.l != 0:
				ster.append(s)

		brush = QBrush(Qt.SolidPattern)
		brush.setColor(Qt.white)
		painter.setBrush(brush)

		for s in ster:
			length = s.l * base_length
			pnt = center + QPoint(math.cos(angle) * length, math.sin(angle) * length)
			painter.drawLine(center, pnt)
			painter.drawEllipse(QRect(pnt - QPoint(5, 5), pnt + QPoint(5, 5)))
			angle -= deg(s.angle)

		painter.drawEllipse(QRect(center - QPoint(5, 5), center + QPoint(5, 5)))