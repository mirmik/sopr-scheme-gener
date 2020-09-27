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
		super().__init__("Стержневая система (Тип 2)")
		self.setwidgets(ConfWidget_T1(self), PaintWidget_T1(), common.TableWidget())

class ConfWidget_T1(common.ConfWidget):
	class sect:
		def __init__(self, xoff=0, yoff=0, l=1, A=1, angle=30, sharn="шарн+заделка", insharn="шарн", body=True, force="нет", ftxt="", alttxt=False, addangle=0):
			self.yoff = xoff
			self.xoff = yoff
			self.l = l
			self.A = A
			self.body = body
			self.sharn = sharn
			self.insharn = insharn
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

	def hover_sect(self, row, column, hint):
		self.shemetype.paintwidget.highlited_sect = (hint, row)
		self.redraw()

		self.save_row = row
		self.save_hint = hint

	def table_unhover(self):
		self.shemetype.paintwidget.highlited_sect = None
		self.shemetype.paintwidget.highlited_node = None
		self.redraw()

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("xoff", "float", "Смещ")
		self.table.addColumn("yoff", "float", "Смещ")
		self.table.addColumn("l", "float", "Длина")
		self.table.addColumn("angle", "float", "Угол")
		self.table.addColumn("body", "bool", "Стержень")
		self.table.addColumn("force", "list", "Сила", variant=["нет", "к", "от", "вдоль"])
		self.table.addColumn("ftxt", "str", "Сила")
		self.table.addColumn("alttxt", "bool", "Пол.Ткст.")
		self.table.addColumn("addangle", "float", "Доб.Угол")
		self.table.addColumn("sharn", "list", "Шарн.", variant=["нет", "шарн", "шарн+заделка"])
		#self.table.addColumn("insharn", "list", "ВхШарн.", variant=["нет", "шарн"])
		self.table.updateTable()

		self.table.hover_hint.connect(self.hover_sect)
		self.table.unhover.connect(self.table_unhover)

		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)
		self.vlayout.addWidget(self.shemetype.texteditor)
		
	"""Виджет настроек задачи T0"""
	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		#self.shemetype.first_dir = self.sett.add("Положение первого стержня (верт/гор):", "bool", True)
		self.shemetype.base_length = self.sett.add("Базовая длина:", "int", "80")
		self.sett.updated.connect(self.redraw)

		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter

		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		
		self.update_interface()
		self.setLayout(self.vlayout)

	def add_action_impl(self):
		self.shemetype.task["sections"].append(self.sect())
		self.redraw()
		self.updateTables()

	def insert_action_impl(self, idx):
		self.shemetype.task["sections"].insert(idx, self.sect())
		self.redraw()
		self.updateTables()

	def del_action_impl(self, idx):
		if len(self.shemetype.task["sections"]) == 1: return
		del self.shemetype.task["sections"][idx]
		self.redraw()
		self.updateTables()

	def inittask(self):
		#compat
		return {}

	def updateTables(self):
		self.table.updateTable()



