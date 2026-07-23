import functools

import numpy
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QInputDialog, QMenu, QTextEdit

import common
import paintool
import paintwdg
import sections
import taskconf_menu
from sopr_scheme_gener.layouts.beam_sections import BeamSectionSpec
from sopr_scheme_gener.layouts.spatial_beams import (
	SpatialBeamsLayoutBuilder,
	SpatialBeamsLayoutSettings,
)
from sopr_scheme_gener.scene.qt import (
	QtGraphicsSceneRenderer,
	QtSceneInteraction,
	QtTextMetrics,
)


class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Пространственные балки")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())


class ConfWidget(common.ConfWidget):
	class sect:
		def __init__(
			self,
			ax,
			ay,
			az,
			bx,
			by,
			bz,
			distrib=None,
			internal_node=None,
		):
			self.ax = ax
			self.ay = ay
			self.az = az
			self.bx = bx
			self.by = by
			self.bz = bz
			self.distrib = distrib
			self.internal_node = ConfWidget.node(
				(self.ax + self.bx) / 2,
				(self.ay + self.by) / 2,
				(self.az + self.bz) / 2,
				section=self,
			)

		def __str__(self):
			return str((self.ax, self.ay, self.az, self.bx, self.by, self.bz))

		def has_node(self, node):
			return (
				(self.ax, self.ay, self.az) == (node.x, node.y, node.z)
				or (self.bx, self.by, self.bz) == (node.x, node.y, node.z)
			)

	class node:
		def __init__(
			self,
			x,
			y,
			z,
			type="",
			sharn="нет",
			sharn_vec=numpy.array([0, 0, 0]),
			sharn_vec2=numpy.array([0, 0, 0]),
			force_x=None,
			force_y=None,
			force_z=None,
			moment_x=None,
			moment_y=None,
			moment_z=None,
			section=None,
			torque=None,
		):
			self.x = x
			self.y = y
			self.z = z
			self.sharn = sharn
			self.sharn_vec = sharn_vec
			self.sharn_vec2 = sharn_vec2
			self.force_x = force_x
			self.force_y = force_y
			self.force_z = force_z
			self.moment_x = moment_x
			self.moment_y = moment_y
			self.moment_z = moment_z
			self.section = section
			self.torque = torque

		def pos(self):
			return numpy.array((self.x, self.y, self.z))

		def equal(self, other):
			return (self.x, self.y, self.z) == (other.x, other.y, other.z)

	class label:
		def __init__(self, text, pos):
			self.text = text
			self.pos = pos

		def move2(self, delta):
			self.pos = (
				self.pos[0] + delta.x(),
				self.pos[1] + delta.y(),
			)

	def __init__(self, scheme):
		super().__init__(scheme, noinitbuttons=True)
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		self.sett = taskconf_menu.TaskConfMenu()
		self.shemetype.axonom = self.sett.add("Аксонометрия:", "bool", True)
		self.shemetype.zrot = self.sett.add("Направление:", "int", "20")
		self.shemetype.xrot = self.sett.add("Подъём:", "int", "40")
		self.shemetype.zmul = self.sett.add("Z-сжатие:", "float", "0.6")
		self.shemetype.rebro = self.sett.add("Длина ребра:", "float", "150")
		self.shemetype.wborder = self.sett.add(
			"Поля по горизонтали:", "float", "10"
		)
		self.shemetype.hborder = self.sett.add(
			"Поля по вертикали:", "float", "10"
		)
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
		self.update_interface()

	def update_interface(self):
		self.vlayout.addWidget(self.sett)
		self.vlayout.addWidget(self.shemetype.texteditor)
		self.setLayout(self.vlayout)

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": [
				self.sect(0, 0, 0, 0, -1, 0),
				self.sect(0, -1, 0, 1, -1, 0),
				self.sect(1, -1, 0, 1, -1, 1),
			],
			"nodes": [
				self.node(0, 0, 0),
				self.node(0, -1, 0),
				self.node(1, -1, 0),
				self.node(1, -1, 1),
			],
			"labels": [],
		}

	def inittask(self):
		return {}

	def add_sect(self, first, second):
		self.shemetype.task["sections"].append(
			self.sect(first.x, first.y, first.z, second.x, second.y, second.z)
		)
		self.shemetype.task["nodes"].append(
			self.node(second.x, second.y, second.z)
		)

	def nodes_clean(self):
		nodes = self.shemetype.task["nodes"]
		used = []
		for node in nodes:
			if any(section.has_node(node) for section in self.shemetype.task["sections"]):
				used.append(node)
		nodes[:] = used or [self.node(0, 0, 0)]

	def delete_sect(self, section):
		self.shemetype.task["sections"].remove(section)
		self.nodes_clean()

	def delete_node(self, node):
		self.shemetype.task["sections"][:] = [
			section
			for section in self.shemetype.task["sections"]
			if not section.has_node(node)
		]
		self.shemetype.task["nodes"][:] = [
			candidate
			for candidate in self.shemetype.task["nodes"]
			if not candidate.equal(node)
		]
		self.nodes_clean()


