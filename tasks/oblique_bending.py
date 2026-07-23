"""Qt widget adapter for the oblique-bending task."""

import common
import paintwdg
import paintool
import sections
import tablewidget
import taskconf_menu
import util

from PyQt5.QtWidgets import QLabel, QTextEdit

from sopr_scheme_gener.layouts.beam_sections import BeamSectionSpec
from sopr_scheme_gener.layouts.oblique_bending import (
	ObliqueBendingLayoutBuilder,
	ObliqueBendingLayoutSettings,
)
from sopr_scheme_gener.scene.qt import QtPainterRenderer, QtSceneInteraction, QtTextMetrics


class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Косой изгиб")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())


class ConfWidget(common.ConfWidget):
	class sect:
		def __init__(self, l=1):
			self.l = l

	class betsect:
		def __init__(
			self,
			xF="нет",
			xFtxt="",
			yF="нет",
			yFtxt="",
			xM="нет",
			xMtxt="",
			yM="нет",
			yMtxt="",
			xS="нет",
			yS="нет",
			zS="нет",
		):
			self.xF = xF
			self.yF = yF
			self.xFtxt = xFtxt
			self.yFtxt = yFtxt
			self.xM = xM
			self.yM = yM
			self.xMtxt = xMtxt
			self.yMtxt = yMtxt
			self.xS = xS
			self.yS = yS
			self.zS = zS

	class sectforce:
		def __init__(self, xF="нет", xFtxt="", yF="нет", yFtxt=""):
			self.xF = xF
			self.yF = yF
			self.xFtxt = xFtxt
			self.yFtxt = yFtxt

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": [self.sect(l=1), self.sect(l=2)],
			"betsect": [self.betsect(), self.betsect(), self.betsect()],
			"sectforce": [self.sectforce(), self.sectforce()],
		}

	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.console = self.sett.add(
			"Консоль:", ("bool", "int"), (True, "30")
		)
		self.shemetype.axonom = self.sett.add("Аксонометрия:", "bool", False)
		self.shemetype.axonom_deg = self.sett.add(
			"45 градусов:", "bool", False
		)
		self.shemetype.xoffset = self.sett.add("Смещение:", "int", "30")
		self.shemetype.zrot = self.sett.add("Направление:", "int", "30")
		self.shemetype.xrot = self.sett.add("Подъём:", "int", "20")
		self.shemetype.L = self.sett.add("Длина:", "int", "600")
		self.shemetype.offdown = self.sett.add(
			"Вынос разм. линий:", "int", "100"
		)
		self.shemetype.arrlen = self.sett.add("Длина Стрелок:", "int", "60")
		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.section_container = self.sett.add_widget(
			sections.SectionContainer(None)
		)
		self.shemetype.section_container.updated.connect(self.redraw)
		self.shemetype.arrow_size = self.sett.add(
			"Размер стрелки:", "int", "15"
		)
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.sett.updated.connect(self.redraw)
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		self.update_interface()
		self.setLayout(self.vlayout)

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("l", "float", "Длина")
		self.table.updateTable()
		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn(
			"xF", "list", note="Fx", variant=["нет", "+1", "+2", "-1", "-2"]
		)
		self.table2.addColumn("xFtxt", "str", "Fx")
		self.table2.addColumn(
			"yF", "list", "Fy", variant=["нет", "+1", "+2", "-1", "-2"]
		)
		self.table2.addColumn("yFtxt", "str", "Fy", "yF")
		self.table2.addColumn("xM", "list", "Mx", variant=["нет", "+", "-"])
		self.table2.addColumn("xMtxt", "str", "Mx")
		self.table2.addColumn("yM", "list", "My", variant=["нет", "+", "-"])
		self.table2.addColumn("yMtxt", "str", "My")
		for name, title in (("xS", "Sx"), ("yS", "Sy"), ("zS", "Sz")):
			self.table2.addColumn(
				name,
				"list",
				title,
				variant=["нет", "+1", "-1", "+2", "-2"],
			)
		self.table2.updateTable()
		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table1.addColumn(
			"xF", "list", "Fx", variant=["нет", "+", "-"]
		)
		self.table1.addColumn("xFtxt", "str", "Fx")
		self.table1.addColumn(
			"yF", "list", "Fy", variant=["нет", "+", "-"]
		)
		self.table1.addColumn("yFtxt", "str", "Fy")
		self.table1.updateTable()
		self.vlayout.addWidget(QLabel("Геометрия:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Локальные силы:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(QLabel("Распределенные силы:"))
		self.vlayout.addWidget(self.table1)
		self.vlayout.addWidget(self.sett)
		for table in (self.table, self.table1, self.table2):
			table.updated.connect(self.redraw)
		self.vlayout.addWidget(self.shemetype.texteditor)

	def add_action_impl(self):
		self.sections().append(self.sect())
		self.shemetype.task["sectforce"].append(self.sectforce())
		self.shemetype.task["betsect"].append(self.betsect())
		self.redraw()
		self.updateTables()

	def insert_action_impl(self, idx):
		self.sections().insert(idx, self.sect())
		self.shemetype.task["sectforce"].insert(idx, self.sectforce())
		self.shemetype.task["betsect"].insert(idx, self.betsect())
		self.redraw()
		self.updateTables()

	def del_action_impl(self, idx):
		if len(self.sections()) == 1:
			return
		del self.sections()[idx]
		del self.shemetype.task["betsect"][idx]
		del self.shemetype.task["sectforce"][idx]
		self.redraw()
		self.updateTables()

	def updateTables(self):
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def inittask(self):
		return {}


def _section_spec(container):
	section_type = container.section_type.get()
	if section_type == sections.MAIN_SECTION_TYPE:
		general = container.main_section_0
		return BeamSectionSpec(
			section_type=section_type,
			arg0=general.w.get()[1],
			arg1=general.h.get()[1],
			arg2=general.iw.get()[1],
			text0=general.w.get()[0],
			text1=general.h.get()[0],
			text2=general.iw.get()[0],
			outer_type=general.outer_type.get(),
			inner_type=general.inner_type.get(),
		)
	if section_type == "Прямоугольник с прямоугольным отверстием":
		rect = container.rect_minus_rect
		return BeamSectionSpec(
			section_type=section_type,
			arg0=rect.w.get()[1],
			arg1=rect.h.get()[1],
			arg2=rect.hw.get()[1],
			arg3=rect.hh.get()[1],
			text0=rect.w.get()[0],
			text1=rect.h.get()[0],
			text2=rect.hw.get()[0],
			text3=rect.hh.get()[0],
			offset_enabled=rect.s.get()[0],
			offset_value=rect.s.get()[2],
			offset_text=rect.s.get()[1],
			edge=rect.edge.get(),
		)
	if section_type == "H - профиль":
		profile = container.hrect
		return BeamSectionSpec(
			section_type=section_type,
			arg0=profile.w.get()[1],
			arg1=profile.h.get()[1],
			arg2=profile.h1.get()[1],
			arg3=profile.w1.get()[1],
			text0=profile.w.get()[0],
			text1=profile.h.get()[0],
			text2=profile.h1.get()[0],
			text3=profile.w1.get()[0],
			rotated=profile.orient.get(),
		)
	if section_type not in ("Тонкая труба", "Треугольник"):
		return BeamSectionSpec(section_type=section_type)
	base = container.base_section_widget
	return BeamSectionSpec(
		section_type=section_type,
		arg0=base.arg0.get(),
		arg1=base.arg1.get(),
		arg2=base.arg2.get(),
		text0=base.txt0.get(),
		text1=base.txt1.get(),
		text2=base.txt2.get(),
	)


class PaintWidget(paintwdg.PaintWidget):
	def __init__(self):
		super().__init__()
		self.last_scene = None

	def paintEventImplementation(self, ev):
		settings = ObliqueBendingLayoutSettings(
			width=self.width(),
			height=self.height(),
			console_enabled=self.shemetype.console.get()[0],
			console_width=self.shemetype.console.get()[1],
			axonometric=self.shemetype.axonom.get(),
			forty_five_degrees=self.shemetype.axonom_deg.get(),
			x_offset=self.shemetype.xoffset.get(),
			z_rotation_degrees=self.shemetype.zrot.get(),
			x_rotation_degrees=self.shemetype.xrot.get(),
			rod_length=self.shemetype.L.get(),
			dimension_offset=self.shemetype.offdown.get(),
			force_length=self.shemetype.arrlen.get(),
			arrow_size=self.shemetype.arrow_size.get(),
			font_size=self.shemetype.font_size.get(),
			line_width=self.shemetype.line_width.get(),
			section=_section_spec(self.shemetype.section_container),
		)
		metrics = QtTextMetrics()
		scene = ObliqueBendingLayoutBuilder().build(
			self.shemetype.task,
			settings,
			metrics,
			text_transform=paintool.greek,
			length_text=util.text_prepare_ltext,
		)
		self.last_scene = scene
		self.scene_interaction = QtSceneInteraction(scene, text_metrics=metrics)
		QtPainterRenderer(metrics).render(scene, self.painter)
