"""Qt widget adapter for the eccentric-bending task."""

import common
import paintwdg
import paintool
import tablewidget
import taskconf_menu

from PyQt5.QtWidgets import QLabel, QTextEdit

from sopr_scheme_gener.layouts.eccentric_bending import (
	EccentricBendingLayoutBuilder,
	EccentricBendingLayoutSettings,
)
from sopr_scheme_gener.scene.qt import QtPainterRenderer, QtSceneInteraction, QtTextMetrics


class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Внецентренный изгиб")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())


class ConfWidget(common.ConfWidget):
	class sect:
		def __init__(
			self,
			Fx="нет",
			Fy="нет",
			Fz="нет",
			Fx_txt="",
			Fy_txt="",
			Fz_txt="",
			Fx_txt_alttxt="1",
			Fy_txt_alttxt="1",
			Fz_txt_alttxt="1",
		):
			self.Fx = Fx
			self.Fy = Fy
			self.Fz = Fz
			self.Fx_txt = Fx_txt
			self.Fy_txt = Fy_txt
			self.Fz_txt = Fz_txt
			self.Fx_txt_alttxt = "1" if Fx_txt_alttxt is None else Fx_txt_alttxt
			self.Fy_txt_alttxt = "1" if Fy_txt_alttxt is None else Fy_txt_alttxt
			self.Fz_txt_alttxt = "1" if Fz_txt_alttxt is None else Fz_txt_alttxt

	def create_task_structure(self):
		self.shemetype.task = {"sections": [self.sect() for _ in range(8)]}

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
		self.shemetype.section_type = self.sett.add(
			"Тип сечения:",
			"list",
			defval=3,
			variant=["прямоугольник", "круг", "ромб", "труба"],
		)
		self.shemetype.console = self.sett.add("Длина Консоли:", "int", "100")
		self.shemetype.zrot = self.sett.add("Направление:", "int", "30")
		self.shemetype.xrot = self.sett.add("Подъём:", "int", "30")
		self.shemetype.L = self.sett.add("Длина:", "int", "600")
		self.shemetype.offdown = self.sett.add(
			"Вынос разм. линий:", "int", "100"
		)
		self.shemetype.arrlen = self.sett.add("Длина Стрелок:", "int", "60")
		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.sett.updated.connect(self.redraw)
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		self.update_interface()
		self.setLayout(self.vlayout)

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn(
			"Fx",
			"list",
			variant=["нет", "слева +", "слева -", "справа +", "справа -"],
		)
		self.table.addColumn("Fx_txt", "str")
		self.table.addColumn(
			"Fx_txt_alttxt", "list", variant=["1", "2", "3", "4", "5", "6"]
		)
		self.table.addColumn(
			"Fy",
			"list",
			variant=["нет", "сверху +", "сверху -", "снизу +", "снизу -"],
		)
		self.table.addColumn("Fy_txt", "str")
		self.table.addColumn(
			"Fy_txt_alttxt", "list", variant=["1", "2", "3", "4", "5", "6"]
		)
		self.table.addColumn("Fz", "list", variant=["нет", "+", "-"])
		self.table.addColumn("Fz_txt", "str")
		self.table.addColumn(
			"Fz_txt_alttxt", "list", variant=["1", "2", "3", "4", "5", "6"]
		)
		self.table.updateTable()
		self.table.updated.connect(self.redraw)
		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(self.sett)
		self.vlayout.addWidget(self.shemetype.texteditor)

	def inittask(self):
		return {}


class PaintWidget(paintwdg.PaintWidget):
	def __init__(self):
		super().__init__()
		self.last_scene = None

	def paintEventImplementation(self, ev):
		settings = EccentricBendingLayoutSettings(
			width=self.width(),
			height=self.height(),
			hcenter=self.hcenter,
			x_size=self.shemetype.x.get(),
			y_size=self.shemetype.y.get(),
			x_text=self.shemetype.x_txt.get(),
			y_text=self.shemetype.y_txt.get(),
			length_text=self.shemetype.l_txt.get(),
			axonometric=self.shemetype.axonom.get(),
			sixty_degrees=self.shemetype.axonom_deg.get(),
			section_type=self.shemetype.section_type.get(),
			console_length=self.shemetype.console.get(),
			z_rotation_degrees=self.shemetype.zrot.get(),
			x_rotation_degrees=self.shemetype.xrot.get(),
			rod_length=self.shemetype.L.get(),
			dimension_offset=self.shemetype.offdown.get(),
			force_length=self.shemetype.arrlen.get(),
			font_size=self.shemetype.font_size.get(),
			line_width=self.shemetype.line_width.get(),
		)
		metrics = QtTextMetrics()
		scene = EccentricBendingLayoutBuilder().build(
			self.shemetype.task,
			settings,
			metrics,
			text_transform=paintool.greek,
		)
		self.last_scene = scene
		self.scene_interaction = QtSceneInteraction(scene, text_metrics=metrics)
		QtPainterRenderer(metrics).render(scene, self.painter)
