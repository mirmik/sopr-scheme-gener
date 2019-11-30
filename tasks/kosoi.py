import common
import paintwdg
import numpy
import math

from paintool import deg
import paintool
import taskconf_menu
import util
import elements
import tablewidget
import sections

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Внецентренный изгиб")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())


class ConfWidget(common.ConfWidget):
	"""Виджет настроек задачи T0"""
	class sect:
		def __init__(self, Fx="нет", Fy="нет", Fz="нет", Fx_txt="", Fy_txt="", Fz_txt="", Fx_txt_alttxt=False, Fy_txt_alttxt=False, Fz_txt_alttxt=False):
			self.Fx = Fx
			self.Fy = Fy
			self.Fz = Fz

			self.Fx_txt = Fx_txt
			self.Fy_txt = Fy_txt
			self.Fz_txt = Fz_txt

			self.Fx_txt_alttxt = Fx_txt_alttxt
			self.Fy_txt_alttxt = Fy_txt_alttxt
			self.Fz_txt_alttxt = Fz_txt_alttxt

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(),
				self.sect(),
				self.sect(),
				self.sect(),
				self.sect(),
				self.sect(),
				self.sect(),
				self.sect(),
			],
			#"betsect":
			#[
			#	self.betsect(),
			#	self.betsect(),
			#	self.betsect(sharn="2"),
			#	self.betsect()
			#],
			#"sectforce":
			#[
			#	self.sectforce(),
			#	self.sectforce(),
			#	self.sectforce(Fr="+", FrT="ql")
			#]
		}
		

	def __init__(self, sheme):
		super().__init__(sheme)
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		#self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")

		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.x = self.sett.add("x:", "int", "200")
		self.shemetype.y = self.sett.add("y:", "int", "100")
		self.shemetype.x_txt = self.sett.add("x_txt:", "str", "размер_x")
		self.shemetype.y_txt = self.sett.add("y_txt:", "str", "размер_y")
		self.shemetype.l_txt = self.sett.add("l_txt:", "str", "длина")
		self.shemetype.axonom = self.sett.add("Аксонометрия:", "bool", False)
		self.shemetype.axonom_deg = self.sett.add("60 градусов:", "bool", True)
	
		self.shemetype.section_type = self.sett.add("Тип сечения:", "list", 
			defval=0,
			variant=["прямоугольник", "круг", "ромб"])

		self.shemetype.console = self.sett.add("Длина Консоли:", "int", "100")
		self.shemetype.zrot = self.sett.add("Направление:", "int", "30")
		self.shemetype.xrot = self.sett.add("Подъём:", "int", "30")
		self.shemetype.L = self.sett.add("Длина:", "int", "600")
		self.shemetype.offdown = self.sett.add("Вынос разм. линий:", "int", "100")
		self.shemetype.arrlen = self.sett.add("Длина Стрелок:", "int", "60")
#		self.shemetype.axis = self.sett.add("Нарисовать ось:", "bool", True)
#		self.shemetype.zleft = self.sett.add("Разрез слева:", "bool", True)
#		self.shemetype.zright = self.sett.add("Разрез справа:", "bool", True)
#		self.shemetype.kamera = self.sett.add("Внешняя камера:", "bool", False)
#		self.shemetype.inkamera = self.sett.add("Внутренняя камера:", "bool", False)
#		self.shemetype.inkamera_dist = self.sett.add("Отступ до камеры:", "int", "30")
		#		self.shemetype.razm = self.sett.add("Размерные линии:", "bool", True)

		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		#self.shemetype.base_section_height = self.sett.add("Базовая высота секции:", "int", "6")
		#self.shemetype.leftterm = self.sett.add("Закрепление:", "list", 1, variant=["", "слева", "справа"])
		#self.shemetype.sharnterm = self.sett.add("Закрепление заделка/шарнир:", "bool", True)
				
		#self.shemetype.section_enable = self.sett.add("Отображение сечения:", "bool", True)
#		self.shemetype.section_txt0 = self.sett.add("Сечение.Текст1:", "str", "D")
#		self.shemetype.section_txt1 = self.sett.add("Сечение.Текст2:", "str", "d")
#		self.shemetype.section_txt2 = self.sett.add("Сечение.Текст3:", "str", "d")

