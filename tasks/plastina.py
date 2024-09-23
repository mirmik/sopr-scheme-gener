import common
import paintwdg
import math

import tablewidget
import paintool
import taskconf_menu

from paintool import deg
from items.squaremoment import *

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ShemeTypeT3(common.SchemeType):
	def __init__(self):
		super().__init__("Пластина")
		self.setwidgets(ConfWidget_T3(self), PaintWidget_T3(), common.TableWidget())

class ConfWidget_T3(common.ConfWidget):
	class sect:
		def __init__(self, d = 1, h = 1, shtrih = False, intgran=True, 
				dtext="", htext="", dtext_en=True, htext_en=True):
			self.d = d
			self.h = h
			self.shtrih = shtrih
			self.intgran = intgran
			self.dtext = dtext
			self.htext = htext
			self.dtext_en = dtext_en
			self.htext_en = htext_en

	class sectforce:
		def __init__(self, distrib=False):
			self.distrib = distrib


	class betsect:
		def __init__(self, fen="нет", men="нет", sharn="нет"):
			if men == "clean": men = "нет"
			self.fen = fen
			self.men = men
			self.sharn = sharn

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(d=1.5, h=2),
				self.sect(d=3, h=2, shtrih=True, intgran=False),
				self.sect(d=4.5, h=1, shtrih=True)
			],

			"sectforce": 
			[
				self.sectforce(),
				self.sectforce(),
				self.sectforce(),
			],

			"betsect": 
			[
				self.betsect(),
				self.betsect(),
				self.betsect()
			],

			"labels": []
		}

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("d", "float", "Длина")
		self.table.addColumn("dtext", "str", "Текст")
		self.table.addColumn("dtext_en", "bool", "Текст")
		self.table.addColumn("h", "float", "Высота")
		self.table.addColumn("htext", "str", "Текст")
		self.table.addColumn("htext_en", "bool", "Текст")
		self.table.addColumn("shtrih", "bool", "Штрих")
		self.table.addColumn("intgran", "bool", "Вн гран")
		self.table.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table1.addColumn("distrib", "bool", "Распр. нагрузка")
		self.table1.updateTable()


		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("fen", "list", "Сила", variant=["нет", "+", "-"])
		self.table2.addColumn("men", "list", "Момент", variant=["нет", "+", "-"])
		self.table2.addColumn("sharn", "list", "Шарнир", variant=["нет", "1", "2"])
		self.table2.updateTable()

		#self.table2.addColumn("l", "float", "Длина опоры")
		#self.table2.updateTable()

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

		self.vlayout.addWidget(self.shemetype.texteditor)


	"""Виджет настроек задачи T0"""
	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		#self.shemetype.base_d = self.sett.add("Базовая длина:", "int", "40")
		self.shemetype.base_h = self.sett.add("Базовая толщина:", "int", "20")
		self.shemetype.zadelka = self.sett.add("Заделка:", "bool", True)
		self.shemetype.axis = self.sett.add("Центральная ось:", "bool", True)
		self.shemetype.zadelka_len = self.sett.add("Длина заделки:", "float", "30")
		self.shemetype.dimlines_start_step = self.sett.add("Отступ размерных линий:", "float", "20")
		self.shemetype.dimlines_step = self.sett.add("Шаг размерных линий:", "float", "40")
		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "13")
		#self.shemetype.base_height = self.sett.add("Базовая высота стержня:", "int", "10")
		self.sett.updated.connect(self.redraw)

		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)

		self.update_interface()
		self.setLayout(self.vlayout)

	def add_action_impl(self):
		self.shemetype.task["sections"].append(self.sect())
		self.shemetype.task["betsect"].append(self.betsect())
		self.shemetype.task["sectforce"].append(self.sectforce())
		self.redraw()
		self.updateTables()

	def insert_action_impl(self, idx):
		self.shemetype.task["sections"].insert(idx, self.sect())
		self.shemetype.task["betsect"].insert(idx, self.betsect())
		self.shemetype.task["sectforce"].insert(idx, self.sectforce())
		self.redraw()
		self.updateTables()

	def del_action_impl(self, idx):
		if len(self.shemetype.task["sections"]) == 1: return
		del self.shemetype.task["sections"][idx]
		del self.shemetype.task["betsect"][idx]
		del self.shemetype.task["sectforce"][idx]
		self.redraw()
		self.updateTables()

	def inittask(self):
		#compat
		return {}

	def updateTables(self):
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

