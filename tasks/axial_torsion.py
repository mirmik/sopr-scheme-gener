"""Qt widget adapter for the axial-torsion task."""

import common
import paintwdg
import paintool
import tablewidget
import taskconf_menu

from PyQt5.QtWidgets import QLabel, QTextEdit

from sopr_scheme_gener.layouts.axial_torsion import (
	AXIAL,
	TORSION_DIAMETER,
	TORSION_STIFFNESS,
	AxialTorsionLayoutBuilder,
	AxialTorsionLayoutSettings,
)
from sopr_scheme_gener.scene.qt import QtPainterRenderer, QtSceneInteraction, QtTextMetrics


SUBTYPE_RASTYAZHENIE_SJATIE = AXIAL
SUBTYPE_KRUCHENIE_1 = TORSION_STIFFNESS
SUBTYPE_KRUCHENIE_2 = TORSION_DIAMETER


class ShemeTypeT0(common.SchemeType):
	def __init__(self):
		super().__init__("Растяжение/сжатие/кручение стержня")
		self.setwidgets(ConfWidget_T0(self), PaintWidget_T0(), common.TableWidget())


class ConfWidget_T0(common.ConfWidget):
	"""Настройки растяжения/сжатия и кручения стержня."""

	class sect:
		def __init__(
			self,
			A=1,
			GIk=1,
			d=1,
			l=1,
			E=1,
			text="",
			dtext="",
			delta=False,
			label="",
			label_height=20,
		):
			self.label = label
			self.label_height = label_height
			self.A = A
			self.GIk = GIk
			self.d = d
			self.l = l
			self.E = E
			self.text = text
			self.dtext = dtext
			self.delta = delta

	class sectforce:
		def __init__(self, mkr="нет", mkrT="", Fr="нет"):
			self.mkr = mkr
			self.mkrT = mkrT
			self.Fr = Fr

	class betsect:
		def __init__(
			self,
			F="нет",
			Fstyle="от узла",
			Mkr="нет",
			T="",
			label="",
			label_up=False,
			label_off="справа",
		):
			self.F = F
			self.Fstyle = Fstyle
			self.Mkr = Mkr
			self.T = T
			self.label = label
			self.label_up = label_up
			self.label_off = label_off

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": [
				self.sect(A=1, l=1, E=1),
				self.sect(A=2, l=1, E=1),
				self.sect(A=1, l=2, E=1),
			],
			"betsect": [
				self.betsect(),
				self.betsect(),
				self.betsect(),
				self.betsect(),
			],
			"sectforce": [
				self.sectforce(),
				self.sectforce(),
				self.sectforce(),
			],
		}

	def __init__(self, sheme):
		super().__init__(sheme, noinitbuttons=True)
		self.presett = taskconf_menu.TaskConfMenu()
		self.shemetype.task_subtype = self.presett.add(
			"Подтип задачи:",
			"list",
			variant=[
				"Растяжение/сжатие",
				"Кручение (крутильная жесткость)",
				"Кручение (диаметры)",
			],
			vars=[
				SUBTYPE_RASTYAZHENIE_SJATIE,
				SUBTYPE_KRUCHENIE_1,
				SUBTYPE_KRUCHENIE_2,
			],
			defval=0,
			handler=self.clean_and_update_interface,
		)

		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.axis = self.sett.add("Нарисовать ось:", "bool", True)
		self.shemetype.zleft = self.sett.add("Заделка слева:", "bool", False)
		self.shemetype.zright = self.sett.add("Заделка справа:", "bool", False)
		self.shemetype.razm = self.sett.add("Размерные линии:", "bool", True)
		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.base_section_height = self.sett.add(
			"Базовая высота секции:", "int", "40"
		)
		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "20")
		self.shemetype.dimlines_start_step = self.sett.add(
			"Отступ размерных линий:", "int", "40"
		)
		self.shemetype.left_zone = self.sett.add("Отступ слева:", "int", "30")
		self.shemetype.right_zone = self.sett.add("Отступ справа:", "int", "30")
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.sett.updated.connect(self.redraw)

		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		self.update_interface()
		self.setLayout(self.vlayout)

	def update_interface(self):
		subtype = self.shemetype.task_subtype.get()
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		if subtype == SUBTYPE_RASTYAZHENIE_SJATIE:
			self.table.addColumn("A", "float", "Площадь")
		elif subtype == SUBTYPE_KRUCHENIE_1:
			self.table.addColumn("GIk", "float", "КрутЖестк")
		else:
			self.table.addColumn("d", "float", "Диаметр")
			self.table.addColumn("dtext", "str", "Д.Текст")
		self.table.addColumn("l", "float", "Длина")
		if subtype == SUBTYPE_RASTYAZHENIE_SJATIE:
			self.table.addColumn("E", "float", "МодульЮнга")
		self.table.addColumn("text", "str", "Текст")
		self.table.addColumn("label", "str", "Метка")
		if subtype == SUBTYPE_RASTYAZHENIE_SJATIE:
			self.table.addColumn("delta", "bool", "Зазор")
		self.table.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		if subtype == SUBTYPE_RASTYAZHENIE_SJATIE:
			self.table1.addColumn(
				"Fr", "list", variant=["нет", "+", "-"]
			)
		else:
			self.table1.addColumn(
				"mkr", "list", variant=["нет", "+", "-"]
			)
		self.table1.addColumn("mkrT", "str", "Текст")
		self.table1.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		if subtype == SUBTYPE_RASTYAZHENIE_SJATIE:
			self.table2.addColumn("F", "list", variant=["нет", "+", "-"])
			self.table2.addColumn(
				"Fstyle",
				"list",
				"Рис.",
				variant=["от узла", "к узлу", "выносн."],
			)
		else:
			self.table2.addColumn(
				"Mkr", "list", variant=["нет", "+", "-"]
			)
		self.table2.addColumn("T", "str", "Текст")
		self.table2.addColumn("label", "str", "Метка")
		self.table2.addColumn(
			"label_off",
			"list",
			"МеткаПолож.",
			variant=["справа", "справа-сверху", "слева-снизу"],
		)
		self.table2.updateTable()

		for table, handler in (
			(self.table, self.hover_sect),
			(self.table1, self.hover_sect),
			(self.table2, self.hover_node),
		):
			table.updated.connect(self.redraw)
			table.hover_hint.connect(handler)
			table.unhover.connect(self.table_unhover)

		self.vlayout.addWidget(self.presett)
		self.add_buttons_to_layout(self.vlayout)
		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Распределенные силы:"))
		self.vlayout.addWidget(self.table1)
		self.vlayout.addWidget(QLabel("Локальные силы, метки узлов:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)
		self.vlayout.addWidget(self.shemetype.texteditor)

	def hover_node(self, row, column, hint):
		self.shemetype.paintwidget.highlited_node = (hint, row)
		self.redraw()

	def hover_sect(self, row, column, hint):
		self.shemetype.paintwidget.highlited_sect = (hint, row)
		self.redraw()

	def table_unhover(self):
		self.shemetype.paintwidget.highlited_sect = None
		self.shemetype.paintwidget.highlited_node = None
		self.redraw()

	def serialize_list(self):
		return [
			("presett", self.presett),
			("task", self.shemetype.task),
			("sett", self.sett),
			("texteditor", self.shemetype.texteditor),
		]

	def add_action_impl(self):
		self.sections().append(self.sect())
		self.sectforces().append(self.sectforce())
		self.bsections().append(self.betsect())
		self.redraw()
		self.updateTables()

	def insert_action_impl(self, idx):
		self.sections().insert(idx, self.sect())
		self.sectforces().insert(idx, self.sectforce())
		self.bsections().insert(idx, self.betsect())
		self.redraw()
		self.updateTables()

	def del_action_impl(self, idx):
		if len(self.sections()) == 1:
			return
		del self.sections()[idx]
		del self.sectforces()[idx]
		del self.bsections()[idx]
		self.redraw()
		self.updateTables()

	def updateTables(self):
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def inittask(self):
		return {}


class PaintWidget_T0(paintwdg.PaintWidget):
	def __init__(self):
		super().__init__()
		self.highlited_node = None
		self.highlited_sect = None
		self.last_scene = None

	def paintEventImplementation(self, ev):
		highlighted_section = (
			self.highlited_sect[1] if self.highlited_sect is not None else -1
		)
		highlighted_node = (
			self.highlited_node[1] if self.highlited_node is not None else -1
		)
		settings = AxialTorsionLayoutSettings(
			width=self.width(),
			height=self.height(),
			hcenter=self.hcenter,
			subtype=self.shemetype.task_subtype.get(),
			axis=self.shemetype.axis.get(),
			left_fixed=self.shemetype.zleft.get(),
			right_fixed=self.shemetype.zright.get(),
			dimensions=self.shemetype.razm.get(),
			base_section_height=self.shemetype.base_section_height.get(),
			arrow_size=self.shemetype.arrow_size.get(),
			dimension_offset=self.shemetype.dimlines_start_step.get(),
			left_margin=self.shemetype.left_zone.get(),
			right_margin=self.shemetype.right_zone.get(),
			font_size=self.shemetype.font_size.get(),
			line_width=self.shemetype.line_width.get(),
			highlighted_section=highlighted_section,
			highlighted_node=highlighted_node,
		)
		metrics = QtTextMetrics()
		scene = AxialTorsionLayoutBuilder().build(
			self.shemetype.task,
			settings,
			metrics,
			text_transform=paintool.greek,
			pretty_value=common.pretty_str,
		)
		self.last_scene = scene
		self.scene_interaction = QtSceneInteraction(scene, text_metrics=metrics)
		QtPainterRenderer(metrics).render(scene, self.painter)
