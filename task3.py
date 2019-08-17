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

class ShemeTypeT3(common.SchemeType):
	def __init__(self):
		super().__init__("Тип3 (Пластина)")
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

	class betsect:
		def __init__(self):
			pass

	"""Виджет настроек задачи T0"""
	def __init__(self, sheme):
		super().__init__()
		self.shemetype = sheme

		self.shemetype.task = {
			"sections": 
			[
				self.sect(d=1.5, h=2),
				self.sect(d=3, h=2, shtrih=True, intgran=False),
				self.sect(d=4.5, h=1, shtrih=True)
			],

			"betsect": 
			[
				self.betsect(),
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
		#self.shemetype.base_d = self.sett.add("Базовая длина:", "int", "40")
		self.shemetype.base_h = self.sett.add("Базовая толщина:", "int", "20")
		self.shemetype.zadelka = self.sett.add("Заделка:", "bool", True)
		self.shemetype.axis = self.sett.add("Центральная ось:", "bool", True)
		self.shemetype.zadelka_len = self.sett.add("Длина заделки:", "float", "30")
		self.shemetype.dimlines_start_step = self.sett.add("Отступ размерных линий:", "float", "20")
		self.shemetype.dimlines_step = self.sett.add("Шаг размерных линий:", "float", "40")
		#self.shemetype.base_height = self.sett.add("Базовая высота стержня:", "int", "10")
		self.sett.updated.connect(self.redraw)

		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter

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

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		#self.table2.addColumn("l", "float", "Длина опоры")
		#self.table2.updateTable()
		
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

class PaintWidget_T3(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()

	def paintEventImplementation(self, ev):
		assert len(self.sections()) + 1 == len(self.bsections())

		width = self.width()
		height = self.height()

		center = QPoint(width/2, height/2)

		font_size = self.shemetype.font_size.get()
		lwidth = self.shemetype.line_width.get()

		base_h = self.shemetype.base_h.get()
		zadelka = self.shemetype.zadelka.get()
		axis = self.shemetype.axis.get()
		zadelka_len = self.shemetype.zadelka_len.get()
		dimlines_step = self.shemetype.dimlines_step.get()
		dimlines_start_step = self.shemetype.dimlines_start_step.get()
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

		left_span = 50
		right_span = 50
		up_span = 100
		down_span = 100 + len(self.sections()) * dimlines_step + dimlines_start_step

		if zadelka:
			left_span += base_h + zadelka_len
			right_span += base_h + zadelka_len

		width_span = left_span + right_span
		height_span = up_span + down_span
		center = center + QPoint(left_span - right_span, (up_span - down_span) / 2)

		maxd = 0
		maxh = 0
		for s in self.sections():
			if s.d > maxd: maxd = s.d
			if s.h > maxh: maxh = s.h

		base_d = (width - width_span) / maxd
		#base_h = (height - height_span) / maxh

		sprev = None
		for s in reversed(self.sections()):
			shtrih = s.shtrih
			w = s.d * base_d
			h = s.h * base_h

			if sprev:
				sprev_d = sprev.d * base_d
				sprev_h = sprev.h * base_h

			if s.intgran:
				painter.drawRect(QRect(center.x() - w /2, center.y() - h/2, w, h))

			else:
				pen = QPen()
				pen.setWidth(lwidth)
				pen.setColor(Qt.white)
				painter.setPen(pen)
		
				brush = QBrush(Qt.SolidPattern)
				brush.setColor(Qt.white)
				painter.setBrush(brush)

				painter.drawRect(QRect(center.x() - w /2, center.y() - (maxh * base_h)/2, w, maxh * base_h))

				pen.setColor(Qt.black)
				painter.setPen(pen)

				painter.drawLine(QPoint(center.x() - w/2, center.y() - h/2), QPoint(center.x() + w/2, center.y() - h/2))
				painter.drawLine(QPoint(center.x() - w/2, center.y() + h/2), QPoint(center.x() + w/2, center.y() + h/2))
				
				if sprev:
					painter.drawLine(QPoint(center.x() - w/2, center.y() - h/2), QPoint(center.x() - w/2, center.y() - sprev_h/2))
					painter.drawLine(QPoint(center.x() - w/2, center.y() + h/2), QPoint(center.x() - w/2, center.y() + sprev_h/2))
					painter.drawLine(QPoint(center.x() + w/2, center.y() - h/2), QPoint(center.x() + w/2, center.y() - sprev_h/2))
					painter.drawLine(QPoint(center.x() + w/2, center.y() + h/2), QPoint(center.x() + w/2, center.y() + sprev_h/2))

			if shtrih:
				pen = QPen(Qt.NoPen)
				pen.setWidth(lwidth)
				painter.setPen(pen)

				brush = QBrush(Qt.BDiagPattern)
				brush.setColor(Qt.black)
				painter.setBrush(brush)
				
				painter.drawRect(QRect(center.x() - w /2 - lwidth/2, center.y() - h/2 - lwidth/2, w + lwidth, h + lwidth))

			painter.setPen(default_pen)
			painter.setBrush(default_brush)
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
			painter.setPen(pen)

			brush = QBrush(Qt.FDiagPattern)
			brush.setColor(Qt.black)
			painter.setBrush(brush)

			painter.drawRect(QRect(llx - c, uy - c, w + c, h + 2*c))
			painter.drawRect(QRect(rx, uy - c, w + c, h + 2*c))

			brush = QBrush(Qt.SolidPattern)
			brush.setColor(Qt.white)
			painter.setBrush(brush)

			painter.drawRect(QRect(llx - lwidth/2, uy - lwidth/2, w + lwidth, h + lwidth))
			painter.drawRect(QRect(rx- lwidth/2, uy- lwidth/2, w+ lwidth, h+ lwidth))

			painter.setBrush(default_brush)

			brush = QBrush(Qt.BDiagPattern)
			brush.setColor(Qt.black)
			painter.setBrush(brush)

			painter.drawRect(QRect(llx - lwidth/2, uy - lwidth/2, w + lwidth, h + lwidth))
			painter.drawRect(QRect(rx- lwidth/2, uy- lwidth/2, w+ lwidth, h+ lwidth))

			painter.setPen(default_pen)

			painter.drawLine(QPoint(llx, uy), QPoint(lx, uy))
			painter.drawLine(QPoint(llx, uy), QPoint(llx, dy))
			painter.drawLine(QPoint(llx, dy), QPoint(lx, dy))

			painter.drawLine(QPoint(rx, uy), QPoint(rrx, uy))
			painter.drawLine(QPoint(rrx, uy), QPoint(rrx, dy))
			painter.drawLine(QPoint(rx, dy), QPoint(rrx, dy))

			painter.setPen(default_pen)
			painter.setBrush(default_brush)

		if axis:
			pen = QPen(Qt.DashDotLine)
			pen.setWidth(lwidth)
			painter.setPen(pen)

			painter.drawLine(QPoint(center.x(), center.y() + (maxh) * base_h/2 + 10), QPoint(center.x(), center.y() - (maxh) * base_h /2 - 10))


		i = 0
		wprev = 0
		for s in self.sections():
			"""Текстовые поля"""

			w = s.d * base_d
			h = s.h * base_h
			c = center

			i += 1

			painter.setPen(default_pen)
			painter.setBrush(default_brush)

			pen = QPen()
			pen.setWidth(lwidth/2)
			painter.setPen(pen)

			if s.dtext_en:		
				p0 = QPoint(center.x() - s.d/2 * base_d, center.y() + s.h/2 * base_h)
				p1 = QPoint(center.x() + s.d/2 * base_d, center.y() + s.h/2 * base_h)
				level = center.y() + maxh/2 * base_h + dimlines_start_step + dimlines_step * i 

				if s.dtext == "":
					dtxt = paintool.greek("\\diam{}d".format(s.d if s.d != 1 else "")) 
				else:
					dtxt = paintool.greek(s.dtext) 

				paintool.dimlines(painter, p0, p1, level)
				paintool.draw_text_centered(painter, QPoint((p0.x() + p1.x())/2, level - 5), dtxt, font)

			if s.htext_en:

				if s.htext == "":
					htxt = paintool.greek("{}h".format(s.h if s.h != 1 else "")) 
				else:
					htxt = paintool.greek(s.htext) 

				paintool.draw_vertical_splashed_dimlines_with_text(
					painter, 
					c + QPoint(wprev/2+(w-wprev)/4, -h/2), 
					c + QPoint(wprev/2+(w-wprev)/4, h/2), 
					arrow_size, c, htxt, font)

			wprev = w