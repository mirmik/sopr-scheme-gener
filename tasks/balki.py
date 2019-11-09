import common
import paintwdg
import math

from paintool import deg
import paintool
import taskconf_menu
import util
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
		def __init__(self, sharn = False, sectname="", F="clean", M="clean", Mkr="clean", MT="", FT=""):
			self.sectname = sectname
			self.M = M
			self.Mkr = Mkr 
			self.F=F
			self.MT = MT
			self.FT = FT
			self.sharn = sharn

	class sectforce:
		def __init__(self, Fr="clean", FrT=""):
			#self.mkr = mkr
			#self.mkrT = mkrT
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
				self.betsect(sharn=True),
				self.betsect(),
				self.betsect(),
				self.betsect()
			],
			"sectforce":
			[
				self.sectforce(),
				self.sectforce(),
				self.sectforce(Fr="+", FrT="ql")
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
			defval=4,
			variant=[
				"Круг",  
				"Толстая труба",
				"Тонкая труба",
				"Прямоугольник",
				"Треугольник",
				"Квадрат - окружность",
			])

		self.shemetype.section_txt0 = self.sett.add("Сечение.Текст1:", "str", "D")
		self.shemetype.section_txt1 = self.sett.add("Сечение.Текст2:", "str", "d")
		self.shemetype.section_txt2 = self.sett.add("Сечение.Текст3:", "str", "d")

		self.shemetype.section_arg0 = self.sett.add("Сечение.Аргумент1:", "int", "60")
		self.shemetype.section_arg1 = self.sett.add("Сечение.Аргумент2:", "int", "50")
		self.shemetype.section_arg2 = self.sett.add("Сечение.Аргумент3:", "int", "10")
		

		#self.shemetype.arrow_line_size = self.sett.add("Размер линии стрелки:", "int", "20")
		#self.shemetype.dimlines_start_step = self.sett.add("Отступ размерных линий:", "int", "40")
		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "15")
		#self.shemetype.font_size = common.CONFVIEW.font_size_getter
#		self.shemetype.left_zone = self.sett.add("Отступ слева:", "int", "20")
#		self.shemetype.right_zone = self.sett.add("Отступ справа:", "int", "20")
		
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.sett.updated.connect(self.redraw)



		self.table = tablewidget.TableWidget(self.shemetype, "sections")
#		self.table.addColumn("d", "float", "Диаметр")
#		self.table.addColumn("dtext", "str", "Текст")
		self.table.addColumn("l", "float", "Длина")
		#self.table.addColumn("delta", "float", "Зазор")
		self.table.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("sectname", "str", "Имя")
		self.table2.addColumn("sharn", "bool", "Шарн.")
		self.table2.addColumn("F", "list", variant=["clean", "+", "-"])
		self.table2.addColumn("M", "list", variant=["clean", "+", "-"])