#		self.shemetype.section_arg0 = self.sett.add("Сечение.Аргумент1:", "int", "60")
#		self.shemetype.section_arg1 = self.sett.add("Сечение.Аргумент2:", "int", "50")
#		self.shemetype.section_arg2 = self.sett.add("Сечение.Аргумент3:", "int", "10")
		

		#self.shemetype.arrow_line_size = self.sett.add("Размер линии стрелки:", "int", "20")
		#self.shemetype.dimlines_start_step = self.sett.add("Отступ размерных линий:", "int", "40")
		#self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "15")
		#self.shemetype.font_size = common.CONFVIEW.font_size_getter
#		self.shemetype.left_zone = self.sett.add("Отступ слева:", "int", "20")
#		self.shemetype.right_zone = self.sett.add("Отступ справа:", "int", "20")
		
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.sett.updated.connect(self.redraw)



		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("Fx", "list", variant=["нет", "слева +", "слева -", "справа +", "справа -"])
		self.table.addColumn("Fx_txt", "str")
		self.table.addColumn("Fx_txt_alttxt", "bool")
		self.table.addColumn("Fy", "list", variant=["нет", "сверху +", "сверху -", "снизу +", "снизу -"])
		self.table.addColumn("Fy_txt", "str")
		self.table.addColumn("Fy_txt_alttxt", "bool")
		self.table.addColumn("Fz", "list", variant=["нет", "+", "-"])
		self.table.addColumn("Fz_txt", "str")
		self.table.addColumn("Fz_txt_alttxt", "bool")
#		self.table.addColumn("dtext", "str", "Текст")
		#self.table.addColumn("l", "float", "Длина")
		#self.table.addColumn("delta", "float", "Зазор")
		self.table.updateTable()

		#self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		#self.table2.addColumn("sectname", "str", "Имя")
		#self.table2.addColumn("sharn", "list", "Шарн.", variant=["", "1", "2"])
		#self.table2.addColumn("xF", "list", variant=["нет", "+", "-"])
		#self.table2.addColumn("xFtxt", "str", "xF")
		#self.table2.addColumn("yF", "list", variant=["нет", "+", "-"])
		#self.table2.addColumn("yFtxt", "str", "yF")

		#self.table2.addColumn("xM", "list", variant=["нет", "+", "-"])
		#self.table2.addColumn("xMtxt", "str", "xM")
		#self.table2.addColumn("yM", "list", variant=["нет", "+", "-"])
		#self.table2.addColumn("yMtxt", "str", "yM")
		#self.table2.addColumn("M", "list", variant=["clean", "+", "-"])
#		self.table2.addColumn("Mkr", "list", variant=["clean", "+", "-"])
		#self.table2.addColumn("FT", "str", "Текст")
		#self.table2.addColumn("MT", "str", "Текст")
		#self.table2.updateTable()

		#self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		#self.table1.addColumn("Fr", "list", variant=["clean", "+", "-"])
		#self.table1.addColumn("FrT", "str", "Текст")
		#self.table1.updateTable()

		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		#self.vlayout.addWidget(QLabel("Локальные силы:"))
		#self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)


		self.table.updated.connect(self.redraw)
		#self.table1.updated.connect(self.redraw)
		#self.table2.updated.connect(self.redraw)


		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		self.vlayout.addWidget(self.shemetype.texteditor)

		self.setLayout(self.vlayout)

	def add_action(self):
		pass
#		self.sections().append(self.sect())
#		self.shemetype.task["sectforce"].append(self.sectforce())
		#self.shemetype.task["betsect"].append(self.betsect())
#		self.redraw()
#		self.table.updateTable()
#		self.table1.updateTable()
#		self.table2.updateTable()

	def del_action(self):
		pass
#		if len(self.sections()) == 1:
#			return

#		del self.sections()[-1]
		#del self.shemetype.task["betsect"][-1]
#		del self.shemetype.task["sectforce"][-1]
#		self.redraw()
#		self.table.updateTable()
#		self.table1.updateTable()
		#self.table2.updateTable()

	def inittask(self):
		return {}

