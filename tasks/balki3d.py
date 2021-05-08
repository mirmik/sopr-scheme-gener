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
from items.sharn3d import *

import functools

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

		def __str__(self):
			return str((self.ax, self.ay, self.az, self.bx, self.by, self.bz))

		def has_node(self, node):
			if self.ax == node.x and self.ay==node.y and self.az == node.z: 
				return True
			if self.bx == node.x and self.by==node.y and self.bz == node.z: 
				return True
			return False

	class node:
		def __init__(self, x, y, z, type="", sharn="нет"):
			self.x = x
			self.y = y
			self.z = z
			self.sharn = sharn
			self.sharn_vec = numpy.array([0,0,0])
			self.sharn_vec2 = numpy.array([0,0,0])
			self.force_x = None
			self.force_y = None
			self.force_z = None
			self.moment_x = None
			self.moment_y = None
			self.moment_z = None

		def equal(self, oth):
			return self.x == oth.x and self.y==oth.y and self.z == oth.z

	def add_sect(self, a, b):
		x, y, z = a.x, a.y, a.z
		q, w, e = b.x, b.y, b.z
		self.shemetype.task["sections"].append(self.sect(x,y,z,q,w,e))
		self.shemetype.task["nodes"].append(self.node(q,w,e))

	def nodes(self):
		return self.shemetype.task["nodes"]

	def sictions(self):
		return self.shemetype.task["sections"]

	def nodes_clean(self):
		to_del = []

		for n in self.nodes():
			for s in self.sections():
				if s.has_node(n):
					break
			else:
				to_del.append(n)

		for t in to_del:
			self.nodes().remove(t)

		if len(self.nodes() == 0):
			self.nodes.append(self.node(0,0,0))


	def delete_node(self, node):
		sections = self.shemetype.task["sections"]
		sectidx = []

		nodes = self.shemetype.task["nodes"]
		nidx = []

		for s in sections:
			if s.has_node(node):
				sectidx.append(s)

		for n in nodes:
			if n.equal(node):
				nidx.append(n)

		for s in sectidx:
			sections.remove(s)

		for s in nidx:
			nodes.remove(s)

		self.nodes_clean()



	def __init__(self, scheme):
		super().__init__(scheme, noinitbuttons=True)
		
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
	class point:
		def __init__(self, x,y=None,z=None):
			if y is None:
				self.x, self.y, self.z = x
				return

			self.x, self.y, self.z = x,y,z

		def __getitem__(self,i):
			if i == 0 : 
				return self.x
			elif i == 1:
				return self.y
			else:
				return self.z

		def __str__(self):
			return str((self.x, self.y, self.z))

	def __init__(self):
		super().__init__()
		self.track_point = QPointF(0,0)
		self.offset = QPointF(0,0)
		self.pressed_nodes = []
		self.hovered_node_pressed=None
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

	def draw_sharn(self, node, scene = None):
		if scene is None:
			scene = self.scene
		rebro = self.shemetype.rebro.get()

		_pnt = numpy.array((node.x * rebro, node.y * rebro, node.z * rebro))
		pnt = node.sharn_vec * 6 + _pnt
		vec = node.sharn_vec * 20
		xvec = node.sharn_vec2 * 20
		yvec = node.sharn_vec * 15

		if node.sharn == "нет":
			return

		if node.sharn == "врез":
			scene.addEllipse(QRectF(
				self.proj(_pnt) + QPointF(-4.5,-4.5), 
				self.proj(_pnt) + QPointF(4.5,4.5)),

			pen = self.pen, brush=Qt.white)
			return

		if node.sharn == "sharn":
			item = Sharn3dItem(
				self.proj, 
				pnt=pnt, 
				vec=vec, 
				xvec=xvec, 
				yvec=yvec, 
				pen = self.pen,
				brush = Qt.BDiagPattern)

		elif node.sharn == "zadelka":
			if node.sharn_vec[0] == 1:
				p=1
				e1 = numpy.array((0,1,0)) 
				e2 = numpy.array((0,0,1))
				e0 = numpy.array((-1,0,0))

			elif node.sharn_vec[1] == 1:
				p=2
				e1 = numpy.array((1,0,0))
				e2 = numpy.array((0,0,1))
				e0 = numpy.array((0,-1,0))

			elif node.sharn_vec[2] == 1:
				p=3
				e1 = numpy.array((1,0,0))
				e2 = numpy.array((0,1,0))
				e0 = numpy.array((0,0,-1))

			Z = 20

			a = _pnt - e1 * Z - e2 * Z
			b = _pnt + e1 * Z - e2 * Z
			c = _pnt + e1 * Z + e2 * Z
			d = _pnt - e1 * Z + e2 * Z

			a2 = _pnt - e1 * Z - e2 * Z + e0 * Z
			b2 = _pnt + e1 * Z - e2 * Z + e0 * Z
			c2 = _pnt + e1 * Z + e2 * Z + e0 * Z
			d2 = _pnt - e1 * Z + e2 * Z + e0 * Z

			scene.addLine(QLineF(self.proj(a), self.proj(b)), pen=self.pen)
			scene.addLine(QLineF(self.proj(b), self.proj(c)), pen=self.pen)
			scene.addLine(QLineF(self.proj(c), self.proj(d)), pen=self.pen)
			scene.addLine(QLineF(self.proj(d), self.proj(a)), pen=self.pen)

			#if p!=1: scene.addLine(QLineF(self.proj(a), self.proj(a2)), pen=self.pen)
			scene.addLine(QLineF(self.proj(b), self.proj(b2)), pen=self.pen)
			scene.addLine(QLineF(self.proj(c), self.proj(c2)), pen=self.pen)
			scene.addLine(QLineF(self.proj(d), self.proj(d2)), pen=self.pen)

			return

		scene.addItem(item)

	def draw_forces(self, node, scene=None):
		if scene is None:
			scene = self.scene

		rebro = self.shemetype.rebro.get()
		_pnt = numpy.array((node.x * rebro, node.y * rebro, node.z * rebro))

		def doit(f):
			print(f)
			if f is None:
				return

			a = self.proj(_pnt) + self.proj(numpy.array(f[0])*40)
			b = self.proj(_pnt) + self.proj(numpy.array(f[1])*40)
			item = ArrowItem(a,b, (8,4), pen=self.pen, brush=Qt.black)
			scene.addItem(item)

		doit(node.force_x)
		doit(node.force_y)
		doit(node.force_z)

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
				
		# Рисуем линии.
		for s in self.shemetype.task["sections"]:
			self.scene.addLine(QLineF(
				proj(s.ax, s.ay, s.az) * rebro,
				proj(s.bx, s.by, s.bz) * rebro,
			), pen = self.pen)

		# Кружки нодов.
		for n in self.shemetype.task["nodes"]:
		#	self.scene.addEllipse(QRectF(
		#		proj(n.x, n.y, n.z) * rebro + QPointF(-1,-1),
		#		proj(n.x, n.y, n.z) * rebro + QPointF(1,1),					
		#	), pen = self.pen)
