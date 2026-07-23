"""Qt widget adapter for the frames task."""

import common
import paintwdg
import paintool
import sections
import tablewidget
import taskconf_menu
import util

from sopr_scheme_gener.layouts.beam_sections import BeamSectionSpec
from sopr_scheme_gener.layouts.frames import FramesLayoutBuilder, FramesLayoutSettings
from sopr_scheme_gener.scene import Point
from sopr_scheme_gener.scene.qt import (
	QtPainterRenderer,
	QtSceneInteraction,
	QtTextMetrics,
)

from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QLabel, QTextEdit


LABEL_DIRECTIONS = [
	"слева",
	"справа",
	"сверху",
	"снизу",
	"слева сверху",
	"справа сверху",
	"слева снизу",
	"справа снизу",
]
MOMENT_TYPES = [
	"нет",
	"слева +",
	"слева -",
	"справа +",
	"справа -",
	"сверху +",
	"сверху -",
	"снизу +",
	"снизу -",
]
FORCE_TYPES = [
	"нет",
	"слева от",
	"слева к",
	"справа от",
	"справа к",
	"сверху от",
	"сверху к",
	"снизу от",
	"снизу к",
]
SUPPORT_TYPES = [
	"нет",
	"слева шарн1",
	"справа шарн1",
	"сверху шарн1",
	"снизу шарн1",
	"слева шарн2",
	"справа шарн2",
	"сверху шарн2",
	"снизу шарн2",
	"слева врез1",
	"справа врез1",
	"сверху врез1",
	"снизу врез1",
	"врезанный",
	"заделка",
]


class ShemeTypeT4(common.SchemeType):
	def __init__(self):
		super().__init__("Рамы")
		self.setwidgets(ConfWidget_T4(self), PaintWidget_T4(), common.TableWidget())


