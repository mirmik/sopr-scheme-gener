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
		def __init__(self, Fx="нет", Fy="нет", Fz="нет", Fx_txt="", Fy_txt="", Fz_txt="", Fx_txt_alttxt="1", Fy_txt_alttxt="1", Fz_txt_alttxt="1"):
			if Fx_txt_alttxt is None: Fx_txt_alttxt = "1"
			if Fy_txt_alttxt is None: Fy_txt_alttxt = "1"
			if Fz_txt_alttxt is None: Fz_txt_alttxt = "1"
			
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

	def update_interface(self):	
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("Fx", "list", variant=["нет", "слева +", "слева -", "справа +", "справа -"])
		self.table.addColumn("Fx_txt", "str")
		self.table.addColumn("Fx_txt_alttxt", "list", variant=["1","2","3","4","5","6"])
		self.table.addColumn("Fy", "list", variant=["нет", "сверху +", "сверху -", "снизу +", "снизу -"])
		self.table.addColumn("Fy_txt", "str")
		self.table.addColumn("Fy_txt_alttxt", "list", variant=["1","2","3","4","5","6"])
		self.table.addColumn("Fz", "list", variant=["нет", "+", "-"])
		self.table.addColumn("Fz_txt", "str")
		self.table.addColumn("Fz_txt_alttxt", "list", variant=["1","2","3","4","5","6"])
		self.table.updateTable()
		self.table.updated.connect(self.redraw)

		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(self.sett)

		self.vlayout.addWidget(self.shemetype.texteditor)
		

	def __init__(self, sheme):
		super().__init__(sheme, noinitbuttons=True)

		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.x = self.sett.add("x:", "int", "200")
		self.shemetype.y = self.sett.add("y:", "int", "100")
		self.shemetype.x_txt = self.sett.add("x_txt:", "str", "размер_x")
		self.shemetype.y_txt = self.sett.add("y_txt:", "str", "размер_y")
		self.shemetype.l_txt = self.sett.add("l_txt:", "str", "длина")
		self.shemetype.axonom = self.sett.add("Аксонометрия:", "bool", False)
		self.shemetype.axonom_deg = self.sett.add("60 градусов:", "bool", True)
	
		self.shemetype.section_type = self.sett.add("Тип сечения:", "list", 
			defval=3,
			variant=["прямоугольник", "круг", "ромб", "труба"])

		self.shemetype.console = self.sett.add("Длина Консоли:", "int", "100")
		self.shemetype.zrot = self.sett.add("Направление:", "int", "30")
		self.shemetype.xrot = self.sett.add("Подъём:", "int", "30")
		self.shemetype.L = self.sett.add("Длина:", "int", "600")
		self.shemetype.offdown = self.sett.add("Вынос разм. линий:", "int", "100")
		self.shemetype.arrlen = self.sett.add("Длина Стрелок:", "int", "60")
		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.sett.updated.connect(self.redraw)

		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)

		self.update_interface()
		self.setLayout(self.vlayout)

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
			return QPointF(float(p[0]), float(p[2]))
		else:
			if self.axonom_deg:
				return QPointF(self.base_x-y*math.cos(deg(60))+x, self.base_y+y*math.sin(deg(60))-z)

			p = self.trans_matrix * numpy.array([[0],[y],[0],[1]])
			return QPointF(float(p[0])+x, float(p[2])-z)

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
		hcenter = self.hcenter

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
		self.base_y = hcenter - trans(0,-L,0).y() / 2 - offdown/8*3
		self.init_trans_matrix()

		refpoints=[]
		if self.shemetype.section_type.get() == "прямоугольник":
			self.painter.setBrush(QColor(220,220,220))
			self.painter.setPen(Qt.NoPen)
			self.painter.drawPolygon(QPolygonF([
				trans(-a/2-S,-L,-b/2-S),
				trans(-a/2-S,-L,b/2+S),
				trans(a/2+S,-L,b/2+S),
				trans(a/2+S,-L,-b/2-S),
			]))

			self.painter.setBrush(Qt.white)
			self.painter.setPen(self.pen)
			self.painter.drawPolygon(QPolygonF([
				trans(-a/2,0,-b/2),
				trans(-a/2,0,b/2),
				trans(a/2,0,b/2),
				trans(a/2,0,-b/2),
			]))

			self.painter.drawPolygon(QPolygonF([
				trans(-a/2,0,b/2),
				trans(-a/2,-L,b/2),
				trans(a/2,-L,b/2),
				trans(a/2,0,b/2),
			]))

			self.painter.drawPolygon(QPolygonF([
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
				offset= QPointF(-dimoff, 0), 
				textoff = QPointF(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)


			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,0,-b/2), 
				bpnt=trans(-a/2,0,-b/2), 
				offset= QPointF(0,dimoff), 
				textoff = QPointF(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,-L,-b/2), 
				bpnt=trans(a/2,0,-b/2), 
				offset= QPointF(dimoff*0.7,dimoff*0.7), 
				textoff = QPointF(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(-a/2,0,-b/2)+QPointF(-dimoff, 0), 
				fini=trans(-a/2,0,b/2)+QPointF(-dimoff, 0), 
				txt=greek(self.shemetype.y_txt.get()), 
				alttxt=False, 
				off=10, 
				polka=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(-a/2,0,-b/2)+QPointF(0,dimoff), 
				fini=trans(a/2,0,-b/2)+QPointF(0,dimoff), 
				txt=greek(self.shemetype.x_txt.get()), 
				alttxt=True, 
				off=14, 
				polka=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(a/2,-L,-b/2)+QPointF(dimoff*0.7,dimoff*0.7), 
				fini=trans(a/2,0,-b/2)+QPointF(dimoff*0.7,dimoff*0.7), 
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
			self.painter.drawPolygon(QPolygonF([
				trans(-a/2-S,-L,-b/2-S),
				trans(-a/2-S,-L,b/2+S),
				trans(a/2+S,-L,b/2+S),
				trans(a/2+S,-L,-b/2-S),
			]))

			self.painter.setBrush(Qt.white)
			self.painter.setPen(self.pen)
			self.painter.drawPolygon(QPolygonF([
				trans(-a/2,0,0),
				trans(-a/2,-L,0),
				trans(0,-L,b/2),
				trans(0,0,b/2),
			]))

			self.painter.drawPolygon(QPolygonF([
				trans(a/2,0,0),
				trans(a/2,-L,0),
				trans(0,-L,-b/2),
				trans(0,0,-b/2),
			]))

			self.painter.drawPolygon(QPolygonF([
				trans(0,0,b/2),
				trans(0,-L,b/2),
				trans(a/2,-L,0),
				trans(a/2,0,0),
			]))

			self.painter.drawPolygon(QPolygonF([
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
				offset= QPointF(-dimoff-a/2, 0), 
				textoff = QPointF(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,0,0), 
				bpnt=trans(-a/2,0,0), 
				offset= QPointF(0,dimoff+b/2), 
				textoff = QPointF(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,-L,0), 
				bpnt=trans(a/2,0,0), 
				offset= QPointF(dimoff,0), 
				textoff = QPointF(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(0,0,-b/2)+QPointF(-dimoff-a/2, 0), 
				fini=trans(0,0,b/2)+QPointF(-dimoff-a/2, 0), 
				txt=greek(self.shemetype.y_txt.get()), 
				alttxt=False, 
				off=10, 
				polka=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(-a/2,0,0)+QPointF(0,dimoff+b/2), 
				fini=trans(a/2,0,0)+QPointF(0,dimoff+b/2), 
				txt=greek(self.shemetype.x_txt.get()), 
				alttxt=True, 
				off=14, 
				polka=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(a/2,-L,0)+QPointF(dimoff,0), 
				fini=trans(a/2,0,0)+QPointF(dimoff,0), 
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
			self.painter.drawPolygon(QPolygonF([
				trans(-a/2-S,-L,-a/2-S),
				trans(-a/2-S,-L,a/2+S),
				trans(a/2+S,-L,a/2+S),
				trans(a/2+S,-L,-a/2-S),
			]))

			self.painter.setBrush(Qt.white)
			self.painter.setPen(self.pen)
			
			self.painter.drawEllipse(QRectF(
				trans(-a/2,-L,-a/2),
				trans(a/2,-L,a/2)
			))

			#self.painter.setBrush(Qt.NoBrush)
			self.painter.setPen(Qt.NoPen)
			self.painter.drawPolygon(QPolygonF([
				trans(0,-L,0) - QPointF(a/2*math.sin(deg(60)), a/2*math.cos(deg(60))),
				trans(0,-L,0) + QPointF(a/2*math.sin(deg(60))+1.5, a/2*math.cos(deg(60))+1.5),
				trans(0,0,0) + QPointF(a/2*math.sin(deg(60))+1.5, a/2*math.cos(deg(60))+1.5),
				trans(0,0,0) - QPointF(a/2*math.sin(deg(60)), a/2*math.cos(deg(60))),
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

			self.painter.drawEllipse(QRectF(
				trans(-a/2,0,-a/2),
				trans(a/2,0,a/2)
			))

			self.painter.setPen(self.halfpen)
			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,0,0), 
				bpnt=trans(-a/2,0,0), 
				offset= QPointF(0,dimoff+a/2), 
				textoff = QPointF(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			self.painter.setPen(self.halfpen)
			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,-L,0),
				bpnt=trans(a/2,0,0),
				offset= QPointF(dimoff,0), 
				textoff = QPointF(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)
		
			elements.draw_text_by_points(
				self, 
				strt=trans(-a/2,0,-a/2)+QPointF(0,dimoff), 
				fini=trans(a/2,0,-a/2)+QPointF(0,dimoff), 
				txt=greek(self.shemetype.x_txt.get()), 
				alttxt=True, 
				off=14, 
				polka=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(a/2,-L,0)+QPointF(dimoff,0), 
				fini=trans(a/2,0,0)+QPointF(dimoff,0), 
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

		elif self.shemetype.section_type.get() == "труба":
			self.painter.setBrush(QColor(220,220,220))
			self.painter.setPen(Qt.NoPen)
			self.painter.drawPolygon(QPolygonF([
				trans(-a/2-S,-L,-a/2-S),
				trans(-a/2-S,-L,a/2+S),
				trans(a/2+S,-L,a/2+S),
				trans(a/2+S,-L,-a/2-S),
			]))

			self.painter.setBrush(Qt.white)
			self.painter.setPen(self.pen)
			
			self.painter.drawEllipse(QRectF(
				trans(-a/2,-L,-a/2),
				trans(a/2,-L,a/2)
			))

			#self.painter.setBrush(Qt.NoBrush)
			self.painter.setPen(Qt.NoPen)
			self.painter.drawPolygon(QPolygonF([
				trans(0,-L,0) - QPointF(a/2*math.sin(deg(60)), a/2*math.cos(deg(60))),
				trans(0,-L,0) + QPointF(a/2*math.sin(deg(60))+1.5, a/2*math.cos(deg(60))+1.5),
				trans(0,0,0) + QPointF(a/2*math.sin(deg(60))+1.5, a/2*math.cos(deg(60))+1.5),
				trans(0,0,0) - QPointF(a/2*math.sin(deg(60)), a/2*math.cos(deg(60))),
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

			self.painter.drawEllipse(QRectF(
				trans(-a/2,0,-a/2),
				trans(a/2,0,a/2)
			))

			self.painter.drawEllipse(QRectF(
				trans(-b/2,0,-b/2),
				trans(b/2,0,b/2)
			))

			self.painter.setPen(self.axpen)
			self.painter.setBrush(Qt.NoBrush)
			self.painter.drawEllipse(QRectF(
				trans(-(a+b)/4,0,-(a+b)/4),
				trans((a+b)/4,0,(a+b)/4)
			))
			self.painter.setPen(self.pen)

			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans((a+b)/4,0,0), 
				bpnt=trans(-(a+b)/4,0,0), 
				offset= QPointF(0,dimoff+a/2), 
				textoff = QPointF(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)

			ar = 67.5
			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2*math.cos(deg(ar)),0,a/2*math.sin(deg(ar))), 
				bpnt=trans(b/2*math.cos(deg(ar)),0,b/2*math.sin(deg(ar))), 
				offset= QPointF(0,0), 
				textoff = (trans(a/2*math.cos(deg(ar)),0,a/2*math.sin(deg(ar))) - trans(b/2*math.cos(deg(ar)),0,b/2*math.sin(deg(ar))))/2 + QPointF(30,-30), 
				text = greek(self.shemetype.y_txt.get()), 
				arrow_size = 12, 
				splashed=True, 
				textline_from="apnt")

			self.painter.setPen(self.halfpen)
			paintool.draw_dimlines(
				painter=self.painter, 
				apnt=trans(a/2,-L,0),
				bpnt=trans(a/2,0,0),
				offset= QPointF(dimoff,0), 
				textoff = QPointF(), 
				text = "", 
				arrow_size = 12, 
				splashed=False, 
				textline_from=None)
		
			elements.draw_text_by_points(
				self, 
				strt=trans(-a/2,0,-a/2)+QPointF(0,dimoff), 
				fini=trans(a/2,0,-a/2)+QPointF(0,dimoff), 
				txt=greek(self.shemetype.x_txt.get()), 
				alttxt=True, 
				off=14, 
				polka=None)

			elements.draw_text_by_points(
				self, 
				strt=trans(a/2,-L,0)+QPointF(dimoff,0), 
				fini=trans(a/2,0,0)+QPointF(dimoff,0), 
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

			a = (a+b)/2
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

		def force(apnt, bpnt, txt, txtpnt_type):
			if txtpnt_type is None or txtpnt_type is True or txtpnt_type is False:
				txtpnt_type = "1"

			diff = bpnt - apnt
			x = abs(diff.x())
			y = abs(diff.y())
			if y > x:
				offset = 10
			else:
				offset= 14
			
			#elements.draw_text_by_points(
			#	self,
			#	apnt,
			#	bpnt,
			#	txt=txt,
			#	off = offset,
			#	alttxt=alttxt
			#)

			print(repr(txtpnt_type))
			print(txtpnt_type.__class__)
			#txtpnt = apnt if apnt.x() < bpnt.x() else bpnt

			if txtpnt_type == "5":
				elements.draw_text_by_points(
					self,
					apnt,
					bpnt,
					txt=txt,
					off = offset,
					alttxt=False
				)
				self.painter.setPen(self.doublepen)
				paintool.common_arrow(
					self.painter,
					apnt,
					bpnt,
					arrow_size=arrow_size,
				)
				self.painter.setPen(self.pen)

				return
			elif txtpnt_type == "6":
				elements.draw_text_by_points(
					self,
					apnt,
					bpnt,
					txt=txt,
					off = offset,
					alttxt=True
				)
				self.painter.setPen(self.doublepen)
				paintool.common_arrow(
					self.painter,
					apnt,
					bpnt,
					arrow_size=arrow_size,
				)
				self.painter.setPen(self.pen)
				return

			txtpnt = None
			if txtpnt_type == "1":
				txtpnt = bpnt + QPointF(7,QFontMetrics(self.font).height()/4)
			elif txtpnt_type == "2":
				txtpnt = bpnt + QPointF(-8-QFontMetrics(self.font).width(txt),QFontMetrics(self.font).height()/4)
			elif txtpnt_type == "3":
				txtpnt = apnt + QPointF(7,QFontMetrics(self.font).height()/4)
			elif txtpnt_type == "4":
				txtpnt = apnt + QPointF(-8-QFontMetrics(self.font).width(txt),QFontMetrics(self.font).height()/4)

			self.painter.setPen(Qt.NoPen)
			self.painter.setBrush(Qt.white)
			self.painter.drawRect(QRectF(
				txtpnt - QPointF(+2,-QFontMetrics(self.font).height()/7), 
				txtpnt + QPointF(+2+QFontMetrics(self.font).width(txt),-QFontMetrics(self.font).height()/3*2)))

			self.painter.setPen(self.pen)

			self.painter.setBrush(Qt.black)
			self.painter.drawText(
				txtpnt,
				txt
			)

			self.painter.setPen(self.doublepen)
			paintool.common_arrow(
				self.painter,
				apnt,
				bpnt,
				arrow_size=arrow_size,
			)
			self.painter.setPen(self.pen)

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
				
				elif self.sections()[i].Fz == "-":
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

