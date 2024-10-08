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
		super().__init__("Косой изгиб")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())


class ConfWidget(common.ConfWidget):
	"""Виджет настроек задачи T0"""
	class sect:
		def __init__(self, l=1, 
			#delta=False
		):
			self.l=l

	class betsect:
		def __init__(self, xF="нет", xFtxt="", yF="нет", yFtxt="",
						xM="нет", xMtxt="", yM="нет", yMtxt="",
						xS="нет", yS="нет", zS="нет"):
			self.xF=xF
			self.yF=yF
			self.xFtxt=xFtxt
			self.yFtxt=yFtxt

			self.xM=xM
			self.yM=yM
			self.xMtxt=xMtxt
			self.yMtxt=yMtxt
			#self.sectname = sectname
			
			self.xS=xS
			self.yS=yS
			self.zS=zS

	class sectforce:
		def __init__(self, xF="нет", xFtxt="", yF="нет", yFtxt=""):
			self.xF = xF
			self.yF = yF
			self.xFtxt = xFtxt
			self.yFtxt = yFtxt
			
	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(l=1),
				self.sect(l=2),
			],
			"betsect":
			[
				self.betsect(),
				self.betsect(),
				self.betsect(),
			],
			"sectforce":
			[
				self.sectforce(),
				self.sectforce(),
			]
		}
		
	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("l", "float", "Длина")
		self.table.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("xF", "list", note="Fx", variant=["нет", "+1", "+2", "-1", "-2"])
		self.table2.addColumn("xFtxt", "str", "Fx")
		self.table2.addColumn("yF", "list", "Fy", variant=["нет", "+1", "+2", "-1", "-2"])
		self.table2.addColumn("yFtxt", "str", "Fy", "yF")

		self.table2.addColumn("xM", "list", "Mx", variant=["нет", "+", "-"])
		self.table2.addColumn("xMtxt", "str", "Mx")
		self.table2.addColumn("yM", "list", "My", variant=["нет", "+", "-"])
		self.table2.addColumn("yMtxt", "str", "My")
		
		self.table2.addColumn("xS", "list", "Sx", variant=["нет", "+1", "-1", "+2", "-2"])
		self.table2.addColumn("yS", "list", "Sy", variant=["нет", "+1", "-1", "+2", "-2"])
		self.table2.addColumn("zS", "list", "Sz", variant=["нет", "+1", "-1", "+2", "-2"])
		self.table2.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table1.addColumn("xF", "list", "Fx", variant=["нет", "+", "-"])
		self.table1.addColumn("xFtxt", "str", "Fx")
		self.table1.addColumn("yF", "list", "Fy", variant=["нет", "+", "-"])
		self.table1.addColumn("yFtxt", "str", "Fy")
		self.table1.updateTable()

		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Локальные силы:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(QLabel("Распределенные силы:"))
		self.vlayout.addWidget(self.table1)
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)
		self.table1.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)
		self.vlayout.addWidget(self.shemetype.texteditor)


	def __init__(self, sheme):
		super().__init__(sheme)
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")

		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.console = self.sett.add("Консоль:", ("bool", "int"), (True, "30"))
		self.shemetype.axonom = self.sett.add("Аксонометрия:", "bool", False)
		self.shemetype.axonom_deg = self.sett.add("45 градусов:", "bool", False)
		self.shemetype.xoffset = self.sett.add("Смещение:", "int", "30")
		self.shemetype.zrot = self.sett.add("Направление:", "int", "30")
		self.shemetype.xrot = self.sett.add("Подъём:", "int", "20")
		self.shemetype.L = self.sett.add("Длина:", "int", "600")
		self.shemetype.offdown = self.sett.add("Вынос разм. линий:", "int", "100")
		self.shemetype.arrlen = self.sett.add("Длина Стрелок:", "int", "60")
		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter

		self.shemetype.section_container = self.sett.add_widget(sections.SectionContainer(None))
		self.shemetype.section_container.updated.connect(self.redraw)

		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "15")
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.sett.updated.connect(self.redraw)

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
		self.AXDEG = 0.5

	def draw_distribload(self, apnt, bpnt, vec, to_from=False, txt=None, alttxt=False):
		trans = self.trans
		apnt = numpy.array(apnt)
		bpnt = numpy.array(bpnt)
		vec = numpy.array(vec)
		self.painter.setPen(self.halfpen)
		self.painter.drawLine(trans(apnt+vec), trans(bpnt+vec))
		self.painter.drawLine(trans(apnt+vec), trans(apnt))
		self.painter.drawLine(trans(bpnt+vec), trans(bpnt))

		diff = bpnt - apnt
		difflen = math.sqrt(diff.dot(diff))

		n = int(difflen / 30)
		step = difflen / n

		for i in range(n+1):
			k = (n - i) / n
			paintool.common_arrow(
				self.painter,
				trans(apnt * k + bpnt * (1-k) + vec),
				trans(apnt * k + bpnt * (1-k)), 
				arrow_size=10)

		elements.draw_text_by_points(
			self,
			trans(apnt + vec),
			trans(bpnt + vec), 
			txt=txt, 
			alttxt=alttxt, off=10
		)

	def draw_sharn(self, pnt, vec, xvec, yvec, brush = Qt.BDiagPattern):
		trans = self.trans
		apnt = trans(pnt)
		bpnt = trans(numpy.array(pnt)+numpy.array(vec))

		c0pnt = trans(numpy.array(pnt)+numpy.array(vec)+numpy.array(xvec))
		c1pnt = trans(numpy.array(pnt)+numpy.array(vec)+numpy.array(xvec)+numpy.array(yvec))
		c2pnt = trans(numpy.array(pnt)+numpy.array(vec)-numpy.array(xvec)+numpy.array(yvec))
		c3pnt = trans(numpy.array(pnt)+numpy.array(vec)-numpy.array(xvec))

		circ0 = paintool.radrect(apnt, 4)
		circ1 = paintool.radrect(bpnt, 4)

		self.painter.setPen(self.pen)
		self.painter.setBrush(Qt.white)
		self.painter.drawLine(apnt, bpnt)

		self.painter.drawLine(c0pnt, c3pnt)
		self.painter.setPen(Qt.NoPen)
		self.painter.setBrush(brush)
		self.painter.drawPolygon(
			QPolygonF([
				c0pnt, c1pnt, c2pnt, c3pnt
			])
		)

		self.painter.setPen(self.pen)
		self.painter.setBrush(Qt.white)
		self.painter.drawEllipse(circ0)
		self.painter.drawEllipse(circ1)
		self.painter.setPen(self.pen)

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


	def trans(self,x,y=None,z=None):
		if y is None:
			x,y,z = x[0], x[1], x[2]
		if self.axonom:
			p = self.trans_matrix * numpy.array([[x],[y],[-z],[1]])
			return QPointF(float(p[0]), float(p[2]))
		else:
			if self.axonom_deg:
				return QPointF(self.base_x-y*self.AXDEG+x, self.base_y+y*self.AXDEG-z)

			p = self.trans_matrix * numpy.array([[0],[y],[0],[1]])
			return QPointF(float(p[0])+x, float(p[2])-z)

	def drawConsole(self):
		L = self.L
		L2 = self.L2
		w = self.shemetype.console.get()[1]
		w2 = 0
		S=20
		
		if not self.shemetype.console.get()[0]:
			return

		self.painter.setPen(self.pen)

		self.painter.setBrush(QColor(220,220,220))		
		self.painter.drawPolygon(QPolygonF([
			self.trans(w,L,-w), self.trans(w,L,w), self.trans(w,0,w), self.trans(w,0,-w), 
		]))
		self.painter.setBrush(Qt.white)

		self.painter.setPen(self.axpen)
		self.painter.drawLine(self.trans(-w-S,L,0), self.trans(w+S,L,0))
		self.painter.drawLine(self.trans(0,L,-w-S), self.trans(0,L,w+S))

		self.painter.setPen(self.pen)
		self.painter.drawLine(self.trans(-w,0,w), self.trans(w,0,w))
		self.painter.drawLine(self.trans(w,0,w), self.trans(w,0,-w))
		
		self.painter.drawLine(self.trans(-w,L,-w), self.trans(-w,L,w))
		self.painter.drawLine(self.trans(-w,L,w), self.trans(w,L,w))
		self.painter.drawLine(self.trans(w,L,w), self.trans(w,L,-w))
		self.painter.drawLine(self.trans(w,L,-w), self.trans(-w,L,-w))

		self.painter.drawLine(self.trans(-w,L,w), self.trans(-w,0,w))
		self.painter.drawLine(self.trans(w,L,w), self.trans(w,0,w))
		self.painter.drawLine(self.trans(w,L,-w), self.trans(w,0,-w))

		self.painter.drawLine(self.trans(-w2,L,w2), self.trans(w2,L,w2))
		self.painter.drawLine(self.trans(w2,L,w2), self.trans(w2,L,-w2))
		
		self.painter.drawLine(self.trans(-w2,L2,-w2), self.trans(-w2,L2,w2))
		self.painter.drawLine(self.trans(-w2,L2,w2), self.trans(w2,L2,w2))
		self.painter.drawLine(self.trans(w2,L2,w2), self.trans(w2,L2,-w2))
		self.painter.drawLine(self.trans(w2,L2,-w2), self.trans(-w2,L2,-w2))

		self.painter.drawLine(self.trans(-w2,L2,w2), self.trans(-w2,L,w2))
		self.painter.drawLine(self.trans(w2,L2,w2), self.trans(w2,L,w2))
		self.painter.drawLine(self.trans(w2,L2,-w2), self.trans(w2,L,-w2))

		self.painter.setBrush(Qt.white)
		self.painter.drawPolygon(QPolygonF([
			self.trans(-w2,L2,w2), self.trans(w2,L2,w2), self.trans(w2,L,w2), self.trans(-w2,L,w2), 
		]))

		self.painter.setBrush(QColor(220,220,220))
		self.painter.drawPolygon(QPolygonF([
			self.trans(w2,L2,-w2), self.trans(w2,L2,w2), self.trans(w2,L,w2), self.trans(w2,L,-w2), 
		]))


	def paintEventImplementation(self, ev):
		bsects = self.bsections()
		sforces = self.sectforces()
		moff = 40
		"""Рисуем сцену согласно объекта задания"""

		#if self.shemetype.width_getter != "600":
		#	self.shemetype.width_getter.set("600")
			#common.CONFVIEW.update_after.emit()
		#	e = QResizeEvent(QSize(20,20), common.PAINT_CONTAINER.size());
		#	QApplication.postEvent(common.PAINT_CONTAINER, e);
		#	self.painter.end()

		#	return
		self.axonom = deg(self.shemetype.axonom.get())
		self.axonom_deg = deg(self.shemetype.axonom_deg.get())
		self.zrot = deg(self.shemetype.zrot.get())
		self.xrot = deg(self.shemetype.xrot.get())
		stlen = self.shemetype.L.get()
		offdown = self.shemetype.offdown.get()
		arrlen = self.shemetype.arrlen.get()
		marrlen = arrlen /2 
		arrow_size = 18

		#stlen = 600

		fini_width = self.width() - 20
		hcenter = self.height() / 2

		lwidth = self.shemetype.lwidth.get()

		section_width = sections.draw_section_routine(
			self, 
			hcenter=hcenter, 
			right=fini_width)

		right_zone  = fini_width - section_width + self.shemetype.xoffset.get()

		if not self.axonom or not self.axonom_deg:
			SIN = math.sin(self.zrot)
		else:
			SIN = self.AXDEG

		self.base_x = right_zone / 2 + SIN * stlen / 2
		self.base_y = 40 + 40
		self.init_trans_matrix()

		self.painter.setPen(self.pen)
		trans = self.trans

		L = 20
		L2 = L + stlen
		self.L = L
		self.L2 = L2

		lsum = 0
		for s in self.sections():
			lsum+=s.l

		lkoeff = stlen / lsum

		def coord(sectno):
			l = 0
			for i in range(sectno):
				l += self.sections()[i].l

			return L + lkoeff * l

		w2 = 0

		# Draw console root
		self.drawConsole()
		


		off = QPointF(0,offdown)
		self.painter.setPen(self.halfpen)
		for i in range(len(self.sections())):
			paintool.draw_dimlines(
				painter=self.painter, 
				apnt = trans(0,coord(i),0), 
				bpnt = trans(0,coord(i+1),0), 
				offset = off, 
				textoff = QPointF(0,0), 
				text = "", 
				arrow_size=10, 
				splashed=False, 
				textline_from=None)

			elements.draw_text_by_points(
				self, 
				strt = trans(0,coord(i),0) + off, 
				fini = trans(0,coord(i+1),0) + off, 
				txt=util.text_prepare_ltext(self.sections()[i].l, suffix="l"), 
				alttxt=True, 
				off=10)

		for i in range(len(self.sections())+1):
			self.painter.setPen(self.doublepen)
			if bsects[i].xF != "нет":
				if bsects[i].xF == "+1":
					paintool.common_arrow(
						self.painter,
						trans(-w2-arrlen,coord(i),0),
						trans(-w2,coord(i),0),
						arrow_size=arrow_size
					)

					self.painter.setPen(self.pen)
					elements.draw_text_by_points(
						self,
						trans(-w2-arrlen/2,coord(i),0),
						trans(-w2-arrlen,coord(i),0),
						txt=bsects[i].xFtxt, 
						alttxt=False, off=14, polka=None
					)
				
				if bsects[i].xF == "+2":
					paintool.common_arrow(
						self.painter,
						trans(-w2,coord(i),0),
						trans(-w2+arrlen,coord(i),0),
						arrow_size=arrow_size
					)

					self.painter.setPen(self.pen)
					elements.draw_text_by_points(
						self,
						trans(-w2+arrlen/2,coord(i),0),
						trans(-w2+arrlen,coord(i),0),
						txt=bsects[i].xFtxt, 
						alttxt=False, off=14, polka=None
					)

				if bsects[i].xF == "-1":
					paintool.common_arrow(
						self.painter,
						trans(w2+arrlen,coord(i),0),
						trans(w2,coord(i),0),
						arrow_size=arrow_size,
					)

					self.painter.setPen(self.pen)
					elements.draw_text_by_points(self,
						trans(w2+arrlen/2,coord(i),0),
						trans(w2+arrlen,coord(i),0),
						txt=paintool.greek(bsects[i].xFtxt), 
						alttxt=False, off=14, polka=None
					)

				if bsects[i].xF == "-2":
					paintool.common_arrow(
						self.painter,
						trans(w2,coord(i),0),
						trans(w2-arrlen,coord(i),0),
						arrow_size=arrow_size,
					)

					self.painter.setPen(self.pen)
					elements.draw_text_by_points(self,
						trans(w2-arrlen/2,coord(i),0),
						trans(w2-arrlen,coord(i),0),
						txt=paintool.greek(bsects[i].xFtxt), 
						alttxt=False, off=14, polka=None
					)


	
			self.painter.setPen(self.doublepen)
			if bsects[i].yF != "нет":
				if bsects[i].yF == "+1":
					paintool.common_arrow(
						self.painter,
						trans(0,coord(i),-w2-arrlen),
						trans(0,coord(i),-w2),
						arrow_size=arrow_size
					)
					
					self.painter.setPen(self.pen)
					elements.draw_text_by_points(
						self,
						trans(0,coord(i),-w2-arrlen),
						trans(0,coord(i),-w2-arrlen/2),
						txt=bsects[i].yFtxt, 
						alttxt=False, off=10, polka=None
					)

				if bsects[i].yF == "+2":
					paintool.common_arrow(
						self.painter,
						trans(0,coord(i),-w2),
						trans(0,coord(i),-w2+arrlen),
						arrow_size=arrow_size
					)
					
					self.painter.setPen(self.pen)
					elements.draw_text_by_points(
						self,
						trans(0,coord(i),-w2+arrlen),
						trans(0,coord(i),-w2+arrlen/2),
						txt=bsects[i].yFtxt, 
						alttxt=False, off=10, polka=None
					)

				if bsects[i].yF == "-1":
					paintool.common_arrow(
						self.painter,
						trans(0,coord(i),w2+arrlen),
						trans(0,coord(i),w2),
						arrow_size=arrow_size
					)

					self.painter.setPen(self.pen)
					elements.draw_text_by_points(
						self,
						trans(0,coord(i),w2+arrlen),
						trans(0,coord(i),w2+arrlen/2),
						txt=paintool.greek(bsects[i].yFtxt), 
						alttxt=False, off=10, polka=None
					)

				if bsects[i].yF == "-2":
					paintool.common_arrow(
						self.painter,
						trans(0,coord(i),w2),
						trans(0,coord(i),w2-arrlen),
						arrow_size=arrow_size
					)

					self.painter.setPen(self.pen)
					elements.draw_text_by_points(
						self,
						trans(0,coord(i),w2-arrlen),
						trans(0,coord(i),w2-arrlen/2),
						txt=paintool.greek(bsects[i].yFtxt), 
						alttxt=False, off=10, polka=None
					)

			self.painter.setPen(self.pen)
			if bsects[i].yM != "нет":
				if bsects[i].yM == "-":
					off = -moff
					alttxt = True
				else:
					off = moff
					alttxt = False

				if i == len(bsects)-1:
					ws = 0
				else:
					ws = -w2

				self.painter.drawLine(
					trans(ws,coord(i),0),
					trans(-w2-marrlen,coord(i),0)
					)
				paintool.common_arrow(
					self.painter,
					trans(-w2-marrlen,coord(i),0),
					trans(-w2-marrlen,coord(i)+off,0),
					arrow_size=arrow_size,
				)
				self.painter.setPen(self.pen)
				elements.draw_text_by_points(
					self,
					trans(-w2-marrlen,coord(i),0),
					trans(-w2-marrlen,coord(i)+off,0),
					txt=paintool.greek(bsects[i].yMtxt), 
					alttxt=alttxt, off=14, polka=None
				)

			self.painter.setPen(self.pen)
			if bsects[i].xM != "нет":
				if bsects[i].xM == "-":
					off = moff
					alttxt = True
				else:
					off = -moff
					alttxt = False

				if i == len(bsects)-1:
					ws = 0
				else:
					ws = w2

				self.painter.drawLine(
					trans(0,coord(i),-ws),
					trans(0,coord(i),-w2-marrlen)
					)
				paintool.common_arrow(
					self.painter,
					trans(0,coord(i),-w2-marrlen),
					trans(0,coord(i)+off,-w2-marrlen),
					arrow_size=arrow_size,
				)
				self.painter.setPen(self.pen)
				elements.draw_text_by_points(
					self,
					trans(0,coord(i),w2+marrlen),
					trans(0,coord(i)-off,+w2+marrlen),
					txt=paintool.greek(bsects[i].xMtxt), 
					alttxt=alttxt, off=14, polka=None
				)

		self.painter.setPen(self.doublepen)
		self.painter.drawLine(
			trans(0,L,0),
			trans(0,L2,0),
		)

		for i in range(len(self.sections())+1):
