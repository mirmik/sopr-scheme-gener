import common
import paintwdg

import util
import tablewidget
import paintool
import taskconf_menu

from sopr_scheme_gener.layouts.rod_system_1 import (
	RodSystem1LayoutBuilder,
	RodSystem1LayoutSettings,
)
from sopr_scheme_gener.scene.qt import QtPainterRenderer, QtSceneInteraction, QtTextMetrics

from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QLabel, QTextEdit


class ShemeTypeT2(common.SchemeType):
	def __init__(self):
		super().__init__("Стержневая система (Тип 1)")
		self.setwidgets(ConfWidget_T2(self), PaintWidget_T2(), common.TableWidget())


class ConfWidget_T2(common.ConfWidget):
	class sect:
		def __init__(self, l=1, label="", label_height=20, dims=True):
			self.l = l
			self.label = label
			self.label_height = label_height
			self.dims = dims

	class betsect:
		def __init__(
			self,
			l=0,
			A=1,
			lbl="",
			sectlbl="",
			F="нет",
			Ftxt="",
			sterzn_text1="",
			sterzn_text2="",
			sterzn_text_horizontal=True,
			sterzn_text_alt=False,
			sterzn_text_off=0,
			F2="нет",
			F2txt="",
			zazor=False,
			zazor_txt="\\Delta",
			sharn="нет",
		):
			self.l = l
			self.A = A
			self.lbl = lbl
			self.sectlbl = sectlbl
			self.sterzn_text1 = sterzn_text1
			self.sterzn_text2 = sterzn_text2
			self.sterzn_text_horizontal = sterzn_text_horizontal
			self.sterzn_text_alt = sterzn_text_alt
			self.sterzn_text_off = sterzn_text_off
			self.F = F
			self.Ftxt = Ftxt
			self.F2 = F2
			self.F2txt = F2txt
			self.zazor = zazor
			self.zazor_txt = zazor_txt
			self.sharn = sharn

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": [
				self.sect(l=1.5),
				self.sect(l=1),
				self.sect(l=1),
			],
			"betsect": [
				self.betsect(l=0),
				self.betsect(l=1),
				self.betsect(l=2, F="+"),
				self.betsect(l=-2),
			],
		}

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("l", "float", "Длина секции")
		self.table.addColumn("label", "str", "Подпись")
		self.table.addColumn("label_height", "float", "Расположение подписи")
		self.table.addColumn("dims", "bool", "Отрисовка разм.")
		self.table.updateTable()

		self.table3 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table3.addColumn("l", "float", "Длина опоры")
		self.table3.addColumn("A", "float", "Площадь(А)")
		self.table3.addColumn("sterzn_text1", "str", "Текст1")
		self.table3.addColumn("sterzn_text2", "str", "Текст2")
		self.table3.addColumn("sterzn_text_off", "float", "ТСмещ.")
		self.table3.addColumn("sterzn_text_horizontal", "bool", "Гориз./Верт.")
		self.table3.addColumn("sterzn_text_alt", "bool", "Слева./Справа.")
		self.table3.addColumn("sharn", "list", "Шарнир", variant=["нет", "1", "2"])
		self.table3.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("lbl", "str", "М.Стержень")
		self.table2.addColumn("F", "list", "Сила", variant=["нет", "+", "-"])
		self.table2.addColumn("Ftxt", "str", "Текст")
		self.table2.addColumn("F2", "list", "Ст.Сила", variant=["нет", "+", "-"])
		self.table2.addColumn("F2txt", "str", "Ст.Текст")
		self.table2.addColumn("zazor", "bool", "Зазор")
		self.table2.addColumn("zazor_txt", "str", "З.Текст")
		self.table2.updateTable()

		self.vlayout.addWidget(QLabel("Геометрия секций:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Геометрия стержня, шарниры:"))
		self.vlayout.addWidget(self.table3)
		self.vlayout.addWidget(QLabel("Силы прилож. к стержню, зазоры, метки:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)
		self.table2.updated.connect(self.redraw)
		self.table3.updated.connect(self.redraw)
		self.table2.hover_hint.connect(self.hover_node)
		self.table3.hover_hint.connect(self.hover_node)
		self.table2.unhover.connect(self.table_unhover)
		self.table3.unhover.connect(self.table_unhover)
		self.vlayout.addWidget(self.shemetype.texteditor)

	def hover_node(self, row, column, hint):
		self.shemetype.paintwidget.highlited_node = (hint, row)
		self.redraw()
		self.save_row = row
		self.save_hint = hint

	def table_unhover(self):
		self.shemetype.paintwidget.highlited_node = None
		self.redraw()

	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		self.sett.add_delimiter()
		self.shemetype.zadelka1 = self.sett.add(
			"Шарнир слева:",
			"list",
			serlbl="Заделка:",
			defval=0,
			variant=["нет", "1", "2"],
		)
		self.shemetype.zadelka2 = self.sett.add(
			"Шарнир справа:",
			"list",
			defval=0,
			variant=["нет", "1", "2"],
			noaddtog=True,
		)
		self.sett.add_delimiter()
		self.shemetype.base_height = self.sett.add("Базовая толщина:", "int", "22")
		self.shemetype.dimlines_level = self.sett.add(
			"Уровень размерных линий:", "int", "80"
		)
		self.shemetype.dimlines_level2 = self.sett.add("Отступ справа:", "int", "60")
		self.shemetype.sterzn_off = self.sett.add(
			"Вынос стрелок для сил в стержнях:", "int", "28"
		)
		self.shemetype.arrow_size = self.sett.add("Размер стрелок сил:", "int", "14")
		self.sett.updated.connect(self.redraw)
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		self.update_interface()
		self.setLayout(self.vlayout)

	def add_action_impl(self):
		self.shemetype.task["sections"].append(self.sect())
		self.shemetype.task["betsect"].append(self.betsect())
		self.redraw()
		self.updateTables()

	def insert_action_impl(self, idx):
		self.shemetype.task["sections"].insert(idx, self.sect())
		self.shemetype.task["betsect"].insert(idx, self.betsect())
		self.redraw()
		self.updateTables()

	def del_action_impl(self, idx):
		if len(self.shemetype.task["sections"]) == 1:
			return
		del self.shemetype.task["sections"][idx]
		del self.shemetype.task["betsect"][idx]
		self.redraw()
		self.updateTables()

	def inittask(self):
		return {}

	def updateTables(self):
		self.table.updateTable()
		self.table2.updateTable()
		self.table3.updateTable()


class PaintWidget_T2(paintwdg.PaintWidget):
	def __init__(self):
		self.highlited_node = None
		super().__init__()

	def paintEventImplementation(self, ev):
		highlighted_node = (
			self.highlited_node[1] if self.highlited_node is not None else -1
		)
		settings = RodSystem1LayoutSettings(
			width=self.width(),
			height=self.height(),
			hcenter=self.hcenter,
			text_height=self.text_height,
			base_height=self.shemetype.base_height.get(),
			dimension_level=self.shemetype.dimlines_level.get(),
			right_margin=self.shemetype.dimlines_level2.get(),
			rod_force_offset=self.shemetype.sterzn_off.get(),
			arrow_size=self.shemetype.arrow_size.get(),
			font_size=self.shemetype.font_size.get(),
			line_width=self.shemetype.line_width.get(),
			left_support=self.shemetype.zadelka1.get(),
			right_support=self.shemetype.zadelka2.get(),
			highlighted_node=highlighted_node,
		)
		metrics = QtTextMetrics()
		scene = RodSystem1LayoutBuilder().build(
			self.shemetype.task,
			settings,
			text_metrics=metrics,
			text_transform=paintool.greek,
			length_text=util.text_prepare_ltext,
		)
		self.scene_interaction = QtSceneInteraction(scene, text_metrics=metrics)
		self.last_scene = scene
		QtPainterRenderer(metrics).render(scene, self.painter)
