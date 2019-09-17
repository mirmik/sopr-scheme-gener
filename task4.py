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
		def __init__(self, direct=1, strt=("",""), fini=(1,1), lsharn="clean", rsharn="clean"):
			self.xstrt=str(strt[0])
			self.ystrt=str(strt[1])
			self.xfini=str(fini[0])
			self.yfini=str(fini[1])
			self.lsharn = lsharn
			self.rsharn = rsharn

	class sectforce:
		def __init__(self, distrib="clean"):
			self.distrib = distrib

	class betsect:
		def __init__(self, 
					fenl="clean", fenr="clean", 
					menl="clean", menr="clean"):
			self.fenl = fenl
			self.fenr = fenr
			self.menl = menl
			self.menr = menr
			
	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(strt=(0,0), fini=(1,1), lsharn="1f"),
				self.sect(strt=("",""), fini=(2,1)),
				self.sect(strt=("",""), fini=(3,0))
			],

			"sectforce": 
			[
				self.sectforce(distrib="clean"),
				self.sectforce(distrib="clean"),
				self.sectforce(distrib="-"),
			],

			"betsect": 
			[
				self.betsect(menr="+"),
				self.betsect(),
				self.betsect()
			],
		}

	def __init__(self, sheme):
		super().__init__(sheme)

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

		sharnir_arr= ["clean", "1f", "1r", "1l", "2"]
		men_arr= ["clean", "+", "-"]
		fen_arr= ["clean", "+", "-"]

		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("xstrt", "str", "X0")
		self.table.addColumn("ystrt", "str", "Y0")
		self.table.addColumn("xfini", "str", "X1")
		self.table.addColumn("yfini", "str", "Y1")
		self.table.addColumn("lsharn", "list", "ШарнирЛ", variant=sharnir_arr)
		self.table.addColumn("rsharn", "list", "ШарнирП", variant=sharnir_arr)
		self.table.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table1.addColumn("distrib", "list", "Распр.", variant=["clean", "+", "-"])
		self.table1.updateTable()


		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("fenl", "list", "Сила", variant=fen_arr)
		self.table2.addColumn("fenr", "list", "Сила", variant=fen_arr)
		self.table2.addColumn("menl", "list", "Момент", variant=men_arr)
		self.table2.addColumn("menr", "list", "Момент", variant=men_arr)
		self.table2.updateTable()

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
		distrib_step = 10
		distrib_alen = 20
		#base_h = self.shemetype.base_h.get()
		#zadelka = self.shemetype.zadelka.get()
		#axis = self.shemetype.axis.get()
		#zadelka_len = self.shemetype.zadelka_len.get()
		#dimlines_step = self.shemetype.dimlines_step.get()
		#dimlines_start_step = self.shemetype.dimlines_start_step.get()
		arrow_size = self.shemetype.arrow_size_getter.get()

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

		last = None
		for s in self.sections():
			xstrt = float(s.xstrt) if s.xstrt != "" else float(last.xfini)
			ystrt = float(s.ystrt) if s.ystrt != "" else float(last.yfini)
			xfini = float(s.xfini)
			yfini = float(s.yfini)

			xmin = min(xmin, xstrt, xfini)
			xmax = max(xmax, xstrt, xfini)
			ymin = min(ymin, ystrt, yfini)
			ymax = max(ymin, ystrt, yfini)

			last = s

		xshift = - (xmin + xmax) / 2 * base_length
		yshift = (ymin + ymax) / 2 * base_length
		
		last = None
		for s in self.sections():
			xstrt = float(s.xstrt) if s.xstrt != "" else float(last.xfini)
			ystrt = float(s.ystrt) if s.ystrt != "" else float(last.yfini)
			xfini = float(s.xfini)
			yfini = float(s.yfini)

			coordes.append((
				QPoint(
					xstrt * base_length + center.x() + xshift, 
					- ystrt * base_length + center.y() + yshift), 
				QPoint(
					xfini * base_length + center.x() + xshift, 
					- yfini * base_length + center.y() + yshift)))

			last = s


		# Начинаем рисовать
		for strt, fini in coordes:
			painter.drawLine(strt, fini)

		# Распределённая нагрузка
		for i in range(len(self.sections())):
			strt, fini = coordes[i]
			sect = self.sections()[i]
			bsect = self.sectforce()[i]
			angle = common.angle(strt, fini) 

			if bsect.distrib == "+":
				paintool.draw_distribload(painter, pen=self.halfpen, 
					apnt=strt, 
					bpnt=fini, 
					step=distrib_step, 
					arrow_size=arrow_size/3*2, 
					alen=distrib_alen)

			elif bsect.distrib == "-":
				paintool.draw_distribload(painter, pen=self.halfpen, 
					apnt=fini, 
					bpnt=strt, 
					step=distrib_step, 
					arrow_size=arrow_size/3*2, 
					alen=distrib_alen)

		# Шарниры и заделки
		for i in range(len(self.sections())):
			strt, fini = coordes[i]
			sect = self.sections()[i]
			bsect = self.sectforce()[i]
			angle = common.angle(strt, fini) 

			def draw_sharn(pnt, angle, tp):
				if tp == "1f":
					paintool.draw_sharnir_1dim(
						painter=painter, 
						pnt=pnt, 
						angle=angle, 
						rad=4, 
						termrad=15, 
						termx=15, 
						termy=10, 
						pen=self.default_pen,
						halfpen=self.halfpen)

				elif tp == "1r":
					paintool.draw_sharnir_1dim(
						painter=painter, 
						pnt=pnt, 
						angle=angle + deg(90), 
						rad=4, 
						termrad=15, 
						termx=15, 
						termy=10, 
						pen=self.default_pen,
						halfpen=self.halfpen)

				elif tp == "1l":
					paintool.draw_sharnir_1dim(
						painter=painter, 
						pnt=pnt, 
						angle=angle - deg(90), 
						rad=4, 
						termrad=15, 
						termx=15, 
						termy=10, 
						pen=self.default_pen,
						halfpen=self.halfpen)

				elif tp == "2":
					paintool.draw_sharnir_2dim(
						painter=painter, 
						pnt=pnt, 
						angle=angle, 
						rad=4, 
						termrad=15, 
						termx=15, 
						termy=10, 
						pen=self.default_pen,
						halfpen=self.halfpen)

			if sect.lsharn != "clean":
				tp = sect.lsharn
				draw_sharn(strt, angle+ deg(180), tp)

			if sect.rsharn != "clean":
				tp = sect.rsharn
				draw_sharn(fini, angle, tp)


		# Силы и моменты
		for i in range(len(self.sections())):
			strt, fini = coordes[i]
			sect = self.sections()[i]
			sectforce = self.sectforce()[i]
			bsect = self.bsections()[i]
			angle = common.angle(strt, fini) 

			def draw_moment(pnt, angle, tp):
				rad=40

				if tp == "+":
					paintool.half_moment_arrow(
						painter=painter, 
						pnt=pnt, 
						rad=rad, 
						left=True, 
						inverse = False, 
						arrow_size=arrow_size)

				elif tp == "-":
					paintool.half_moment_arrow(
						painter=painter, 
						pnt=pnt, 
						rad=rad, 
						left=True, 
						inverse = False, 
						arrow_size=arrow_size)

			if bsect.menl != "clean":
				tp = bsect.menl
				draw_moment(strt, angle, tp)

			if bsect.menr != "clean":
				tp = bsect.menr
				draw_moment(strt, angle, tp)
				