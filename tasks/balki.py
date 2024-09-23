import common
import paintwdg
import math

from paintool import deg
import paintool
import taskconf_menu
import util
import tablewidget
import sections

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Балки")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())


class ConfWidget(common.ConfWidget):
	"""Виджет настроек задачи T0"""
	class sect:
		def __init__(self, l=1):
			self.l=l

	class betsect:
		def __init__(self, sharn = "Нет", sectname="", F="Нет", M="Нет", Mkr="Нет", MT="", FT=""):
			self.sectname = sectname
			self.M = M
			self.Mkr = Mkr 
			self.F=F
			self.MT = MT
			self.FT = FT
			self.sharn = sharn

	class sectforce:
		def __init__(self, Fr="Нет", FrT=""):
			self.Fr = Fr
			self.FrT = FrT


	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(l=1),
				self.sect(l=1),
				self.sect(l=2),
			],
			"betsect":
			[
				self.betsect(sharn="1"),
				self.betsect(),
				self.betsect(sharn="2"),
				self.betsect()
			],
			"sectforce":
			[
				self.sectforce(),
				self.sectforce(),
				self.sectforce(Fr="+", FrT="ql")
			],

			"labels" : []
		}

	def init_taskconf(self):
		node_variant = ["Нет", "Заделка", "Шарнир"]

		self.sett.add_delimiter()		
		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.left_node = self.sett.add("Левый узел", "list", defval=0, variant=node_variant)
		self.shemetype.right_node = self.sett.add("Правый узел", "list", defval=0, variant=node_variant)
		self.shemetype.postfix = self.sett.add("Постфикс:", ("bool", "str"), (False, ", EIx"))
				
		self.sett.add_delimiter()
		self.shemetype.section_enable = self.sett.add("Отображение сечения:", "bool", True)
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter

		self.shemetype.section_container = self.sett.add_widget(sections.SectionContainer(self.shemetype.section_enable))

		self.sett.add_delimiter()
		self.shemetype.base_section_height = self.sett.add("Базовая высота секции:", "int", "6")
		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "15")
		self.sett.add_delimiter()
		
	def section_enable_handle(self):
		pass
		
	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("l", "float", "Длина")
		self.table.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("sectname", "str", "Имя")
		self.table2.addColumn("sharn", "list", "Шарн.", variant=["Нет", "1", "2"])
		self.table2.addColumn("F", "list", variant=["Нет", "+", "-", "влево", "вправо"])
		self.table2.addColumn("M", "list", variant=["Нет", "+", "-"])
		self.table2.addColumn("FT", "str", "Текст F")
		self.table2.addColumn("MT", "str", "Текст M")
		self.table2.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table1.addColumn("Fr", "list", "q", variant=["Нет", "+", "-"])
		self.table1.addColumn("FrT", "str", "Текст q")
		self.table1.updateTable()

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

	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		self.init_taskconf()
		self.sett.updated.connect(self.redraw)
		self.shemetype.section_container.updated.connect(self.redraw)

		self.shemetype.section_enable.element().updated.connect(self.section_enable_handle)

		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)

		self.update_interface()
		self.setLayout(self.vlayout)

	def add_action_impl(self):
		self.sections().append(self.sect())
		self.shemetype.task["sectforce"].append(self.sectforce())
		self.shemetype.task["betsect"].append(self.betsect())
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def insert_action_impl(self, idx):
		self.sections().insert(idx, self.sect())
		self.shemetype.task["sectforce"].insert(idx, self.sectforce())
		self.shemetype.task["betsect"].insert(idx, self.betsect())
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def del_action_impl(self, idx):
		if len(self.sections()) == 1:
			return

		del self.sections()[idx]
		del self.shemetype.task["betsect"][idx]
		del self.shemetype.task["sectforce"][idx]
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def inittask(self):
		return {}

