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
		super().__init__("Тип соедиения звезда.")
		self.setwidgets(ConfWidget_T1(self), PaintWidget_T1(), common.TableWidget())

class ConfWidget_T1(common.ConfWidget):
	class sect:
		def __init__(self, l=1, angle=30, body=True, force="нет", ftxt=""):
			self.l = l
			self.body = body
			self.force = force
			self.angle = angle
			self.ftxt = ftxt
			
	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(l=1.5, angle=135),
				self.sect(l=1, angle=90),
				self.sect(l=1, angle=0),
				self.sect(l=1, angle=-90, body=False, force="к", ftxt="F")
			],
		}

		
	"""Виджет настроек задачи T0"""
	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		#self.shemetype.first_dir = self.sett.add("Положение первого стержня (верт/гор):", "bool", True)
		self.shemetype.base_length = self.sett.add("Базовая длина:", "int", "80")
		self.sett.updated.connect(self.redraw)

		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter

		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("l", "float", "Длина")
		self.table.addColumn("angle", "float", "Угол")
		self.table.addColumn("body", "bool", "Стержень")
		self.table.addColumn("force", "list", "Сила", variant=["нет", "к", "от"])
		self.table.addColumn("ftxt", "str", "Сила")
		self.table.updateTable()

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

		#firstdir = self.shemetype.first_dir.get()
		#angle = deg(180) if firstdir else deg(90)

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

		brush = QBrush(Qt.SolidPattern)
		brush.setColor(Qt.white)
		painter.setBrush(brush)

		# Расчитываем центр.

		xmin, ymin = 0, 0
		xmax, ymax = 0, 0

		for i in range(len(sects)):
			sect = self.sections()[i]
			angle = deg(sect.angle)
			length = sect.l

			point = (
				math.cos(angle) * length,
				-math.sin(angle) * length,
			)

			xmin, xmax = min(xmin, point[0]) , max(xmax, point[0])
			ymin, ymax = min(ymin, point[0]) , max(ymax, point[0])



		for i in range(len(sects)):
			sect = self.sections()[i]
			angle = deg(sect.angle)

			if sect.body:
				length = sect.l * base_length
				pnt = center + QPoint(math.cos(angle) * length, -math.sin(angle) * length)
				painter.drawLine(center, pnt)
				paintool.zadelka_sharnir(painter, pnt, -angle, 30, 10, 5)

		painter.drawEllipse(QRect(center - QPoint(5, 5), center + QPoint(5, 5)))