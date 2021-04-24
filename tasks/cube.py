import common
import paintwdg
import paintool

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from projector import Projector
import math

import taskconf_menu
import tablewidget
from items.arrow import *
from items.text import *

class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Напряжения")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())

class ConfWidget(common.ConfWidget):
	def __init__(self, scheme):
		self.second_cube = False
		super().__init__(scheme)
		
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)

		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.second_cube = self.sett.add("Второй куб:", "bool", False)
		self.shemetype.axonom = self.sett.add("Аксонометрия:", "bool", False)
		self.shemetype.zrot = self.sett.add("Направление:", "int", "20")
		self.shemetype.xrot = self.sett.add("Подъём:", "int", "40")
		self.shemetype.zmul = self.sett.add("Z-сжатие:", "float", "0.6")
		self.shemetype.rebro = self.sett.add("Длина ребра:", "float", "50")
		self.shemetype.wborder = self.sett.add("Поля по горизонтали:", "float", "10")
		self.shemetype.hborder = self.sett.add("Поля по вертикали:", "float", "0")
		self.sett.updated.connect(self.redraw)
		
		self.update_interface()

	def redraw(self):
		if self.shemetype.second_cube.get() != self.second_cube:
			self.second_cube = self.shemetype.second_cube.get()
			if self.second_cube:
				self.shemetype.task["sections"].append(self.sect())
			else:
				del self.shemetype.task["sections"][1]
			self.clean_and_update_interface()

		super().redraw()

	def table_clearing(self):
		self.shemetype.task["labels"][0].clear(self.shemetype.task["sections"][0].qx == "нет")
		self.shemetype.task["labels"][1].clear(self.shemetype.task["sections"][0].qy == "нет")
		self.shemetype.task["labels"][2].clear(self.shemetype.task["sections"][0].qz == "нет")
		self.shemetype.task["labels"][3].clear(self.shemetype.task["sections"][0].mx == "нет")
		self.shemetype.task["labels"][4].clear(self.shemetype.task["sections"][0].my == "нет")
		self.shemetype.task["labels"][5].clear(self.shemetype.task["sections"][0].mz == "нет")
		if self.second_cube:
			self.shemetype.task["labels"][0].clear2(self.shemetype.task["sections"][1].qx == "нет")
			self.shemetype.task["labels"][1].clear2(self.shemetype.task["sections"][1].qy == "нет")
			self.shemetype.task["labels"][2].clear2(self.shemetype.task["sections"][1].qz == "нет")
			self.shemetype.task["labels"][3].clear2(self.shemetype.task["sections"][1].mx == "нет")
			self.shemetype.task["labels"][4].clear2(self.shemetype.task["sections"][1].my == "нет")
			self.shemetype.task["labels"][5].clear2(self.shemetype.task["sections"][1].mz == "нет")
			self.table2.updateTable()

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("qx", "list", variant=["нет", "-", "+"])
		self.table.addColumn("qy", "list", variant=["нет", "-", "+"])
		self.table.addColumn("qz", "list", variant=["нет", "-", "+"])
		self.table.addColumn("mx", "list", variant=["нет", "-", "+"])
		self.table.addColumn("my", "list", variant=["нет", "-", "+"])
		self.table.addColumn("mz", "list", variant=["нет", "-", "+"])
		self.table.updateTable()
		self.table.updated.connect(self.table_clearing)
		self.table.updated.connect(self.redraw)
		self.vlayout.addWidget(self.table)

		self.table2 = tablewidget.TableWidget(self.shemetype, "labels")
		self.table2.addColumn("text", "str")
		self.table2.addColumn("x", "int")
		self.table2.addColumn("y", "int")

		if self.second_cube:
			self.table2.addColumn("text2", "str")
			self.table2.addColumn("x2", "int")
			self.table2.addColumn("y2", "int")

		self.table_clearing()
		self.table2.updateTable()
		self.table2.updated.connect(self.redraw)
		self.table2.setVerticalHeaderLabels(["qx", "qy", "qz", "mx", "my", "mz"])
		self.vlayout.addWidget(self.table2)

		self.vlayout.addWidget(self.sett)
		self.vlayout.addWidget(self.shemetype.texteditor)
		self.setLayout(self.vlayout)

	class sect:
		def __init__(self, qx="нет", qy="нет", qz="нет", mx="нет", my="нет", mz="нет"):
			self.qx = qx
			self.qy = qy
			self.qz = qz
			self.mx = mx
			self.my = my
			self.mz = mz

	class label:
		def __init__(self, text="", x=-10, y=-10, text2="", x2=-10, y2=-10):
			self.text = text
			self.x = x
			self.y = y

			self.text2 = text2
			self.x2 = x2
			self.y2 = y2

		def move(self,pnt):
			self.x += pnt.x()
			self.y += pnt.y()  

		def move2(self,pnt):
			self.x2 += pnt.x()
			self.y2 += pnt.y()  

		def clear(self, en):
			if en:
				self.x=0
				self.y=0
				self.text=""
			else:
				if self.text == "":
					self.text = "10"

		def clear2(self, en):
			if en:
				self.x2=0
				self.y2=0
				self.text2=""
			else:
				if self.text2 == "":
					self.text2 = "10"

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect("нет", "нет", "нет", "нет", "нет", "нет"),			
			],

			"labels": [
				self.label("10"),
				self.label("10"),
				self.label("10"),
				self.label("10"),
				self.label("10"),
				self.label("10"),
			]
		}

	def inittask(self):
		return {}

