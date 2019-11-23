import common
import paintwdg
import math

import tablewidget
import paintool
import taskconf_menu

import elements
import util
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
		def __init__(self, xoff=0, yoff=0, l=1, A=1, angle=30, sharn=True, body=True, force="нет", ftxt="", alttxt=False, addangle=0):
			self.yoff = xoff
			self.xoff = yoff
			self.l = l
			self.A = A
			self.body = body
			self.sharn = sharn
			self.force = force
			self.angle = angle
			self.ftxt = ftxt
			self.alttxt = alttxt
			self.addangle = addangle
			
	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(l=1.5, angle=135),
				self.sect(l=1, angle=90),
				self.sect(l=1, angle=0, addangle=45),
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
		self.table.addColumn("xoff", "float", "Смещ")
		self.table.addColumn("yoff", "float", "Смещ")
		self.table.addColumn("l", "float", "Длина")
		self.table.addColumn("angle", "float", "Угол")
		self.table.addColumn("body", "bool", "Стержень")
		self.table.addColumn("force", "list", "Сила", variant=["нет", "к", "от"])
		self.table.addColumn("ftxt", "str", "Сила")
		self.table.addColumn("alttxt", "bool", "Пол.Ткст.")
		self.table.addColumn("addangle", "float", "Доб.Угол")
		self.table.addColumn("sharn", "bool", "Шарн.")
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

		font_size = self.shemetype.font_size.get()
		lwidth = self.shemetype.line_width.get()

		base_length = self.shemetype.base_length.get()
		
		# Расчитываем центр.
		xmin, ymin = 0, 0
		xmax, ymax = 0, 0

		for i in range(len(sects)):
			sect = self.sections()[i]
			angle = deg(sect.angle)
			length = sect.l

			point = (
				math.cos(angle) * (length)  + sect.xoff,
				-math.sin(angle) * (length) + sect.yoff,
			)

			xmin, xmax = min(xmin, point[0]) , max(xmax, point[0])
			ymin, ymax = min(ymin, point[0]) , max(ymax, point[0])

		center = QPoint(width/2, height/2) + \
			QPoint(xmax - xmin, -ymax + ymin) / 2

		for i in range(len(sects)):
			# Рисуем доб угол
			sect = self.sections()[i]
			angle = sects[i].angle
			strt = center + QPointF(base_length * sect.xoff, base_length * sect.yoff)

			if sect.addangle != 0:
				rad = 50
				rad2 = 60
				rad3 = 65
				tgtangle = sect.angle + sect.addangle
				pen = QPen(Qt.DashDotLine)
				pen.setWidth(2)
				self.painter.setPen(pen)

				pnt1 = strt + rad2 * QPointF(math.cos(deg(angle)), -math.sin(deg(angle)))
				pnt2 = strt + rad2 * QPointF(math.cos(deg(tgtangle)), -math.sin(deg(tgtangle)))
				cpnt = strt + rad3 * QPointF(math.cos(deg(tgtangle+angle)/2), -math.sin(deg(tgtangle+angle)/2))

				self.painter.drawLine(center, pnt1)
				self.painter.drawLine(center, pnt2)

				self.painter.setPen(self.halfpen)
				self.painter.drawArc(paintool.radrect(center, rad), 
					angle*16, 
					sect.addangle*16)

				paintool.draw_text_centered(
					painter=self.painter, 
					pnt=cpnt, 
					text=paintool.greek(str(sect.addangle)+"\\degree"), 
					font=self.font)


		for i in range(len(sects)):
			sect = self.sections()[i]
			angle = deg(sect.angle)
			self.painter.setPen(self.pen)

			if sect.body:
				length = sect.l * base_length			
				strt = center + QPointF(base_length * sect.xoff, base_length * sect.yoff)

				spnt = strt + QPoint(math.cos(angle) * 6, -math.sin(angle) * 6)
				pnt = strt + QPoint(math.cos(angle) * length, -math.sin(angle) * length)
				self.painter.drawLine(spnt, pnt)
				if sect.sharn:
					paintool.zadelka_sharnir(self.painter, pnt, -angle, 30, 10, 5)
				else:
					self.painter.drawEllipse(paintool.radrect(pnt,5))

				ltxt = util.text_prepare_ltext(sect.l, suffix="l")
				Atxt = util.text_prepare_ltext(sect.A, suffix="A")
				txt = "{},{}".format(ltxt,Atxt)

				elements.draw_text_by_points_angled(self, strt, pnt, txt=txt, alttxt=sect.alttxt)

		# риуем силы
		for i in range(len(sects)):
			sect = self.sections()[i]
			angle = deg(sect.angle)
			rad = 50
			circrad = 6

			strt = center + QPointF(base_length * sect.xoff, base_length * sect.yoff)

			self.painter.setBrush(Qt.black)
			if sect.force != "нет":
				apnt = strt + QPointF(math.cos(angle) * circrad, - math.sin(angle) * circrad)
				bpnt = strt + QPointF(math.cos(angle) * rad, - math.sin(angle) * rad)
				cpnt = strt + QPointF(math.cos(angle) * rad/2, - math.sin(angle) * rad/2)

				if sect.force == "к":
					paintool.common_arrow(
						self.painter, 
						bpnt,
						apnt, 
						arrow_size=15)	
				elif sect.force == "от":
					paintool.common_arrow(
						self.painter, 
						apnt, 
						bpnt,
						arrow_size=15)	

				elements.draw_text_by_points(
					self, 
					cpnt, 
					bpnt, 
					paintool.greek(sect.ftxt), 
					alttxt=sect.alttxt, 
					off=12, 
					polka=None)

		self.painter.setPen(self.pen)
		self.painter.setBrush(Qt.white)
		self.painter.drawEllipse(QRect(center - QPoint(5, 5), center + QPoint(5, 5)))