class PaintWidget_T1(paintwdg.PaintWidget):
	def __init__(self):
		self.highlited_node=None
		self.highlited_sect=None
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
			length=0
			sect = self.sections()[i]
			if sects[i].body == True:
				length = sect.l

			elif sects[i].body == False and (sects[i].force == "к" or sects[i].force == "от"):
				length = 40 / base_length			

			elif sects[i].body == False and (sects[i].force == "нет" or sects[i].force == "вдоль"):
				continue

			angle = deg(sect.angle)

			point = (
				math.cos(angle) * (length)  + sect.xoff,
				-math.sin(angle) * (length) + sect.yoff,
			)

			xmin, xmax = min(xmin, point[0]) , max(xmax, point[0])
			ymin, ymax = min(ymin, point[1]) , max(ymax, point[1])

		center = QPoint(width/2, self.hcenter) + \
			QPoint(-(xmax + xmin)* base_length, -(ymax + ymin)* base_length)/2

		def get_coord(i):
			sect = self.sections()[i]
			angle=sect.angle
			length = sect.l * base_length			
			strt = center + QPointF(base_length * sect.xoff, base_length * sect.yoff)
			pnt = strt + QPoint(math.cos(angle) * length, -math.sin(angle) * length)
			return pnt

		def hasnode(pnt):
			jpnt = center
			diff = math.sqrt((pnt.x()-jpnt.x())**2 + (pnt.y()-jpnt.y())**2)
			if diff < 0.1:
				return True
			
			for i in range(len(self.sections())):
				if self.sections()[i].body==False or self.sections()[i].sharn=="нет":
					continue
				jpnt = get_coord(i)
				diff = math.sqrt((pnt.x()-jpnt.x())**2 + (pnt.y()-jpnt.y())**2)
				if diff < 0.1: 
					return True

			return False


		# Рисуем доб угол
		for i in range(len(sects)):
			sect = self.sections()[i]
			angle = sects[i].angle
			strt = center + QPointF(base_length * sect.xoff, base_length * sect.yoff)

			if sect.addangle != 0:
				rad = 50
				rad2 = 60
				rad3 = 70
				tgtangle = sect.angle + sect.addangle

				if self.highlited_sect is not None and self.highlited_sect[1] == i:
					pen = self.dashgreen
				else:
					pen = QPen(Qt.DashDotLine)
		
				pen.setWidth(2)
				self.painter.setPen(pen)

				pnt1 = strt + rad2 * QPointF(math.cos(deg(angle)), -math.sin(deg(angle)))
				pnt2 = strt + rad2 * QPointF(math.cos(deg(tgtangle)), -math.sin(deg(tgtangle)))
				cpnt = strt + rad3 * QPointF(math.cos(deg(tgtangle+angle)/2), -math.sin(deg(tgtangle+angle)/2))

				self.painter.drawLine(strt, pnt1)
				self.painter.drawLine(strt, pnt2)


				if self.highlited_sect is not None and self.highlited_sect[1] == i:
					pen = self.halfgreen
				else:
					pen = self.halfpen

				self.painter.setPen(pen)
				self.painter.drawArc(paintool.radrect(strt, rad), 
					angle*16, 
					sect.addangle*16)

				paintool.draw_text_centered(
					painter=self.painter, 
					pnt=cpnt + QPointF(0,QFontMetrics(self.font).height()/4), 
					text=paintool.greek(str(abs(sect.addangle))+"\\degree"), 
					font=self.font)


		# Рисуем тело
		for i in range(len(sects)):
			sect = self.sections()[i]
			angle = deg(sect.angle)
			self.painter.setPen(self.pen)

			if self.highlited_sect is not None and self.highlited_sect[1] == i:
				self.painter.setPen(self.widegreen)
			else:
				self.painter.setPen(self.doublepen)

			if sect.body:
				length = sect.l * base_length			
				strt = center + QPointF(base_length * sect.xoff, base_length * sect.yoff)

				if hasnode(strt):
					spnt = strt + QPoint(math.cos(angle) * 7, -math.sin(angle) * 7)
				else:
					spnt = strt
				pnt = strt + QPoint(math.cos(angle) * length, -math.sin(angle) * length)
				self.painter.drawLine(spnt, pnt)
				
				if self.highlited_sect is not None and self.highlited_sect[1] == i:
					self.painter.setPen(self.green)
				else:
					self.painter.setPen(self.pen)

				if sect.sharn=="шарн+заделка":
					paintool.zadelka_sharnir(self.painter, pnt, -angle, 30, 10, 5)
				elif sect.sharn=="шарн":
					self.painter.drawEllipse(paintool.radrect(pnt,5))

				ltxt = util.text_prepare_ltext(sect.l, suffix="l")
				Atxt = util.text_prepare_ltext(sect.A, suffix="A")
				txt = "{},{},E".format(ltxt,Atxt)

				elements.draw_text_by_points_angled(self, strt, pnt, off=14, txt=txt, alttxt=sect.alttxt)

			self.painter.setPen(self.default_pen)

		# риуем силы
		for i in range(len(sects)):
			sect = self.sections()[i]
			angle = deg(sect.angle)
			rad = 50
			circrad = 0		
		
			strt = center + QPointF(base_length * sect.xoff, base_length * sect.yoff)

			for j in range(len(sects)):
				jsect = self.sections()[j]
				#length = jsect.l * base_length		
				#pnt = strt + QPoint(math.cos(jsect.angle) * length, -math.sin(jsect.angle) * length)
				
				if hasnode(strt):
					circrad = 6
					break
				else:
					circrad = 0

			if self.highlited_sect is not None and self.highlited_sect[1] == i:
				self.painter.setPen(self.green)
				self.painter.setBrush(Qt.green)
				pen = self.green
				brush = Qt.green
			else:
				self.painter.setPen(self.pen)
				self.painter.setBrush(Qt.black)
				pen = None
				brush = Qt.black
			
			if sect.force != "нет":
				apnt = strt + QPointF(math.cos(angle) * circrad, - math.sin(angle) * circrad)
				bpnt = strt + QPointF(math.cos(angle) * rad, - math.sin(angle) * rad)
				cpnt = strt + QPointF(math.cos(angle) * rad/2, - math.sin(angle) * rad/2)

				if sect.force == "к":
					paintool.common_arrow(
						self.painter, 
						bpnt,
						apnt, 
						arrow_size=15,
						pen=pen, brush=brush)	
				elif sect.force == "от":
					paintool.common_arrow(
						self.painter, 
						apnt, 
						bpnt,
						arrow_size=15,
						pen=pen, brush=brush)	
				elif sect.force == "вдоль":
					rad = 20
					vec = QPointF(math.cos(angle) * rad, - math.sin(angle) * rad)
					norm = QPointF(vec.y(), -vec.x())

					apnt1 = strt + norm
					bpnt1 = strt - norm
					apnt2 = strt + norm + vec
					bpnt2 = strt - norm + vec
					cpnt1 = strt 
					cpnt2 = strt + vec
					
					paintool.common_arrow(
						self.painter, 
						apnt1, 
						apnt2,
						arrow_size=10)	
					paintool.common_arrow(
						self.painter, 
						bpnt1, 
						bpnt2,
						arrow_size=10,
						pen=pen, brush=brush)	

					self.painter.drawLine(apnt1, bpnt1)


				if sect.force != "вдоль":
					elements.draw_text_by_points(
						self, 
						cpnt, 
						bpnt, 
						paintool.greek(sect.ftxt), 
						alttxt=sect.alttxt, 
						off=12, 
						polka=None)

				else:
					elements.draw_text_by_points(
						self, 
						cpnt1, 
						cpnt2, 
						paintool.greek(sect.ftxt), 
						alttxt=sect.alttxt, 
						off=12 + 15, 
						polka=None)

		self.painter.setPen(self.pen)
		self.painter.setBrush(Qt.white)
		self.painter.drawEllipse(QRect(center - QPoint(5, 5), center + QPoint(5, 5)))