class PaintWidget(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()
		self.AXDEG = 0.5

	def init_trans_matrix(self):
		t = numpy.matrix([
			[1,0,0,self.base_x],
			[0,1,0,0],
			[0,0,1,self.base_y],
			[0,0,0,1]
		])

		a=self.zrot
		m0 = numpy.matrix([
			[math.cos(a),-math.sin(a),0,0],
			[math.sin(a),math.cos(a),0,0],
			[0,0,1,0],
			[0,0,0,1]
		])

		b=self.xrot
		m1 = numpy.matrix([
			[1,0,0,0],
			[0,math.cos(b),-math.sin(b),0],
			[0,math.sin(b),math.cos(b),0],
			[0,0,0,1]
		])
		
		self.trans_matrix = t * m1 * m0


	def trans(self,x,y,z):
		if self.axonom:
			p = self.trans_matrix * numpy.array([[x],[y],[-z],[1]])
			return QPoint(p[0], p[2])
		else:
			if self.axonom_deg:
				return QPoint(self.base_x-y*math.cos(deg(60))+x, self.base_y+y*math.sin(deg(60))-z)

			p = self.trans_matrix * numpy.array([[0],[y],[0],[1]])
			return QPoint(p[0]+x, p[2]-z)

	def paintEventImplementation(self, ev):
		greek = paintool.greek
		trans = self.trans
		self.axonom = deg(self.shemetype.axonom.get())
		self.axonom_deg = deg(self.shemetype.axonom_deg.get())
		self.zrot = deg(self.shemetype.zrot.get())
		self.xrot = deg(self.shemetype.xrot.get())
		stlen = self.shemetype.L.get()
		offdown = self.shemetype.offdown.get()
		arrlen = self.shemetype.arrlen.get()
		marrlen = arrlen /2 
		arrow_size = 14

		#stlen = 600

		fini_width = self.width() - 20
		hcenter = self.height() / 2

		lwidth = self.shemetype.lwidth.get()

		L = self.shemetype.console.get()
		a = self.shemetype.x.get()
		b = self.shemetype.y.get()
		S = 25
		dimoff = offdown
		
		self.base_x = 0
		self.base_y = 0
		self.init_trans_matrix()

		self.base_x = self.width() / 2 - trans(0,-L,0).x() / 2
		self.base_y = self.height() / 2 - trans(0,-L,0).y() / 2 - offdown/8*3
		self.init_trans_matrix()

		refpoints=[]
		if self.shemetype.section_type.get() == "прямоугольник":
			self.painter.setBrush(QColor(220,220,220))
			self.painter.setPen(Qt.NoPen)
			self.painter.drawPolygon(QPolygon([
				trans(-a/2-S,-L,-b/2-S),
				trans(-a/2-S,-L,b/2+S),
				trans(a/2+S,-L,b/2+S),
				trans(a/2+S,-L,-b/2-S),
			]))

			self.painter.setBrush(Qt.white)
			self.painter.setPen(self.pen)
			self.painter.drawPolygon(QPolygon([
				trans(-a/2,0,-b/2),
				trans(-a/2,0,b/2),
				trans(a/2,0,b/2),
				trans(a/2,0,-b/2),
			]))

			self.painter.drawPolygon(QPolygon([
				trans(-a/2,0,b/2),
				trans(-a/2,-L,b/2),
				trans(a/2,-L,b/2),
				trans(a/2,0,b/2),
			]))

			self.painter.drawPolygon(QPolygon([
				trans(a/2,0,b/2),
				trans(a/2,-L,b/2),
				trans(a/2,-L,-b/2),
				trans(a/2,0,-b/2),
			]))

			self.painter.setPen(self.halfpen)
			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(-a/2,0,-b/2), 
				bpnt=trans(-a/2,0,b/2), 
				offset= QPoint(-dimoff, 0), 
				textoff = QPoint(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)


			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,0,-b/2), 
				bpnt=trans(-a/2,0,-b/2), 
				offset= QPoint(0,dimoff), 
				textoff = QPoint(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,-L,-b/2), 
				bpnt=trans(a/2,0,-b/2), 
				offset= QPoint(dimoff*0.7,dimoff*0.7), 
				textoff = QPoint(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(-a/2,0,-b/2)+QPoint(-dimoff, 0), 
				fini=trans(-a/2,0,b/2)+QPoint(-dimoff, 0), 
				txt=greek(self.shemetype.y_txt.get()), 
				alttxt=False, 
				off=10, 
				polka=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(-a/2,0,-b/2)+QPoint(0,dimoff), 
				fini=trans(a/2,0,-b/2)+QPoint(0,dimoff), 
				txt=greek(self.shemetype.x_txt.get()), 
				alttxt=True, 
				off=14, 
				polka=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(a/2,-L,-b/2)+QPoint(dimoff*0.7,dimoff*0.7), 
				fini=trans(a/2,0,-b/2)+QPoint(dimoff*0.7,dimoff*0.7), 
				txt=greek(self.shemetype.l_txt.get()), 
				alttxt=True, 
				off=14, 
				polka=None)

			self.painter.setPen(self.axpen)
			self.painter.drawLine(
				trans(-a/2-S,0,0),
				trans(a/2+S,0,0)
			)
			self.painter.drawLine(
				trans(0,0,-b/2-S),
				trans(0,0,b/2+S)
			)

			refpoints = [
				trans(-a/2, 0, b/2),
				trans(0, 0, b/2),
				trans(a/2, 0, b/2),
				trans(-a/2, 0, 0),
				trans(a/2, 0, 0),
				trans(-a/2, 0, -b/2),
				trans(0, 0, -b/2),
				trans(a/2, 0, -b/2),
			]

		elif self.shemetype.section_type.get() == "ромб":
			self.painter.setBrush(QColor(220,220,220))
			self.painter.setPen(Qt.NoPen)
			self.painter.drawPolygon(QPolygon([
				trans(-a/2-S,-L,-b/2-S),
				trans(-a/2-S,-L,b/2+S),
				trans(a/2+S,-L,b/2+S),
				trans(a/2+S,-L,-b/2-S),
			]))

			self.painter.setBrush(Qt.white)
			self.painter.setPen(self.pen)
			self.painter.drawPolygon(QPolygon([
				trans(-a/2,0,0),
				trans(-a/2,-L,0),
				trans(0,-L,b/2),
				trans(0,0,b/2),
			]))

			self.painter.drawPolygon(QPolygon([
				trans(a/2,0,0),
				trans(a/2,-L,0),
				trans(0,-L,-b/2),
				trans(0,0,-b/2),
			]))

			self.painter.drawPolygon(QPolygon([
				trans(0,0,b/2),
				trans(0,-L,b/2),
				trans(a/2,-L,0),
				trans(a/2,0,0),
			]))

			self.painter.drawPolygon(QPolygon([
				trans(0,0,-b/2),
				trans(-a/2,0,0),
				trans(0,0,b/2),
				trans(a/2,0,0),
			]))

			self.painter.setPen(self.halfpen)
			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(0,0,-b/2), 
				bpnt=trans(0,0,b/2), 
				offset= QPoint(-dimoff-a/2, 0), 
				textoff = QPoint(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,0,0), 
				bpnt=trans(-a/2,0,0), 
				offset= QPoint(0,dimoff+b/2), 
				textoff = QPoint(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,-L,0), 
				bpnt=trans(a/2,0,0), 
				offset= QPoint(dimoff,0), 
				textoff = QPoint(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(0,0,-b/2)+QPoint(-dimoff-a/2, 0), 
				fini=trans(0,0,b/2)+QPoint(-dimoff-a/2, 0), 
				txt=greek(self.shemetype.y_txt.get()), 
				alttxt=False, 
				off=10, 
				polka=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(-a/2,0,0)+QPoint(0,dimoff+b/2), 
				fini=trans(a/2,0,0)+QPoint(0,dimoff+b/2), 
				txt=greek(self.shemetype.x_txt.get()), 
				alttxt=True, 
				off=14, 
				polka=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(a/2,-L,0)+QPoint(dimoff,0), 
				fini=trans(a/2,0,0)+QPoint(dimoff,0), 
				txt=greek(self.shemetype.l_txt.get()), 
				alttxt=True, 
				off=14, 
				polka=None)

			self.painter.setPen(self.axpen)
			self.painter.drawLine(
				trans(-a/2-S,0,0),
				trans(a/2+S,0,0)
			)
			self.painter.drawLine(
				trans(0,0,-b/2-S),
				trans(0,0,b/2+S)
			)

			refpoints = [
				trans(-a/4, 0, b/4),
				trans(0, 0, b/2),
				trans(a/4, 0, b/4),
				trans(-a/2, 0, 0),
				trans(a/2, 0, 0),
				trans(-a/4, 0, -b/4),
				trans(0, 0, -b/2),
				trans(a/4, 0, -b/4),
			]

		elif self.shemetype.section_type.get() == "круг":
			self.painter.setBrush(QColor(220,220,220))
			self.painter.setPen(Qt.NoPen)
			self.painter.drawPolygon(QPolygon([
				trans(-a/2-S,-L,-a/2-S),
				trans(-a/2-S,-L,a/2+S),
				trans(a/2+S,-L,a/2+S),
				trans(a/2+S,-L,-a/2-S),
			]))

			self.painter.setBrush(Qt.white)
			self.painter.setPen(self.pen)
			
			self.painter.drawEllipse(QRect(
				trans(-a/2,-L,-a/2),
				trans(a/2,-L,a/2)
			))

			#self.painter.setBrush(Qt.NoBrush)
			self.painter.setPen(Qt.NoPen)
			self.painter.drawPolygon(QPolygon([
				trans(0,-L,0) - QPoint(a/2*math.sin(deg(60)), a/2*math.cos(deg(60))),
				trans(0,-L,0) + QPoint(a/2*math.sin(deg(60))+1.5, a/2*math.cos(deg(60))+1.5),
				trans(0,0,0) + QPoint(a/2*math.sin(deg(60))+1.5, a/2*math.cos(deg(60))+1.5),
				trans(0,0,0) - QPoint(a/2*math.sin(deg(60)), a/2*math.cos(deg(60))),
			]))
			self.painter.setPen(self.pen)
			self.painter.drawLine(
				trans(0,-L,0) - QPointF(a/2*math.sin(deg(60)), a/2*math.cos(deg(60))),
				trans(0,0,0) - QPointF(a/2*math.sin(deg(60)), a/2*math.cos(deg(60)))
			)
			self.painter.drawLine(
				trans(0,-L,0) + QPointF(a/2*math.sin(deg(60))+1.5, a/2*math.cos(deg(60))+1.5),
				trans(0,0,0) + QPointF(a/2*math.sin(deg(60))+1.5, a/2*math.cos(deg(60))+1.5)
			)

			self.painter.setPen(self.halfpen)
			self.painter.drawLine(trans(a/2,-L,0), trans(a/2,0,0))
			self.painter.drawLine(trans(0,-L,a/2), trans(0,0,a/2))
			self.painter.setPen(self.pen)

			self.painter.drawEllipse(QRect(
				trans(-a/2,0,-a/2),
				trans(a/2,0,a/2)
			))

			self.painter.setPen(self.halfpen)
			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,0,0), 
				bpnt=trans(-a/2,0,0), 
				offset= QPoint(0,dimoff+a/2), 
				textoff = QPoint(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			self.painter.setPen(self.halfpen)
			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,-L,0),
				bpnt=trans(a/2,0,0),
				offset= QPoint(dimoff,0), 
				textoff = QPoint(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)
		
			elements.draw_text_by_points(
				self, 
				strt=trans(-a/2,0,-a/2)+QPoint(0,dimoff), 
				fini=trans(a/2,0,-a/2)+QPoint(0,dimoff), 
				txt=greek(self.shemetype.x_txt.get()), 
				alttxt=True, 
				off=14, 
				polka=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(a/2,-L,0)+QPoint(dimoff,0), 
				fini=trans(a/2,0,0)+QPoint(dimoff,0), 
				txt=greek(self.shemetype.l_txt.get()), 
				alttxt=True, 
				off=14, 
				polka=None)

			self.painter.setPen(self.axpen)
			self.painter.drawLine(
				trans(-a/2-S,0,0),
				trans(a/2+S,0,0)
			)
			self.painter.drawLine(
				trans(0,0,-a/2-S),
				trans(0,0,a/2+S)
			)

			refpoints = [
				trans(-a/2/math.sqrt(2), 0, a/2/math.sqrt(2)),
				trans(0, 0, a/2),
				trans(a/2/math.sqrt(2), 0, a/2/math.sqrt(2)),
				trans(-a/2, 0, 0),
				trans(a/2, 0, 0),
				trans(-a/2/math.sqrt(2), 0, -a/2/math.sqrt(2)),
				trans(0, 0, -a/2),
				trans(a/2/math.sqrt(2), 0, -a/2/math.sqrt(2)),
			]

		def force(apnt, bpnt, txt, alttxt):
			diff = bpnt - apnt
			x = abs(diff.x())
			y = abs(diff.y())
			if y > x:
				offset = 10
			else:
				offset= 14

			self.painter.setPen(self.doublepen)
			paintool.common_arrow(
				self.painter,
				apnt,
				bpnt,
				arrow_size=arrow_size,
			)
			
			elements.draw_text_by_points(
				self,
				apnt,
				bpnt,
				txt=txt,
				off = offset,
				alttxt=alttxt
			)

		arrlen = self.shemetype.arrlen.get()
		for i in range(len(refpoints)):
			self.painter.setPen(self.pen)
			if self.sections()[i].Fx != "нет":
				if self.sections()[i].Fx == "справа +":
					force(
						refpoints[i],
						refpoints[i]+trans(arrlen,0,0)-trans(0,0,0),
						self.sections()[i].Fx_txt,
						self.sections()[i].Fx_txt_alttxt
					)
				
				elif self.sections()[i].Fx == "справа -":
					force(
						refpoints[i]+trans(arrlen,0,0)-trans(0,0,0),
						refpoints[i],
						self.sections()[i].Fx_txt,
						self.sections()[i].Fx_txt_alttxt
					)
				
				elif self.sections()[i].Fx == "слева +":
					force(
						refpoints[i]+trans(-arrlen,0,0)-trans(0,0,0),
						refpoints[i],
						self.sections()[i].Fx_txt,
						self.sections()[i].Fx_txt_alttxt
					)
					
				elif self.sections()[i].Fx == "слева -":
					force(
						refpoints[i],
						refpoints[i]+trans(-arrlen,0,0)-trans(0,0,0),
						self.sections()[i].Fx_txt,
						self.sections()[i].Fx_txt_alttxt
					)

			if self.sections()[i].Fy != "нет":
				if self.sections()[i].Fy == "сверху +":
					force(
						refpoints[i],
						refpoints[i]+trans(0,0,arrlen)-trans(0,0,0),
						self.sections()[i].Fy_txt,
						self.sections()[i].Fy_txt_alttxt
					)
				
				elif self.sections()[i].Fy == "сверху -":
					force(
						refpoints[i]+trans(0,0,arrlen)-trans(0,0,0),
						refpoints[i],
						self.sections()[i].Fy_txt,
						self.sections()[i].Fy_txt_alttxt
					)
				
				elif self.sections()[i].Fy == "снизу +":
					force(
						refpoints[i]+trans(0,0,-arrlen)-trans(0,0,0),
						refpoints[i],
						self.sections()[i].Fy_txt,
						self.sections()[i].Fy_txt_alttxt
					)
					
				elif self.sections()[i].Fy == "снизу -":
					force(
						refpoints[i],
						refpoints[i]+trans(0,0,-arrlen)-trans(0,0,0),
						self.sections()[i].Fy_txt,
						self.sections()[i].Fy_txt_alttxt
					)

			if self.sections()[i].Fz != "нет":
				if self.sections()[i].Fz == "+":
					force(
						refpoints[i]+trans(0,arrlen,0)-trans(0,0,0),
						refpoints[i],
						self.sections()[i].Fz_txt,
						self.sections()[i].Fz_txt_alttxt
					)
				
				elif self.sections()[i].Fy == "-":
					force(
						refpoints[i],
						refpoints[i]+trans(0,arrlen,0)-trans(0,0,0),
						self.sections()[i].Fz_txt,
						self.sections()[i].Fz_txt_alttxt
					)
				
#					self.painter.setPen(self.pen)
#					elements.draw_text_by_points(
#						self,
#							trans(w2+arrlen,coord(i+1),0),
#						trans(w2+arrlen/2,coord(i+1),0),
#						txt=bsects[i].xFtxt, 
#						alttxt=False, off=14, polka=None
#					)

