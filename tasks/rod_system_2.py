"""Qt widget adapter for the second rod-system task."""

import math

import common
import paintwdg
import paintool
import tablewidget
import taskconf_menu
import util

from sopr_scheme_gener.layouts.rod_system_2 import (
	RodSystem2LayoutBuilder,
	RodSystem2LayoutSettings,
)
from sopr_scheme_gener.scene import Point
from sopr_scheme_gener.scene.qt import (
	QtPainterRenderer,
	QtSceneInteraction,
	QtTextMetrics,
)

from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QTextEdit


class ShemeTypeT1(common.SchemeType):
	def __init__(self):
		super().__init__("Стержневая система (Тип 2)")
		self.setwidgets(ConfWidget_T1(self), PaintWidget_T1(), common.TableWidget())


class ConfWidget_T1(common.ConfWidget):
	class sect:
		def __init__(
			self,
			l=1,
			A=1,
			angle=30,
			sharn="шарн+заделка",
			insharn="шарн",
			body=True,
			force="нет",
			ftxt="",
			alttxt=False,
			addangle=0,
			start_from=-1,
			wide=False,
		):
			self.start_from = start_from
			self.l = l
			self.A = A
			self.body = body
			self.sharn = sharn
			self.insharn = insharn
			self.force = force
			self.angle = angle
			self.ftxt = ftxt
			self.alttxt = alttxt
			self.addangle = addangle
			self.wide = wide

	def create_task_structure(self):
		self.shemetype.task = {"sections": []}

	def hover_sect(self, row, column, hint):
		self.shemetype.paintwidget.highlited_sect = (hint, row)
		self.redraw()
		self.save_row = row
		self.save_hint = hint

	def table_unhover(self):
		self.shemetype.paintwidget.highlited_sect = None
		self.shemetype.paintwidget.highlited_node = None
		self.redraw()

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table2 = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("start_from", "int", "ВыходитИз")
		self.table.addColumn("l", "float", "Длина")
		self.table.addColumn("angle", "float", "Угол")
		self.table2.addColumn("body", "bool", "Стержень")
		self.table2.addColumn(
			"force", "list", "Сила", variant=["нет", "к", "от", "вдоль"]
		)
		self.table2.addColumn("ftxt", "str", "Сила")
		self.table2.addColumn("alttxt", "bool", "Пол.Ткст.")
		self.table2.addColumn("addangle", "float", "Доб.Угол")
		self.table2.addColumn(
			"sharn",
			"list",
			"Шарн.",
			variant=["нет", "шарн", "шарн+заделка"],
		)
		self.table.updateTable()
		self.table2.updateTable()
		self.table.hover_hint.connect(self.hover_sect)
		self.table2.hover_hint.connect(self.hover_sect)
		self.table.unhover.connect(self.table_unhover)
		self.table2.unhover.connect(self.table_unhover)
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)
		self.table.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)
		self.vlayout.addWidget(self.shemetype.texteditor)

	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.base_length = self.sett.add("Базовая длина:", "int", "80")
		self.shemetype.sharnrad = self.sett.add("Радиус шарнира:", "int", "4")
		self.sett.updated.connect(self.redraw)
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		self.update_interface()
		self.setLayout(self.vlayout)

	def add_action_impl(self):
		self.shemetype.task["sections"].append(self.sect())
		self.redraw()
		self.updateTables()

	def _add_action(self, start, target, node_index):
		xs = start.x()
		ys = start.y()
		xf = target.x()
		yf = target.y()
		angle = math.degrees(math.atan2(ys - yf, xf - xs))
		length = math.hypot(xf - xs, yf - ys)
		angle = round(angle / 15) * 15
		length = round(length / 0.5) * 0.5
		self.shemetype.task["sections"].append(
			self.sect(
				start_from=node_index - 1,
				angle=angle,
				l=length,
			)
		)
		self.redraw()
		self.updateTables()

	def insert_action_impl(self, idx):
		self.shemetype.task["sections"].insert(idx, self.sect())
		self.redraw()
		self.updateTables()

	def del_action_impl(self, idx):
		if not self.shemetype.task["sections"]:
			return
		del self.shemetype.task["sections"][idx]
		self.redraw()
		self.updateTables()

	def inittask(self):
		return {}

	def updateTables(self):
		self.table.updateTable()
		self.table2.updateTable()


