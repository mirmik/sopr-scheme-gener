import common
import paintwdg
import math

import paintool
import taskconf_menu
import tablewidget
import util
import elements

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

SUBTYPE_RASTYAZHENIE_SJATIE = 0
SUBTYPE_KRUCHENIE_1 = 1
SUBTYPE_KRUCHENIE_2 = 2

class ShemeTypeT0(common.SchemeType):
	def __init__(self):
		super().__init__("Растяжение/сжатие/кручение стержня")
		self.setwidgets(ConfWidget_T0(self), PaintWidget_T0(), common.TableWidget())


class ConfWidget_T0(common.ConfWidget):
	"""Виджет настроек задачи T0"""
	class sect:
		def __init__(self, A=1, GIk=1, d=1, l=1, E=1, text="", dtext="", delta=False):
			self.A=A
			self.GIk=GIk
			self.d=d
			self.l=l
			self.E=E
			self.text = text
			self.dtext = dtext
			self.delta = delta

	class sectforce:
		def __init__(self, mkr="нет", mkrT="", Fr="нет"):
			self.mkr = mkr
			self.mkrT = mkrT
			self.Fr = Fr

	class betsect:
		def __init__(self, F="нет", Fstyle="от узла", Mkr="нет", T="", label="", label_up=False):
			self.F = F 
			self.Fstyle = Fstyle
			self.Mkr = Mkr 
			self.T = T
			self.label = label
			self.label_up = label_up

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(A=1, l=1, E=1),
				self.sect(A=2, l=1, E=1),
				self.sect(A=1, l=2, E=1),
			],
			"betsect":
			[
				self.betsect(),
				self.betsect(),
				self.betsect(),
				self.betsect()
			],
			"sectforce":
			[
				self.sectforce(),
				self.sectforce(),
				self.sectforce()
			]
		}
	
	def update_interface(self):
		SUBTYPE = self.shemetype.task_subtype.get()

		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")

		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		
		if SUBTYPE == SUBTYPE_RASTYAZHENIE_SJATIE:
			self.table.addColumn("A", "float", "Площадь")

		if SUBTYPE == SUBTYPE_KRUCHENIE_1:
			self.table.addColumn("GIk", "float", "КрутЖестк")
		
		if SUBTYPE == SUBTYPE_KRUCHENIE_2:
			self.table.addColumn("d", "float", "Диаметр")
			self.table.addColumn("dtext", "str", "Д.Текст")

		self.table.addColumn("l", "float", "Длина")
		
		if SUBTYPE == SUBTYPE_RASTYAZHENIE_SJATIE:
			self.table.addColumn("E", "float", "МодульЮнга")
		
		self.table.addColumn("text", "str", "Текст")
	
		if SUBTYPE == SUBTYPE_RASTYAZHENIE_SJATIE:
			self.table.addColumn("delta", "bool", "Зазор")
	
		self.table.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		if SUBTYPE == SUBTYPE_RASTYAZHENIE_SJATIE:
			self.table1.addColumn("Fr", "list", variant=["нет", "+", "-"])
	
		if SUBTYPE == SUBTYPE_KRUCHENIE_1 or \
		   SUBTYPE == SUBTYPE_KRUCHENIE_2:
			self.table1.addColumn("mkr", "list", variant=["нет", "+", "-"])
	
		self.table1.addColumn("mkrT", "str", "Текст")
		self.table1.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")

		if SUBTYPE == SUBTYPE_RASTYAZHENIE_SJATIE:
			self.table2.addColumn("F", "list", variant=["нет", "+", "-"])
			self.table2.addColumn("Fstyle", "list", "Рис.", variant=["от узла", "к узлу", "выносн."])
	
		if SUBTYPE == SUBTYPE_KRUCHENIE_1 or \
		   SUBTYPE == SUBTYPE_KRUCHENIE_2:
			self.table2.addColumn("Mkr", "list", variant=["нет", "+", "-"])

		self.table2.addColumn("T", "str", "Текст")
		self.table2.addColumn("label", "str", "Метка")
		self.table2.addColumn("label_up", "bool", "МеткаПолож.")
		self.table2.updateTable()

		self.table.updated.connect(self.redraw)
		self.table1.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)

		self.table.hover_hint.connect(self.hover_sect)
		self.table1.hover_hint.connect(self.hover_sect)
		self.table2.hover_hint.connect(self.hover_node)

		self.table.unhover.connect(self.table_unhover)
		self.table1.unhover.connect(self.table_unhover)
		self.table2.unhover.connect(self.table_unhover)

		self.vlayout.addWidget(self.presett)
		self.add_buttons_to_layout(self.vlayout)
		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Распределенные силы:"))
		self.vlayout.addWidget(self.table1)
		self.vlayout.addWidget(QLabel("Локальные силы, метки узлов:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)
		self.vlayout.addWidget(self.shemetype.texteditor)

	def hover_node(self, row, column, hint):
		self.shemetype.paintwidget.highlited_node = (hint, row)
		self.redraw()

		self.save_row = row
		self.save_hint = hint

	def hover_sect(self, row, column, hint):
		self.shemetype.paintwidget.highlited_sect = (hint, row)
		self.redraw()

		self.save_row = row
		self.save_hint = hint

	def table_unhover(self):
		self.shemetype.paintwidget.highlited_sect = None
		self.shemetype.paintwidget.highlited_node = None
		self.redraw()

	def __init__(self, sheme):
		super().__init__(sheme, noinitbuttons=True)

		self.presett = taskconf_menu.TaskConfMenu()
		self.shemetype.task_subtype = self.presett.add("Подтип задачи:", "list", 
				variant=["Растяжение/сжатие", "Кручение (крутильная жесткость)", "Кручение (диаметры)"],
				vars=[SUBTYPE_RASTYAZHENIE_SJATIE, SUBTYPE_KRUCHENIE_1, SUBTYPE_KRUCHENIE_2],
				defval=0,
				handler=self.clean_and_update_interface)
		
		self.sett = taskconf_menu.TaskConfMenu()
		#self.shemetype.kruch_flag = self.sett.add("Сечение/Крутильная жесткость:", "bool", True)
		self.shemetype.axis = self.sett.add("Нарисовать ось:", "bool", True)
		self.shemetype.zleft = self.sett.add("Заделка слева:", "bool", False)
		self.shemetype.zright = self.sett.add("Заделка справа:", "bool", False)
		self.shemetype.razm = self.sett.add("Размерные линии:", "bool", True)

		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.base_section_height = self.sett.add("Базовая высота секции:", "int", "40")
		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "20")
		self.shemetype.dimlines_start_step = self.sett.add("Отступ размерных линий:", "int", "40")
		self.shemetype.left_zone = self.sett.add("Отступ слева:", "int", "30")
		self.shemetype.right_zone = self.sett.add("Отступ справа:", "int", "30")
		
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.sett.updated.connect(self.redraw)

		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)

		self.update_interface()
		self.setLayout(self.vlayout)

	def serialize_list(self):
		return [
			("presett", self.presett),
			("task", self.shemetype.task),
			("sett", self.sett),
			("texteditor", self.shemetype.texteditor)			
		]

	def add_action_impl(self):
		self.sections().append(self.sect())
		self.sectforces().append(self.sectforce())
		self.bsections().append(self.betsect())
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def insert_action_impl(self, idx):
		self.sections().insert(idx, self.sect())
		self.sectforces().insert(idx, self.sectforce())
		self.bsections().insert(idx, self.betsect())
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def del_action_impl(self, idx):
		if len(self.sections()) == 1:
			return

		del self.sections()[idx]
		del self.sectforces()[idx]
		del self.bsections()[idx]
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def inittask(self):
		return {}

