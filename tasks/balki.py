import common
import paintwdg
import math

import paintool
import taskconf_menu
import tablewidget

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
		def __init__(self, l=1, 
			#delta=False
		):
			self.l=l

	class betsect:
		def __init__(self, sharn = False, M="clean", Mkr="clean", T=""):
			self.M = M
			self.Mkr = Mkr 
			self.T = T
			self.sharn = sharn

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
				self.betsect(),
				self.betsect(),
				self.betsect(),
				self.betsect()
			]
		}
		

	def __init__(self, sheme):
		super().__init__(sheme)
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")

		self.sett = taskconf_menu.TaskConfMenu()
#		self.shemetype.axis = self.sett.add("Нарисовать ось:", "bool", True)
#		self.shemetype.zleft = self.sett.add("Разрез слева:", "bool", True)
#		self.shemetype.zright = self.sett.add("Разрез справа:", "bool", True)
#		self.shemetype.kamera = self.sett.add("Внешняя камера:", "bool", False)
#		self.shemetype.inkamera = self.sett.add("Внутренняя камера:", "bool", False)
#		self.shemetype.inkamera_dist = self.sett.add("Отступ до камеры:", "int", "30")
		#		self.shemetype.razm = self.sett.add("Размерные линии:", "bool", True)

		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.base_section_height = self.sett.add("Базовая высота секции:", "int", "6")
		self.shemetype.leftterm = self.sett.add("Левый терминатор:", "bool", True)
		
		self.shemetype.section_enable = self.sett.add("Отображение сечения:", "bool", True)
		self.shemetype.section_type = self.sett.add("Тип сечения:", "list", 
			defval=1,
			variant=[
				"ring", 
				"square - circle"
			])

		self.shemetype.section_txt0 = self.sett.add("Сечение.Текст1:", "str", "D")
		self.shemetype.section_txt1 = self.sett.add("Сечение.Текст2:", "str", "d")
		self.shemetype.section_txt2 = self.sett.add("Сечение.Текст3:", "str", "d")

		self.shemetype.section_arg0 = self.sett.add("Сечение.Аргумент1:", "int", "60")
		self.shemetype.section_arg1 = self.sett.add("Сечение.Аргумент2:", "int", "50")
		self.shemetype.section_arg2 = self.sett.add("Сечение.Аргумент3:", "int", "10")
		

		#self.shemetype.arrow_line_size = self.sett.add("Размер линии стрелки:", "int", "20")
		#self.shemetype.dimlines_start_step = self.sett.add("Отступ размерных линий:", "int", "40")
		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "20")
		#self.shemetype.font_size = common.CONFVIEW.font_size_getter
#		self.shemetype.left_zone = self.sett.add("Отступ слева:", "int", "20")
#		self.shemetype.right_zone = self.sett.add("Отступ справа:", "int", "20")
		
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.sett.updated.connect(self.redraw)



		self.table = tablewidget.TableWidget(self.shemetype, "sections")
#		self.table.addColumn("d", "float", "Диаметр")
#		self.table.addColumn("dtext", "str", "Текст")
#		self.table.addColumn("l", "float", "Длина")
		#self.table.addColumn("delta", "float", "Зазор")
		self.table.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("sharn", "bool", "Шарн.")
#		#self.table2.addColumn("F", "list", variant=["clean", "+", "-"])
		self.table2.addColumn("M", "list", variant=["clean", "+", "-"])
#		self.table2.addColumn("Mkr", "list", variant=["clean", "+", "-"])
#		self.table2.addColumn("T", "str", "Текст")
		self.table2.updateTable()




		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Локальные силы:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)


		self.table.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)



		self.setLayout(self.vlayout)

	def add_action(self):
		self.sections().append(self.sect())
		self.shemetype.task["betsect"].append(self.betsect())
		self.redraw()
		self.table.updateTable()
		self.table2.updateTable()

	def del_action(self):
		if len(self.sections()) == 1:
			return

		del self.sections()[-1]
		del self.shemetype.task["betsect"][-1]
		self.redraw()
		self.table.updateTable()
		self.table2.updateTable()

	def inittask(self):
		return {}

