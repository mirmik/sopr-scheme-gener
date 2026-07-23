"""Qt widget adapter for the shafts-pipes task."""

import common
import paintwdg
import paintool
import tablewidget
import taskconf_menu

from PyQt5.QtWidgets import QTextEdit

from sopr_scheme_gener.layouts.shafts_pipes import (
	ShaftsPipesLayoutBuilder,
	ShaftsPipesLayoutSettings,
)
from sopr_scheme_gener.scene.qt import (
	QtGraphicsSceneRenderer,
	QtSceneInteraction,
	QtTextMetrics,
)


class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Валы и трубки")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())


class ConfWidget(common.ConfWidget):
	class sect:
		def __init__(self, D=30, Dtext="d"):
			self.D = D
			self.Dtext = Dtext

	def __init__(self, scheme):
		super().__init__(scheme, noinitbuttons=True)
		self.has_central = False
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)

		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.has_central = self.sett.add(
			"Центральная секция:", "bool", False
		)
		self.shemetype.external_camera = self.sett.add(
			"Внешняя камера:", "bool", True
		)
		self.shemetype.socr = self.sett.add("Сокращённая длина:", "bool", False)
		self.shemetype.ztube = self.sett.add("Полая труба:", "bool", True)
		self.shemetype.razrez = self.sett.add(
			"Тип торца:",
			"list",
			0,
			variant=["труба", "камера", "разрез"],
		)
		self.sett.add_delimiter()
		self.shemetype.uncentered_force = self.sett.add(
			"Сила:", "list", 0, variant=["нет", "+", "-"]
		)
		self.shemetype.is_uncentered_force = self.sett.add(
			"Внецентренная сила:", "bool", True
		)
		self.shemetype.is_uncentered_force_alternate = self.sett.add(
			"сверху / снизу:", "bool", False
		)
		self.shemetype.text_force = self.sett.add("Текст силы:", "str", "P")
		self.sett.add_delimiter()
		self.shemetype.invert_moment = self.sett.add(
			"Направление момента:",
			"list",
			0,
			variant=["нет", "+", "-"],
		)
		self.shemetype.text_moment = self.sett.add("Текст момента:", "str", "M")
		self.shemetype.torc_moment = self.sett.add(
			"Моменты на торцах:", "bool", False
		)
		self.sett.add_delimiter()
		self.shemetype.invert_izgmoment = self.sett.add(
			"Направление изг. момента:",
			"list",
			0,
			variant=["нет", "+", "-"],
		)
		self.shemetype.text_izgmoment = self.sett.add(
			"Текст изг. момента:", "str", "M"
		)
		self.shemetype.var_izgmoment = self.sett.add(
			"Вариант изображения:",
			"list",
			0,
			variant=["круговой", "угловой"],
		)
		self.sett.add_delimiter()
		self.shemetype.text_pressure = self.sett.add(
			"Метка давления внешн.:", "str", "p"
		)
		self.shemetype.text_pressure_in = self.sett.add(
			"Метка давления внутр.:", "str", ""
		)
		self.shemetype.htext = self.sett.add(
			"Текст толщины трубы", "str", "h"
		)
		self.shemetype.Ltext = self.sett.add(
			"Размер расчётной секции", "str", ""
		)
		self.sett.add_delimiter()
		self.shemetype.camera_w = self.sett.add(
			"Толщина камеры:", "int", "25"
		)
		self.shemetype.tubewidth = self.sett.add(
			"Толщина трубы:", "int", "10"
		)
		self.shemetype.wborder = self.sett.add(
			"Поля по горизонтали:", "float", "10"
		)
		self.shemetype.hborder = self.sett.add(
			"Поля по вертикали:", "float", "20"
		)
		self.sett.updated.connect(self.redraw)
		self.update_interface()

	def redraw(self):
		if (
			self.shemetype.has_central.get()
			and len(self.shemetype.task["sections"]) != 2
		):
			self.shemetype.task["sections"].append(self.sect())
			self.clean_and_update_interface()
		if (
			not self.shemetype.has_central.get()
			and len(self.shemetype.task["sections"]) != 1
		):
			del self.shemetype.task["sections"][1]
			self.clean_and_update_interface()
		super().redraw()

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("D", "float")
		self.table.addColumn("Dtext", "str")
		self.table.updateTable()
		self.table.updated.connect(self.redraw)
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(self.sett)
		self.vlayout.addWidget(self.shemetype.texteditor)
		self.setLayout(self.vlayout)

	def create_task_structure(self):
		self.shemetype.task = {"sections": [self.sect(40)]}

	def inittask(self):
		return {}


class PaintWidget(paintwdg.PaintWidget):
	def __init__(self):
		super().__init__()
		self.no_text_render = True
		self.no_resize = True
		self.last_scene = None

	def paintEventImplementation(self, ev):
		settings = ShaftsPipesLayoutSettings(
			has_central=self.shemetype.has_central.get(),
			external_camera=self.shemetype.external_camera.get(),
			short_length=self.shemetype.socr.get(),
			hollow=self.shemetype.ztube.get(),
			end_type=self.shemetype.razrez.get(),
			force_direction=self.shemetype.uncentered_force.get(),
			eccentric_force=self.shemetype.is_uncentered_force.get(),
			force_below=self.shemetype.is_uncentered_force_alternate.get(),
			force_text=self.shemetype.text_force.get(),
			torque_direction=self.shemetype.invert_moment.get(),
			torque_text=self.shemetype.text_moment.get(),
			torque_at_ends=self.shemetype.torc_moment.get(),
			bending_direction=self.shemetype.invert_izgmoment.get(),
			bending_text=self.shemetype.text_izgmoment.get(),
			bending_style=self.shemetype.var_izgmoment.get(),
			pressure_text=self.shemetype.text_pressure.get(),
			inner_pressure_text=self.shemetype.text_pressure_in.get(),
			thickness_text=self.shemetype.htext.get(),
			length_text=self.shemetype.Ltext.get(),
			camera_width=self.shemetype.camera_w.get(),
			tube_width=self.shemetype.tubewidth.get(),
			horizontal_border=self.shemetype.wborder.get(),
			vertical_border=self.shemetype.hborder.get(),
			note=self.shemetype.texteditor.toPlainText(),
			font_size=self.shemetype.font_size.get(),
			line_width=self.shemetype.line_width.get(),
		)
		metrics = QtTextMetrics()
		scene = ShaftsPipesLayoutBuilder().build(
			self.shemetype.task,
			settings,
			metrics,
			text_transform=paintool.greek,
		)
		self.last_scene = scene
		self.scene_interaction = QtSceneInteraction(scene, text_metrics=metrics)
		QtGraphicsSceneRenderer(metrics, one_to_one=True).render(
			scene,
			self.painter,
		)
		self.resize_after_render(scene.viewport.width, scene.viewport.height)