class PaintWidget_T3(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()
		self.enable_common_mouse_events()

	def paintEventImplementation(self, ev):
		assert len(self.sections()) == len(self.bsections())

		width = self.width()
		height = self.height()

		center = QPointF(width/2, self.hcenter)
		self.labels_center = center

		font_size = self.shemetype.font_size.get()
		lwidth = self.shemetype.line_width.get()

		base_h = self.shemetype.base_h.get()
		zadelka = self.shemetype.zadelka.get()
		axis = self.shemetype.axis.get()
		zadelka_len = self.shemetype.zadelka_len.get()
		dimlines_step = self.shemetype.dimlines_step.get()
		dimlines_start_step = self.shemetype.dimlines_start_step.get()
		arrow_size = self.shemetype.arrow_size.get()

		font = self.painter.font()
		font.setItalic(True)
		font.setPointSize(font_size)
		self.painter.setFont(font)

		default_pen = QPen()
		default_pen.setWidth(lwidth)
		self.painter.setPen(default_pen)

		default_brush = QBrush(Qt.SolidPattern)
		default_brush.setColor(Qt.white)
		self.painter.setBrush(default_brush)

		font = self.painter.font()
		font.setItalic(True)
		font.setPointSize(font_size)
		self.painter.setFont(font)

		left_span = 50
		right_span = 50
		up_span = 100
		down_span = 100 + len(self.sections()) * dimlines_step + dimlines_start_step

		if zadelka:
			left_span += base_h + zadelka_len
			right_span += base_h + zadelka_len

		width_span = left_span + right_span
		height_span = up_span + down_span
		center = center + QPointF(left_span - right_span, (up_span - down_span) / 2)

		maxd = 0
		maxh = 0
		for s in self.sections():
			if s.d > maxd: maxd = s.d
			if s.h > maxh: maxh = s.h

		base_d = (width - width_span) / maxd
		self.labels_width_scale = base_d

		sprev = None
		for s in reversed(self.sections()):
			shtrih = s.shtrih
			w = s.d * base_d
			h = s.h * base_h

			if sprev:
				sprev_d = sprev.d * base_d
				sprev_h = sprev.h * base_h

			if s.intgran:
				self.painter.drawRect(QRectF(center.x() - w /2, center.y() - h/2, w, h))

			else:
				pen = QPen()
				pen.setWidth(lwidth)
				pen.setColor(Qt.white)
				self.painter.setPen(pen)
		
				brush = QBrush(Qt.SolidPattern)
				brush.setColor(Qt.white)
				self.painter.setBrush(brush)

				self.painter.drawRect(QRectF(center.x() - w /2, center.y() - (maxh * base_h)/2, w, maxh * base_h))

				pen.setColor(Qt.black)
				self.painter.setPen(pen)

				self.painter.drawLine(QPointF(center.x() - w/2, center.y() - h/2), QPointF(center.x() + w/2, center.y() - h/2))
				self.painter.drawLine(QPointF(center.x() - w/2, center.y() + h/2), QPointF(center.x() + w/2, center.y() + h/2))
				
				if sprev:
					self.painter.drawLine(QPointF(center.x() - w/2, center.y() - h/2), QPointF(center.x() - w/2, center.y() - sprev_h/2))
					self.painter.drawLine(QPointF(center.x() - w/2, center.y() + h/2), QPointF(center.x() - w/2, center.y() + sprev_h/2))
					self.painter.drawLine(QPointF(center.x() + w/2, center.y() - h/2), QPointF(center.x() + w/2, center.y() - sprev_h/2))
					self.painter.drawLine(QPointF(center.x() + w/2, center.y() + h/2), QPointF(center.x() + w/2, center.y() + sprev_h/2))

			if shtrih:
				pen = QPen(Qt.NoPen)
				pen.setWidth(lwidth)
				self.painter.setPen(pen)

				brush = QBrush(Qt.BDiagPattern)
				brush.setColor(Qt.black)
				self.painter.setBrush(brush)
				
				self.painter.drawRect(QRectF(center.x() - w /2 - lwidth/2, center.y() - h/2 - lwidth/2, w + lwidth, h + lwidth))

			self.painter.setPen(default_pen)
			self.painter.setBrush(default_brush)
			sprev = s

		if zadelka:
			fsect = self.sections()[-1]
			h = fsect.h * base_h
			w = zadelka_len
			c = base_h

			lx = center.x() - fsect.d * base_d / 2
			llx = center.x() - fsect.d * base_d / 2 - w
			rx = center.x() + fsect.d * base_d / 2
			rrx = center.x() + fsect.d * base_d / 2 + w

			uy = center.y() - h / 2
			dy = center.y() + h / 2

			pen = QPen(Qt.NoPen)
			pen.setWidth(lwidth)
			self.painter.setPen(pen)

			brush = QBrush(Qt.FDiagPattern)
			brush.setColor(Qt.black)
			self.painter.setBrush(brush)

			self.painter.drawRect(QRectF(llx - c, uy - c, w + c, h + 2*c))
			self.painter.drawRect(QRectF(rx, uy - c, w + c, h + 2*c))

			brush = QBrush(Qt.SolidPattern)
			brush.setColor(Qt.white)
			self.painter.setBrush(brush)

			self.painter.drawRect(QRectF(llx - lwidth/2, uy - lwidth/2, w + lwidth, h + lwidth))
			self.painter.drawRect(QRectF(rx- lwidth/2, uy- lwidth/2, w+ lwidth, h+ lwidth))

			self.painter.setBrush(default_brush)

			brush = QBrush(Qt.BDiagPattern)
			brush.setColor(Qt.black)
			self.painter.setBrush(brush)

			self.painter.drawRect(QRectF(llx - lwidth/2, uy - lwidth/2, w + lwidth, h + lwidth))
			self.painter.drawRect(QRectF(rx- lwidth/2, uy- lwidth/2, w+ lwidth, h+ lwidth))

			self.painter.setPen(default_pen)

			self.painter.drawLine(QPointF(llx, uy), QPointF(lx, uy))
			self.painter.drawLine(QPointF(llx, uy), QPointF(llx, dy))
			self.painter.drawLine(QPointF(llx, dy), QPointF(lx, dy))

			self.painter.drawLine(QPointF(rx, uy), QPointF(rrx, uy))
			self.painter.drawLine(QPointF(rrx, uy), QPointF(rrx, dy))
			self.painter.drawLine(QPointF(rx, dy), QPointF(rrx, dy))

			self.painter.setPen(default_pen)
			self.painter.setBrush(default_brush)

		if axis:
			pen = QPen(Qt.DashDotLine)
			pen.setWidth(lwidth)
			self.painter.setPen(pen)

			self.painter.drawLine(QPointF(center.x(), center.y() + (maxh) * base_h/2 + 10), QPointF(center.x(), center.y() - (maxh) * base_h /2 - 10))


		i = 0
		wprev = 0
		for s in self.sections():
			"""Текстовые поля"""

			w = s.d * base_d
			h = s.h * base_h
			c = center

			i += 1

			self.painter.setPen(default_pen)
			self.painter.setBrush(default_brush)

			pen = QPen()
			pen.setWidth(int(lwidth/2))
			self.painter.setPen(pen)

			if s.dtext_en:		
				p0 = QPointF(center.x() - s.d/2 * base_d, center.y() + s.h/2 * base_h)
				p1 = QPointF(center.x() + s.d/2 * base_d, center.y() + s.h/2 * base_h)
				level = center.y() + maxh/2 * base_h + dimlines_start_step + dimlines_step * i 

				if s.dtext == "":
					dtxt = paintool.greek("\\diam{}d".format(s.d if s.d != 1 else "")) 
				else:
					dtxt = paintool.greek(s.dtext) 

				paintool.dimlines(self.painter, p0, p1, level)
				paintool.draw_text_centered(self.painter, QPointF((p0.x() + p1.x())/2, level - 5), dtxt, font)

			if s.htext_en:

				if s.htext == "":
					htxt = paintool.greek("{}h".format(s.h if s.h != 1 else "")) 
				else:
					htxt = paintool.greek(s.htext) 

				paintool.draw_vertical_splashed_dimlines_with_text(
					self.painter, 
					c + QPointF(wprev/2+(w-wprev)/4, -h/2), 
					c + QPointF(wprev/2+(w-wprev)/4, h/2), 
					10, c, htxt, font)

			wprev = w


		wprev = 0
		for i in range(len(self.sectforce())):
			""" Отрисовываем распределенную нагрузку."""

			s = self.sections()[i]
			sf = self.sectforce()[i]

			distrib_step = 10
			distrib_alen = 20

			w = s.d * base_d
			h = s.h * base_h
			c = center

			if sf.distrib:
				apnt = center + QPointF(w/2, -h/2-lwidth)
				bpnt = center + QPointF(wprev/2, -h/2-lwidth)
				paintool.draw_distribload(self.painter, apnt, bpnt, distrib_step, arrow_size/3*2, distrib_alen)

				apnt = center + QPointF(-wprev/2, -h/2-lwidth)
				bpnt = center + QPointF(-w/2, -h/2-lwidth)
				paintool.draw_distribload(self.painter, apnt, bpnt, distrib_step, arrow_size/3*2, distrib_alen)

				apnt = center + QPointF(wprev/2, -h/2-lwidth-distrib_alen)
				bpnt = center + QPointF(-wprev/2, -h/2-lwidth-distrib_alen)
				self.painter.drawLine(apnt, bpnt)

			wprev = w


		for i in range(len(self.bsections())):
			b = self.bsections()[i]
			s = self.sections()[i]

			w = s.d * base_d
			h = s.h * base_h
			c = center

			alen = 40
			moment_radius = 40

			if b.fen != "нет":
				apnt0 = center + QPointF(w/2, -h/2-lwidth)
				apnt1 = center + QPointF(-w/2, -h/2-lwidth)

				if b.fen == "-":
					paintool.common_arrow(self.painter, apnt0 + QPointF(0,-alen), apnt0, arrow_size)	
					paintool.common_arrow(self.painter, apnt1 + QPointF(0,-alen), apnt1, arrow_size)				

				if b.fen == "+":
					paintool.common_arrow(self.painter, apnt0, apnt0 + QPointF(0,-alen), arrow_size)	
					paintool.common_arrow(self.painter, apnt1, apnt1 + QPointF(0,-alen), arrow_size)				

				self.painter.drawLine(apnt0+ QPointF(0,-alen),apnt1+ QPointF(0,-alen))

			if b.men != "нет":
				direction = b.men == "+"

				arrow_size_pair = (arrow_size, 4)
				for apnt, direction in [
					(center + QPointF(w/2, 0),not direction), 
					(center + QPointF(-w/2, 0), direction)
				]:
					self.common_scene.addItem(SquareMomentItem(
						apnt, 
						moment_radius/2, 
						h/2 + 32,  
						inverse=direction, 
						arrow_size=arrow_size_pair,
						brush=Qt.black
					))

			if b.sharn != "нет":
				termrad = 20
				for w in [w, -w]:
					if self.bsections()[i].sharn == "1":
						paintool.draw_sharnir_1dim(
							self.painter, 
							pnt=center+QPointF(w/2,h/2+3), 
							angle=math.pi/2, 
							rad=3.5, 
							termrad=termrad, 
							termx=15, 
							termy=10, pen=self.pen, halfpen=self.halfpen, doublepen=self.doublepen)

					elif self.bsections()[i].sharn == "2":
						paintool.draw_sharnir_2dim(
							self.painter, 
							pnt=center+QPointF(w/2,h/2+3), 
							angle=math.pi/2, 
							rad=3.5, 
							termrad=termrad, 
							termx=15, 
							termy=10, pen=self.pen, halfpen=self.halfpen)


		self.draw_labels()
