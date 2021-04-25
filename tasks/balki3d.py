import common
import paintwdg

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import taskconf_menu
import tablewidget
from items.arrow import *
from items.text import *

from projector import Projector
import math

def deg(x): return x / 180.0 * math.pi

class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Пространственные балки")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())

class ConfWidget(common.ConfWidget):
	class sect:
		def __init__(self, ax, ay, az, bx, by, bz):
			self.ax = ax
			self.ay = ay
			self.az = az
			self.bx = bx
			self.by = by
			self.bz = bz

	class node:
		def __init__(self, x, y, z, type=""):
			self.x = x
			self.y = y
			self.z = z


	def __init__(self, scheme):
		super().__init__(scheme)
		
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)

		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.axonom = self.sett.add("Аксонометрия:", "bool", True)
		self.shemetype.zrot = self.sett.add("Направление:", "int", "20")
		self.shemetype.xrot = self.sett.add("Подъём:", "int", "40")
		self.shemetype.zmul = self.sett.add("Z-сжатие:", "float", "0.6")
		self.shemetype.rebro = self.sett.add("Длина ребра:", "float", "150")
		self.shemetype.wborder = self.sett.add("Поля по горизонтали:", "float", "10")
		self.shemetype.hborder = self.sett.add("Поля по вертикали:", "float", "10")
		self.sett.updated.connect(self.redraw)
		
		self.update_interface()

	def update_interface(self):
		self.vlayout.addWidget(self.sett)
		self.vlayout.addWidget(self.shemetype.texteditor)
		self.setLayout(self.vlayout)

	def create_task_structure(self):
		self.shemetype.task = {
			"sections" : 
			[
				self.sect(0,0,0, 0,-1,0),
				self.sect(0,-1,0, 1,-1,0),
				self.sect(1,-1,0, 1,-1,1),
			],

			"nodes" : 
			[
				self.node(0,0,0),
				self.node(0,-1,0),
				self.node(1,-1,0),
				self.node(1,-1,1),
			]
		}

	def inittask(self):
		return {}