class PaintWidget(paintwdg.PaintWidget):
	def __init__(self):
		super().__init__()
		self.no_text_render = True
		self.no_resize = True
		self.mouse_pressed = False
		self.hovered_node = None
		self.hovered_sect = None
		self.hovered_node_pressed = None
		self.selected_label_id = None
		self.last_scene_point = None
		self.grid_enabled = False
		self.last_scene = None
		self.setMouseTracking(True)

	def _section_spec(self):
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

	def _index_of(self, sequence, value):
		try:
			return sequence.index(value)
		except (ValueError, AttributeError):
			return None

	def paintEventImplementation(self, ev):
		node_index = self._index_of(
			self.shemetype.task["nodes"], self.hovered_node
		)
		section_index = self._index_of(
			self.shemetype.task["sections"], self.hovered_sect
		)
		settings = SpatialBeamsLayoutSettings(
			axonometric=self.shemetype.axonom.get(),
			z_rotation_degrees=self.shemetype.zrot.get(),
			x_rotation_degrees=self.shemetype.xrot.get(),
			z_scale=self.shemetype.zmul.get(),
			edge_length=self.shemetype.rebro.get(),
			horizontal_border=self.shemetype.wborder.get(),
			vertical_border=self.shemetype.hborder.get(),
			arrow_size=self.shemetype.arrow_size.get(),
			font_size=self.shemetype.font_size.get(),
			line_width=self.shemetype.line_width.get(),
			note=self.shemetype.texteditor.toPlainText(),
			section=self._section_spec(),
			hovered_node=node_index,
			hovered_section=section_index,
			pressed=self.mouse_pressed,
			preview_point=self.hovered_node_pressed,
			selected_label=self.selected_label_id,
		)
		metrics = QtTextMetrics()
		scene = SpatialBeamsLayoutBuilder().build(
			self.shemetype.task,
			settings,
			metrics,
			text_transform=paintool.greek,
		)
		self.last_scene = scene
		self.scene_interaction = QtSceneInteraction(
			scene,
			text_metrics=metrics,
			device_width=max(1, self.width()),
			device_height=max(1, self.height()),
			aspect_fit=True,
		)
		QtGraphicsSceneRenderer(metrics).render(scene, self.painter)
		self.resize_after_render(scene.viewport.width, scene.viewport.height)

	def Action(self, name, parent, trig=None):
		action = QAction(name, parent)
		if trig:
			action.triggered.connect(trig)
		return action

	def _scene_point(self, qt_point):
		if self.scene_interaction is None:
			return qt_point
		return self.scene_interaction.point(qt_point)

	def mouseMoveEvent(self, ev):
		if self.scene_interaction is None:
			return
		scene_point = self._scene_point(ev.pos())
		if self.mouse_pressed and self.selected_label_id is not None:
			if self.last_scene_point is not None:
				label = self.shemetype.task["labels"][self.selected_label_id]
				label.move2(scene_point - self.last_scene_point)
				self.update()
		elif self.mouse_pressed:
			hit = self.scene_interaction.hit_test(
				ev.pos(), kinds=("candidate",)
			)
			self.hovered_node_pressed = (
				(
					hit.metadata_value("x"),
					hit.metadata_value("y"),
					hit.metadata_value("z"),
				)
				if hit is not None
				else None
			)
			self.update()
		else:
			self.selected_label_id = None
			self.hovered_node = None
			self.hovered_sect = None
			hit = self.scene_interaction.hit_test(ev.pos(), kinds=("label",))
			if hit is not None:
				self.selected_label_id = hit.metadata_value("index")
			else:
				hit = self.scene_interaction.hit_test(ev.pos(), kinds=("node",))
				if hit is not None:
					self.hovered_node = self.shemetype.task["nodes"][
						hit.metadata_value("index")
					]
				else:
					hit = self.scene_interaction.hit_test(
						ev.pos(), kinds=("section",)
					)
					if hit is not None:
						self.hovered_sect = self.shemetype.task["sections"][
							hit.metadata_value("index")
						]
			self.update()
		self.last_scene_point = scene_point

	def mousePressEvent(self, ev):
		scene_point = self._scene_point(ev.pos())
		self.last_scene_point = scene_point
		if ev.button() == Qt.RightButton:
			self._show_context_menu(ev, scene_point)
			return
		if ev.button() == Qt.LeftButton:
			self.mouse_pressed = True
			self.hovered_node_pressed = None
			self.update()

	def mouseReleaseEvent(self, ev):
		was_pressed = self.mouse_pressed
		self.mouse_pressed = False
		if (
			was_pressed
			and ev.button() == Qt.LeftButton
			and self.hovered_node is not None
			and self.hovered_node_pressed is not None
		):
			x, y, z = self.hovered_node_pressed
			self.shemetype.confwidget.add_sect(
				self.hovered_node,
				self.shemetype.confwidget.node(x, y, z),
			)
		self.hovered_node_pressed = None
		self.update()

	def _show_context_menu(self, ev, scene_point):
		menu = QMenu(self)
		create_label = self.Action(
			"Создать метку",
			self,
			functools.partial(self.create_label, scene_point),
		)
		if self.hovered_node is not None:
			supports = QMenu("Шарниры и заделки", self)
			for title, kind, first, second in (
				("Врезанный", "врез", (0, 0, 1), (0, 0, 0)),
				("Шарнир -x(y)", "sharn", (-1, 0, 0), (0, 1, 0)),
				("Шарнир -x(z)", "sharn", (-1, 0, 0), (0, 0, 1)),
				("Шарнир +x(y)", "sharn", (1, 0, 0), (0, 1, 0)),
				("Шарнир +x(z)", "sharn", (1, 0, 0), (0, 0, 1)),
				("Шарнир -y(x)", "sharn", (0, -1, 0), (1, 0, 0)),
				("Шарнир -y(z)", "sharn", (0, -1, 0), (0, 0, 1)),
				("Шарнир +y(x)", "sharn", (0, 1, 0), (1, 0, 0)),
				("Шарнир +y(z)", "sharn", (0, 1, 0), (0, 0, 1)),
				("Шарнир -z(x)", "sharn", (0, 0, -1), (1, 0, 0)),
				("Шарнир -z(y)", "sharn", (0, 0, -1), (0, 1, 0)),
				("Шарнир +z(x)", "sharn", (0, 0, 1), (1, 0, 0)),
				("Шарнир +z(y)", "sharn", (0, 0, 1), (0, 1, 0)),
				("Заделка x", "zadelka", (1, 0, 0), (0, 0, 0)),
				("Заделка y", "zadelka", (0, 1, 0), (0, 0, 0)),
				("Заделка z", "zadelka", (0, 0, 1), (0, 0, 0)),
			):
				supports.addAction(
					self.Action(
						title,
						self,
						functools.partial(
							self.set_sharn_flag, kind, first, second
						),
					)
				)
			menu.addMenu(supports)
			menu.addMenu(self._forces_menu())
			menu.addMenu(self._moments_menu())
			menu.addAction(
				self.Action(
					"Очистить узел",
					self,
					functools.partial(
						self.set_sharn_flag,
						"нет",
						(0, 0, 0),
						(0, 0, 0),
					),
				)
			)
			menu.addSeparator()
			menu.addAction(
				self.Action("Удалить узел и граничащие балки", self, self.delete_node)
			)
		elif self.hovered_sect is not None:
			loads = QMenu("Распределённые силы", self)
			for title, vector in (
				("нет", None),
				("-x", (-1, 0, 0)),
				("+x", (1, 0, 0)),
				("-y", (0, -1, 0)),
				("+y", (0, 1, 0)),
				("-z", (0, 0, -1)),
				("+z", (0, 0, 1)),
			):
				loads.addAction(
					self.Action(
						title,
						self,
						functools.partial(self.set_distrib_force, vector),
					)
				)
			menu.addMenu(loads)
			menu.addAction(self.Action("Удалить балку", self, self.delete_sect))
		elif self.selected_label_id is not None:
			menu.addAction(self.Action("Редактировать текст", self, self.edit_text))
			menu.addAction(self.Action("Удалить метку", self, self.delete_label))
			menu.addAction(
				self.Action(
					"Клонировать метку",
					self,
					functools.partial(self.clone_label, scene_point),
				)
			)
		menu.addSeparator()
		menu.addAction(create_label)
		menu.popup(self.mapToGlobal(ev.pos()))

	def _forces_menu(self):
		menu = QMenu("Сосредоточенные силы", self)
		short = 0.1
		for axis, vectors in (
			(
				"x",
				(
					((-1, 0, 0), (-short, 0, 0)),
					((short, 0, 0), (1, 0, 0)),
					((1, 0, 0), (short, 0, 0)),
					((-short, 0, 0), (-1, 0, 0)),
				),
			),
			(
				"y",
				(
					((0, -1, 0), (0, -short, 0)),
					((0, short, 0), (0, 1, 0)),
					((0, 1, 0), (0, short, 0)),
					((0, -short, 0), (0, -1, 0)),
				),
			),
			(
				"z",
				(
					((0, 0, -1), (0, 0, -short)),
					((0, 0, short), (0, 0, 1)),
					((0, 0, 1), (0, 0, short)),
					((0, 0, -short), (0, 0, -1)),
				),
			),
		):
			for index, (start, end) in enumerate(vectors):
				menu.addAction(
					self.Action(
						"Сила {}{}".format(axis, index + 1),
						self,
						functools.partial(
							self.set_force, "force_" + axis, start, end
						),
					)
				)
			menu.addAction(
				self.Action(
					"Сила {} нет".format(axis),
					self,
					functools.partial(
						self.set_force,
						"force_" + axis,
						(0, 0, 0),
						(0, 0, 0),
					),
				)
			)
		return menu

	def _moments_menu(self):
		menu = QMenu("Сосредоточенные моменты", self)
		for title, first, second in (
			("-x(y)", (0, 1, 0), (0, 0, 1)),
			("-x(z)", (0, 0, 1), (0, 1, 0)),
			("+x(y)", (0, 1, 0), (0, 0, -1)),
			("+x(z)", (0, 0, 1), (0, -1, 0)),
			("-y(x)", (1, 0, 0), (0, 0, 1)),
			("-y(z)", (0, 0, 1), (1, 0, 0)),
			("+y(x)", (1, 0, 0), (0, 0, -1)),
			("+y(z)", (0, 0, 1), (-1, 0, 0)),
			("-z(x)", (1, 0, 0), (0, 1, 0)),
			("-z(y)", (0, 1, 0), (1, 0, 0)),
			("+z(x)", (1, 0, 0), (0, -1, 0)),
			("+z(y)", (0, 1, 0), (-1, 0, 0)),
			("нет", (0, 0, 0), (0, 0, 0)),
		):
			menu.addAction(
				self.Action(
					"Момент " + title,
					self,
					functools.partial(self.set_torque, first, second),
				)
			)
		return menu

	def set_sharn_flag(self, kind, first, second):
		self.hovered_node.sharn = kind
		self.hovered_node.sharn_vec = numpy.array(first)
		self.hovered_node.sharn_vec2 = numpy.array(second)
		self.update()

	def set_force(self, name, first, second):
		setattr(self.hovered_node, name, (first, second))
		self.update()

	def set_torque(self, first, second):
		self.hovered_node.torque = (first, second)
		self.update()

	def set_distrib_force(self, vector):
		self.hovered_sect.distrib = vector
		self.update()

	def delete_node(self):
		self.shemetype.confwidget.delete_node(self.hovered_node)
		self.hovered_node = None
		self.update()

	def delete_sect(self):
		self.shemetype.confwidget.delete_sect(self.hovered_sect)
		self.hovered_sect = None
		self.update()

	def create_label(self, pos):
		self.shemetype.task["labels"].append(
			self.shemetype.confwidget.label("Text", (pos.x(), pos.y()))
		)
		self.update()

	def clone_label(self, pos):
		label = self.shemetype.task["labels"][self.selected_label_id]
		self.shemetype.task["labels"].append(
			self.shemetype.confwidget.label(
				label.text,
				(pos.x() + 30, pos.y()),
			)
		)
		self.update()

	def delete_label(self):
		del self.shemetype.task["labels"][self.selected_label_id]
		self.selected_label_id = None
		self.update()

	def edit_text(self):
		label = self.shemetype.task["labels"][self.selected_label_id]
		text, accepted = QInputDialog.getText(
			self, "Текст", "Введите текст:", text=label.text
		)
		if accepted:
			label.text = text
			self.update()

	def enterEvent(self, ev):
		self.grid_enabled = True
		self.update()

	def leaveEvent(self, ev):
		self.grid_enabled = False
		self.hovered_node = None
		self.hovered_sect = None
		self.update()