#		self.table2.addColumn("Mkr", "list", variant=["clean", "+", "-"])
		self.table2.addColumn("FT", "str", "Текст")
		self.table2.addColumn("MT", "str", "Текст")
		self.table2.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table1.addColumn("Fr", "list", variant=["clean", "+", "-"])
		self.table1.addColumn("FrT", "str", "Текст")
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


		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		self.vlayout.addWidget(self.shemetype.texteditor)

		self.setLayout(self.vlayout)

	def add_action(self):
		self.sections().append(self.sect())
		self.shemetype.task["sectforce"].append(self.sectforce())
		self.shemetype.task["betsect"].append(self.betsect())
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def del_action(self):
		if len(self.sections()) == 1:
			return

		del self.sections()[-1]
		del self.shemetype.task["betsect"][-1]
		del self.shemetype.task["sectforce"][-1]
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
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
		
		atxt = paintool.greek(self.shemetype.section_txt0.get())
		btxt = paintool.greek(self.shemetype.section_txt1.get())
		ctxt = paintool.greek(self.shemetype.section_txt2.get())

		arrow_size = self.shemetype.arrow_size.get()
		
		if section_type == "Круг":
			center = QPoint(right - 10 -20 - arg0/2, hcenter)
			section_width = arg0 + 100

			dimlines_off = arg0 + 30

			painter.setPen(self.pen)

			painter.setBrush(QBrush(Qt.BDiagPattern))
			painter.drawEllipse(
				QRect(center - QPoint(arg0,arg0), center + QPoint(arg0,arg0)))

			painter.setPen(self.halfpen)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center-QPoint(arg0, 0),
				bpnt = center+QPoint(arg0, 0),
				offset = QPoint(0,dimlines_off),
				textoff = QPoint(0, -10),
				text = atxt,
				arrow_size = arrow_size / 3 * 2
			)

			painter.setPen(self.axpen)
			llen = arg0 + 10
			painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
			painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))

		elif section_type == "Тонкая труба":
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

			painter.setBrush(QBrush(Qt.NoBrush))
			painter.setPen(self.axpen)
			painter.drawEllipse(
				QRect(center - QPoint((arg1+arg0)/2,(arg0+arg1)/2), center + QPoint((arg1+arg0)/2,(arg0+arg1)/2)))

			painter.setPen(self.halfpen)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center-QPoint(0,(arg1+arg0)/2),
				bpnt = center+QPoint(0,(arg1+arg0)/2),
				offset = QPoint(-dimlines_off,0),
				textoff = QPoint(-10, 0) - QPoint(QFontMetrics(self.font).width(atxt)/2, 0),
				text = atxt,
				arrow_size = arrow_size / 3 * 2
			)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
				bpnt = center+QPoint(+ math.cos(math.pi/4) * arg0, + math.sin(math.pi/4) * arg0),
				offset = QPoint(0,0),
				textoff = QPoint(+ math.cos(math.pi/4) * (arg0-arg1) + 15, + math.sin(math.pi/4) * (arg0-arg1)),
				text = btxt,
				arrow_size = arrow_size / 3 * 2,
				splashed=True,
				textline_from = "bpnt"
			)

			painter.setPen(self.axpen)
			llen = arg0 + 10
			painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
			painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))

		elif section_type == "Толстая труба":
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
				textoff = QPoint(-10, 0) - QPoint(QFontMetrics(self.font).width(atxt)/2, 0),
				text = atxt,
				arrow_size = arrow_size / 3 * 2
			)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
				bpnt = center+QPoint(- math.cos(math.pi/4) * arg1, - math.sin(math.pi/4) * arg1),
				offset = QPoint(0,0),
				textoff = QPoint(10,-10),
				text = btxt,
				arrow_size = arrow_size / 3 * 2,
			)
			
			painter.setPen(self.axpen)
			llen = arg0 + 10
			painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
			painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))

		elif section_type == "Квадрат - окружность":
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

		elif section_type == "Прямоугольник":
			center = QPoint(right - 20 - 10 - arg0/2, hcenter)
			section_width = arg1 + 120

			painter.setPen(self.pen)

			painter.setBrush(QBrush(Qt.BDiagPattern))
			painter.drawRect(
				QRect(center - QPoint(arg1,arg0), center + QPoint(arg1,arg0)))

			painter.setBrush(QBrush(Qt.white))
	
			painter.setPen(self.halfpen)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(-arg1,arg0),
				bpnt = center+QPoint(-arg1,-arg0),
				offset = QPoint(-20,0),
				textoff = QPoint(-10, 0),
				text = atxt,
				arrow_size = arrow_size / 3 * 2
			)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(arg1,arg0),
				bpnt = center+QPoint(-arg1,arg0),
				offset = QPoint(0,25),
				textoff = QPoint(0, -6),
				text = btxt,
				arrow_size = arrow_size / 3 * 2
			)

			#paintool.draw_dimlines(
			#	painter = painter,
			#	apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
			#	bpnt = center+QPoint(- math.cos(math.pi/4) * arg1, - math.sin(math.pi/4) * arg1),
			#	offset = QPoint(0,0),
			#	textoff = QPoint(8,-8),
			#	text = ctxt,
			#	arrow_size = arrow_size / 3 * 2
			#)

			painter.setPen(self.axpen)
			llen = arg0 + 10
			painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
			painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))


		elif section_type == "Треугольник":
			center = QPoint(right - 20 - 10 - arg0/2, hcenter)
			section_width = arg1 + 120

			painter.setPen(self.pen)

			painter.setBrush(QBrush(Qt.BDiagPattern))
			painter.drawPolygon(
				QPolygon([
					center+QPoint(-arg1, arg0),
					center+QPoint(arg1, arg0),
					center+QPoint(0, -arg0),
				])
			)

			painter.setBrush(QBrush(Qt.white))
	
			painter.setPen(self.halfpen)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(0,arg0),
				bpnt = center+QPoint(0,-arg0),
				offset = QPoint(-20-arg0,0),
				textoff = QPoint(-10, 0),
				text = atxt,
				arrow_size = arrow_size / 3 * 2
			)

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(arg1,arg0),
				bpnt = center+QPoint(-arg1,arg0),
				offset = QPoint(0,25),
				textoff = QPoint(0, -6),
				text = btxt,
				arrow_size = arrow_size / 3 * 2
			)

			#paintool.draw_dimlines(
			#	painter = painter,
			#	apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
			#	bpnt = center+QPoint(- math.cos(math.pi/4) * arg1, - math.sin(math.pi/4) * arg1),
			#	offset = QPoint(0,0),
			#	textoff = QPoint(8,-8),
			#	text = ctxt,
			#	arrow_size = arrow_size / 3 * 2
			#)

			painter.setPen(self.axpen)
			llen = arg0 + 10
			painter.drawLine(center + QPoint(-llen,-arg0+4/3*arg0), center + QPoint(llen,-arg0+4/3*arg0))
			painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))

		else:
			print("Unresolved section type:", section_type)
			exit(0)

		return section_width

	def lsum(self):
		ret = 0
		for sect in self.sections():
			ret += sect.l
		return ret

	def draw_body(self,hcenter, left, right):
		painter = QPainter(self)
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
	
			if self.bsections()[i].M != "clean":
				fdown=True
				pnt = QPoint(wpnts[i], hcenter)
				if self.bsections()[i].M == "+":
					paintool.half_moment_arrow_common(
						painter=painter, 
						pnt=pnt, 
						rad=rad, 
						angle=deg(60), 
						angle2=deg(120),
						#left=True, 
						#inverse = False, 
						arrow_size=arrow_size)
				if self.bsections()[i].M == "-":
					paintool.half_moment_arrow_common(
						painter=painter, 
						pnt=pnt, 
						rad=rad, 
						angle=deg(120), 
						angle2=deg(60),
						#left=True, 
						#inverse = False, 
						arrow_size=arrow_size)

			if self.bsections()[i].F != "clean":
				apnt=QPoint(wpnts[i], hcenter-rad) 
				bpnt=QPoint(wpnts[i], hcenter)
				if fdown:
					apnt = apnt + QPoint(0, rad+hsect/2)
					bpnt = bpnt + QPoint(0, rad+hsect/2)
				else:
					apnt = apnt + QPoint(0, -hsect/2)
					bpnt = bpnt + QPoint(0, -hsect/2)
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
					#F_text_policy = "up"
					#F_level = - sectrad(i) * 3.2/2 + hcenter
				
			if self.bsections()[i].M != "clean":
				paintool.draw_text_centered(
					painter,
					pnt=QPoint(wpnts[i], hcenter-rad-5), 
					text=paintool.greek(self.bsections()[i].MT),
					font=self.font)

			if self.bsections()[i].F != "clean" and fdown == False:
				paintool.draw_text_centered(
					painter,
					pnt=QPoint(wpnts[i], hcenter-rad-5), 
					text=paintool.greek(self.bsections()[i].FT),
					font=self.font)

			if self.bsections()[i].F != "clean" and fdown == True:
				painter.drawText(
					QPoint(wpnts[i]+10, hcenter+25), 
					paintool.greek(self.bsections()[i].FT))

			if self.bsections()[i].sectname != "":
				off = 11 if self.bsections()[i].sharn else 5
				painter.drawText(
					QPoint(wpnts[i]-off-QFontMetrics(self.font).width(self.bsections()[i].sectname), hcenter+21), 
					self.bsections()[i].sectname)


		rad2 = rad/2
		step = 10
		# Отрисовка распределённых нагрузок:
		for i in range(len(self.sectforce())):
			#отрисовка распределённой силы.
			if self.sectforce()[i].Fr != "clean":
				if self.sectforce()[i].Fr == "+":
					paintool.raspred_force_vertical(painter=painter,
						apnt=QPoint(wpnts[i], hcenter-3),
						bpnt=QPoint(wpnts[i+1], hcenter-3),
						step=step,
						offset=QPoint(0, -rad2),
						dim = True,
					arrow_size=arrow_size/3*2)
				elif self.sectforce()[i].Fr == "-":
					paintool.raspred_force_vertical(painter=painter,
						apnt=QPoint(wpnts[i], hcenter-3),
						bpnt=QPoint(wpnts[i+1], hcenter-3),
						step=step,
						offset=QPoint(0, -rad2),
						dim = False,
						arrow_size=arrow_size/3*2)

				paintool.draw_text_centered(
					painter,
					QPoint((wpnts[i] + wpnts[i+1])/2, hcenter-8-rad2),
					paintool.greek(self.sectforce()[i].FrT),
					font=self.font
				)
			
		painter.setBrush(Qt.white)
		painter.setPen(self.pen)



		painter.drawRect(QRect(
			QPoint(left+prefix, hcenter-hsect/2),
			QPoint(right-prefix, hcenter+hsect/2),
		))

		#dimlines
		for i in range(len(self.bsections())-1):
			paintool.dimlines(painter, 
				QPoint(wpnts[i], hcenter), 
				QPoint(wpnts[i+1], hcenter), 
				hcenter+80)
			text = util.text_prepare_ltext(self.sections()[i].l)
			if not self.shemetype.section_enable.get():
				text += ", EIx"
			paintool.draw_text_centered(painter, 
				QPoint((wpnts[i]+wpnts[i+1])/2, 
					hcenter+80-5), text, self.font)


		termpos = wpnts[0] if self.shemetype.leftterm.get() else wpnts[-1]
		termangle = math.pi if self.shemetype.leftterm.get() else 0
		paintool.draw_sharnir_1dim(
				painter, 
				pnt=QPoint(termpos, hcenter), 
				angle=termangle, 
				rad=5.5, 
				termrad=25, 
				termx=20, 
				termy=10, pen=self.pen, halfpen=self.halfpen, doublepen=self.doublepen)

		for i in range(len(self.bsections())):
			if self.bsections()[i].sharn:
				hoff = 0 if i == 0 or i == len(self.bsections()) - 1 else 8
				ihoff = 8 if i == 0 or i == len(self.bsections()) - 1 else 0
				paintool.draw_sharnir_1dim(
					painter, 
					pnt=QPoint(wpnts[i], hcenter + hoff), 
					angle=math.pi/2, 
					rad=5.5, 
					termrad=25+ihoff, 
					termx=20, 
					termy=10, pen=self.pen, halfpen=self.halfpen, doublepen=self.doublepen)




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

#		height_zone = base_section_height

		strt_width = 20#self.shemetype.left_zone.get()
		fini_width = width-20#width-self.shemetype.right_zone.get()

		actual_width = fini_width - strt_width

		addtext = self.shemetype.texteditor.toPlainText()
		arrow_line_size = 50
		hcenter = height/2 -10 - QFontMetrics(self.font).height() * len(addtext.splitlines()) / 2


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

		painter = QPainter(self)
		painter.setPen(self.pen)
		painter.setFont(self.font)
		painter.setBrush(Qt.black)
		for i, l in enumerate(addtext.splitlines()):
			painter.drawText(QPoint(
				40, 
				hcenter + 75 + 30 + QFontMetrics(self.font).height()*i), 
			paintool.greek(l))