class ConfWidget_T4(common.ConfWidget):
	class sect:
		def __init__(
			self,
			direct=1,
			strt=("", ""),
			fini=(1, 1),
			lsharn="нет",
			rsharn="нет",
			txt="",
			alttxt=False,
			xstrt=None,
			ystrt=None,
			xfini=None,
			yfini=None,
		):
			self.xstrt = str(strt[0]) if xstrt is None else xstrt
			self.ystrt = str(strt[1]) if ystrt is None else ystrt
			self.xfini = str(fini[0]) if xfini is None else xfini
			self.yfini = str(fini[1]) if yfini is None else yfini
			self.lsharn = lsharn
			self.rsharn = rsharn
			self.txt = txt
			self.alttxt = alttxt

	class label:
		def __init__(
			self,
			smaker="",
			fmaker="",
			smaker_pos="сверху",
			fmaker_pos="сверху",
		):
			self.smaker = smaker
			self.fmaker = fmaker
			self.smaker_pos = smaker_pos
			self.fmaker_pos = fmaker_pos

	class sectforce:
		def __init__(self, distrib="clean", txt=""):
			self.distrib = distrib
			self.txt = txt

	class betsect:
		def __init__(
			self,
			fenl="нет",
			fenr="нет",
			menl="нет",
			menr="нет",
			fl_txt="",
			fr_txt="",
			ml_txt="",
			mr_txt="",
			fl_txt_alt=False,
			fr_txt_alt=False,
		):
			self.fenl = fenl
			self.fenr = fenr
			self.menl = menl
			self.menr = menr
			self.fl_txt = fl_txt
			self.fr_txt = fr_txt
			self.ml_txt = ml_txt
			self.mr_txt = mr_txt
			self.fl_txt_alt = fl_txt_alt
			self.fr_txt_alt = fr_txt_alt

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": [
				self.sect(strt=(0, 0), fini=(1, 1), lsharn="слева шарн2"),
				self.sect(strt=("", ""), fini=(2, 1)),
				self.sect(strt=("", ""), fini=(3, 0)),
			],
			"sectforce": [
				self.sectforce(distrib="clean"),
				self.sectforce(distrib="clean"),
				self.sectforce(distrib="-"),
			],
			"betsect": [
				self.betsect(menr="слева +"),
				self.betsect(),
				self.betsect(),
			],
			"label": [self.label(), self.label(), self.label()],
		}

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("xstrt", "str", "X0", hint="N0")
		self.table.addColumn("ystrt", "str", "Y0", hint="N0")
		self.table.addColumn(
			"lsharn", "list", "ШарнирЛ", variant=SUPPORT_TYPES, hint="N0"
		)
		self.table.addColumn("xfini", "str", "X1", hint="N1")
		self.table.addColumn("yfini", "str", "Y1", hint="N1")
		self.table.addColumn(
			"rsharn", "list", "ШарнирП", variant=SUPPORT_TYPES, hint="N1"
		)
		self.table.addColumn("txt", "str", "Текст", hint="S")
		self.table.addColumn("alttxt", "bool", "alt", hint="S")
		self.table.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table1.addColumn(
			"distrib",
			"list",
			"Распред. нагрузка",
			variant=["clean", "+", "-"],
			hint="S",
		)
		self.table1.addColumn("txt", "str", "Текст q.", hint="S")
		self.table1.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn(
			"fenl", "list", "0:Сила", variant=FORCE_TYPES, hint="N0"
		)
		self.table2.addColumn("fl_txt", "str", "0:Т.F", hint="N0")
		self.table2.addColumn(
			"menl", "list", "0:Момент", variant=MOMENT_TYPES, hint="N0"
		)
		self.table2.addColumn("ml_txt", "str", "0:Т.M", hint="N0")
		self.table2.addColumn("fl_txt_alt", "bool", "0:Alt", hint="N0")
		self.table2.addColumn(
			"fenr", "list", "1:Сила", variant=FORCE_TYPES, hint="N1"
		)
		self.table2.addColumn("fr_txt", "str", "1:Т.F", hint="N1")
		self.table2.addColumn(
			"menr", "list", "1:Момент", variant=MOMENT_TYPES, hint="N1"
		)
		self.table2.addColumn("mr_txt", "str", "1:Т.M", hint="N1")
		self.table2.addColumn("fr_txt_alt", "bool", "1:Alt", hint="N1")
		self.table2.updateTable()

		self.table3 = tablewidget.TableWidget(self.shemetype, "label")
		self.table3.addColumn("smaker", "str", "0: Метка", hint="N0")
		self.table3.addColumn(
			"smaker_pos",
			"list",
			"0: Метка",
			variant=LABEL_DIRECTIONS,
			hint="N0",
		)
		self.table3.addColumn("fmaker", "str", "1: Метка", hint="N1")
		self.table3.addColumn(
			"fmaker_pos",
			"list",
			"1: Метка",
			variant=LABEL_DIRECTIONS,
			hint="N1",
		)
		self.table3.updateTable()

		for table in (self.table, self.table1, self.table2, self.table3):
			table.hover_hint.connect(self.hover_node)
			table.unhover.connect(self.table_unhover)
		self.vlayout.addWidget(QLabel("Геометрия и текст:"))
		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(QLabel("Распределённые силы:"))
		self.vlayout.addWidget(self.table1)
		self.vlayout.addWidget(QLabel("Локальные силы:"))
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(QLabel("Метки:"))
		self.vlayout.addWidget(self.table3)
		self.vlayout.addWidget(self.sett)
		for table in (self.table, self.table1, self.table2, self.table3):
			table.updated.connect(self.redraw)
		self.vlayout.addWidget(self.shemetype.texteditor)

	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		self.sett.updated.connect(self.redraw)
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.init_taskconf()
		self.shemetype.section_container.updated.connect(self.redraw)
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		self.save_row = None
		self.save_hint = None
		self.highlited_element = None
		self.update_interface()
		self.setLayout(self.vlayout)

	def hover_node(self, row, column, hint):
		self.shemetype.paintwidget.highlited_element = (hint, row)
		self.redraw()
		self.save_row = row
		self.save_hint = hint

	def table_unhover(self):
		self.shemetype.paintwidget.highlited_element = None
		self.redraw()

	def init_taskconf(self):
		self.sett.add_delimiter()
		self.shemetype.base_length = self.sett.add("Базовая длина:", "int", "100")
		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "12")
		self.shemetype.postfix = self.sett.add("Постфикс:", "str", ",EIx")
		self.sett.add_delimiter()
		self.shemetype.section_enable = self.sett.add(
			"Отображение сечения:", "bool", True
		)
		self.shemetype.section_container = self.sett.add_widget(
			sections.SectionContainer(self.shemetype.section_enable)
		)

	def _add_action(self, strt=("", ""), fini=(1, 1)):
		self.shemetype.task["sections"].append(self.sect(strt=strt, fini=fini))
		self.shemetype.task["betsect"].append(self.betsect())
		self.shemetype.task["sectforce"].append(self.sectforce())
		self.shemetype.task["label"].append(self.label())
		self.redraw()
		self.updateTables()

	def _insert_action(self, idx, strt=("", ""), fini=(1, 1)):
		self.shemetype.task["sections"].insert(
			idx, self.sect(strt=strt, fini=fini)
		)
		self.shemetype.task["betsect"].insert(idx, self.betsect())
		self.shemetype.task["sectforce"].insert(idx, self.sectforce())
		self.shemetype.task["label"].insert(idx, self.label())
		self.redraw()
		self.updateTables()

	def add_action_impl(self):
		self._add_action()

	def insert_action_impl(self, idx):
		self._insert_action(idx)

	def del_action_impl(self, idx):
		if not self.shemetype.task["sections"]:
			return
		del self.shemetype.task["sections"][idx]
		del self.shemetype.task["betsect"][idx]
		del self.shemetype.task["sectforce"][idx]
		del self.shemetype.task["label"][idx]
		self.redraw()
		self.updateTables()

	def inittask(self):
		return {}

	def updateTables(self):
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()
		self.table3.updateTable()


