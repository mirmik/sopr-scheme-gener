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

class ShemeTypeT01(common.SchemeType):
	def __init__(self):
		super().__init__("Кручение/Изгиб + Камера")
		self.setwidgets(ConfWidget_T01(self), PaintWidget_T01(), common.TableWidget())


class ConfWidget_T01(common.ConfWidget):
	"""Виджет настроек задачи T0"""
	class sect:
		def __init__(self, d=1, l=1, dtext="", 
			#delta=False
		):
			self.d=d
			self.dtext=dtext
			self.l=l

	class betsect:
		def __init__(self, M="clean", Mkr="clean", T=""):
			self.M = M
			self.Mkr = Mkr 
			self.T = T

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(d=1, l=1),
				self.sect(d=2, l=1),
				self.sect(d=1, l=2),
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
		self.shemetype.zleft = self.sett.add("Разрез слева:", "bool", True)
		self.shemetype.zright = self.sett.add("Разрез справа:", "bool", True)
		self.shemetype.kamera = self.sett.add("Внешняя камера:", "bool", False)
		self.shemetype.inkamera = self.sett.add("Внутренняя камера:", "bool", False)
		self.shemetype.inkamera_dist = self.sett.add("Отступ до камеры:", "int", "30")
		#		self.shemetype.razm = self.sett.add("Размерные линии:", "bool", True)

		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.base_section_height = self.sett.add("Базовая высота секции:", "int", "40")
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
		self.table.addColumn("d", "float", "Диаметр")
		self.table.addColumn("dtext", "str", "Текст")
		self.table.addColumn("l", "float", "Длина")
		#self.table.addColumn("delta", "float", "Зазор")
		self.table.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		#self.table2.addColumn("F", "list", variant=["clean", "+", "-"])
		#self.table2.addColumn("M", "list", variant=["clean", "+", "-"])
		self.table2.addColumn("Mkr", "list", variant=["clean", "+", "-"])
		self.table2.addColumn("T", "str", "Текст")
		self.table2.updateTable()




		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Локальные силы:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)


		self.table.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)


		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		self.vlayout.addWidget(self.shemetype.texteditor)

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