class PaintWidget_T1(paintwdg.PaintWidget):
	def __init__(self):
		self.highlited_node = None
		self.highlited_sect = None
		self.grid_enabled = False
		self.hovered_point = None
		self.hovered_point_index = None
		self.pressed_point = None
		self.pressed_point_index = None
		self.target_point = QPointF(0, 0)
		self.c = QPointF(0, 0)
		self.base_length = 80
		super().__init__()
		self.setMouseTracking(True)

	def _point_for_node(self, index):
		if self.scene_interaction is None:
			return None
		bounds = self.scene_interaction.index.bounds("node/{}".format(index))
		if bounds is None:
			return None
		return QPointF(
			bounds.x + bounds.width / 2,
			bounds.y + bounds.height / 2,
		)

	def nodes_numered(self):
		points = []
		index = 0
		while True:
			point = self._point_for_node(index)
			if point is None:
				break
			points.append(point)
			index += 1
		return points

	def get_node_coordinate(self, section_index):
		return self._point_for_node(section_index + 1)

	def paintEventImplementation(self, ev):
		highlighted_section = (
			self.highlited_sect[1] if self.highlited_sect is not None else -1
		)
		preview_target = None
		preview_start = -1
		if self.mouse_pressed and self.pressed_point_index is not None:
			preview_start = self.pressed_point_index
			preview_target = Point(self.target_point.x(), self.target_point.y())
		settings = RodSystem2LayoutSettings(
			width=self.width(),
			height=self.height(),
			hcenter=self.hcenter,
			base_length=self.shemetype.base_length.get(),
			joint_radius=self.shemetype.sharnrad.get(),
			font_size=self.shemetype.font_size.get(),
			line_width=self.shemetype.line_width.get(),
			highlighted_section=highlighted_section,
			hovered_node=(
				self.hovered_point_index
				if self.grid_enabled and self.hovered_point_index is not None
				else -1
			),
			preview_start_node=preview_start,
			preview_target=preview_target,
		)
		metrics = QtTextMetrics()
		scene = RodSystem2LayoutBuilder().build(
			self.shemetype.task,
			settings,
			text_metrics=metrics,
			text_transform=paintool.greek,
			length_text=util.text_prepare_ltext,
		)
		self.scene_interaction = QtSceneInteraction(scene, text_metrics=metrics)
		self.last_scene = scene
		self.base_length = settings.base_length
		root = self._point_for_node(0)
		if root is not None:
			self.c = root
		QtPainterRenderer(metrics).render(scene, self.painter)

	def enterEvent(self, ev):
		self.grid_enabled = True
		self.update()

	def leaveEvent(self, ev):
		self.grid_enabled = False
		self.hovered_point = None
		self.hovered_point_index = None
		self.update()

	def mouseMoveEvent(self, ev):
		self.target_point = QPointF(ev.pos())
		if self.scene_interaction is None:
			return
		hit = self.scene_interaction.hit_test(ev.pos(), kinds=("node",))
		if hit is None:
			self.hovered_point = None
			self.hovered_point_index = None
		else:
			self.hovered_point_index = hit.metadata_value("index")
			self.hovered_point = self._point_for_node(self.hovered_point_index)
		self.update()

	def mousePressEvent(self, ev):
		if self.hovered_point_index is None:
			return
		self.mouse_pressed = True
		self.pressed_point = self.hovered_point
		self.pressed_point_index = self.hovered_point_index
		self.target_point = QPointF(ev.pos())
		self.update()

	def mouseReleaseEvent(self, ev):
		if not self.mouse_pressed:
			return
		self.mouse_pressed = False
		self.target_point = QPointF(ev.pos())
		if self.pressed_point is not None and self.pressed_point_index is not None:
			start = (self.pressed_point - self.c) / self.base_length
			target = (self.target_point - self.c) / self.base_length
			self.shemetype.confwidget._add_action(
				start,
				target,
				self.pressed_point_index,
			)
		self.pressed_point = None
		self.pressed_point_index = None
		self.update()
