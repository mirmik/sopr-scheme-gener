import common
import paintwdg

import paintool
import taskconf_menu
import tablewidget
import sections
from sopr_scheme_gener.layouts.beams import (
	BeamLayoutBuilder,
	BeamLayoutSettings,
)
from sopr_scheme_gener.layouts.beam_sections import BeamSectionSpec, beam_section_width
from sopr_scheme_gener.scene import Color, Fill, Rectangle, Scene, Stroke, metadata
from sopr_scheme_gener.scene.qt import (
	QtPainterRenderer,
	QtSceneInteraction,
	QtTextMetrics,
)

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Балки")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())


class ConfWidget(common.ConfWidget):
	"""Виджет настроек задачи T0"""
	class sect:
		def __init__(self, l=1):
			self.l=l

	class betsect:
		def __init__(self, sharn = "Нет", sectname="", F="Нет", M="Нет", Mkr="Нет", MT="", FT=""):
			self.sectname = sectname
			self.M = M
			self.Mkr = Mkr 
			self.F=F
			self.MT = MT
			self.FT = FT
			self.sharn = sharn

	class sectforce:
		def __init__(self, Fr="Нет", FrT=""):
			self.Fr = Fr
			self.FrT = FrT


	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(l=1),
				self.sect(l=1),
				self.sect(l=2),
			],
			"betsect":
			[
				self.betsect(sharn="1"),
				self.betsect(),
				self.betsect(sharn="2"),
				self.betsect()
			],
			"sectforce":
			[
				self.sectforce(),
				self.sectforce(),
				self.sectforce(Fr="+", FrT="ql")
			],

			"labels" : []
		}

	def init_taskconf(self):
		node_variant = ["Нет", "Заделка", "Шарнир"]

		self.sett.add_delimiter()		
		self.shemetype.lwidth = common.CONFVIEW.lwidth_getter
		self.shemetype.left_node = self.sett.add("Левый узел", "list", defval=0, variant=node_variant)
		self.shemetype.right_node = self.sett.add("Правый узел", "list", defval=0, variant=node_variant)
		self.shemetype.postfix = self.sett.add("Постфикс:", ("bool", "str"), (False, ", EIx"))
				
		self.sett.add_delimiter()
		self.shemetype.section_enable = self.sett.add("Отображение сечения:", "bool", True)
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter

		self.shemetype.section_container = self.sett.add_widget(sections.SectionContainer(self.shemetype.section_enable))

		self.sett.add_delimiter()
		self.shemetype.base_section_height = self.sett.add("Базовая высота секции:", "int", "6")
		self.shemetype.arrow_size = self.sett.add("Размер стрелки:", "int", "15")
		self.sett.add_delimiter()
		
	def section_enable_handle(self):
		pass
		
	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("l", "float", "Длина")
		self.table.updateTable()

		self.table2 = tablewidget.TableWidget(self.shemetype, "betsect")
		self.table2.addColumn("sectname", "str", "Имя")
		self.table2.addColumn("sharn", "list", "Шарн.", variant=["Нет", "1", "2"])
		self.table2.addColumn("F", "list", variant=["Нет", "+", "-", "влево", "вправо"])
		self.table2.addColumn("M", "list", variant=["Нет", "+", "-"])
		self.table2.addColumn("FT", "str", "Текст F")
		self.table2.addColumn("MT", "str", "Текст M")
		self.table2.updateTable()

		self.table1 = tablewidget.TableWidget(self.shemetype, "sectforce")
		self.table1.addColumn("Fr", "list", "q", variant=["Нет", "+", "-"])
		self.table1.addColumn("FrT", "str", "Текст q")
		self.table1.updateTable()

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
		self.init_taskconf()
		self.sett.updated.connect(self.redraw)
		self.shemetype.section_container.updated.connect(self.redraw)

		self.shemetype.section_enable.element().updated.connect(self.section_enable_handle)

		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)

		self.update_interface()
		self.setLayout(self.vlayout)

	def add_action_impl(self):
		self.sections().append(self.sect())
		self.shemetype.task["sectforce"].append(self.sectforce())
		self.shemetype.task["betsect"].append(self.betsect())
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def insert_action_impl(self, idx):
		self.sections().insert(idx, self.sect())
		self.shemetype.task["sectforce"].insert(idx, self.sectforce())
		self.shemetype.task["betsect"].insert(idx, self.betsect())
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def del_action_impl(self, idx):
		if len(self.sections()) == 1:
			return

		del self.sections()[idx]
		del self.shemetype.task["betsect"][idx]
		del self.shemetype.task["sectforce"][idx]
		self.redraw()
		self.table.updateTable()
		self.table1.updateTable()
		self.table2.updateTable()

	def inittask(self):
		return {}

class PaintWidget(paintwdg.PaintWidget):

	def __init__(self):
		super().__init__()
		self.enable_common_mouse_events()

	def beam_section_spec(self):
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

	def paintEventImplementation(self, ev):
		"""Рисуем сцену согласно объекта задания"""

		lwidth = self.shemetype.lwidth.get()

		task = self.shemetype.task

		size = self.size()
		width = size.width()
		height = size.height()

		section_spec = self.beam_section_spec()
		scene_settings = BeamLayoutSettings(
			width=width,
			height=height,
			hcenter=self.hcenter,
			line_width=lwidth,
			font_size=self.shemetype.font_size.get(),
			base_section_height=self.shemetype.base_section_height.get(),
			arrow_size=self.shemetype.arrow_size.get(),
			left_node=self.shemetype.left_node.get(),
			right_node=self.shemetype.right_node.get(),
			postfix_enabled=self.shemetype.postfix.get()[0],
			postfix=self.shemetype.postfix.get()[1],
			section=section_spec,
		)
		scene = BeamLayoutBuilder().build(
			task,
			scene_settings,
			text_transform=paintool.greek,
			text_metrics=QtTextMetrics(),
		)
		section_width = beam_section_width(section_spec)
		body_right = width - 20 - section_width
		self.labels_center = QPointF((20 + body_right) / 2, self.hcenter)
		self.labels_width_scale = width - 40 - section_width
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
					scene.objects + (
						Rectangle(
							bounds,
							stroke=Stroke(),
							fill=Fill(Color(0, 255, 0)),
							object_id=self.selected_label_id + "/hover",
							metadata=metadata(kind="hover"),
						),
					),
					content_bounds=scene.content_bounds,
					background=scene.background,
				)
		self.last_scene = scene
		QtPainterRenderer().render(scene, self.painter)