class PaintWidget(paintwdg.PaintWidget):
	def __init__(self):
		super().__init__()
		self.no_text_render = True
		self.hovers = {}
		self.setMouseTracking(True)
		self.track_point = QPointF(0,0)
		self.mouse_pressed = False
		self.selected_item = None
		self.last_point = QPointF(0,0)
		self.last_size = (0,0)

	def scene_bound(self):
		return (self.scene.itemsBoundingRect().width(),
			self.scene.itemsBoundingRect().height())

	def drawCube(self, i, off=0):
		def deg(x): return x / 180.0 * math.pi
		proj = Projector()
		proj.set_yaw(deg(self.shemetype.zrot.get()))
		proj.set_pitch(-deg(self.shemetype.xrot.get()))
		proj.set_zmul(self.shemetype.zmul.get())
		proj.set_iso_projection(not self.shemetype.axonom.get())

		if i == 1:
			proj.set_mov(off,0)

		P = self.shemetype.rebro.get()
		red = QPen()
		green = QPen()
		blue = QPen()

		red.setColor(QColor(255,0,0))
		green.setColor(QColor(0,255,0))
		blue.setColor(QColor(0,0,255))

		self.scene.addLine(QLineF(proj(+P, +P, +P), proj(-P, +P, +P)), self.pen)
		self.scene.addLine(QLineF(proj(+P, +P, +P), proj(+P, -P, +P)), self.pen)
		self.scene.addLine(QLineF(proj(+P, +P, +P), proj(+P, +P, -P)), self.pen)
		self.scene.addLine(QLineF(proj(+P, +P, -P), proj(-P, +P, -P)), self.pen)
		self.scene.addLine(QLineF(proj(+P, +P, -P), proj(+P, -P, -P)), self.pen)
		self.scene.addLine(QLineF(proj(-P, +P, -P), proj(-P, +P, +P)), self.pen)
		self.scene.addLine(QLineF(proj(+P, -P, -P), proj(+P, -P, +P)), self.pen)
		self.scene.addLine(QLineF(proj(-P, -P, +P), proj(-P, +P, +P)), self.pen)
		self.scene.addLine(QLineF(proj(-P, -P, +P), proj(+P, -P, +P)), self.pen)

		#axes:
		self.scene.addItem(ArrowItem(proj(+P, -P, -P), proj(+2*P, -P, -P), arrow_size=(15,3), pen=self.halfpen, brush=Qt.black))
		self.scene.addItem(ArrowItem(proj(-P, +P, -P), proj(-P, +2*P, -P), arrow_size=(15,3), pen=self.halfpen, brush=Qt.black))
		self.scene.addItem(ArrowItem(proj(-P, -P, +P), proj(-P, -P, +2*P), arrow_size=(15,3), pen=self.halfpen, brush=Qt.black))
		self.scene.addItem(TextItem("x", font=self.font, center=proj(+2*P, -P, -P)+QPointF(0,-10), pen=self.pen))
		self.scene.addItem(TextItem("z", font=self.font, center=proj(-P, +2*P, -P)+QPointF(-8,0), pen=self.pen))
		self.scene.addItem(TextItem("y", font=self.font, center=proj(-P, -P, +2*P)+QPointF(-8,0), pen=self.pen))

		#forces:
		qx = self.shemetype.task["sections"][i].qx
		qy = self.shemetype.task["sections"][i].qy
		qz = self.shemetype.task["sections"][i].qz
		mx = self.shemetype.task["sections"][i].mx
		my = self.shemetype.task["sections"][i].my
		mz = self.shemetype.task["sections"][i].mz

		qx_pnt = proj(2.5*P,0,0)
		qy_pnt = proj(0,0,2.5*P)
		qz_pnt = proj(0,2.5*P,0)
		
		if qx!="нет": self.scene.addItem(ArrowItem(proj(P,0,0), qx_pnt, arrow_size=(15,5), pen=self.pen, brush=Qt.black, reverse=qx=="-"))
		if qy!="нет": self.scene.addItem(ArrowItem(proj(0,0,P), qy_pnt, arrow_size=(15,5), pen=self.pen, brush=Qt.black, reverse=qy=="-"))
		if qz!="нет": self.scene.addItem(ArrowItem(proj(0,P,0), qz_pnt, arrow_size=(15,5), pen=self.pen, brush=Qt.black, reverse=qz=="-"))

		M = 3/4
		if mz!="нет":
			reverse = mz == "-"
			self.scene.addItem(ArrowItem(proj(-P*M,0,P), proj(P*M,0,P), arrow_size=(15,5), pen=self.pen, brush=Qt.black, reverse=reverse))
			self.scene.addItem(ArrowItem(proj(P,0,-P*M), proj(P,0,P*M), arrow_size=(15,5), pen=self.pen, brush=Qt.black, reverse=reverse))

		if my!="нет":
			reverse = my == "-"
			self.scene.addItem(ArrowItem(proj(-P*M,P,0), proj(P*M,P,0), arrow_size=(15,5), pen=self.pen, brush=Qt.black, reverse=reverse))
			self.scene.addItem(ArrowItem(proj(P,-P*M,0), proj(P,P*M,0), arrow_size=(15,5), pen=self.pen, brush=Qt.black, reverse=reverse))

		if mx!="нет":
			reverse = mx == "-"
			self.scene.addItem(ArrowItem(proj(0,-P*M,P), proj(0,P*M,P), arrow_size=(15,5), pen=self.pen, brush=Qt.black, reverse=reverse))
			self.scene.addItem(ArrowItem(proj(0,P,-P*M), proj(0,P,P*M), arrow_size=(15,5), pen=self.pen, brush=Qt.black, reverse=reverse))

		#labels:
		if i == 0:
			def do_label(i, pnt=QPointF(0,0), hint=None):
				text = self.shemetype.task["labels"][i].text
				x = self.shemetype.task["labels"][i].x
				y = self.shemetype.task["labels"][i].y
				item = TextItem(text, font=self.font, center=pnt+QPointF(x,y), pen=self.pen)
				self.scene.addItem(item)
				self.hovers[hint] = item
				item.hint = hint
	
			section = self.shemetype.task["sections"][0]
			if section.qx!="нет": do_label(0, qx_pnt, hint="qx")
			if section.qy!="нет": do_label(1, qy_pnt, hint="qy")
			if section.qz!="нет": do_label(2, qz_pnt, hint="qz")
			if section.mx!="нет": do_label(3, proj(0,0,P), hint="mx")
			if section.my!="нет": do_label(4, proj(0,P,0), hint="my")
			if section.mz!="нет": do_label(5, proj(P,0,0), hint="mz")

		if i == 1:
			def do_label(i, pnt=QPointF(0,0), hint=None):
				text = self.shemetype.task["labels"][i].text2
				x = self.shemetype.task["labels"][i].x2
				y = self.shemetype.task["labels"][i].y2
				item = TextItem(text, font=self.font, center=pnt+QPointF(x,y), pen=self.pen)
				self.scene.addItem(item)
				self.hovers[hint] = item
				item.hint = hint
	
			section = self.shemetype.task["sections"][1]
			if section.qx!="нет": do_label(0, qx_pnt, hint="qx2")
			if section.qy!="нет": do_label(1, qy_pnt, hint="qy2")
			if section.qz!="нет": do_label(2, qz_pnt, hint="qz2")
			if section.mx!="нет": do_label(3, proj(0,0,P), hint="mx2")
			if section.my!="нет": do_label(4, proj(0,P,0), hint="my2")
			if section.mz!="нет": do_label(5, proj(P,0,0), hint="mz2")

	def paintEventImplementation(self, ev):
		self.scene = QGraphicsScene()
		self.painter.setRenderHints(QPainter.Antialiasing)

		self.drawCube(0)
		if self.shemetype.second_cube.get():
			self.drawCube(1, off=self.scene.itemsBoundingRect().width())

		for k, h in self.hovers.items():
			if self.selected_item == k:
				green70 = QColor(0,255,0)
				green70.setAlphaF(0.7)
				self.scene.addRect(h.boundingRect(), brush=green70)

		height = self.scene_bound()[1]
		text = self.scene.addText(paintool.greek(self.shemetype.texteditor.toPlainText()), self.font)
		text.setPos(self.scene.itemsBoundingRect().x(), self.scene.itemsBoundingRect().height() + self.scene.itemsBoundingRect().y())

		WBORDER = self.shemetype.wborder.get()
		HBORDER = self.shemetype.hborder.get()
		#self.BORDER = BORDER
		rect = self.scene.itemsBoundingRect()
		br = QColor(0,0,0)
		br.setAlphaF(0)
		p = QPen()
		p.setColor(br)
		self.scene.addRect(QRectF(rect.x()-WBORDER, rect.y()-HBORDER, rect.width()+WBORDER*2, rect.height()+HBORDER*2), pen = p, brush=br)
		#self.scene.addEllipse(QRectF(self.track_point - QPointF(3,3), self.track_point + QPointF(3,3)))
		#self.rect = self.scene.itemsBoundingRect()
		self.offset = QPointF(rect.x()-WBORDER, rect.y()-HBORDER)
		#self.scene.setSceneRect(rect.x() - 1*BORDER, rect.y() - 1*BORDER, rect.width() + 2*BORDER, rect.height() + 2*BORDER)
		self.scene.render(self.painter)

		if self.scene_bound() != self.last_size:
			self.resize_after_render(*self.scene_bound())

	def mousePressEvent(self, ev):
		self.mouse_pressed=True

	def mouseReleaseEvent(self, ev):
		self.mouse_pressed = False

	def mouseMoveEvent(self, ev):
		self.track_point = QPointF(ev.pos().x(), ev.pos().y()) + self.offset

		diff = self.track_point - self.last_point
		if self.mouse_pressed and self.selected_item:
			if self.selected_item == "qx" : self.shemetype.task["labels"][0].move(diff)
			if self.selected_item == "qy" : self.shemetype.task["labels"][1].move(diff)
			if self.selected_item == "qz" : self.shemetype.task["labels"][2].move(diff)
			if self.selected_item == "mx" : self.shemetype.task["labels"][3].move(diff)
			if self.selected_item == "my" : self.shemetype.task["labels"][4].move(diff)
			if self.selected_item == "mz" : self.shemetype.task["labels"][5].move(diff)
			if self.selected_item == "qx2" : self.shemetype.task["labels"][0].move2(diff)
			if self.selected_item == "qy2" : self.shemetype.task["labels"][1].move2(diff)
			if self.selected_item == "qz2" : self.shemetype.task["labels"][2].move2(diff)
			if self.selected_item == "mx2" : self.shemetype.task["labels"][3].move2(diff)
			if self.selected_item == "my2" : self.shemetype.task["labels"][4].move2(diff)
			if self.selected_item == "mz2" : self.shemetype.task["labels"][5].move2(diff)
			self.shemetype.confwidget.table2.updateTable()

		if not self.mouse_pressed:
			self.selected_item = None
			for k, h in self.hovers.items():
				if h.boundingRect().contains(self.track_point):
					self.selected_item = k
					break

		self.last_point = self.track_point 
		self.repaint()

		