#			self.painter.setPen(self.doublepen)
			#if bsects[i].xF != "нет":
				
#			self.painter.setPen(self.doublepen)
#			if bsects[i].yF != "нет":
	


			self.painter.setPen(self.pen)
			if bsects[i].yM != "нет":
				if bsects[i].yM == "-":
					off = moff
				else:
					off = -moff

				if i == len(bsects)-1:
					ws = 0
				else:
					ws = w2

				self.painter.drawLine(
					trans(ws,coord(i),0),
					trans(w2+marrlen,coord(i),0)
					)
				paintool.common_arrow(
					self.painter,
					trans(w2+marrlen,coord(i),0),
					trans(w2+marrlen,coord(i)+off,0),
					arrow_size=arrow_size,
				)

			self.painter.setPen(self.pen)
			if bsects[i].xM != "нет":
				if bsects[i].xM == "-":
					off = -moff
				else:
					off = moff

				if i == len(bsects)-1:
					ws = 0
				else:
					ws = w2

				self.painter.drawLine(
					trans(0,coord(i),ws),
					trans(0,coord(i),w2+marrlen)
					)
				paintool.common_arrow(
					self.painter,
					trans(0,coord(i),w2+marrlen),
					trans(0,coord(i)+off,w2+marrlen),
					arrow_size=arrow_size,
				)
				self.painter.setPen(self.pen)

	#			self.painter.setPen(self.pen)
	#			elements.draw_text_by_points(
	#				self,
	#						trans(w2+arrlen,coord(i+1),0),
	#					trans(w2+arrlen/2,coord(i+1),0),
	#					txt=bsects[i].xFtxt, 
	#					alttxt=False, off=14, polka=None
	#				)


		darrlen = 40
		for i in range(len(self.sections())):
			self.painter.setPen(self.doublepen)
			if sforces[i].xF != "нет":
				if sforces[i].xF == "+":
					self.draw_distribload((0,coord(i),0), (0,coord(i+1),0), 
						vec=(darrlen,0,0), 
						txt=sforces[i].xFtxt,
						alttxt=True)

				if sforces[i].xF == "-":
					self.draw_distribload((0,coord(i),0), (0,coord(i+1),0), 
						vec=(-darrlen,0,0), 
						txt=sforces[i].xFtxt,
						alttxt=False)


			if sforces[i].yF != "нет":
				if sforces[i].yF == "+":
					self.draw_distribload((0,coord(i),0), (0,coord(i+1),0), 
						vec=(0,0,darrlen), 
						txt=sforces[i].yFtxt,
						alttxt=False)

				if sforces[i].yF == "-":
					self.draw_distribload((0,coord(i),0), (0,coord(i+1),0), 
						vec=(0,0,-darrlen), 
						txt=sforces[i].yFtxt,
						alttxt=True)


		for i in range(len(self.bsections())):
			lxvec = 40
			lyvec=20 
			if bsects[i].xS != "нет":
				if bsects[i].xS == "-1":
					self.draw_sharn((0,coord(i),0), 
						vec=(-40,0,0),
						xvec=(0,lxvec,0), 
						yvec=(-lyvec,0,0), brush=Qt.FDiagPattern)				
				
				if bsects[i].xS == "+1":
					self.draw_sharn((0,coord(i),0), 
						vec=(40,0,0),
						xvec=(0,lxvec,0), 
						yvec=(lyvec,0,0), brush=Qt.FDiagPattern)				

				if bsects[i].xS == "-2":
					self.draw_sharn((0,coord(i),0), 
						vec=(-40,0,0),
						xvec=(0,0,lxvec/3*2), 
						yvec=(-lyvec/3*2,0,0), brush=Qt.FDiagPattern)				
				
				if bsects[i].xS == "+2":
					self.draw_sharn((0,coord(i),0), 
						vec=(40,0,0),
						xvec=(0,0,lxvec/3*2), 
						yvec=(lyvec/3*2,0,0), brush=Qt.FDiagPattern)				
			
			if bsects[i].zS != "нет":
				if bsects[i].zS == "-1":
					self.draw_sharn((0,coord(i),0), 
						vec=(0,-40,0),
						xvec=(0,0,lxvec/3*2), 
						yvec=(0,-lyvec*3/2,0))				
				
				if bsects[i].zS == "+1":
					self.draw_sharn((0,coord(i),0), 
						vec=(0,40,0),
						xvec=(0,0,lxvec/3*2), 
						yvec=(0,lyvec*3/2,0))				
			
				if bsects[i].zS == "-2":
					self.draw_sharn((0,coord(i),0), 
						vec=(0,-40,0),
						xvec=(lxvec/3*2,0,0), 
						yvec=(0,-lyvec*3/2,0))				
				
				if bsects[i].zS == "+2":
					self.draw_sharn((0,coord(i),0), 
						vec=(0,40,0),
						xvec=(lxvec/3*2,0,0), 
						yvec=(0,lyvec*3/2,0))				
			
			if bsects[i].yS != "нет":
				if bsects[i].yS == "-1":
					self.draw_sharn((0,coord(i),0), 
						vec=(0,0,-35),
						xvec=(0,lxvec,0), 
						yvec=(0,0,-lyvec/3*2),
						brush=Qt.FDiagPattern)				
				
				if bsects[i].yS == "+1":
					self.draw_sharn((0,coord(i),0), 
						vec=(0,0,35),
						xvec=(0,lxvec,0), 
						yvec=(0,0,lyvec/3*2),
						brush=Qt.FDiagPattern)	
			
				if bsects[i].yS == "-2":
					self.draw_sharn((0,coord(i),0), 
						vec=(0,0,-35),
						xvec=(lxvec/3*2,0,0), 
						yvec=(0,0,-lyvec/3*2))				
				
				if bsects[i].yS == "+2":
					self.draw_sharn((0,coord(i),0), 
						vec=(0,0,35),
						xvec=(lxvec/3*2,0,0), 
						yvec=(0,0,lyvec/3*2))				
			