class PaintWidget(paintwdg.PaintWidget):
	def __init__(self):
		super().__init__()
		self.track_point = QPointF(0,0)
		self.offset = QPointF(0,0)
		self.mouse_pressed = False
		self.no_text_render = True
		self.no_resize = True
		self.hovered_node = None
		self.grid_enabled = False

	def scene_bound(self):
		return (self.scene.itemsBoundingRect().width(),
			self.scene.itemsBoundingRect().height())

	def draw_point(self, pnt, pen):
		rebro = self.shemetype.rebro.get()
		pnt = self.proj(pnt[0], pnt[1], pnt[2]) * rebro
		self.scene.addEllipse(QRectF(pnt + QPointF(-3,-3), pnt + QPointF(3,3)), pen=pen)

	def draw_line(self, pnt1, pnt2, pen):
		rebro = self.shemetype.rebro.get()
		pnt1 = self.proj(pnt1[0], pnt1[1], pnt1[2]) * rebro
		pnt2 = self.proj(pnt2[0], pnt2[1], pnt2[2]) * rebro
		self.scene.addLine(QLineF(pnt1, pnt2), pen=pen)

	def paintEventImplementation(self, ev):
		self.scene = QGraphicsScene()
		self.painter.setRenderHints(QPainter.Antialiasing)
		
		proj = Projector()
		proj.set_yaw(deg(self.shemetype.zrot.get()))
		proj.set_pitch(-deg(self.shemetype.xrot.get()))
		proj.set_zmul(self.shemetype.zmul.get())
		proj.set_iso_projection(not self.shemetype.axonom.get())
		self.proj = proj

		rebro = self.shemetype.rebro.get()

		br = QColor(0,0,0)
		br.setAlphaF(0)
		p = QPen()
		p.setColor(br)


		#self.scene.addEllipse(QRectF(
		#	self.track_point + QPointF(-3,-3),
		#	self.track_point + QPointF(3,3)
		#), brush=br, pen=self.pen)
				
		for s in self.shemetype.task["sections"]:
			self.scene.addLine(QLineF(
				proj(s.ax, s.ay, s.az) * rebro,
				proj(s.bx, s.by, s.bz) * rebro,
			), pen = self.pen)

		if self.hovered_node:
			h = self.hovered_node
			pnt = self.proj(h.x, h.y, h.z) * rebro
			self.scene.addEllipse(QRectF(
				pnt + QPointF(-3,-3),
				pnt + QPointF(3,3)
			), pen=self.green, brush=Qt.green)

			if self.mouse_pressed:
				def do(a, b, pen):
					if not self.has_node(*b):
						self.draw_point(b, pen)
						self.draw_line(a, b, pen)

				do((h.x,h.y,h.z), (h.x+1, h.y, h.z), self.green)
				do((h.x,h.y,h.z), (h.x-1, h.y, h.z), self.green)
				do((h.x,h.y,h.z), (h.x, h.y+1, h.z), self.green)
				do((h.x,h.y,h.z), (h.x, h.y-1, h.z), self.green)
				do((h.x,h.y,h.z), (h.x, h.y, h.z+1), self.green)
				do((h.x,h.y,h.z), (h.x, h.y, h.z-1), self.green)

		
		WBORDER = self.shemetype.wborder.get()
		HBORDER = self.shemetype.hborder.get()

		if len(self.shemetype.task["sections"]) == 0:
			self.scene.addRect(QRectF(
				QPointF(-20,-20),
				QPointF( 20, 20)
			), brush=br, pen=p)

		rect = self.scene.itemsBoundingRect()
		addtext = paintool.greek(self.shemetype.texteditor.toPlainText())
		n = len(addtext.splitlines())
		for i, l in enumerate(addtext.splitlines()):
			t = self.scene.addText(l, self.font)
			t.setPos(
				rect.x(), 
				rect.height() + rect.y() + QFontMetrics(self.font).height()*i
			)
			
		rect = self.scene.itemsBoundingRect()
		
		self.scene.addRect(QRectF(rect.x()-WBORDER, rect.y()-HBORDER, rect.width()+WBORDER*2, rect.height()+HBORDER*2), pen = p, brush=br)
		self.offset = QPointF(rect.x()-WBORDER, rect.y()-HBORDER)
		self.scene.render(self.painter)

		self.resize_after_render(*self.scene_bound())

	def mousePressEvent(self, ev):
		if ev.button() == Qt.RightButton:
			
			if self.hovered_node:
				menu = QMenu(self)
				
				nodevars = QMenu("Шарниры и заделки", self)
				acts = [
					 QAction("Шарнир -x", self),
					 QAction("Шарнир +x", self),
					 QAction("Шарнир -y", self),
					 QAction("Шарнир +y", self),
					 QAction("Шарнир -z", self),
					 QAction("Шарнир +z", self),

					 QAction("Заделка x", self),
					 QAction("Заделка y", self),
					 QAction("Заделка z", self),
				]

				for a in acts:
					nodevars.addAction(a)
				delete = QAction(("Очистить узел"), self)
	
				menu.addMenu(nodevars)
				menu.addAction(delete)
				
				menu.popup(self.mapToGlobal(ev.pos()))

			return

		self.mouse_pressed=True
		self.update()

	def mouseReleaseEvent(self, ev):
		self.mouse_pressed = False
		self.hovered_node = None
		self.update()

	def has_node(self, x, y, z):
		for n in self.nodes():
			if x == n.x and y == n.y and z == n.z:
				return True

		return False

	def nodes(self):
		return self.shemetype.task["nodes"]

	def find_for_node(self, pos, lst):
		rebro = self.shemetype.rebro.get()
		t = None
		mindist = 1000000
		for i in range(len(lst)):
			s = lst[i]
			s = self.proj(s[0], s[1], s[2]) * rebro
			xdiff = s.x() - pos.x()
			ydiff = s.y() - pos.y()
			dist = math.sqrt(xdiff**2 + ydiff**2)
			if dist < mindist:
				mindist = dist
				t = i
		if mindist < 40:
			return True, t
		else:
			return False, None


	def mouseMoveEvent(self, ev):
		self.track_point = QPointF(ev.pos().x(), ev.pos().y()) + self.offset
		pos = self.track_point
#		rebro = self.shemetype.rebro.get()

		if not self.mouse_pressed:
			sts, idx = self.find_for_node(pos, [(n.x, n.y, n.z) for n in self.shemetype.task["nodes"]])
			if sts: 
				self.hovered_node = self.shemetype.task["nodes"][idx]
			else:
				self.hovered_node = None
		#if not self.mouse_pressed:
		#	self.selected_item = None
		#	for k, h in self.hovers.items():
		#		if h.boundingRect().contains(self.track_point):
		#			self.selected_item = k
		#			break

		self.last_point = self.track_point 
		self.repaint()


	def enterEvent(self, ev):
		self.grid_enabled = True
		self.update()

	def leaveEvent(self, ev):
		self.grid_enabled = False
		self.update()


#endif  //_ContextMenu_h_
