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
			label="",
			label_height = 20,
			dims = True
		):
			self.l = l
			self.label = label
			self.label_height = label_height
			self.dims = dims

	class betsect:
		def __init__(self, 
			l=0, 
			A=1,
			lbl="",
			F = "нет",
			Ftxt="",
			sterzn_text1="",
			sterzn_text2="",
			sterzn_text_horizontal=True,
			sterzn_text_alt=False,
			sterzn_text_off=0,
			F2 = "нет",
			F2txt="",
			zazor = False,
			zazor_txt = "\\Delta",
			sharn="нет"
		):
			self.l = l
			self.A = A
			self.lbl = lbl

			self.sterzn_text1 = sterzn_text1
			self.sterzn_text2 = sterzn_text2
			self.sterzn_text_horizontal=sterzn_text_horizontal
			self.sterzn_text_alt=sterzn_text_alt
			self.sterzn_text_off=sterzn_text_off

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
		self.table.addColumn("label", "str", "Подпись")
		self.table.addColumn("label_height", "float", "Расположение подписи")
		self.table.addColumn("dims", "bool", "Отрисовка разм.")
		self.table.updateTable()

		self.table3 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table3.addColumn("l", "float", "Длина опоры")
		self.table3.addColumn("A", "float", "Площадь(А)")
		self.table3.addColumn("sterzn_text1", "str", "Текст1")
		self.table3.addColumn("sterzn_text2", "str", "Текст2")
		self.table3.addColumn("sterzn_text_off", "float", "ТСмещ.")
		self.table3.addColumn("sterzn_text_horizontal", "bool", "Гориз./Верт.")
		self.table3.addColumn("sterzn_text_alt", "bool", "Слева./Справа.")
		self.table3.addColumn("sharn", "list", "Шарнир", variant=["нет", "1", "2"])
		self.table3.updateTable()
		
		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("lbl", "str", "Метка")
		self.table2.addColumn("F", "list", "Сила", variant=["нет", "+", "-"])
		self.table2.addColumn("Ftxt", "str", "Текст")
		self.table2.addColumn("F2", "list", "Ст.Сила", variant=["нет", "+", "-"])
		self.table2.addColumn("F2txt", "str", "Ст.Текст")
		self.table2.addColumn("zazor", "bool", "Зазор")
		self.table2.addColumn("zazor_txt", "str", "З.Текст")
		self.table2.updateTable()		
		

		self.vlayout.addWidget(QLabel("Геометрия секций:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Геометрия стержня, шарниры:"))
		self.vlayout.addWidget(self.table3)
		self.vlayout.addWidget(QLabel("Силы прилож. к стержню, зазоры, метки:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)
		self.table3.updated.connect(self.redraw)

		self.table2.hover_hint.connect(self.hover_node)
		self.table3.hover_hint.connect(self.hover_node)

		self.table2.unhover.connect(self.table_unhover)
		self.table3.unhover.connect(self.table_unhover)

		self.vlayout.addWidget(self.shemetype.texteditor)

	def hover_node(self, row, column, hint):
		self.shemetype.paintwidget.highlited_node = (hint, row)
		self.redraw()

		self.save_row = row
		self.save_hint = hint

	def table_unhover(self):
		self.shemetype.paintwidget.highlited_node = None
		self.redraw()
		

	"""Виджет настроек задачи T0"""
	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		self.sett.add_delimiter()
		self.shemetype.zadelka1 = self.sett.add("Шарнир слева:", "list", serlbl="Заделка:", defval=0, variant=["нет", "1", "2"])
		self.shemetype.zadelka2 = self.sett.add("Шарнир справа:", "list", defval=0, variant=["нет", "1", "2"])
		self.sett.add_delimiter()
		self.shemetype.base_height = self.sett.add("Базовая толщина:", "int", "22")
		self.shemetype.dimlines_level = self.sett.add("Уровень размерных линий:", "int", "80")
		self.shemetype.dimlines_level2 = self.sett.add("Отступ справа:", "int", "60")
		self.shemetype.sterzn_off = self.sett.add("Вынос стрелок для сил в стержнях:", "int", "28")
		self.shemetype.arrow_size = self.sett.add("Размер стрелок сил:", "int", "14")
		self.sett.updated.connect(self.redraw)

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
		self.highlited_node=None
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
		sterzn_off = self.shemetype.sterzn_off.get()

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
		down_span = 30 if hasnegative else 10 + dimlines_level
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
			if n==-1:
				n = len(sects)

			x = 0
			for i in range(n): x += sects[i].l * lkoeff
			return left_span + x


		# Размерные линии горизонтальные.
		for i in range(len(self.sections())):
			xl = xnode(i)
			xr = xnode(i+1)

			if sects[i].dims:

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

		self.painter.setPen(self.halfpen)
		for i in range(len(sects)):
			if sects[i].label != "":
				elements.draw_text_by_points(
					self,
					QPoint(xnode(i), hbase-sects[i].label_height), 
					QPoint(xnode(i+1), hbase-sects[i].label_height), 
					txt=paintool.greek(sects[i].label) + ("" if sects[i].label_height > -20 else "  "),
					alttxt=True,
					polka=QPointF((xnode(i+1) + xnode(i)) / 2, hbase+base_height/2)
				)

		self.painter.setPen(self.pen)


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
					if self.highlited_node and self.highlited_node[1] == i:
						self.painter.setPen(self.widegreen)

					self.painter.drawLine(strt, fini)
				
					self.painter.setPen(self.pen)
					if self.highlited_node and self.highlited_node[1] == i:
						self.painter.setPen(self.green)
					self.painter.drawEllipse(paintool.radrect(strt, 4))

				else:
					self.painter.setPen(self.doublepen)
				
					if self.highlited_node and self.highlited_node[1] == i:
						self.painter.setPen(self.widegreen)

					self.painter.drawLine(strt_z, fini)				
					self.painter.setPen(self.pen)					

					self.painter.setPen(self.halfpen)
		
					if self.highlited_node and self.highlited_node[1] == i:
						self.painter.setPen(self.green)

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
				txt_var1 = txt_var2

				if bsects[i].sterzn_text1:
					txt = bsects[i].sterzn_text1
					txt_var1 = txt

				if bsects[i].sterzn_text2:
					txt_var2 = bsects[i].sterzn_text2

				dimlines_level2=0


				center= QPointF(xnode(i)+dimlines_level2, hbase)
				alttxt = False

				if bsects[i].l < 0:
					ap = ap + base_height
	
				cp = (ap+bp)/2
				
				offset = QPointF(0, -bsects[i].sterzn_text_off)
				if bsects[i].sterzn_text_horizontal:
					offfff = 10
					if bsects[i].sterzn_text_alt:
						a = center + QPointF(0,(ap+bp)/2) + QPointF(-QFontMetrics(self.font).width(txt)-offfff, QFontMetrics(self.font).height()/2) + offset
						b = center + QPointF(0,(ap+bp)/2) + QPointF(0, QFontMetrics(self.font).height()/2) + offset
						a1 = center + QPointF(0,(ap+cp)/2) + QPointF(-QFontMetrics(self.font).width(txt_var1)-offfff, QFontMetrics(self.font).height()/2)
						b1 = center + QPointF(0,(ap+cp)/2) + QPointF(0, QFontMetrics(self.font).height()/2)
						a2 = center + QPointF(0,(cp+bp)/2) + QPointF(-QFontMetrics(self.font).width(txt_var2)-offfff, QFontMetrics(self.font).height()/2)
						b2 = center + QPointF(0,(cp+bp)/2) + QPointF(0, QFontMetrics(self.font).height()/2)

					else:
						a = center + QPointF(0,(ap+bp)/2) + QPointF(0, QFontMetrics(self.font).height()/2) + offset
						b = center + QPointF(0,(ap+bp)/2) + QPointF(QFontMetrics(self.font).width(txt)+offfff, QFontMetrics(self.font).height()/2) + offset
						a1 = center + QPointF(0,(ap+cp)/2) + QPointF(0, QFontMetrics(self.font).height()/2)
						b1 = center + QPointF(0,(ap+cp)/2) + QPointF(QFontMetrics(self.font).width(txt_var1)+offfff, QFontMetrics(self.font).height()/2)
						a2 = center + QPointF(0,(cp+bp)/2) + QPointF(0, QFontMetrics(self.font).height()/2)
						b2 = center + QPointF(0,(cp+bp)/2) + QPointF(QFontMetrics(self.font).width(txt_var2)+offfff, QFontMetrics(self.font).height()/2)

				else:
					a = center + QPointF(0,ap) + offset
					b = center + QPointF(0,bp) + offset
					a1 = center + QPointF(0,ap)
					b1 = center + QPointF(0,cp)
					a2 = center + QPointF(0,cp)
					b2 = center + QPointF(0,bp)
					alttxt = not bsects[i].sterzn_text_alt


				if bsects[i].F2 == "нет":							
					elements.draw_text_by_points_angled(
						self,
						a,
						b,
						txt=txt,
						alttxt=alttxt,
						off = 15
					)

				else:
					cp = (ap+bp)/2
					elements.draw_text_by_points_angled(
						self,
						a1, b1,
#						QPoint(xnode(i)+dimlines_level2, hbase + ap),
#						QPoint(xnode(i)+dimlines_level2, hbase + cp),
						txt=txt_var1,
						alttxt=alttxt,
						off = 15
					)
					elements.draw_text_by_points_angled(
						self,
						a2, b2,
#						QPoint(xnode(i)+dimlines_level2, hbase + cp),
#						QPoint(xnode(i)+dimlines_level2, hbase + bp),
						txt=txt_var2,
						alttxt=alttxt,
						off = 15
					)

				self.painter.setPen(self.halfpen)
				if bp == 0:
					cp = ap/2
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
					if bsects[i].lbl != "":
						elements.draw_text_by_points(
							self,
							QPoint(xnode(i), hbase+ap),
							QPoint(xnode(i), hbase+cp),
							txt=paintool.greek(bsects[i].lbl),
							alttxt=False,
							polka=QPointF(xnode(i), hbase+cp/2+5)

						)						

				self.painter.setPen(self.pen)
				self.painter.setBrush(Qt.white)

			if bsects[i].l == 0:
				if bsects[i].lbl != "":
					self.painter.setPen(self.halfpen)
					elements.draw_text_by_points(
						self,
						QPoint(xnode(i), hbase),
						QPoint(xnode(i), hbase-60),
						txt=paintool.greek(bsects[i].lbl),
						alttxt=False,
						polka=QPointF(xnode(i), hbase)
					)						
	
				if self.highlited_node and self.highlited_node[1] == i:
					self.painter.setPen(self.green)
					self.painter.drawEllipse(paintool.radrect(QPoint(xnode(i), hbase), 4))


		self.painter.setPen(self.pen)
		self.painter.setBrush(Qt.white)

		# Рисуем силы
		for i in range(len(bsects)):
			if bsects[i].F != "нет":
				if bsects[i].l > 0:
					type = "снизу к" if bsects[i].F == "+" else "снизу от"
					pnt = QPointF(xnode(i), hbase+base_height) 
					arrow_length = (dimlines_level-base_height)*2/3
				else:
					type = "сверху от" if bsects[i].F == "+" else "сверху к"
					pnt = QPointF(xnode(i), hbase)
					arrow_length = dimlines_level*2/3
					
				elements.draw_element_force(self, 
					pnt, type, 
					arrow_length, arrow_size, bsects[i].Ftxt, 
					True, pen=self.pen)

			if bsects[i].F2 != "нет":
				h = bsects[i].l * hkoeff
				arrow_size_2 = arrow_size
				arrow_size_3 = 28
				if bsects[i].l != 0:
					if bsects[i].F2 == "+":
						paintool.common_arrow(self.painter, 
							QPointF(xnode(i)+sterzn_off, hbase - h/2), 
							QPointF(xnode(i)+sterzn_off, hbase - h/2 - arrow_size_3), 
							arrow_size_2)
	
						paintool.common_arrow(self.painter, 
							QPointF(xnode(i)-sterzn_off, hbase - h/2), 
							QPointF(xnode(i)-sterzn_off, hbase - h/2 - arrow_size_3), 
							arrow_size_2)
	
						self.painter.setPen(self.halfpen)
						self.painter.drawLine(
							QPointF(xnode(i)-sterzn_off, hbase - h/2),
							QPointF(xnode(i)+sterzn_off, hbase - h/2)
						)
					else:
						paintool.common_arrow(self.painter, 
							QPointF(xnode(i)+sterzn_off, hbase - h/2), 
							QPointF(xnode(i)+sterzn_off, hbase - h/2 + arrow_size_3), 
							arrow_size_2)
		
						paintool.common_arrow(self.painter, 
							QPointF(xnode(i)-sterzn_off, hbase - h/2), 
							QPointF(xnode(i)-sterzn_off, hbase - h/2 + arrow_size_3), 
							arrow_size_2)
		
						self.painter.setPen(self.halfpen)
						self.painter.drawLine(
							QPointF(xnode(i)-sterzn_off, hbase - h/2),
							QPointF(xnode(i)+sterzn_off, hbase - h/2)
						)
					if bsects[i].F2txt != "":
						elements.draw_text_by_points(self, 
							QPointF(xnode(i)-sterzn_off, hbase - h/2 - dimlines_level/5), 
							QPointF(xnode(i)-sterzn_off, hbase - h/2 + dimlines_level/5), 
							txt = bsects[i].F2txt,
							alttxt = False,
							off = 10)
						
				

		# Рисуем заделку на левом крае
		self.painter.setPen(self.doublepen)
		if self.shemetype.zadelka1.get() == "2":
			#paintool.zadelka_sharnir_type2(self.painter, QPoint(xnode(0), hbase), deg(0), 30, 10, 5)
			elements.draw_element_sharn(self, 
				pnt=QPoint(xnode(0), hbase+base_height/2), 
				type="слева шарн2", 
				termrad=25,
				termx=25,
				termy=10,
				rad=4)

		elif self.shemetype.zadelka1.get() == "1":
			elements.draw_element_sharn(self, 
				pnt=QPoint(xnode(0), hbase+base_height/2), 
				type="слева врез1", 
				termrad=25,
				termx=25,
				termy=10,
				rad=4)

		if self.shemetype.zadelka2.get() == "2":
			#paintool.zadelka_sharnir_type2(self.painter, QPoint(xnode(0), hbase), deg(0), 30, 10, 5)
			elements.draw_element_sharn(self, 
				pnt=QPoint(xnode(-1), hbase+base_height/2), 
				type="справа шарн2", 
				termrad=25,
				termx=25,
				termy=10,
				rad=4)

		elif self.shemetype.zadelka2.get() == "1":
			elements.draw_element_sharn(self, 
				pnt=QPoint(xnode(-1), hbase+base_height/2), 
				type="справа врез1", 
				termrad=25,
				termx=25,
				termy=10,
				rad=4)