class PaintWidget_T0(paintwdg.PaintWidget):

	def __init__(self):
		self.highlited_node=None
		self.highlited_sect=None
		super().__init__()

	def next_raspred(self, i):
		if i == len(self.sections()):
			return False
		return self.task["sectforce"][i].Fr != "нет"

	def prev_raspred(self, i):
		if i == 0:
			return False
		return self.task["sectforce"][i-1].Fr != "нет"

	def wsect(self, i):
		l = len(self.task["sections"])
		k0 = self.summary_length - self.ll[i]
		k1 = self.ll[i]
		return (self.fini_width * k1 + self.strt_width * k0) // self.summary_length

	def sectrad_koeff(self, i):
		if self.subtype == SUBTYPE_RASTYAZHENIE_SJATIE:
			return math.sqrt(self.shemetype.task["sections"][i].A)
		   
		if self.subtype == SUBTYPE_KRUCHENIE_1:
			return math.sqrt(self.shemetype.task["sections"][i].GIk)

		if self.subtype == SUBTYPE_KRUCHENIE_2:
			return self.shemetype.task["sections"][i].d

	def sectrad(self, i):
		return self.sectrad_koeff(i) * self.height_zone / 2

	def msectrad(self, i):
		leftA = 0 if i == 0 else self.sectrad(i-1)
		rightA = 0 if i == -1 + len(self.shemetype.task["betsect"]) else self.sectrad(i)
		return max(leftA, rightA)

	def msectrad2(self, i):
		leftA = 0 if i == 0 else self.sectrad(i-1)
		rightA = 0 if i == -1 + len(self.shemetype.task["betsect"]) else self.sectrad(i)
		rm = False
		lm = self.shemetype.task["sectforce"][i-1].mkr != "нет"
		
		if i != len(self.task["sectforce"]):
			rm = self.task["sectforce"][i].mkr != "нет"
		
		ret = max(leftA, rightA)

		if ((max(leftA, rightA) == leftA and lm)
			or
			(max(leftA, rightA) == rightA and rm)):
			ret += 20

		return ret


	def force_drawing(self):
		font = self.font
		task = self.shemetype.task
		hcenter = self.hcenter
		height_zone = self.height_zone
		arrow_size = self.arrow_size
		arrow_head_size = self.arrow_head_size
		arrow_line_size = self.arrow_line_size

		for i in range(len(task["betsect"])):
			self.painter.setPen(self.default_pen)
			arrow_head_size = 15

			F_text_policy = "simple"
			F_level = 0

			if task["betsect"][i].F != "нет":
				#Отрисовываем сосредоточенные силы.

				if task["betsect"][i].F == "+":
					if task["betsect"][i].Fstyle == "выносн.": #not self.next_raspred(i):
						paintool.right_arrow_double(self.painter, 
							QPoint(self.wsect(i), hcenter), 
							arrow_line_size, 
							arrow_head_size,
							h = self.msectrad(i) * 3.2)
						F_text_policy = "up"
						F_level = - self.msectrad(i) * 3.2/2 + hcenter
					elif task["betsect"][i].Fstyle == "от узла": #not self.next_raspred(i):
						paintool.right_arrow(self.painter, QPoint(self.wsect(i), hcenter), arrow_line_size, arrow_head_size)
					else:
						paintool.right_arrow(self.painter, QPoint(self.wsect(i) - arrow_line_size, hcenter), arrow_line_size, arrow_head_size)
					
				if task["betsect"][i].F == "-":
					if task["betsect"][i].Fstyle == "выносн.":
						paintool.left_arrow_double(self.painter, 
							QPoint(self.wsect(i), hcenter), 
							arrow_line_size, 
							arrow_head_size,
							h = self.msectrad(i) * 3.2)
						F_text_policy = "up"
						F_level = - self.msectrad(i) * 3.2/2 + hcenter					
					elif task["betsect"][i].Fstyle == "от узла":
						paintool.left_arrow(self.painter, QPoint(self.wsect(i), hcenter), arrow_line_size, arrow_head_size)
					else:
						paintool.left_arrow(self.painter, QPoint(self.wsect(i) + arrow_line_size, hcenter), arrow_line_size, arrow_head_size)

			self.painter.setPen(self.pen)
			if task["betsect"][i].F != "нет":
				if task["betsect"][i].T != "":
					leftA = 0 if i == 0 else math.sqrt(task["sections"][i-1].A)
					rightA = 0 if i == -1 + len(task["betsect"]) else math.sqrt(task["sections"][i].A)
					
					size = QFontMetrics(font).width(task["betsect"][i].T)
					text = task["betsect"][i].T
	
					desp = +arrow_line_size/2 if task["betsect"][i].F == "+" else -arrow_line_size/2
					if task["betsect"][i].Fstyle == "к узлу":
						desp = - desp
					
					if F_text_policy == "simple":
						paintool.placedtext(self.painter,
							QPoint(self.wsect(i)+desp, hcenter), 
							max(leftA, rightA) * height_zone / 2 + 10, 
							size, 
							text,
							right = False)
	
					if F_text_policy == "up":
						paintool.draw_text_centered(self.painter,
							QPoint(
								self.wsect(i)+desp, 
								F_level - 6), 
							text, font)

		# Отрисовка распределённых нагрузок:
		for i in range(len(task["sectforce"])):
			hkoeff = math.sqrt(task["sections"][i].A)

			strt_height = hcenter - height_zone*hkoeff/2
			fini_height = hcenter + height_zone*hkoeff/2

			step = 18
			alen = 15
			rad = 10

			xa = self.wsect(i)
			xb = self.wsect(i+1)
			fxa = self.wsect(i)
			fxb = self.wsect(i+1)

			if i == 0 and self.zleft:
				xa = xa + step*2/3

			if i == len(self.sections())-1 and self.zright:
				xb = xb - step*2/3

			#отрисовка распределённой силы.
			if task["sectforce"][i].Fr != "нет":
				if task["sectforce"][i].Fr == "+":
					tp = True
				else:
					tp = False
				
				step = 20

				self.painter.setPen(Qt.NoPen)
				self.painter.setBrush(Qt.white)
				
				self.painter.drawRect(QRectF(
					QPointF(fxa+2, hcenter-5),
					QPointF(fxb-2, hcenter+5)
				))

				self.painter.setPen(self.pen)
				paintool.raspred_force(painter=self.painter,
					apnt=QPointF(fxa, hcenter),
					bpnt=QPointF(fxb, hcenter),
					step=step,
					tp = tp)

				self.painter.setPen(self.pen)
				if task["sectforce"][i].mkrT:
					leftA = 0 if i == 0 else math.sqrt(task["sections"][i-1].A)
					rightA = 0 if i == -1 + len(task["betsect"]) else math.sqrt(task["sections"][i].A)
	
					size = QFontMetrics(font).width(task["sectforce"][i].mkrT)
					paintool.placedtext(self.painter,
						QPoint((fxa + fxb)/2, hcenter), 
						self.sectrad(i) + 10, 
						size, 
						task["sectforce"][i].mkrT,
						right = True)

	def torsion_drawing(self):
		font = self.font
		task = self.shemetype.task
		hcenter = self.hcenter
		height_zone = self.height_zone
		arrow_size = self.arrow_size
		arrow_head_size = self.arrow_head_size
		arrow_line_size = self.arrow_line_size

		#Отрисовка граничных эффектов
		for i in range(len(task["betsect"])):
			self.painter.setPen(self.default_pen)
			arrow_head_size = 15

			if task["betsect"][i].Mkr == "+":
				paintool.kr_arrow(self.painter, QPointF(self.wsect(i), hcenter), self.msectrad2(i)+10, 11, False)

			if task["betsect"][i].Mkr == "-":
				paintool.kr_arrow(self.painter, QPointF(self.wsect(i), hcenter), self.msectrad2(i)+10, 11, True)

			if task["betsect"][i].Mkr != "нет":
				if task["betsect"][i].T != "":
					self.painter.drawText(QPointF(
						self.wsect(i) + 14, 
						hcenter - self.msectrad2(i)-14), task["betsect"][i].T)

		# Отрисовка распределённых нагрузок:
		for i in range(len(task["sectforce"])):
			hkoeff = math.sqrt(task["sections"][i].A)

			strt_height = hcenter - self.sectrad(i)
			fini_height = hcenter + self.sectrad(i)

			step = 18
			alen = 15
			rad = 10

			xa = self.wsect(i)
			xb = self.wsect(i+1)
			fxa = self.wsect(i)
			fxb = self.wsect(i+1)

			if i == 0 and self.zleft:
				xa = xa + step*2/3

			if i == len(self.sections())-1 and self.zright:
				xb = xb - step*2/3

			if task["sectforce"][i].mkr != "нет":
				if task["sectforce"][i].mkr == "+":
					tp = True
				else:
					tp = False
	
				paintool.raspred_torsion(painter=self.painter,
					apnt=QPointF(xa, strt_height),
					bpnt=QPointF(xb, strt_height),
					alen=-alen,
					rad=rad,
					step=step,
					tp = tp)
	
				paintool.raspred_torsion(painter=self.painter,
					apnt=QPointF(xa, fini_height),
					bpnt=QPointF(xb, fini_height),
					alen=alen,
					step=step,
					rad=rad,
					tp = not tp)
	
				if task["sectforce"][i].mkrT:
					self.painter.drawText(QPointF((xa+xb)/2, strt_height - 3 - alen - rad), 
						task["sectforce"][i].mkrT)

	def is_delta(self, i):
		if self.subtype != SUBTYPE_RASTYAZHENIE_SJATIE or not self.task["sections"][i].delta:
			return False
		else:
			return True

	def draw_section(self, i, strt_height, fini_height):
		if self.highlited_sect is not None and \
				 self.highlited_sect[1] == i:
			self.painter.setPen(self.widegreen)

		if not self.is_delta(i):
			self.painter.drawRect(
				self.wsect(i), 
				strt_height, 
				self.wsect(i+1)-self.wsect(i), 
				fini_height-strt_height)

	def draw_dimlines(self, i, strt_height, fini_height):		
		task = self.task

		A = task["sections"][i].A
		l = task["sections"][i].l
		E = task["sections"][i].E

		if self.subtype == SUBTYPE_RASTYAZHENIE_SJATIE:
			sechtext = "A"
		else:
			sechtext = "GIk"

		text_E = common.pretty_str(E, "E")
		if not self.is_delta(i):
			if abs(float(A) - int(A)) < 0.0001:
				text_A = "{}{}".format(int(task["sections"][i].A+0.1), sechtext) if task["sections"][i].A != 1 else sechtext
			else:
				text_A = str(float(A)) + sechtext
	
			if abs(float(l) - int(l)) < 0.0001:
				text_l = "{}l".format(int(task["sections"][i].l+0.1)) if task["sections"][i].l != 1 else "l"
			else:
				text_l = str(float(l)) + "l"
		else: 
			text_l = ""
			text_A = ""
		
		text_l = paintool.greek(text_l)
		text_A = paintool.greek(text_A)
		text_E = paintool.greek(text_E)

		self.painter.setPen(Qt.black)

		lW = QFontMetrics(self.font).width(text_l)
		AW = QFontMetrics(self.font).width(text_A)

		if task["sections"][i].text != "" or self.is_delta(i):
			text = paintool.greek(task["sections"][i].text)

		else:
			if self.subtype == SUBTYPE_KRUCHENIE_1:
				text = "{}, {}".format(text_l, text_A)
			
			elif self.subtype == SUBTYPE_RASTYAZHENIE_SJATIE:
				text = "{}, {}, {}".format(text_l, text_A, text_E)
				
			elif self.subtype == SUBTYPE_KRUCHENIE_2:
				text = "{}".format(text_l)
				
		if self.razm:
			self.painter.setPen(self.halfpen)
			splashed = self.wsect(i+1) - self.wsect(i) < 20

			paintool.draw_dimlines(
				self.painter, 
				QPoint(self.wsect(i), fini_height), 
				QPoint(self.wsect(i+1), fini_height), 
				offset=QPoint(0, self.dimlines_level- fini_height), 
				textoff=QPoint(0, -3 -QFontMetrics(self.font).height()/2),
				arrow_size=10,
				text=text,
				splashed=splashed)

	def draw_diameters(self, i, strt_height, fini_height):
		self.painter.setPen(self.default_pen)
		self.painter.setBrush(self.default_brush)

		d = self.task["sections"][i].d
		text = common.pretty_str(d, "d")

		if self.task["sections"][i].dtext:
			text = paintool.greek(self.task["sections"][i].dtext)

		paintool.draw_vertical_dimlines_with_text(
			painter = self.painter, 
			upnt = QPointF((self.wsect(i) + self.wsect(i+1))/2, strt_height), 
			dpnt = QPointF((self.wsect(i) + self.wsect(i+1))/2, fini_height), 
			arrow_size = 10, 
			textpnt = QPointF(0, -QFontMetrics(self.font).height()/4), 
			text = text, 
			font = self.font)

	def paintEventImplementation(self, ev):
		"""Рисуем сцену согласно объекта задания"""
		subtype = self.shemetype.task_subtype.get()
		self.subtype = subtype

		font_size = self.shemetype.font_size.get()
		font = self.painter.font()
		font.setItalic(True)
		font.setPointSize(font_size)
		self.painter.setFont(font)
		self.font = font

		lwidth = self.shemetype.lwidth.get()

		axis = self.shemetype.axis.get()
		zleft = self.shemetype.zleft.get()
		self.zleft = zleft
		zright = self.shemetype.zright.get()
		self.zright = zright

		base_section_height = self.shemetype.base_section_height.get()
		
		arrow_size = self.shemetype.arrow_size.get()
		self.arrow_size = arrow_size

		arrow_head_size = self.shemetype.arrow_size.get()
		self.arrow_head_size = arrow_head_size

		razm = self.shemetype.razm.get()
		self.razm = razm

		task = self.shemetype.task
		self.task = task
		size = self.size()

		width = size.width()
		height = size.height()
		#kruch_flag = self.shemetype.kruch_flag.get()

		kruch_flag = False if subtype == SUBTYPE_RASTYAZHENIE_SJATIE else True

		addtext = self.shemetype.texteditor.toPlainText()

		arrow_line_size = 50
		self.arrow_line_size = arrow_line_size

		hcenter = self.hcenter

		height_zone = base_section_height
		self.height_zone = height_zone 

		self.strt_width = self.shemetype.left_zone.get()
		self.fini_width = width-self.shemetype.right_zone.get()

		if subtype == SUBTYPE_RASTYAZHENIE_SJATIE:
			if self.bsections()[0].Fstyle != "к узлу":
				if self.bsections()[0].F == "-":
					self.strt_width = self.strt_width + arrow_line_size

			if self.bsections()[-1].Fstyle != "к узлу":
				if self.bsections()[-1].F == "+":
					self.fini_width = self.fini_width - arrow_line_size
	
			if self.bsections()[0].Fstyle == "к узлу":
				if self.bsections()[0].F == "+":
					self.strt_width = self.strt_width + arrow_line_size
	
			if self.bsections()[-1].Fstyle == "к узлу":
				if self.bsections()[-1].F == "-":
					self.fini_width = self.fini_width - arrow_line_size

		br = QPen()
		br.setWidth(lwidth)
		self.painter.setPen(br)


		maxl = 0
		maxA = 0
		for s in self.sections():
			if s.l > maxl: maxl = s.l
			if s.A > maxA: maxA = s.A

		dimlines_level = hcenter + base_section_height*math.sqrt(maxA)/2 + self.shemetype.dimlines_start_step.get()
		self.dimlines_level = dimlines_level

		if razm is True:
			hcenter -= self.shemetype.dimlines_start_step.get() / 2 

		self.hcenter = hcenter

		if razm is False:
			pass

		# Длины и дистанции
		self.summary_length = 0
		self.ll = [0]
		for i in range(len(task["sections"])):
			self.summary_length += task["sections"][i].l
			self.ll.append(self.ll[i] + task["sections"][i].l)

		
		# Отрисовка секций
		for i in range(len(task["sections"])):
			hkoeff = self.sectrad_koeff(i)

			strt_height = hcenter - height_zone*hkoeff/2
			fini_height = hcenter + height_zone*hkoeff/2

			self.draw_section(i, strt_height, fini_height)
			self.draw_dimlines(i, strt_height, fini_height)

			self.painter.setBrush(self.default_brush)
			self.painter.setPen(self.default_pen)

		if axis:
			pen = QPen(Qt.CustomDashLine)
			pen.setDashPattern([10,3,1,3])
			self.painter.setPen(pen)
			self.painter.drawLine(QPointF(5, hcenter), QPointF(width - 5, hcenter))
			pen = QPen()
			self.painter.setPen(pen)

		# отрисовка сил		
		if subtype == SUBTYPE_RASTYAZHENIE_SJATIE:
			self.force_drawing()
		else:
			self.torsion_drawing()

		for i in range(len(task["sections"])):
			hkoeff = self.sectrad_koeff(i)

			strt_height = hcenter - height_zone*hkoeff/2
			fini_height = hcenter + height_zone*hkoeff/2

			if self.subtype == SUBTYPE_KRUCHENIE_2:
				self.draw_diameters(i, strt_height, fini_height)

			self.painter.setBrush(self.default_brush)
			self.painter.setPen(self.default_pen)

		for i in range(len(task["betsect"])):
			if task["betsect"][i].label != "":
				self.painter.setPen(self.halfpen)

				if task["betsect"][i].label_up is True:

					elements.draw_text_by_points(
					self, 
					strt = QPointF(self.wsect(i),hcenter - self.msectrad(i)), 
					fini= QPointF(self.wsect(i), hcenter - self.msectrad(i)-40), 
					txt = task["betsect"][i].label, 
					alttxt = False, 
					off=14,
					polka=QPointF(self.wsect(i), hcenter)
					)
				else:
					txt = task["betsect"][i].label
					self.painter.setPen(Qt.NoPen)
					self.painter.drawRect(QRectF(
						QPointF(self.wsect(i) -3 + 14,                                      hcenter - QFontMetrics(self.font).height()/2 ),
						QPointF(self.wsect(i) +3 + 14 + QFontMetrics(self.font).width(txt), hcenter + QFontMetrics(self.font).height()/2 )
					))

					self.painter.setPen(self.default_pen)
					elements.draw_text_by_points(
					self, 
					strt = QPointF(self.wsect(i),hcenter + self.msectrad(i)), 
					fini= QPointF(self.wsect(i), hcenter - self.msectrad(i)), 
					txt = task["betsect"][i].label, 
					alttxt = False, 
					off=14,
					polka=None
					)


		# подсветка узла		
		if self.highlited_node is not None:
			row = self.highlited_node[1]
			
			pen = QPen()
			pen.setColor(Qt.blue)
			pen.setWidth(5)
			p = QPoint(self.wsect(row), self.hcenter)
			self.painter.setBrush(Qt.green)
			self.painter.drawEllipse(QRect(p-QPoint(5,5),p+QPoint(5,5)))
			self.painter.setBrush(Qt.black)

		if zleft:
			y = math.sqrt(task["sections"][0].A) * height_zone
			paintool.zadelka(self.painter, self.wsect(0) - 10, self.wsect(0), hcenter-y, hcenter+y, left_border=False, right_border=True)

		if zright:
			y = math.sqrt(task["sections"][-1].A) * height_zone
			paintool.zadelka(self.painter, self.wsect(-1), self.wsect(-1) + 10, hcenter-y, hcenter+y, left_border=True, right_border=False)


