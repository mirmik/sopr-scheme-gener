import common
import paintwdg
import paintool

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import taskconf_menu
import tablewidget
from sopr_scheme_gener.layouts.stress_cube import (
	StressCubeLayoutBuilder,
	StressCubeLayoutSettings,
)
from sopr_scheme_gener.scene.qt import QtGraphicsSceneRenderer, QtTextMetrics

class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Напряжения")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())

class ConfWidget(common.ConfWidget):
	def __init__(self, scheme):
		self.second_cube = False
		super().__init__(scheme, noinitbuttons=True)
		
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
		if self.shemetype.second_cube.get() and len(self.shemetype.task["sections"]) != 2:
			self.shemetype.task["sections"].append(self.sect())
			self.clean_and_update_interface()

		if not self.shemetype.second_cube.get() and len(self.shemetype.task["sections"]) != 1:
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
		#self.table2.addColumn("x", "int")
		#self.table2.addColumn("y", "int")

		if self.shemetype.second_cube.get():
			self.table2.addColumn("text2", "str")
			#self.table2.addColumn("x2", "int")
			#self.table2.addColumn("y2", "int")

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
		self.no_resize = True


	def scene_bound(self):
		return (self.last_scene.viewport.width, self.last_scene.viewport.height)

	def paintEventImplementation(self, ev):
		self.painter.setRenderHints(QPainter.Antialiasing)
		selected_id = ""
		if self.selected_item:
			cube_index = 1 if self.selected_item.endswith("2") else 0
			name = self.selected_item.rstrip("2")
			selected_id = "cube/{}/label/{}".format(cube_index, name)
		settings = StressCubeLayoutSettings(
			second_cube=self.shemetype.second_cube.get(),
			axonom=self.shemetype.axonom.get(),
			yaw_degrees=self.shemetype.zrot.get(),
			pitch_degrees=self.shemetype.xrot.get(),
			z_scale=self.shemetype.zmul.get(),
			edge=self.shemetype.rebro.get(),
			horizontal_border=self.shemetype.wborder.get(),
			vertical_border=self.shemetype.hborder.get(),
			line_width=self.shemetype.line_width.get(),
			font_size=self.shemetype.font_size.get(),
			note=self.shemetype.texteditor.toPlainText(),
			selected_label_id=selected_id,
		)
		layout = StressCubeLayoutBuilder().build(
			self.shemetype.task,
			settings,
			text_metrics=QtTextMetrics(),
			text_transform=paintool.greek,
		)
		scene = layout.scene
		self.last_scene = scene
		self.hovers = {
			("{}{}".format(name, "2" if cube_index else "")): bounds
			for object_id, bounds in layout.label_bounds
			for cube_index, name in [
				(int(object_id.split("/")[1]), object_id.split("/")[-1])
			]
		}
		self.offset = QPointF(
			layout.interaction_offset.x,
			layout.interaction_offset.y,
		)
		QtGraphicsSceneRenderer().render(scene, self.painter)
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
				if (
					h.x <= self.track_point.x() <= h.right
					and h.y <= self.track_point.y() <= h.bottom
				):
					self.selected_item = k
					break

		self.last_point = self.track_point 
		self.repaint()

		