#
			self.draw_sharn(n)
			self.draw_forces(n)

		# Отрисовка при наведении.
		if self.hovered_node:
			h = self.hovered_node
			pnt = self.proj(h.x, h.y, h.z) * rebro
			self.scene.addEllipse(QRectF(
				pnt + QPointF(-3,-3),
				pnt + QPointF(3,3)
			), pen=self.green, brush=Qt.green)

			if self.mouse_pressed:
				self.pressed_nodes = []

				def do(a, b, pen, force=False):
					if force or not self.has_section(self.point(a),self.point(b)):
						self.draw_point(b, pen)
						self.draw_line(a, b, pen)
						self.pressed_nodes.append(self.point(b[0], b[1], b[2]))

				do((h.x,h.y,h.z), (h.x+1, h.y, h.z), self.green)
				do((h.x,h.y,h.z), (h.x-1, h.y, h.z), self.green)
				do((h.x,h.y,h.z), (h.x, h.y+1, h.z), self.green)
				do((h.x,h.y,h.z), (h.x, h.y-1, h.z), self.green)
				do((h.x,h.y,h.z), (h.x, h.y, h.z+1), self.green)
				do((h.x,h.y,h.z), (h.x, h.y, h.z-1), self.green)

				if self.hovered_node_pressed is not None:
					do((h.x,h.y,h.z), self.hovered_node_pressed, self.blue, force=True)

		
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

	def Action(self, name, parent, trig=None):
		act = QAction(name, parent)
		if trig:
			act.triggered.connect(trig)

		if isinstance(trig, functools.partial) and trig.func == self.set_sharn_flag:
			pix = QPixmap(200,200)
			pix.fill()
			painter = QPainter(pix)
			scene = QGraphicsScene()
			node = self.shemetype.confwidget.node(0,0,0)
			node.sharn = numpy.array(trig.args[0] )		
			node.sharn_vec = numpy.array(trig.args[1]) 	
			node.sharn_vec2 = numpy.array(trig.args[2]) 
			self.draw_sharn(node, scene)
			scene.render(painter)
			painter.end()
			act.setIcon(QIcon(pix))

		if isinstance(trig, functools.partial) and trig.func == self.set_force:
			pix = QPixmap(200,200)
			pix.fill()
			painter = QPainter(pix)
			scene = QGraphicsScene()
			node = self.shemetype.confwidget.node(0,0,0)
			setattr(node, trig.args[0], (trig.args[1],trig.args[2]))
			self.draw_forces(node, scene)
			scene.render(painter)
			painter.end()
			act.setIcon(QIcon(pix))

		return act

	def delete_node_trig(self):
		self.shemetype.confwidget.delete_node(self.hovered_node)
		self.repaint()

	def set_sharn_flag(self, arg, arg1, arg2):
		self.hovered_node.sharn = numpy.array(arg )		
		self.hovered_node.sharn_vec = numpy.array(arg1) 	
		self.hovered_node.sharn_vec2 = numpy.array(arg2) 	
		self.repaint()

	def set_force(self, arg, arg1, arg2):
		setattr(self.hovered_node, arg, (arg1,arg2))
		self.repaint()

	def mousePressEvent(self, ev):
		if ev.button() == Qt.RightButton:
			
			if self.hovered_node:
				menu = QMenu(self)
				
				nodevars = QMenu("Шарниры и заделки", self)
				acts = [
					 self.Action("Врезанный", self, functools.partial(self.set_sharn_flag, "врез", (0,0,+1), (0,0,0))),
					 self.Action("Шарнир -x(y)", self, functools.partial(self.set_sharn_flag, "sharn", (-1,0,0), (0,1,0))),
					 self.Action("Шарнир -x(z)", self, functools.partial(self.set_sharn_flag, "sharn", (-1,0,0), (0,0,1))),
					 self.Action("Шарнир +x(y)", self, functools.partial(self.set_sharn_flag, "sharn", (+1,0,0), (0,1,0))),
					 self.Action("Шарнир +x(z)", self, functools.partial(self.set_sharn_flag, "sharn", (+1,0,0), (0,0,1))),
					 self.Action("Шарнир -y(x)", self, functools.partial(self.set_sharn_flag, "sharn", (0,-1,0), (1,0,0))),
					 self.Action("Шарнир -y(z)", self, functools.partial(self.set_sharn_flag, "sharn", (0,-1,0), (0,0,1))),
					 self.Action("Шарнир +y(x)", self, functools.partial(self.set_sharn_flag, "sharn", (0,+1,0), (1,0,0))),
					 self.Action("Шарнир +y(z)", self, functools.partial(self.set_sharn_flag, "sharn", (0,+1,0), (0,0,1))),
					 self.Action("Шарнир -z(x)", self, functools.partial(self.set_sharn_flag, "sharn", (0,0,-1), (1,0,0))),
					 self.Action("Шарнир -z(y)", self, functools.partial(self.set_sharn_flag, "sharn", (0,0,-1), (0,1,0))),
					 self.Action("Шарнир +z(x)", self, functools.partial(self.set_sharn_flag, "sharn", (0,0,+1), (1,0,0))),
					 self.Action("Шарнир +z(y)", self, functools.partial(self.set_sharn_flag, "sharn", (0,0,+1), (0,1,0))),
					 self.Action("Заделка x", self, functools.partial(self.set_sharn_flag, "zadelka", (1,0,0), (0,0,0))),
					 self.Action("Заделка y", self, functools.partial(self.set_sharn_flag, "zadelka", (0,1,0), (0,0,0))),
					 self.Action("Заделка z", self, functools.partial(self.set_sharn_flag, "zadelka", (0,0,1), (0,0,0))),
				]
				for a in acts:
					nodevars.addAction(a)

				forcesmenu = QMenu("Сосредоточенные силы и моменты", self)
				S = 0.1
				acts = [
					 self.Action("Сила x+1", self, functools.partial(self.set_force, "force_x", (-1,0,0), (-S,0,0))),
					 self.Action("Сила x+2", self, functools.partial(self.set_force, "force_x", (+S,0,0), (+1,0,0))),
					 self.Action("Сила x-1", self, functools.partial(self.set_force, "force_x", (+1,0,0), (+S,0,0))),
					 self.Action("Сила x-2", self, functools.partial(self.set_force, "force_x", (-S,0,0), (-1,0,0))),
					 self.Action("Сила x нет", self, functools.partial(self.set_force, "force_x", (0,0,0), (0,0,0))),	

					 self.Action("Сила y+1", self, functools.partial(self.set_force, "force_y", (0,-1,0), (0,-S,0))),
					 self.Action("Сила y+2", self, functools.partial(self.set_force, "force_y", (0,+S,0), (0,+1,0))),
					 self.Action("Сила y-1", self, functools.partial(self.set_force, "force_y", (0,+1,0), (0,+S,0))),
					 self.Action("Сила y-2", self, functools.partial(self.set_force, "force_y", (0,-S,0), (0,-1,0))),
					 self.Action("Сила y нет", self, functools.partial(self.set_force, "force_y", (0,0,0), (0,0,0))),

					 self.Action("Сила z+1", self, functools.partial(self.set_force, "force_z", (0,0,-1), (0,0,-S))),
					 self.Action("Сила z+2", self, functools.partial(self.set_force, "force_z", (0,0,+S), (0,0,+1))),
					 self.Action("Сила z-1", self, functools.partial(self.set_force, "force_z", (0,0,+1), (0,0,+S))),
					 self.Action("Сила z-2", self, functools.partial(self.set_force, "force_z", (0,0,-S), (0,0,-1))),
					 self.Action("Сила z нет", self, functools.partial(self.set_force, "force_z", (0,0,0), (0,0,0))),
				]
				for a in acts:
					forcesmenu.addAction(a)


				clean = self.Action(("Очистить узел"), self, functools.partial(self.set_sharn_flag, "нет", (0,0,0), (0,0,0)))
				delete = self.Action(("Удалить узел и граничащие балки"), self, self.delete_node_trig)
	
				menu.addMenu(nodevars)
				menu.addMenu(forcesmenu)
				menu.addAction(clean)
				menu.addSeparator()
				menu.addAction(delete)

				
				menu.popup(self.mapToGlobal(ev.pos()))

			return

		self.mouse_pressed=True
		self.update()

	def mouseReleaseEvent(self, ev):
		self.mouse_pressed = False

		if ev.button() == Qt.LeftButton and self.hovered_node_pressed:
			self.shemetype.confwidget.add_sect(self.hovered_node, self.hovered_node_pressed)

		self.hovered_node = None
		self.update()

	def has_node(self, x, y, z):
		for n in self.nodes():
			if x == n.x and y == n.y and z == n.z:
				return True

		return False

	def has_section(self, a, b):
		for s in self.sections():
			if a.x == s.ax and b.x == s.bx and a.y == s.ay and b.y==s.by and a.z == s.az and b.z == s.bz:
				return True

			if b.x == s.ax and a.x == s.bx and b.y == s.ay and a.y==s.by and b.z == s.az and a.z == s.bz:
				return True

		return False

	def sections(self):
		return self.shemetype.task["sections"]

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

	def find_for_sect(self, pos, lst):
		pass	

	def mouseMoveEvent(self, ev):
		self.track_point = QPointF(ev.pos().x(), ev.pos().y()) + self.offset
		pos = self.track_point

		if not self.mouse_pressed:
			sts, idx = self.find_for_node(pos, [(n.x, n.y, n.z) for n in self.shemetype.task["nodes"]])
			if sts: 
				self.hovered_node = self.shemetype.task["nodes"][idx]
			else:
				self.hovered_node = None			
		
			#if self.hovered_node is None:
			#	sts, idx = self.find_for_sect(pos, [((s.ax, s.ay, s.az), (s.bx, s.by, s.bz)) for s in self.shemetype.task["sections"]])
			#	if sts: 
			#		self.hovered_sect = self.shemetype.task["sections"][idx]
			#	else:
			#		self.hovered_sect = None


		else: 
			sts, idx = self.find_for_node(pos, [(n.x, n.y, n.z) for n in self.pressed_nodes])
			if sts: 
				self.hovered_node_pressed = self.pressed_nodes[idx]
			else:
				self.hovered_node_pressed = None
			

		self.last_point = self.track_point 
		self.repaint()


	def enterEvent(self, ev):
		self.grid_enabled = True
		self.update()

	def leaveEvent(self, ev):
		self.grid_enabled = False
		self.update()


#endif  //_ContextMenu_h_