class PaintWidget_T01(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()

	def paintEventImplementation(self, ev):
		"""Рисуем сцену согласно объекта задания"""

		lwidth = self.shemetype.lwidth.get()

		axis = True
		zleft = self.shemetype.zleft.get()
		zright = self.shemetype.zright.get()

		base_section_height = self.shemetype.base_section_height.get()
		arrow_size = self.shemetype.arrow_size.get()
		arrow_head_size = arrow_size
		font_size = self.shemetype.font_size.get()
		kamera = self.shemetype.kamera.get()
		inkamera = self.shemetype.inkamera.get()
		inkamera_dist = self.shemetype.inkamera_dist.get()
		#razm = self.shemetype.razm.get()

		task = self.shemetype.task
		size = self.size()

		width = size.width()
		height = size.height()

		hcenter = self.hcenter

		height_zone = base_section_height

		strt_width = 20#self.shemetype.left_zone.get()
		fini_width = width-20#width-self.shemetype.right_zone.get()

		if kamera:
			strt_width = strt_width + 40
			fini_width = fini_width - 40

		if zleft:
			strt_width = strt_width + 20

		if zright:
			fini_width = fini_width - 20

		font = self.painter.font()
		font.setItalic(True)
		font.setPointSize(font_size)
		self.painter.setFont(font)

		br = QPen()
		br.setWidth(lwidth)
		self.painter.setPen(br)


		maxl = 0
		maxd = 0
		for s in self.sections():
			if s.l > maxl: maxl = s.l
			if s.d > maxd: maxd = s.d

#		dimlines_level = hcenter + base_section_height*maxd/2 + self.shemetype.dimlines_start_step.get()
		#if razm is True:
		#	hcenter -= self.shemetype.dimlines_start_step.get() / 2 

		#if razm is False:
		#	hcenter = 0

		# Длины и дистанции
		summary_length = 0
		ll = [0]
		for i in range(len(task["sections"])):
			summary_length += task["sections"][i].l
			ll.append(ll[i] + task["sections"][i].l)

		def wsect(i):
			l = len(task["sections"])
			k0 = summary_length - ll[i]
			k1 = ll[i]
			return (fini_width * k1 + strt_width * k0) // summary_length

		def sectrad(i):
			return task["sections"][i].d * height_zone / 2

		def msectrad(i):
			leftA = 0 if i == 0 else task["sections"][i-1].d
			rightA = 0 if i == -1 + len(task["betsect"]) else task["sections"][i].d
			return max(leftA, rightA) * height_zone / 2

		#Рисуем камеру, если надо:
		if kamera:
			paintool.draw_kamera(self.painter, 
				lu=QPoint(20,20), 
				rd=QPoint(width-20, height-20), 
				t=10)
		
		if inkamera:
			paintool.draw_inkamera(self.painter, 
				lu=QPoint(wsect(0)+inkamera_dist,inkamera_dist), 
				rd=QPoint(wsect(-1)-inkamera_dist, height-inkamera_dist), 
				t=20)

		# Отрисовка секций
		for i in range(len(task["sections"])):
			hkoeff = task["sections"][i].d

			strt_height = hcenter - height_zone*hkoeff/2
			fini_height = hcenter + height_zone*hkoeff/2

			d = task["sections"][i].d
	
			if abs(float(d) - int(d)) < 0.0001:
				text_d = "{}d".format(int(task["sections"][i].d+0.1)) if task["sections"][i].d != 1 else "d"
			else:
				text_d = str(float(d)) + "d"

			zlen = 10
			self.painter.setBrush(Qt.white)

			if zleft and zright and len(task["sections"]) == 1:
				paintool.draw_rectangle(self.painter,wsect(i)-zlen, strt_height, wsect(i+1)-wsect(i)+zlen*2, fini_height-strt_height, zleft=True, zright=True)

			elif zleft and i == 0:
				paintool.draw_rectangle(self.painter,wsect(i)-zlen, strt_height, wsect(i+1)-wsect(i)+zlen, fini_height-strt_height, zleft=True)

			elif zright and i == len(task["sections"])-1:
				paintool.draw_rectangle(self.painter,wsect(i), strt_height, wsect(i+1)-wsect(i)+zlen, fini_height-strt_height, zright=True)

			else:
				self.painter.drawRect(wsect(i), strt_height, wsect(i+1)-wsect(i), fini_height-strt_height)


#			if razm:
#				self.painter.setPen(self.halfpen)
#				paintool.dimlines(self.painter, QPoint(wsect(i), fini_height), QPoint(wsect(i+1), fini_height), dimlines_level)
#				paintool.draw_text_centered(self.painter, QPoint((wsect(i)+wsect(i+1))/2, dimlines_level-5), text_l, self.font)

#				self.painter.setBrush(self.default_brush)
#				self.painter.setPen(self.default_pen)
		
		#Отрисовка граничных эффектов
		for i in range(len(task["betsect"])):
			if task["betsect"][i].Mkr == "+":
				paintool.kr_arrow(self.painter, QPoint(wsect(i), hcenter), msectrad(i)+10, 11, False)

			if task["betsect"][i].Mkr == "-":
				paintool.kr_arrow(self.painter, QPoint(wsect(i), hcenter), msectrad(i)+10, 11, True)

			if task["betsect"][i].T != "":
				leftA = 0 if i == 0 else task["sections"][i-1].d
				rightA = 0 if i == -1 + len(task["betsect"]) else task["sections"][i].d
				
				size = QFontMetrics(font).width(task["betsect"][i].T)
				text = task["betsect"][i].T


				if task["betsect"][i].Mkr == "clean":
					paintool.placedtext(self.painter,
						QPoint(wsect(i), hcenter), 
						max(leftA, rightA) * height_zone / 2 + 10, 
						size, 
						text,
						right = task["betsect"][i].M == 2)

				else:
					self.painter.drawText(QPoint(wsect(i) - size/2, hcenter - msectrad(i) - 10 - 11*2 - 5), text)

		#if zleft:
		#	y = task["sections"][0].d/2 * height_zone
			#paintool.zadelka(self.painter, wsect(0) - 10, wsect(0), hcenter-y, hcenter+y, left_border=False, right_border=True)
			#paintool.razrez(self.painter, QPoint(wsect(0)-10, hcenter-y), QPoint(wsect(0)-10, hcenter+y))

		#if zright:
		#	y = task["sections"][-1].d/2 * height_zone
			#paintool.zadelka(self.painter, wsect(-1), wsect(-1) + 10, hcenter-y, hcenter+y, left_border=True, right_border=False)
			
		#	self.painter.setBrush(Qt.white)
		#	self.painter.setPen(Qt.white)

			#self.painter.drawRect(QRect(
			#	QPoint(wsect(-1)-1,hcenter+y),
			#	QPoint(wsect(-1)+10,hcenter-y)
			#))
		#	paintool.razrez(self.painter, QPoint(wsect(-1)+10, hcenter-y), QPoint(wsect(-1)+10, hcenter+y))



		if axis:
			pen = QPen(Qt.CustomDashLine)
			pen.setDashPattern([10,3,1,3])
			self.painter.setPen(pen)
			self.painter.drawLine(QPoint(5, hcenter), QPoint(width - 5, hcenter))
			pen = QPen()
			self.painter.setPen(pen)

		#Текст и линии
		for i in range(len(task["sections"])):
			hkoeff = task["sections"][i].d

			strt_height = hcenter - height_zone*hkoeff/2
			fini_height = hcenter + height_zone*hkoeff/2

			if abs(float(d) - int(d)) < 0.0001:
				text_d = "{}d".format(int(task["sections"][i].d+0.1)) if task["sections"][i].d != 1 else "d"
			else:
				text_d = str(float(d)) + "d"
	
			d = task["sections"][i].d

			if task["sections"][i].dtext != "":
				text_d = task["sections"][i].dtext
			
			text_d = paintool.greek(text_d)

			AW = QFontMetrics(font).width(text_d)

			paintool.draw_vertical_dimlines_with_text(
				self.painter, 
				QPoint((wsect(i)*0.35+wsect(i+1)*0.65),strt_height), 
				QPoint((wsect(i)*0.35+wsect(i+1)*0.65),fini_height), 
				arrow_size/2, 
				QPoint(10,0), text_d, font)
