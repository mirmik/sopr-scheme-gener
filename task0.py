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

class ShemeTypeT0(common.SchemeType):
	def __init__(self):
		super().__init__("Растяжение/сжатие/кручение стержня переменного сечения)")
		self.setwidgets(ConfWidget_T0(self), PaintWidget_T0(), common.TableWidget())


class ConfWidget_T0(common.ConfWidget):
	"""Виджет настроек задачи T0"""
	class sect:
		def __init__(self, A=1, l=1, text="", delta=False):
			self.A=A
			self.l=l
			self.text = text
			self.delta=delta

	class sectforce:
		def __init__(self, mkr="clean", mkrT=""):
			self.mkr = mkr
			self.mkrT = mkrT

	class betsect:
		def __init__(self, F="clean", M="clean", Mkr="clean", T=""):
			self.F = F 
			self.M = M
			self.Mkr = Mkr 
			self.T = T

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(A=1, l=1),
				self.sect(A=2, l=1),
				self.sect(A=1, l=2),
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
		

	def __init__(self, sheme):
		super().__init__(sheme)
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")

		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.axis = self.sett.add("Нарисовать ось:", "bool", True)
		self.shemetype.zleft = self.sett.add("Заделка слева:", "bool", False)
		self.shemetype.zright = self.sett.add("Заделка справа:", "bool", False)
		self.shemetype.razm = self.sett.add("Размерные линии:", "bool", True)

		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.base_section_height = self.sett.add("Базовая высота секции:", "int", "40")
		#self.shemetype.arrow_line_size = self.sett.add("Размер линии стрелки:", "int", "20")
		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "20")
		self.shemetype.dimlines_start_step = self.sett.add("Отступ размерных линий:", "int", "40")
		#self.shemetype.font_size = common.CONFVIEW.font_size_getter
		#self.shemetype.left_zone = self.sett.add("Отступ слева:", "int", "20")
		#self.shemetype.right_zone = self.sett.add("Отступ справа:", "int", "20")
		
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.sett.updated.connect(self.redraw)



		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("A", "float", "Толщина")
		self.table.addColumn("l", "float", "Длина")
		self.table.addColumn("text", "str", "Текст")
		self.table.addColumn("delta", "bool", "Зазор")
		self.table.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table1.addColumn("mkr", "list", variant=["clean", "+", "-"])
		self.table1.addColumn("mkrT", "str", "Текст")
		self.table1.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("F", "list", variant=["clean", "+", "-"])
		self.table2.addColumn("M", "list", variant=["clean", "+", "-"])
		self.table2.addColumn("Mkr", "list", variant=["clean", "+", "-"])
		self.table2.addColumn("T", "str", "Текст")
		self.table2.updateTable()

		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Распределенные силы:"))
		self.vlayout.addWidget(self.table1)
		self.vlayout.addWidget(QLabel("Локальные силы:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)
		self.table1.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)



		self.setLayout(self.vlayout)

	def add_action(self):
		self.sections().append(self.sect())
		self.sectforces().append(self.sectforce())
		self.bsections().append(self.betsect())
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def del_action(self):
		if len(self.sections()) == 1:
			return

		del self.sections()[-1]
		del self.sectforces()[-1]
		del self.bsections()[-1]
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def inittask(self):
		return {}

class PaintWidget_T0(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()

	def paintEventImplementation(self, ev):
		"""Рисуем сцену согласно объекта задания"""

		lwidth = self.shemetype.lwidth.get()

		axis = self.shemetype.axis.get()
		zleft = self.shemetype.zleft.get()
		zright = self.shemetype.zright.get()

		base_section_height = self.shemetype.base_section_height.get()
		arrow_size = self.shemetype.arrow_size.get()
		arrow_head_size = self.shemetype.arrow_size.get()
		font_size = self.shemetype.font_size.get()
		razm = self.shemetype.razm.get()

		task = self.shemetype.task
		size = self.size()

		width = size.width()
		height = size.height()

		hcenter = height/2

		height_zone = base_section_height

		strt_width = 30
		fini_width = width-30


		painter = QPainter(self)
		font = painter.font()
		font.setItalic(True)
		font.setPointSize(font_size)
		painter.setFont(font)

		br = QPen()
		br.setWidth(lwidth)
		painter.setPen(br)


		maxl = 0
		maxA = 0
		for s in self.sections():
			if s.l > maxl: maxl = s.l
			if s.A > maxA: maxA = s.A

		dimlines_level = hcenter + base_section_height*math.sqrt(maxA)/2 + self.shemetype.dimlines_start_step.get()
		if razm is True:
			hcenter -= self.shemetype.dimlines_start_step.get() / 2 

		if razm is False:
			pass

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
			return math.sqrt(task["sections"][i].A) * height_zone / 2

		def msectrad(i):
			leftA = 0 if i == 0 else math.sqrt(task["sections"][i-1].A)
			rightA = 0 if i == -1 + len(task["betsect"]) else math.sqrt(task["sections"][i].A)
			return max(leftA, rightA) * height_zone / 2

		def msectrad2(i):
			leftA = 0 if i == 0 else math.sqrt(task["sections"][i-1].A)
			rightA = 0 if i == -1 + len(task["betsect"]) else math.sqrt(task["sections"][i].A)
			rm = False
			lm = task["sectforce"][i-1].mkr != "clean"
			
			if i != len(task["sectforce"]):
				rm = task["sectforce"][i].mkr != "clean"
			
			ret = max(leftA, rightA) * height_zone / 2

			if ((max(leftA, rightA) == leftA and lm)
				or
				(max(leftA, rightA) == rightA and rm)):
				ret += 20

			return ret
		
		# Отрисовка секций
		for i in range(len(task["sections"])):
			hkoeff = math.sqrt(task["sections"][i].A)

			strt_height = hcenter - height_zone*hkoeff/2
			fini_height = hcenter + height_zone*hkoeff/2

			A = task["sections"][i].A
			l = task["sections"][i].l

			if not task["sections"][i].delta:
				if abs(float(A) - int(A)) < 0.0001:
					text_A = "{}A".format(int(task["sections"][i].A+0.1)) if task["sections"][i].A != 1 else "A"
				else:
					text_A = str(float(A)) + "A"
	
				if abs(float(l) - int(l)) < 0.0001:
					text_l = "{}l".format(int(task["sections"][i].l+0.1)) if task["sections"][i].l != 1 else "l"
				else:
					text_l = str(float(l)) + "l"
			else: 
				text_l = ""
				text_A = ""

			text_l = paintool.greek(text_l)
			text_A = paintool.greek(text_A)

			if not task["sections"][i].delta:
				painter.drawRect(wsect(i), strt_height, wsect(i+1)-wsect(i), fini_height-strt_height)

			lW = QFontMetrics(font).width(text_l)
			AW = QFontMetrics(font).width(text_A)

			if task["sections"][i].text == "":
				text = "{}, {}".format(text_l, text_A)
			else:
				text = task["sections"][i].text

			if razm:
				painter.setPen(self.halfpen)
				paintool.dimlines(painter, QPoint(wsect(i), fini_height), QPoint(wsect(i+1), fini_height), dimlines_level)
				paintool.draw_text_centered(painter, QPoint((wsect(i)+wsect(i+1))/2, dimlines_level-5), text, self.font)

				painter.setBrush(self.default_brush)
				painter.setPen(self.default_pen)
		
		#Отрисовка граничных эффектов
		for i in range(len(task["betsect"])):
			if task["betsect"][i].F == "+":
				paintool.right_arrow(painter, QPoint(wsect(i), hcenter), arrow_size, arrow_head_size)

			if task["betsect"][i].F == "-":
				paintool.left_arrow(painter, QPoint(wsect(i), hcenter), arrow_size, arrow_head_size)

			if task["betsect"][i].M == "+":
				paintool.circular_arrow_base(painter, paintool.radrect(QPoint(wsect(i), hcenter), 20), False)

			if task["betsect"][i].M == "-":
				paintool.circular_arrow_base(painter, paintool.radrect(QPoint(wsect(i), hcenter), 20), True)

			if task["betsect"][i].Mkr == "+":
				paintool.kr_arrow(painter, QPoint(wsect(i), hcenter), msectrad2(i)+10, 11, False)

			if task["betsect"][i].Mkr == "-":
				paintool.kr_arrow(painter, QPoint(wsect(i), hcenter), msectrad2(i)+10, 11, True)

			if task["betsect"][i].T != "":
				leftA = 0 if i == 0 else math.sqrt(task["sections"][i-1].A)
				rightA = 0 if i == -1 + len(task["betsect"]) else math.sqrt(task["sections"][i].A)
				
				size = QFontMetrics(font).width(task["betsect"][i].T)
				text = task["betsect"][i].T


				if task["betsect"][i].Mkr == "clean":
					paintool.placedtext(painter,
						QPoint(wsect(i), hcenter), 
						max(leftA, rightA) * height_zone / 2 + 10, 
						size, 
						text,
						right = task["betsect"][i].M == 2)

				else:
					painter.drawText(QPoint(
						wsect(i) + 14, 
						hcenter - msectrad2(i)-14), text)

		# Отрисовка распределённых нагрузок:
		for i in range(len(task["sectforce"])):
			hkoeff = math.sqrt(task["sections"][i].A)

			strt_height = hcenter - height_zone*hkoeff/2
			fini_height = hcenter + height_zone*hkoeff/2

			xa = wsect(i)
			xb = wsect(i+1)

			if task["sectforce"][i].mkr == "clean":
				continue

			if task["sectforce"][i].mkr == "+":
				tp = True
			else:
				tp = False

			step = 15
			alen = 15
			rad = 10

			paintool.raspred_torsion(painter=painter,
				apnt=QPointF(xa, strt_height),
				bpnt=QPointF(xb, strt_height),
				alen=-alen,
				rad=rad,
				step=step,
				tp = tp)

			paintool.raspred_torsion(painter=painter,
				apnt=QPointF(xa, fini_height),
				bpnt=QPointF(xb, fini_height),
				alen=alen,
				step=step,
				rad=rad,
				tp = not tp)

			if task["sectforce"][i].mkrT:
				painter.drawText(QPointF((xa+xb)/2, strt_height - 3 - alen - rad), 
					task["sectforce"][i].mkrT)


		if zleft:
			y = math.sqrt(task["sections"][0].A) * height_zone
			paintool.zadelka(painter, wsect(0) - 10, wsect(0), hcenter-y, hcenter+y, left_border=False, right_border=True)

		if zright:
			y = math.sqrt(task["sections"][-1].A) * height_zone
			paintool.zadelka(painter, wsect(-1), wsect(-1) + 10, hcenter-y, hcenter+y, left_border=True, right_border=False)


		if axis:
			pen = QPen(Qt.CustomDashLine)
			pen.setDashPattern([10,3,1,3])
			painter.setPen(pen)
			painter.drawLine(QPoint(5, hcenter), QPoint(width - 5, hcenter))
			pen = QPen()
			painter.setPen(pen)