class PaintWidget(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()
		self.enable_common_mouse_events()

	def lsum(self):
		ret = 0
		for sect in self.sections():
			ret += sect.l
		return ret

	def draw_terminator(self, pos, angle, type):
		#Рисуем терминатор:
		if type == "Нет":
			pass

		elif type == "Шарнир":
			paintool.draw_sharnir_1dim(
				self.painter, 
				pnt=QPointF(pos, self.hcenter), 
				angle=angle, 
				rad=5.5, 
				termrad=25, 
				termx=20, 
				termy=10, pen=self.pen, halfpen=self.halfpen, doublepen=self.doublepen)
	
		elif type == "Заделка":
			paintool.draw_zadelka(
				self.painter, 
				pnt=QPointF(pos+0.5, self.hcenter), 
				angle=angle, 
				termx=25, 
				termy=15, pen=self.pen, halfpen=self.halfpen, doublepen=self.doublepen)			


	def draw_body(self,hcenter, left, right):
		painter = self.painter
		painter.setFont(self.font)

		prefix = 30
		hsect = self.shemetype.base_section_height.get()

		flen = right - left - 2*prefix
		lsum = self.lsum()
		step = flen/lsum

		cur = left + prefix
		wpnts = [cur]
		for sect in self.sections():
			cur+=sect.l*step
			wpnts.append(cur)

		painter.setPen(self.pen)




		for i in range(len(self.bsections())):
			fdown = False
			arrow_size = self.shemetype.arrow_size.get()
			rad = 60
	
			if self.bsections()[i].M != "Нет":
				fdown=True
				pnt = QPointF(wpnts[i], hcenter)
				if self.bsections()[i].M == "+":
					paintool.half_moment_arrow_common(
						painter=painter, 
						pnt=pnt, 
						rad=rad, 
						angle=deg(60), 
						angle2=deg(120),
						arrow_size=arrow_size)
				if self.bsections()[i].M == "-":
					paintool.half_moment_arrow_common(
						painter=painter, 
						pnt=pnt, 
						rad=rad, 
						angle=deg(120), 
						angle2=deg(60),
						arrow_size=arrow_size)

			if self.bsections()[i].F != "Нет":
				apnt=QPointF(wpnts[i], hcenter-rad) 
				bpnt=QPointF(wpnts[i], hcenter)
				if fdown:
					apnt = apnt + QPointF(0, rad+hsect/2)
					bpnt = bpnt + QPointF(0, rad+hsect/2)
				else:
					apnt = apnt + QPointF(0, -hsect/2)
					bpnt = bpnt + QPointF(0, -hsect/2)
				if self.bsections()[i].F == "-":
					paintool.common_arrow(painter,
						apnt, bpnt,
						arrow_size=arrow_size
					)
				if self.bsections()[i].F == "+":
					paintool.common_arrow(painter,  
						bpnt, apnt,
						arrow_size=self.shemetype.arrow_size.get()
					)

				if self.bsections()[i].F == "влево" or self.bsections()[i].F == "вправо":
					apnt=QPointF(wpnts[i], hcenter)
					d = 40
					
					if i == 0:
						paintool.common_arrow(painter,  
							apnt if self.bsections()[i].F == "влево" else apnt + QPointF(-d,0), 
							apnt + QPointF(-d,0) if self.bsections()[i].F == "влево" else apnt,
							arrow_size=self.shemetype.arrow_size.get()
						)
					elif i == len(self.bsections()) - 1:
						paintool.common_arrow(painter,  
							apnt + QPointF(d,0) if self.bsections()[i].F == "влево" else apnt,
							apnt if self.bsections()[i].F == "влево" else apnt + QPointF(d,0), 
							arrow_size=self.shemetype.arrow_size.get()
						)
					else:
						d=30
						bpnt = apnt + QPointF(0,25)
						cpnt = apnt - QPointF(0,25)
						
						nnn = QPointF(-d,0) if self.bsections()[i].F == "влево" else QPointF(d,0)
						
						paintool.common_arrow(painter,  
							bpnt,
							bpnt+nnn, 
							arrow_size=self.shemetype.arrow_size.get()
						)
						paintool.common_arrow(painter,  
							cpnt,
							cpnt+nnn, 
							arrow_size=self.shemetype.arrow_size.get()
						)
						self.painter.drawLine(bpnt,cpnt)

			if self.bsections()[i].M != "Нет":
				paintool.draw_text_centered(
					painter,
					pnt=QPointF(wpnts[i], hcenter-rad-5), 
					text=paintool.greek(self.bsections()[i].MT),
					font=self.font)
			if self.bsections()[i].F != "Нет":
				if (self.bsections()[i].F != "вправо" and self.bsections()[i].F != "влево"):
					if fdown == False:
						painter.drawText(
							QPointF(wpnts[i]+10, hcenter-rad), 
							paintool.greek(self.bsections()[i].FT))
					
					if fdown == True:
						painter.drawText(
							QPointF(wpnts[i]+10, hcenter+25), 
							paintool.greek(self.bsections()[i].FT))
				else:
					painter.drawText(
						QPointF(wpnts[i]+0, hcenter-30), 
						paintool.greek(self.bsections()[i].FT))



			if self.bsections()[i].sectname != "":
				off = 11 if self.bsections()[i].sharn != "" else 5
				painter.drawText(
					QPointF(wpnts[i]-off-QFontMetrics(self.font).width(self.bsections()[i].sectname), hcenter+21), 
					self.bsections()[i].sectname)


		rad2 = rad/2
		step = 10
		# Отрисовка распределённых нагрузок:
		for i in range(len(self.sectforce())):
			#отрисовка распределённой силы.
			if self.sectforce()[i].Fr != "Нет":
				if self.sectforce()[i].Fr == "+":
					paintool.raspred_force_vertical(painter=painter,
						apnt=QPointF(wpnts[i], hcenter-3),
						bpnt=QPointF(wpnts[i+1], hcenter-3),
						step=step,
						offset=QPointF(0, -rad2),
						dim = True,
					arrow_size=arrow_size/3*2)
				elif self.sectforce()[i].Fr == "-":
					paintool.raspred_force_vertical(painter=painter,
						apnt=QPointF(wpnts[i], hcenter-3),
						bpnt=QPointF(wpnts[i+1], hcenter-3),
						step=step,
						offset=QPointF(0, -rad2),
						dim = False,
						arrow_size=arrow_size/3*2)

				paintool.draw_text_centered(
					painter,
					QPointF((wpnts[i] + wpnts[i+1])/2, hcenter-8-rad2),
					paintool.greek(self.sectforce()[i].FrT),
					font=self.font
				)
			
		painter.setBrush(Qt.white)
		painter.setPen(self.pen)



		painter.drawRect(QRectF(
			QPointF(left+prefix, hcenter-hsect/2),
			QPointF(right-prefix, hcenter+hsect/2),
		))

		#dimlines
		for i in range(len(self.bsections())-1):
			paintool.dimlines(painter, 
				QPointF(wpnts[i], hcenter), 
				QPointF(wpnts[i+1], hcenter), 
				hcenter+80)
			text = util.text_prepare_ltext(self.sections()[i].l)
			if self.shemetype.postfix.get()[0]:
				text += self.shemetype.postfix.get()[1]
			paintool.draw_text_centered(painter, 
				QPointF((wpnts[i]+wpnts[i+1])/2, 
					hcenter+80-5), text, self.font)

		self.draw_terminator(pos=wpnts[0], angle=math.pi, type=self.shemetype.left_node.get())	
		self.draw_terminator(pos=wpnts[-1], angle=0, type=self.shemetype.right_node.get())

		for i in range(len(self.bsections())):
			if self.bsections()[i].sharn == "1":
				hoff = 0 if i == 0 or i == len(self.bsections()) - 1 else 8
				ihoff = 8 if i == 0 or i == len(self.bsections()) - 1 else 0
				paintool.draw_sharnir_1dim(
					painter, 
					pnt=QPointF(wpnts[i], hcenter + hoff), 
					angle=math.pi/2, 
					rad=5.5, 
					termrad=25+ihoff, 
					termx=20, 
					termy=10, pen=self.pen, halfpen=self.halfpen, doublepen=self.doublepen)

			elif self.bsections()[i].sharn == "2":
				hoff = 0 if i == 0 or i == len(self.bsections()) - 1 else 8
				ihoff = 8 if i == 0 or i == len(self.bsections()) - 1 else 0
				paintool.draw_sharnir_2dim(
					painter, 
					pnt=QPointF(wpnts[i], hcenter + hoff), 
					angle=math.pi/2, 
					rad=5.5, 
					termrad=25+ihoff, 
					termx=20, 
					termy=10, pen=self.pen, halfpen=self.halfpen)



	def paintEventImplementation(self, ev):
		"""Рисуем сцену согласно объекта задания"""

		lwidth = self.shemetype.lwidth.get()

		section_enable = self.shemetype.section_enable.get()
		task = self.shemetype.task

		size = self.size()
		width = size.width()
		height = size.height()

		strt_width = 20
		fini_width = width-20
		

		actual_width = fini_width - strt_width

		arrow_line_size = 50
		hcenter = self.hcenter

		section_width = sections.draw_section_routine(self, hcenter=hcenter, right=fini_width)
		
		actual_width -= section_width
		fini_width -= section_width

		self.labels_center= QPointF((strt_width + fini_width)/2, hcenter)
		self.labels_width_scale = actual_width

		self.draw_body(
			hcenter=hcenter, left=strt_width, right=fini_width)
			
		self.draw_labels()
