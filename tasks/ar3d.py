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
		super().__init__("Косой изгиб (Тип 1)")
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
						xM="нет", xMtxt="", yM="нет", yMtxt=""):
			self.xF=xF
			self.yF=yF
			self.xFtxt=xFtxt
			self.yFtxt=yFtxt

			self.xM=xM
			self.yM=yM
			self.xMtxt=xMtxt
			self.yMtxt=yMtxt
			

	class sectforce:
		def __init__(self):
			pass

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
			],
		}
		
	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")

		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("l", "float", "Длина")
		self.table.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("xF", "list", variant=["нет", "+", "-"])
		self.table2.addColumn("xFtxt", "str", "xF")
		self.table2.addColumn("yF", "list", variant=["нет", "+", "-"])
		self.table2.addColumn("yFtxt", "str", "yF")

		self.table2.addColumn("xM", "list", variant=["нет", "+", "-"])
		self.table2.addColumn("xMtxt", "str", "xM")
		self.table2.addColumn("yM", "list", variant=["нет", "+", "-"])
		self.table2.addColumn("yMtxt", "str", "yM")
		self.table2.updateTable()

		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Локальные силы:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)
		self.vlayout.addWidget(self.shemetype.texteditor)


	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.axonom = self.sett.add("Аксонометрия:", "bool", False)
		self.shemetype.axonom_deg = self.sett.add("45 градусов:", "bool", True)
		self.shemetype.xoffset = self.sett.add("Смещение:", "int", "100")
		self.shemetype.zrot = self.sett.add("Направление:", "int", "30")
		self.shemetype.xrot = self.sett.add("Подъём:", "int", "30")
		self.shemetype.L = self.sett.add("Длина:", "int", "600")
		self.shemetype.offdown = self.sett.add("Вынос разм. линий:", "int", "100")
		self.shemetype.arrlen = self.sett.add("Длина Стрелок:", "int", "60")
		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.section_type = self.sett.add("Тип сечения:", "list", 
			defval=4,
			variant=sections.section_variant)

		self.shemetype.section_txt0 = self.sett.add("Сечение.Текст1:", "str", "D")
		self.shemetype.section_txt1 = self.sett.add("Сечение.Текст2:", "str", "d")
		self.shemetype.section_txt2 = self.sett.add("Сечение.Текст3:", "str", "d")

		self.shemetype.section_arg0 = self.sett.add("Сечение.Аргумент1:", "int", "60")
		self.shemetype.section_arg1 = self.sett.add("Сечение.Аргумент2:", "int", "50")
		self.shemetype.section_arg2 = self.sett.add("Сечение.Аргумент3:", "int", "10")
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
		self.shemetype.task["betsect"].append(self.betsect())
		self.redraw()
		self.table.updateTable()
		self.table2.updateTable()

	def insert_action_impl(self,idx):
		self.sections().insert(idx, self.sect())
		self.shemetype.task["betsect"].insert(idx, self.betsect())
		self.redraw()
		self.table.updateTable()
		self.table2.updateTable()

	def del_action_impl(self, idx):
		if len(self.sections()) == 1:
			return

		del self.sections()[idx]
		del self.shemetype.task["betsect"][idx]
		self.redraw()
		self.table.updateTable()
		self.table2.updateTable()

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
				return QPoint(self.base_x-y*self.AXDEG+x, self.base_y+y*self.AXDEG-z)

			p = self.trans_matrix * numpy.array([[0],[y],[0],[1]])
			return QPoint(p[0]+x, p[2]-z)

	def paintEventImplementation(self, ev):
		bsects = self.bsections()
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

		section_width = sections.draw_section(
			wdg = self,
			section_type = self.shemetype.section_type.get(),
			arg0 = int(self.shemetype.section_arg0.get()),
			arg1 = int(self.shemetype.section_arg1.get()),
			arg2 = int(self.shemetype.section_arg2.get()),
	
			txt0 = paintool.greek(self.shemetype.section_txt0.get()),
			txt1 = paintool.greek(self.shemetype.section_txt1.get()),
			txt2 = paintool.greek(self.shemetype.section_txt2.get()),
			arrow_size = self.shemetype.arrow_size.get(),
			right = fini_width,
			hcenter=self.hcenter
		)

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

		w = 50
		L = 20
		w2 = 8
		L2 = L + stlen

		lsum = 0
		for s in self.sections():
			lsum+=s.l

		lkoeff = stlen / lsum

		def coord(sectno):
			l = 0
			for i in range(sectno):
				l += self.sections()[i].l

			return L + lkoeff * l

		off = QPoint(0,offdown)
		for i in range(len(self.sections())):
			paintool.draw_dimlines(
				painter=self.painter, 
				apnt = trans(0,coord(i),0), 
				bpnt = trans(0,coord(i+1),0), 
				offset = off, 
				textoff = QPoint(0,0), 
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

		for i in range(len(self.sections())):
			self.painter.setPen(self.doublepen)
			if bsects[i].xF != "нет":
				if bsects[i].xF == "+":
					paintool.common_arrow(
						self.painter,
						trans(-w2-arrlen,coord(i+1),0),
						trans(-w2,coord(i+1),0),
						arrow_size=arrow_size
					)

					self.painter.setPen(self.pen)
					elements.draw_text_by_points(
						self,
						trans(-w2-arrlen,coord(i+1),0),
						trans(-w2-arrlen/2,coord(i+1),0),
						txt=bsects[i].xFtxt, 
						alttxt=False, off=14, polka=None
					)
	
			self.painter.setPen(self.doublepen)
			if bsects[i].yF != "нет":
				if bsects[i].yF == "+":
					paintool.common_arrow(
						self.painter,
						trans(0,coord(i+1),-w2-arrlen),
						trans(0,coord(i+1),-w2),
						arrow_size=arrow_size
					)
					
					self.painter.setPen(self.pen)
					elements.draw_text_by_points(
						self,
						trans(0,coord(i+1),-w2-arrlen),
						trans(0,coord(i+1),-w2-arrlen/2),
						txt=bsects[i].yFtxt, 
						alttxt=False, off=10, polka=None
					)

			self.painter.setPen(self.doublepen)
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
					trans(ws,coord(i+1),0),
					trans(-w2-marrlen,coord(i+1),0)
					)
				paintool.common_arrow(
					self.painter,
					trans(-w2-marrlen,coord(i+1),0),
					trans(-w2-marrlen,coord(i+1)+off,0),
					arrow_size=arrow_size,
				)
				self.painter.setPen(self.pen)
				elements.draw_text_by_points(
					self,
					trans(-w2-marrlen,coord(i+1),0),
					trans(-w2-marrlen,coord(i+1)+off,0),
					txt=bsects[i].yMtxt, 
					alttxt=alttxt, off=14, polka=None
				)

			self.painter.setPen(self.doublepen)
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
					trans(0,coord(i+1),-ws),
					trans(0,coord(i+1),-w2-marrlen)
					)
				paintool.common_arrow(
					self.painter,
					trans(0,coord(i+1),-w2-marrlen),
					trans(0,coord(i+1)+off,-w2-marrlen),
					arrow_size=arrow_size,
				)
				self.painter.setPen(self.pen)
				elements.draw_text_by_points(
					self,
					trans(0,coord(i+1),w2+marrlen),
					trans(0,coord(i+1)-off,+w2+marrlen),
					txt=bsects[i].xMtxt, 
					alttxt=alttxt, off=14, polka=None
				)

		self.painter.setPen(self.pen)

		self.painter.setBrush(QColor(220,220,220))		
		self.painter.drawPolygon(QPolygon([
			trans(w,L,-w), trans(w,L,w), trans(w,0,w), trans(w,0,-w), 
		]))
		self.painter.setBrush(Qt.white)

		self.painter.setPen(self.axpen)
		S=20
		self.painter.drawLine(self.trans(-w-S,L,0), self.trans(w+S,L,0))
		self.painter.drawLine(self.trans(0,L,-w-S), self.trans(0,L,w+S))
		
		self.painter.setPen(self.pen)
		#self.painter.drawLine(self.trans(-w,0,-w), self.trans(-w,0,w))
		self.painter.drawLine(self.trans(-w,0,w), self.trans(w,0,w))
		self.painter.drawLine(self.trans(w,0,w), self.trans(w,0,-w))
		#self.painter.drawLine(self.trans(w,0,-w), self.trans(-w,0,-w))

		self.painter.drawLine(self.trans(-w,L,-w), self.trans(-w,L,w))
		self.painter.drawLine(self.trans(-w,L,w), self.trans(w,L,w))
		self.painter.drawLine(self.trans(w,L,w), self.trans(w,L,-w))
		self.painter.drawLine(self.trans(w,L,-w), self.trans(-w,L,-w))

		#self.painter.drawLine(self.trans(-w,L,-w), self.trans(-w,0,-w))
		self.painter.drawLine(self.trans(-w,L,w), self.trans(-w,0,w))
		self.painter.drawLine(self.trans(w,L,w), self.trans(w,0,w))
		self.painter.drawLine(self.trans(w,L,-w), self.trans(w,0,-w))

		#self.painter.drawLine(self.trans(-w2,L,-w2), self.trans(-w2,L,w2))
		self.painter.drawLine(self.trans(-w2,L,w2), self.trans(w2,L,w2))
		self.painter.drawLine(self.trans(w2,L,w2), self.trans(w2,L,-w2))
		#self.painter.drawLine(self.trans(w2,L,-w2), self.trans(-w2,L,-w2))

		self.painter.drawLine(self.trans(-w2,L2,-w2), self.trans(-w2,L2,w2))
		self.painter.drawLine(self.trans(-w2,L2,w2), self.trans(w2,L2,w2))
		self.painter.drawLine(self.trans(w2,L2,w2), self.trans(w2,L2,-w2))
		self.painter.drawLine(self.trans(w2,L2,-w2), self.trans(-w2,L2,-w2))

		#self.painter.drawLine(self.trans(-w2,L2,-w2), self.trans(-w2,L,-w2))
		self.painter.drawLine(self.trans(-w2,L2,w2), self.trans(-w2,L,w2))
		self.painter.drawLine(self.trans(w2,L2,w2), self.trans(w2,L,w2))
		self.painter.drawLine(self.trans(w2,L2,-w2), self.trans(w2,L,-w2))

		self.painter.setBrush(Qt.white)
		self.painter.drawPolygon(QPolygon([
			trans(-w2,L2,w2), trans(w2,L2,w2), trans(w2,L,w2), trans(-w2,L,w2), 
		]))

		self.painter.setBrush(QColor(220,220,220))
		self.painter.drawPolygon(QPolygon([
			trans(w2,L2,-w2), trans(w2,L2,w2), trans(w2,L,w2), trans(w2,L,-w2), 
		]))


		for i in range(len(self.sections())):
			c = coord(i)

			self.painter.drawLine(self.trans(w2,c,-w2), self.trans(w2,c,w2))
			self.painter.drawLine(self.trans(-w2,c,w2), self.trans(w2,c,w2))


		for i in range(len(self.sections())):
			self.painter.setPen(self.doublepen)
			if bsects[i].xF != "нет":
				if bsects[i].xF == "-":
					paintool.common_arrow(
						self.painter,
						trans(w2+arrlen,coord(i+1),0),
						trans(w2,coord(i+1),0),
						arrow_size=arrow_size,
					)

					self.painter.setPen(self.pen)
					elements.draw_text_by_points(
						self,
							trans(w2+arrlen,coord(i+1),0),
						trans(w2+arrlen/2,coord(i+1),0),
						txt=bsects[i].xFtxt, 
						alttxt=False, off=14, polka=None
					)

			self.painter.setPen(self.doublepen)
			if bsects[i].yF != "нет":
				if bsects[i].yF == "-":
					paintool.common_arrow(
						self.painter,
						trans(0,coord(i+1),w2+arrlen),
						trans(0,coord(i+1),w2),
						arrow_size=arrow_size
					)

					self.painter.setPen(self.pen)
					elements.draw_text_by_points(
						self,
						trans(0,coord(i+1),w2+arrlen),
						trans(0,coord(i+1),w2+arrlen/2),
						txt=bsects[i].yFtxt, 
						alttxt=False, off=14, polka=None
					)
	


			self.painter.setPen(self.doublepen)
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
					trans(ws,coord(i+1),0),
					trans(w2+marrlen,coord(i+1),0)
					)
				paintool.common_arrow(
					self.painter,
					trans(w2+marrlen,coord(i+1),0),
					trans(w2+marrlen,coord(i+1)+off,0),
					arrow_size=arrow_size,
				)

			self.painter.setPen(self.doublepen)
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
					trans(0,coord(i+1),ws),
					trans(0,coord(i+1),w2+marrlen)
					)
				paintool.common_arrow(
					self.painter,
					trans(0,coord(i+1),w2+marrlen),
					trans(0,coord(i+1)+off,w2+marrlen),
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
