"""Qt widget adapter for column-stability schemes."""

import common
import paintool
import paintwdg
import tablewidget
import taskconf_menu

from PyQt5.QtWidgets import QLabel, QTextEdit

from sopr_scheme_gener.layouts.column_stability import (
	LOAD_DOWN,
	LOAD_NONE,
	LOAD_TYPES,
	SUPPORT_FIXED,
	SUPPORT_FLOATING,
	SUPPORT_NONE,
	SUPPORT_TYPES,
	ColumnStabilityLayoutBuilder,
	ColumnStabilityLayoutSettings,
)
from sopr_scheme_gener.scene.qt import (
	QtPainterRenderer,
	QtSceneInteraction,
	QtTextMetrics,
)


class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Устойчивость стержней")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())


class ConfWidget(common.ConfWidget):
	class segment:
		def __init__(self, length=1.0, length_text="l", rigidity_text=""):
			self.length = length
			self.length_text = length_text
			self.rigidity_text = rigidity_text

	class node:
		def __init__(self, support=SUPPORT_NONE, load=LOAD_NONE, load_text=""):
			self.support = support
			self.load = load
			self.load_text = load_text

	def create_task_structure(self):
		self.shemetype.task = {
			"segments": [
				self.segment(1.0, "l", ""),
				self.segment(1.0, "l", "EJ_min"),
			],
			"nodes": [
				self.node(SUPPORT_FIXED),
				self.node(SUPPORT_FLOATING),
				self.node(SUPPORT_NONE, LOAD_DOWN, "F"),
			],
		}

	def __init__(self, scheme):
		super().__init__(scheme)
		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.rod_width = self.sett.add(
			"Толщина стержня:", "float", "5"
		)
		self.shemetype.support_size = self.sett.add(
			"Размер опор:", "float", "24"
		)
		self.shemetype.arrow_size = self.sett.add(
			"Размер стрелок:", "float", "12"
		)
		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter
		self.sett.updated.connect(self.redraw)

		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.setPlaceholderText("Текст задания")
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		self.update_interface()
		self.setLayout(self.vlayout)

	def update_interface(self):
		self.segment_table = tablewidget.TableWidget(self.shemetype, "segments")
		self.segment_table.addColumn("length", "float", "Длина")
		self.segment_table.addColumn("length_text", "str", "Размер")
		self.segment_table.addColumn("rigidity_text", "str", "Жёсткость")
		self.segment_table.updateTable()

		self.node_table = tablewidget.TableWidget(self.shemetype, "nodes")
		self.node_table.addColumn(
			"support", "list", "Опора", variant=list(SUPPORT_TYPES)
		)
		self.node_table.addColumn("load", "list", "Сила", variant=list(LOAD_TYPES))
		self.node_table.addColumn("load_text", "str", "Текст силы")
		self.node_table.updateTable()

		self.segment_table.updated.connect(self.redraw)
		self.node_table.updated.connect(self.redraw)
		self.vlayout.addWidget(QLabel("Участки (снизу вверх):"))
		self.vlayout.addWidget(self.segment_table)
		self.vlayout.addWidget(QLabel("Узлы (снизу вверх):"))
		self.vlayout.addWidget(self.node_table)
		self.vlayout.addWidget(self.sett)
		self.vlayout.addWidget(self.shemetype.texteditor)

	def add_action_impl(self):
		self.shemetype.task["segments"].append(self.segment())
		self.shemetype.task["nodes"].append(self.node())
		self._update_tables()

	def insert_action_impl(self, idx):
		segments = self.shemetype.task["segments"]
		idx = max(0, min(idx, len(segments)))
		segments.insert(idx, self.segment())
		self.shemetype.task["nodes"].insert(idx + 1, self.node())
		self._update_tables()

	def del_action_impl(self, idx):
		segments = self.shemetype.task["segments"]
		if len(segments) == 1:
			return
		index = idx if idx >= 0 else len(segments) - 1
		del segments[index]
		del self.shemetype.task["nodes"][index + 1]
		self._update_tables()

	def _update_tables(self):
		self.segment_table.updateTable()
		self.node_table.updateTable()
		self.redraw()

	def inittask(self):
		return {}


class PaintWidget(paintwdg.PaintWidget):
	def __init__(self):
		super().__init__()
		self.last_scene = None

	def paintEventImplementation(self, ev):
		metrics = QtTextMetrics()
		scene = ColumnStabilityLayoutBuilder().build(
			self.shemetype.task,
			ColumnStabilityLayoutSettings(
				width=self.width(),
				height=self.height(),
				hcenter=self.hcenter,
				line_width=self.shemetype.line_width.get(),
				font_size=self.shemetype.font_size.get(),
				arrow_size=self.shemetype.arrow_size.get(),
				rod_width=self.shemetype.rod_width.get(),
				support_size=self.shemetype.support_size.get(),
			),
			metrics,
			text_transform=paintool.greek,
		)
		self.last_scene = scene
		self.scene_interaction = QtSceneInteraction(scene, text_metrics=metrics)
		QtPainterRenderer(metrics).render(scene, self.painter)