class PaintWidget_T4(paintwdg.PaintWidget):
	def __init__(self):
		super().__init__()
		self.grid_enabled = False
		self.hovered_point = None
		self.hovered_point_index = None
		self.mouse_pressed = False
		self.pressed_point = None
		self.pressed_point_index = None
		self.highlited_element = None
		self.setMouseTracking(True)

	def frame_section_spec(self):
		if not self.shemetype.section_enable.get():
			return BeamSectionSpec()
		container = self.shemetype.section_container
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

	def _grid_point(self, object_id):
		if self.scene_interaction is None:
			return None
		bounds = self.scene_interaction.index.bounds(object_id)
		if bounds is None:
			return None
		return QPointF(
			bounds.x + bounds.width / 2,
			bounds.y + bounds.height / 2,
		)

	def paintEventImplementation(self, ev):
		highlight_hint = ""
		highlight_row = -1
		if self.highlited_element is not None:
			highlight_hint, highlight_row = self.highlited_element
		preview_start = None
		preview_end = None
		if (
			self.mouse_pressed
			and self.pressed_point_index is not None
			and self.hovered_point_index is not None
		):
			preview_start = Point(*self.pressed_point_index)
			preview_end = Point(*self.hovered_point_index)
		settings = FramesLayoutSettings(
			width=self.width(),
			height=self.height(),
			hcenter=self.hcenter,
			base_length=self.shemetype.base_length.get(),
			arrow_size=self.shemetype.arrow_size.get(),
			postfix=self.shemetype.postfix.get(),
			font_size=self.shemetype.font_size.get(),
			line_width=self.shemetype.line_width.get(),
			section=self.frame_section_spec(),
			grid_enabled=self.grid_enabled,
			hovered_grid=(
				Point(*self.hovered_point_index)
				if self.hovered_point_index is not None
				else None
			),
			preview_start=preview_start,
			preview_end=preview_end,
			highlight_hint=highlight_hint,
			highlight_row=highlight_row,
		)
		metrics = QtTextMetrics()
		scene = FramesLayoutBuilder().build(
			self.shemetype.task,
			settings,
			text_metrics=metrics,
			text_transform=paintool.greek,
			length_text=util.text_prepare_ltext,
		)
		self.scene_interaction = QtSceneInteraction(scene, text_metrics=metrics)
		self.last_scene = scene
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
		pos = ev.pos()
		if pos.x() < 20 or self.width() - pos.x() < 20:
			return
		if pos.y() < 20 or self.height() - pos.y() < 20:
			return
		if self.scene_interaction is None:
			return
		hit = self.scene_interaction.hit_test(pos, kinds=("grid-node",))
		if hit is None:
			return
		new_index = (
			hit.metadata_value("grid_x"),
			hit.metadata_value("grid_y"),
		)
		if new_index != self.hovered_point_index:
			self.hovered_point_index = new_index
			self.hovered_point = self._grid_point(hit.object_id)
			self.update()

	def mousePressEvent(self, ev):
		if self.hovered_point_index is None:
			return
		self.mouse_pressed = True
		self.pressed_point = self.hovered_point
		self.pressed_point_index = self.hovered_point_index
		self.update()

	def mouseReleaseEvent(self, ev):
		if not self.mouse_pressed:
			return
		self.mouse_pressed = False
		release_index = self.hovered_point_index
		if (
			self.pressed_point_index is not None
			and release_index is not None
			and self.pressed_point_index != release_index
		):
			start = self.pressed_point_index
			end = release_index
			if not self.shemetype.task["sections"]:
				end = (end[0] - start[0], end[1] - start[1])
				start = (0, 0)
			self.shemetype.confwidget._add_action(
				(round(start[0]), round(start[1])),
				(round(end[0]), round(end[1])),
			)
		self.pressed_point = None
		self.pressed_point_index = None
		self.update()
