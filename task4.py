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

class ShemeTypeT4(common.SchemeType):
	def __init__(self):
		super().__init__("Тип4 (Свободная ферма)")
		self.setwidgets(ConfWidget_T4(self), PaintWidget_T4(), common.TableWidget())

class ConfWidget_T4(common.ConfWidget):
	class sect:
		def __init__(self, direct=1, strt=(0,0), fini=(1,1)):
			self.xstrt=strt[0]
			self.ystrt=strt[1]
			self.xfini=fini[0]
			self.yfini=fini[1]

	class sectforce:
		def __init__(self, distrib=False):
			self.distrib = distrib

	class betsect:
		def __init__(self, fen=True, men="clean"):
			self.fen = fen
			self.men = men

	def __init__(self, sheme):
		super().__init__()
		self.shemetype = sheme

		self.shemetype.task = {
			"sections": 
			[
				self.sect(strt=(0,0), fini=(1,1)),
				self.sect(strt=(1,1), fini=(2,1)),
				self.sect(strt=(2,1), fini=(3,0))
			],

			"sectforce": 
			[
				self.sectforce(distrib=False),
				self.sectforce(distrib=False),
				self.sectforce(distrib=True),
			],

			"betsect": 
			[
				self.betsect(),
				self.betsect(),
				self.betsect()
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
		self.shemetype.base_length = self.sett.add("Базовая длина:", "int", "80")
		#self.shemetype.base_d = self.sett.add("Базовая длина:", "int", "40")
		#self.shemetype.base_h = self.sett.add("Базовая толщина:", "int", "20")
		#self.shemetype.zadelka = self.sett.add("Заделка:", "bool", True)
		#self.shemetype.axis = self.sett.add("Центральная ось:", "bool", True)
		#self.shemetype.zadelka_len = self.sett.add("Длина заделки:", "float", "30")
		#self.shemetype.dimlines_start_step = self.sett.add("Отступ размерных линий:", "float", "20")
		#self.shemetype.dimlines_step = self.sett.add("Шаг размерных линий:", "float", "40")
		#self.shemetype.base_height = self.sett.add("Базовая высота стержня:", "int", "10")
		self.sett.updated.connect(self.redraw)

		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter

		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("xstrt", "float", "X0")
		self.table.addColumn("ystrt", "float", "Y0")
		self.table.addColumn("xfini", "float", "X1")
		self.table.addColumn("yfini", "float", "Y1")
		#self.table.addColumn("dtext", "str", "Текст")
		#self.table.addColumn("dtext_en", "bool", "Текст")
		#self.table.addColumn("h", "float", "Высота")
		#self.table.addColumn("htext", "str", "Текст")
		#self.table.addColumn("htext_en", "bool", "Текст")
		#self.table.addColumn("shtrih", "bool", "Штрих")
		#self.table.addColumn("intgran", "bool", "Вн гран")
		self.table.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table1.addColumn("distrib", "bool", "Распр. нагрузка")
		self.table1.updateTable()


		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("fen", "bool", "Сила")
		self.table2.addColumn("men", "list", "Момент", variant=["clean", "+", "-"])
		self.table2.updateTable()

		#self.table2.addColumn("l", "float", "Длина опоры")
		#self.table2.updateTable()
		
		self.vlayout.addLayout(self.butlayout)

		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		
		self.vlayout.addWidget(QLabel("Распределённые силы:"))
		self.vlayout.addWidget(self.table1)
		
		self.vlayout.addWidget(QLabel("Локальные силы:"))
		self.vlayout.addWidget(self.table2)
		
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)
		self.table1.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)

		self.setLayout(self.vlayout)

	def add_action(self):
		self.shemetype.task["sections"].append(self.sect())
		self.shemetype.task["betsect"].append(self.betsect())
		self.shemetype.task["sectforce"].append(self.sectforce())
		self.redraw()
		self.updateTables()

	def del_action(self):
		if len(self.shemetype.task["sections"]) == 1: return
		del self.shemetype.task["sections"][-1]
		del self.shemetype.task["betsect"][-1]
		del self.shemetype.task["sectforce"][-1]
		self.redraw()
		self.updateTables()

	def inittask(self):
		#compat
		return {}

	def updateTables(self):
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

class PaintWidget_T4(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()

	def paintEventImplementation(self, ev):
		assert len(self.sections()) == len(self.bsections())

		width = self.width()
		height = self.height()

		center = QPoint(width/2, height/2)

		font_size = self.shemetype.font_size.get()
		lwidth = self.shemetype.line_width.get()

		base_length = self.shemetype.base_length.get()
		#base_h = self.shemetype.base_h.get()
		#zadelka = self.shemetype.zadelka.get()
		#axis = self.shemetype.axis.get()
		#zadelka_len = self.shemetype.zadelka_len.get()
		#dimlines_step = self.shemetype.dimlines_step.get()
		#dimlines_start_step = self.shemetype.dimlines_start_step.get()
		#arrow_size = self.shemetype.arrow_size_getter.get()

		painter = QPainter(self)
		font = painter.font()
		font.setItalic(True)
		font.setPointSize(font_size)
		painter.setFont(font)

		default_pen = QPen()
		default_pen.setWidth(lwidth)
		painter.setPen(default_pen)

		default_brush = QBrush(Qt.SolidPattern)
		default_brush.setColor(Qt.white)
		painter.setBrush(default_brush)

		font = painter.font()
		font.setItalic(True)
		font.setPointSize(font_size)
		painter.setFont(font)

		#left_span = 50
		#right_span = 50
		#up_span = 100
		#down_span = 100 + len(self.sections()) * dimlines_step + dimlines_start_step

		# Расчитываем смещения
		coordes = []
		xmin=0
		ymin=0
		xmax=0
		ymax=0

		for s in self.sections():
			xmin = min(xmin, s.xstrt, s.xfini)
			xmax = max(xmax, s.xstrt, s.xfini)
			ymin = min(ymin, s.ystrt, s.yfini)
			ymax = max(ymin, s.ystrt, s.yfini)

		xshift = - (xmin + xmax) / 2 * base_length
		yshift = (ymin + ymax) / 2 * base_length
		
		for s in self.sections():
			coordes.append((
				QPoint(
					s.xstrt * base_length + center.x() + xshift, 
					- s.ystrt * base_length + center.y() + yshift), 
				QPoint(
					s.xfini * base_length + center.x() + xshift, 
					- s.yfini * base_length + center.y() + yshift)))


		# Начинаем рисовать
		for strt, fini in coordes:
			painter.drawLine(strt, fini)



