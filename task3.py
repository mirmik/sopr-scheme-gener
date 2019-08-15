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
		def __init__(self, shtrih = False, intgran=True, **kwarg):
			self.d = kwarg["d"]
			self.h = kwarg["h"]
			self.shtrih = shtrih
			self.intgran = intgran

	class betsect:
		def __init__(self, **kwarg):
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
		#self.shemetype.base_height = self.sett.add("Базовая высота стержня:", "int", "10")
		self.sett.updated.connect(self.redraw)

		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter

		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("d", "float", "Длина секции")
		self.table.addColumn("h", "float", "Высота секции")
		self.table.addColumn("shtrih", "bool", "Штриховать")
		self.table.addColumn("intgran", "bool", "Внутренняя граница")
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

		left_span = 50
		right_span = 50
		up_span = 100
		down_span = 100

		if zadelka:
			left_span += base_h
			right_span += base_h

		width_span = left_span + right_span
		height_span = up_span + down_span

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

				painter.drawRect(QRect(center.x() - w /2, center.y() - h/2, w, h))

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
			w = fsect.h * 1.5 * base_h
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

