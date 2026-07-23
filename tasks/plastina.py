import common
import paintwdg
import paintool
import tablewidget
import taskconf_menu

from sopr_scheme_gener.layouts.plate import PlateLayoutBuilder, PlateLayoutSettings
from sopr_scheme_gener.scene import Color, Fill, Rectangle, Scene, Stroke, metadata
from sopr_scheme_gener.scene.qt import QtPainterRenderer, QtSceneInteraction, QtTextMetrics

from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QLabel, QTextEdit


class ShemeTypeT3(common.SchemeType):
	def __init__(self):
		super().__init__("Пластина")
		self.setwidgets(ConfWidget_T3(self), PaintWidget_T3(), common.TableWidget())


class ConfWidget_T3(common.ConfWidget):
	class sect:
		def __init__(
			self,
			d=1,
			h=1,
			shtrih=False,
			intgran=True,
			dtext="",
			htext="",
			dtext_en=True,
			htext_en=True,
		):
			self.d = d
			self.h = h
			self.shtrih = shtrih
			self.intgran = intgran
			self.dtext = dtext
			self.htext = htext
			self.dtext_en = dtext_en
			self.htext_en = htext_en

	class sectforce:
		def __init__(self, distrib=False):
			self.distrib = distrib

	class betsect:
		def __init__(self, fen="нет", men="нет", sharn="нет"):
			if men == "clean":
				men = "нет"
			self.fen = fen
			self.men = men
			self.sharn = sharn

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": [
				self.sect(d=1.5, h=2),
				self.sect(d=3, h=2, shtrih=True, intgran=False),
				self.sect(d=4.5, h=1, shtrih=True),
			],
			"sectforce": [
				self.sectforce(),
				self.sectforce(),
				self.sectforce(),
			],
			"betsect": [
				self.betsect(),
				self.betsect(),
				self.betsect(),
			],
			"labels": [],
		}

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("d", "float", "Длина")
		self.table.addColumn("dtext", "str", "Текст")
		self.table.addColumn("dtext_en", "bool", "Текст")
		self.table.addColumn("h", "float", "Высота")
		self.table.addColumn("htext", "str", "Текст")
		self.table.addColumn("htext_en", "bool", "Текст")
		self.table.addColumn("shtrih", "bool", "Штрих")
		self.table.addColumn("intgran", "bool", "Вн гран")
		self.table.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table1.addColumn("distrib", "bool", "Распр. нагрузка")
		self.table1.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("fen", "list", "Сила", variant=["нет", "+", "-"])
		self.table2.addColumn("men", "list", "Момент", variant=["нет", "+", "-"])
		self.table2.addColumn("sharn", "list", "Шарнир", variant=["нет", "1", "2"])
		self.table2.updateTable()

		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Распределённые силы:"))
		self.vlayout.addWidget(self.table1)
		self.vlayout.addWidget(QLabel("Локальные силы:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)
		self.table1.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)
		self.vlayout.addWidget(self.shemetype.texteditor)

	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.base_h = self.sett.add("Базовая толщина:", "int", "20")
		self.shemetype.zadelka = self.sett.add("Заделка:", "bool", True)
		self.shemetype.axis = self.sett.add("Центральная ось:", "bool", True)
		self.shemetype.zadelka_len = self.sett.add("Длина заделки:", "float", "30")
		self.shemetype.dimlines_start_step = self.sett.add(
			"Отступ размерных линий:", "float", "20"
		)
		self.shemetype.dimlines_step = self.sett.add(
			"Шаг размерных линий:", "float", "40"
		)
		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "13")
		self.sett.updated.connect(self.redraw)

		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)

		self.update_interface()
		self.setLayout(self.vlayout)

	def add_action_impl(self):
		self.shemetype.task["sections"].append(self.sect())
		self.shemetype.task["betsect"].append(self.betsect())
		self.shemetype.task["sectforce"].append(self.sectforce())
		self.redraw()
		self.updateTables()

	def insert_action_impl(self, idx):
		self.shemetype.task["sections"].insert(idx, self.sect())
		self.shemetype.task["betsect"].insert(idx, self.betsect())
		self.shemetype.task["sectforce"].insert(idx, self.sectforce())
		self.redraw()
		self.updateTables()

	def del_action_impl(self, idx):
		if len(self.shemetype.task["sections"]) == 1:
			return
		del self.shemetype.task["sections"][idx]
		del self.shemetype.task["betsect"][idx]
		del self.shemetype.task["sectforce"][idx]
		self.redraw()
		self.updateTables()

	def inittask(self):
		return {}

	def updateTables(self):
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()


class PaintWidget_T3(paintwdg.PaintWidget):
	def __init__(self):
		super().__init__()
		self.enable_common_mouse_events()

	def paintEventImplementation(self, ev):
		settings = PlateLayoutSettings(
			width=self.width(),
			height=self.height(),
			hcenter=self.hcenter,
			base_height=self.shemetype.base_h.get(),
			fixed_ends=self.shemetype.zadelka.get(),
			axis=self.shemetype.axis.get(),
			fixed_end_length=self.shemetype.zadelka_len.get(),
			dimension_start=self.shemetype.dimlines_start_step.get(),
			dimension_step=self.shemetype.dimlines_step.get(),
			arrow_size=self.shemetype.arrow_size.get(),
			font_size=self.shemetype.font_size.get(),
			line_width=self.shemetype.line_width.get(),
		)
		scene = PlateLayoutBuilder().build(
			self.shemetype.task,
			settings,
			text_metrics=QtTextMetrics(),
			text_transform=paintool.greek,
		)
		max_width = max(section.d for section in self.sections())
		left_span = 50
		right_span = 50
		if settings.fixed_ends:
			left_span += settings.base_height + settings.fixed_end_length
			right_span += settings.base_height + settings.fixed_end_length
		self.labels_center = QPointF(
			settings.width / 2 + left_span - right_span,
			settings.hcenter
			+ (
				100
				- (
					100
					+ len(self.sections()) * settings.dimension_step
					+ settings.dimension_start
				)
			)
			/ 2,
		)
		self.labels_width_scale = (
			settings.width - left_span - right_span
		) / max_width
		self.scene_interaction = QtSceneInteraction(
			scene,
			text_metrics=QtTextMetrics(),
		)
		if self.selected_label_id:
			bounds = self.scene_interaction.index.bounds(self.selected_label_id)
			if bounds is None:
				self.selected_label_id = None
			else:
				scene = Scene(
					scene.viewport,
					scene.objects
					+ (
						Rectangle(
							bounds,
							Stroke(),
							Fill(Color(0, 255, 0)),
							object_id=self.selected_label_id + "/hover",
							metadata=metadata(kind="hover"),
						),
					),
					content_bounds=scene.content_bounds,
					background=scene.background,
				)
		self.last_scene = scene
		QtPainterRenderer().render(scene, self.painter)