class PaintWidget(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()

	def draw_section(self, right, hcenter):
		painter = QPainter(self)
		painter.setFont(self.font)
		section_type = self.shemetype.section_type.get()

		arg0 = int(self.shemetype.section_arg0.get())
		arg1 = int(self.shemetype.section_arg1.get())
		arg2 = int(self.shemetype.section_arg2.get())
		
		atxt = self.shemetype.section_txt0.get()
		btxt = self.shemetype.section_txt1.get()
		ctxt = self.shemetype.section_txt2.get()

		arrow_size = self.shemetype.arrow_size.get()
		if section_type == "ring":
			center = QPoint(right - 20 - 10 - arg0/2, hcenter)
			section_width = arg0 + 120

			dimlines_off = arg0 + 20

			painter.setPen(self.pen)

			painter.setBrush(QBrush(Qt.BDiagPattern))
			painter.drawEllipse(
				QRect(center - QPoint(arg0,arg0), center + QPoint(arg0,arg0)))

			painter.setBrush(QBrush(Qt.white))
			painter.drawEllipse(
				QRect(center - QPoint(arg1,arg1), center + QPoint(arg1,arg1)))

			painter.setPen(self.halfpen)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center-QPoint(0,arg0),
				bpnt = center+QPoint(0,arg0),
				offset = QPoint(-dimlines_off,0),
				textoff = QPoint(-10, 0),
				text = "D",
				arrow_size = arrow_size / 3 * 2
			)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
				bpnt = center+QPoint(+ math.cos(math.pi/4) * arg0, + math.sin(math.pi/4) * arg0),
				offset = QPoint(0,0),
				textoff = QPoint(+ math.cos(math.pi/4) * (arg0-arg1) + 15, + math.sin(math.pi/4) * (arg0-arg1)),
				text = "d",
				arrow_size = arrow_size / 3 * 2,
				splashed=True,
				textline_from = "bpnt"
			)

			painter.setPen(self.axpen)
			llen = arg0 + 10
			painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
			painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))

		elif section_type == "square - circle":
			center = QPoint(right - 20 - 10 - arg0/2, hcenter)
			section_width = arg0 + 120

			dimlines_off = arg0 + 20

			painter.setPen(self.pen)

			painter.setBrush(QBrush(Qt.BDiagPattern))
			painter.drawRect(
				QRect(center - QPoint(arg0,arg0), center + QPoint(arg0,arg0)))

			painter.setBrush(QBrush(Qt.white))
			painter.drawEllipse(
				QRect(center - QPoint(arg1,arg1), center + QPoint(arg1,arg1)))

			painter.setPen(self.halfpen)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(-arg0,arg0),
				bpnt = center+QPoint(-arg0,-arg0),
				offset = QPoint(-20,0),
				textoff = QPoint(-10, 0),
				text = atxt,
				arrow_size = arrow_size / 3 * 2
			)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(arg0,arg0),
				bpnt = center+QPoint(-arg0,arg0),
				offset = QPoint(0,25),
				textoff = QPoint(0, -6),
				text = btxt,
				arrow_size = arrow_size / 3 * 2
			)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
				bpnt = center+QPoint(- math.cos(math.pi/4) * arg1, - math.sin(math.pi/4) * arg1),
				offset = QPoint(0,0),
				textoff = QPoint(8,-8),
				text = ctxt,
				arrow_size = arrow_size / 3 * 2
			)

			painter.setPen(self.axpen)
			llen = arg0 + 10
			painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
			painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))

		return section_width

	def lsum(self):
		ret = 0
		for sect in self.sections():
			ret += sect.l
		return ret

	def draw_body(self,hcenter, left, right):
		painter = QPainter(self)

		prefix = 20
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
		painter.drawRect(QRect(
			QPoint(left+prefix, hcenter-hsect/2),
			QPoint(right-prefix, hcenter+hsect/2),
		))

		termpos = wpnts[0] if self.shemetype.leftterm.get() else wpnts[-1]
		termangle = math.pi if self.shemetype.leftterm.get() else 0
		paintool.draw_sharnir_1dim(
				painter, 
				pnt=QPoint(termpos, hcenter), 
				angle=termangle, 
				rad=6, 
				termrad=20, 
				termx=20, 
				termy=10, pen=self.pen, halfpen=self.halfpen)

		for i in range(len(self.bsections())):
			paintool.draw_sharnir_1dim(
				painter, 
				pnt=QPoint(wpnts[i], hcenter), 
				angle=math.pi/2, 
				rad=6, 
				termrad=20, 
				termx=20, 
				termy=10, pen=self.pen, halfpen=self.halfpen)




	def paintEventImplementation(self, ev):
		"""Рисуем сцену согласно объекта задания"""

		lwidth = self.shemetype.lwidth.get()

#		axis = True
#		zleft = self.shemetype.zleft.get()
#		zright = self.shemetype.zright.get()

#		base_section_height = self.shemetype.base_section_height.get()
#		arrow_size = self.shemetype.arrow_size.get()
#		arrow_head_size = arrow_size
#		font_size = self.shemetype.font_size.get()
#		kamera = self.shemetype.kamera.get()
#		inkamera = self.shemetype.inkamera.get()
#		inkamera_dist = self.shemetype.inkamera_dist.get()
		#razm = self.shemetype.razm.get()

		section_enable = self.shemetype.section_enable.get()
		task = self.shemetype.task

		size = self.size()
		width = size.width()
		height = size.height()
		hcenter = height/2

#		height_zone = base_section_height

		strt_width = 20#self.shemetype.left_zone.get()
		fini_width = width-20#width-self.shemetype.right_zone.get()

		actual_width = fini_width - strt_width

		if section_enable:
		#	section_width = actual_width / 4

			section_width = self.draw_section(
				#section_width=section_width, 
				right = fini_width,
				hcenter=hcenter
			)

			actual_width -= section_width
			fini_width -= section_width

		self.draw_body(
			hcenter=hcenter, left=strt_width, right=fini_width)
