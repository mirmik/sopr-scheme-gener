import common
import paintwdg
import math

import util
import tablewidget
import paintool
import taskconf_menu
import elements

from paintool import deg

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ShemeTypeT2(common.SchemeType):
	def __init__(self):
		super().__init__("Стержневая система (Тип 1)")
		self.setwidgets(ConfWidget_T2(self), PaintWidget_T2(), common.TableWidget())

class ConfWidget_T2(common.ConfWidget):
	class sect:
		def __init__(self, 
			l=1, 
		):
			self.l = l

	class betsect:
		def __init__(self, 
			l=0, 
			A=1,
			lbl="",
			F = "нет",
			Ftxt="",
			F2 = "нет",
			F2txt="",
			zazor = False,
			zazor_txt = "\\Delta",
			sharn="нет"
		):
			self.l = l
			self.A = A
			self.lbl = lbl
			self.F = F
			self.Ftxt = Ftxt
			self.F2 = F2
			self.F2txt = F2txt
			self.zazor = zazor
			self.zazor_txt = zazor_txt
			self.sharn = sharn 

	def create_task_structure(self):
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
				self.betsect(l=2, F="+"),
				self.betsect(l=-2)
			],
		}

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("l", "float", "Длина секции")
		self.table.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("l", "float", "Длина опоры")
		self.table2.addColumn("A", "float", "Площадь(А)")
		self.table2.addColumn("lbl", "str", "Метка")
		self.table2.addColumn("F", "list", "Сила", variant=["нет", "+", "-"])
		self.table2.addColumn("Ftxt", "str", "Текст")
		self.table2.addColumn("F2", "list", "Ст.Сила", variant=["нет", "+", "-"])
		self.table2.addColumn("F2txt", "str", "Ст.Текст")
		self.table2.addColumn("zazor", "bool", "Зазор")
		self.table2.addColumn("zazor_txt", "str", "Текст")
		self.table2.addColumn("sharn", "list", variant=["нет", "1", "2"])
		self.table2.updateTable()
		
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)

		self.vlayout.addWidget(self.shemetype.texteditor)
		

	"""Виджет настроек задачи T0"""
	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.zadelka = self.sett.add("Заделка:", "list", defval=0, variant=["нет", "1", "2"])
		self.shemetype.base_height = self.sett.add("Базовая толщина:", "int", "22")
		self.shemetype.dimlines_level = self.sett.add("Уровень размерных линий:", "int", "70")
		self.shemetype.dimlines_level2 = self.sett.add("Уровень размерных линий2:", "int", "60")
		self.shemetype.arrow_size = self.sett.add("Размер стрелок:", "int", "10")
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
		self.redraw()
		self.updateTables()

	def insert_action_impl(self, idx):
		self.shemetype.task["sections"].insert(idx, self.sect())
		self.shemetype.task["betsect"].insert(idx, self.betsect())
		self.redraw()
		self.updateTables()

	def del_action_impl(self, idx):
		if len(self.shemetype.task["sections"]) == 1: return
		del self.shemetype.task["sections"][idx]
		del self.shemetype.task["betsect"][idx]
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

		center = QPoint(width/2, self.hcenter)

		font_size = self.shemetype.font_size.get()
		lwidth = self.shemetype.line_width.get()

		base_height = self.shemetype.base_height.get()
		arrow_size = self.shemetype.arrow_size.get()
		dimlines_level = self.shemetype.dimlines_level.get()
		dimlines_level2 = self.shemetype.dimlines_level2.get()

		font = self.painter.font()
		font.setItalic(True)
		font.setPointSize(font_size)
		self.painter.setFont(font)

		br = QPen()
		br.setWidth(lwidth)
		self.painter.setPen(br)

		br = QBrush(Qt.SolidPattern)
		br.setColor(Qt.white)
		self.painter.setBrush(br)

		hasnegative = False
		for b in bsects:
			if b.l < 0:
				hasnegative = True

		hasright = bsects[-1].l != 0  

		left_span = 60
		right_span = 30 if not hasright else 10 + dimlines_level2
		up_span = 30
		down_span = 20 if hasnegative else 10 + dimlines_level
		down_span += self.text_height

		smax = 0
		smin = 0
		for b in bsects:
			if b.l > smax: smax = b.l
			if b.l < smin: smin = b.l

		fheight = height - up_span - down_span
		#hsum = 0
		#for s in bsects: hsum += s.l 

		if smax != smin:
			hkoeff = float(fheight) / (smax - smin)
		else:
			hkoeff = float(fheight)
		hbase = hkoeff * smax + up_span

		lu = QPoint(left_span, hbase)
		ru = QPoint(width - right_span, hbase)
		ld = QPoint(left_span, hbase+base_height)
		rd = QPoint(width - right_span, hbase+base_height)

		fsize = width - right_span - left_span
		lsum = 0
		for s in sects: lsum += s.l 
		lkoeff = float(fsize) / lsum


		def xnode(n):
			x = 0
			for i in range(n): x += sects[i].l * lkoeff
			return left_span + x


		# Размерные линии горизонтальные.
		for i in range(len(self.sections())):
			xl = xnode(i)
			xr = xnode(i+1)

			paintool.dimlines(self.painter, 
				QPoint(xl, hbase), 
				QPoint(xr, hbase), 
				hbase+dimlines_level)

			elements.draw_text_by_points(
						self,
						QPoint(xl, hbase+dimlines_level), 
						QPoint(xr, hbase+dimlines_level), 
						txt=util.text_prepare_ltext(self.sections()[i].l, "a"),
						alttxt=True,
						off = 8
					)

		self.painter.setBrush(Qt.white)




		self.painter.drawLine(lu, ru)
		self.painter.drawLine(lu, ld)
		self.painter.drawLine(ld, rd)
		self.painter.drawLine(rd, ru)

		#Рисуем стержни
		for i in range(len(bsects)):
			#Доп. Шарниры
			if bsects[i].sharn != "нет":
				if bsects[i].sharn == "1":
					sharn_type = "снизу врез1"
				elif bsects[i].sharn == "2":
					sharn_type = "снизу шарн2"
				elements.draw_element_sharn(self,
					pnt=QPoint(xnode(i), hbase+base_height),
					type=sharn_type,
					termrad=25,
					termx=25,
					termy=10,
					rad=4
				)

			# Рисуем стержень
			if bsects[i].l != 0:
				if bsects[i].l > 0:
					strt = QPointF(xnode(i), hbase)
					strt_z = QPointF(xnode(i), hbase - 20)
					fini = QPointF(xnode(i), hbase - bsects[i].l*hkoeff)
				else:
					strt = QPoint(xnode(i), hbase + base_height)
					strt_z = QPointF(xnode(i), hbase + base_height + 20)
					fini = QPointF(xnode(i), hbase - bsects[i].l*hkoeff)
				
				if bsects[i].zazor is False:
					self.painter.setPen(self.doublepen)
					self.painter.drawLine(strt, fini)
				
					self.painter.setPen(self.pen)
					self.painter.drawEllipse(paintool.radrect(strt, 4))

				else:
					self.painter.setPen(self.doublepen)
					self.painter.drawLine(strt_z, fini)				
					self.painter.setPen(self.pen)					

					self.painter.setPen(self.halfpen)
					paintool.draw_dimlines(
						painter=self.painter, 
						apnt=strt, 
						bpnt=strt_z, 
						offset=QPoint(-20,0), 
						textoff=QPoint(-10-QFontMetrics(self.font).width(paintool.greek(bsects[i].zazor_txt))/2,0), 
						text=paintool.greek(bsects[i].zazor_txt), 
						arrow_size=10, 
						splashed=True, 
						textline_from=None)
					self.painter.setPen(self.pen)


				if (bsects[i].l < 0):
					angle = deg(90)
				else:
					angle = deg(-90)
				
				upnt = bsects[i].l*hkoeff
				paintool.zadelka_sharnir(self.painter, QPoint(xnode(i), hbase - upnt), angle, 30, 10, 5)

				ap = -upnt if bsects[i].l < 0 else 0
				bp = 0 if bsects[i].l < 0 else -upnt

				txt = util.text_prepare_ltext(abs(bsects[i].l))
				txt_var2 = util.text_prepare_ltext(abs(bsects[i].l/2))
				txt2 = util.text_prepare_ltext(abs(bsects[i].A), "A")
				txt2 = txt2 + ",E"

				txt = txt+","+txt2
				txt_var2 = txt_var2+","+txt2

				dimlines_level2=0
				if bsects[i].F2 == "нет":
				#	paintool.dimlines_vertical(self.painter,
				#		QPoint(xnode(i), hbase + ap),
				#		QPoint(xnode(i), hbase + bp),
				#		xnode(i) + dimlines_level2)
				
					if bsects[i].l > 0:
						elements.draw_text_by_points_angled(
							self,
							QPoint(xnode(i)+dimlines_level2, hbase + ap),
							QPoint(xnode(i)+dimlines_level2, hbase + bp),
							txt=txt,
							alttxt=False
						)
					else:
						elements.draw_text_by_points_angled(
							self,
							QPoint(xnode(i)+dimlines_level2, hbase + ap),
							QPoint(xnode(i)+dimlines_level2, hbase + (ap+bp)/2),
							txt=txt,
							alttxt=False
						)
						

				else:
					cp = (ap+bp)/2
					#paintool.dimlines_vertical(self.painter,
					#	QPoint(xnode(i), hbase + ap),
					#	QPoint(xnode(i), hbase + cp),
					#	xnode(i) + dimlines_level2)
					#paintool.dimlines_vertical(self.painter,
					#	QPoint(xnode(i), hbase + cp),
					#	QPoint(xnode(i), hbase + bp),
					#	xnode(i) + dimlines_level2)
					elements.draw_text_by_points_angled(
						self,
						QPoint(xnode(i)+dimlines_level2, hbase + ap),
						QPoint(xnode(i)+dimlines_level2, hbase + cp),
						txt=txt_var2,
						alttxt=False
					)
					elements.draw_text_by_points_angled(
						self,
						QPoint(xnode(i)+dimlines_level2, hbase + cp),
						QPoint(xnode(i)+dimlines_level2, hbase + bp),
						txt=txt_var2,
						alttxt=False
					)
					
				if bp == 0:
					cp = ap/2
				#	elements.draw_text_by_points(
				#		self,
				#		QPoint(xnode(i), hbase+cp),
				#		QPoint(xnode(i), hbase+ap),
				#		txt=txt2,
				#		alttxt=False
				#	)

					# рисуем метку
					if bsects[i].lbl != "":
						elements.draw_text_by_points(
							self,
							QPoint(xnode(i), hbase+cp),
							QPoint(xnode(i), hbase+bp),
							txt=paintool.greek(bsects[i].lbl),
							alttxt=False,
							polka=QPointF(xnode(i), hbase+cp/2+5)

						)					


				if ap == 0:
					cp = bp/2
				#	elements.draw_text_by_points(
				#		self,
				#		QPoint(xnode(i), hbase+bp),
				#		QPoint(xnode(i), hbase+cp),
				#		txt=txt2,
				#		alttxt=False
				#	)

					if bsects[i].lbl != "":
						elements.draw_text_by_points(
							self,
							QPoint(xnode(i), hbase+ap),
							QPoint(xnode(i), hbase+cp),
							txt=paintool.greek(bsects[i].lbl),
							alttxt=True,
							polka=QPointF(xnode(i), hbase+cp/2+5)

						)						

				self.painter.setPen(self.pen)
				self.painter.setBrush(Qt.white)

		# Рисуем силы
		for i in range(len(bsects)):
			if bsects[i].F != "нет":
				if bsects[i].l > 0:
					type = "снизу к" if bsects[i].F == "+" else "снизу от"
					pnt = QPointF(xnode(i), hbase+base_height) 
				else:
					type = "сверху от" if bsects[i].F == "+" else "сверху к"
					pnt = QPointF(xnode(i), hbase)
					
				elements.draw_element_force(self, 
					pnt, type, 
					dimlines_level*2/3, arrow_size, bsects[i].Ftxt, 
					True, pen=self.pen)


			if bsects[i].F2 != "нет":
				h = bsects[i].l * hkoeff
				if bsects[i].l != 0:
					if bsects[i].F2 == "+":
						paintool.common_arrow(self.painter, 
							QPointF(xnode(i)+15, hbase - h/2), 
							QPointF(xnode(i)+15, hbase - h/2 - dimlines_level/2.5), 
							arrow_size)
	
						paintool.common_arrow(self.painter, 
							QPointF(xnode(i)-15, hbase - h/2), 
							QPointF(xnode(i)-15, hbase - h/2 - dimlines_level/2.5), 
							arrow_size)
	
						self.painter.setPen(self.halfpen)
						self.painter.drawLine(
							QPointF(xnode(i)-15, hbase - h/2),
							QPointF(xnode(i)+15, hbase - h/2)
						)
					else:
						paintool.common_arrow(self.painter, 
							QPointF(xnode(i)+15, hbase - h/2), 
							QPointF(xnode(i)+15, hbase - h/2 + dimlines_level/2.5), 
							arrow_size)
		
						paintool.common_arrow(self.painter, 
							QPointF(xnode(i)-15, hbase - h/2), 
							QPointF(xnode(i)-15, hbase - h/2 + dimlines_level/2.5), 
							arrow_size)
		
						self.painter.setPen(self.halfpen)
						self.painter.drawLine(
							QPointF(xnode(i)-15, hbase - h/2),
							QPointF(xnode(i)+15, hbase - h/2)
						)
					if bsects[i].F2txt != "":
						elements.draw_text_by_points(self, 
							QPointF(xnode(i)-15, hbase - h/2 - dimlines_level/5), 
							QPointF(xnode(i)-15, hbase - h/2 + dimlines_level/5), 
							txt = bsects[i].F2txt,
							alttxt = False,
							off = 10)
						
				

		# Рисуем заделку на левом крае
		self.painter.setPen(self.doublepen)
		if self.shemetype.zadelka.get() == "2":
			#paintool.zadelka_sharnir_type2(self.painter, QPoint(xnode(0), hbase), deg(0), 30, 10, 5)
			elements.draw_element_sharn(self, 
				pnt=QPoint(xnode(0), hbase+base_height/2), 
				type="слева шарн2", 
				termrad=25,
				termx=25,
				termy=10,
				rad=4)

		elif self.shemetype.zadelka.get() == "1":
			elements.draw_element_sharn(self, 
				pnt=QPoint(xnode(0), hbase+base_height/2), 
				type="слева врез1", 
				termrad=25,
				termx=25,
				termy=10,
				rad=4)
