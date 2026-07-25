from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from items.text import *
import traceback
import common
import functools
import paintool
from sopr_scheme_gener.page_layout import PageFrame, PageLayout
from sopr_scheme_gener.scene.model import Group, Point, Rect, Scene

EXIT_ON_EXCEPT = False
ERROR_REPORTER = None

def set_EXIT_ON_ERROR(enabled=True):
	global EXIT_ON_EXCEPT
	EXIT_ON_EXCEPT = bool(enabled)

def set_ERROR_REPORTER(reporter):
	global ERROR_REPORTER
	ERROR_REPORTER = reporter

class PaintWidgetSetter(QWidget):
	def __init__(self, container):
		super().__init__()
		self.container = container

		self.vlayout = QVBoxLayout()
		self.hlayout = QHBoxLayout()

		self.warr = QWidget(), QWidget(), QWidget(), QWidget()
		
		for w in self.warr[0:2]:
			w.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
			w.setAutoFillBackground(True);

		for w in self.warr[2:4]:
			w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
			w.setAutoFillBackground(True);

		pal = QPalette();

		#pal.setColor(QPalette.Background, Qt.black);
		pal.setColor(QPalette.Background, Qt.gray);
		self.warr[0].setPalette(pal);		
		
		#pal.setColor(QPalette.Background, Qt.red);
		pal.setColor(QPalette.Background, Qt.gray);
		self.warr[1].setPalette(pal);		
		
		#pal.setColor(QPalette.Background, Qt.green);
		pal.setColor(QPalette.Background, Qt.gray);
		self.warr[2].setPalette(pal);		
		
		#pal.setColor(QPalette.Background, Qt.blue);
		pal.setColor(QPalette.Background, Qt.gray);
		self.warr[3].setPalette(pal);		
		
		self.vlayout.addWidget(self.warr[0])
		self.vlayout.addLayout(self.hlayout)
		self.vlayout.addWidget(self.warr[1])

		self.hlayout.addWidget(self.warr[2])
		self.hlayout.addWidget(self.container)		
		self.hlayout.addWidget(self.warr[3])

		self.vlayout.setSpacing(0)
		self.hlayout.setSpacing(0)
		#self.vlayout.setContentsMargins(0,0,0,0)
		#self.hlayout.setContentsMargins(0,0,0,0)

		self.setLayout(self.vlayout)


class PaintPreDialog(QDialog):
	def __init__(self, main):
		super().__init__()
		self.layout = QVBoxLayout()
		self.label = QLabel()
		self.pix = QPixmap(main.make_image())
		self.label.setPixmap(self.pix)
		self.layout.addWidget(self.label)
		self.layout.setContentsMargins(0,0,0,0)
		self.setLayout(self.layout)
		self.window().setFixedSize( self.window().sizeHint() );

class PaintWidget(QWidget):
	def __init__(self):
		self.resize_after_render_data = None
		self.resize_after_render_queued = False
		self.no_text_render = False
		self.no_resize=False
		self.common_mouse_events_enabled = False
		self.offset = QPointF(0,0)

		self.labels_center = QPointF(0,0)
		self.labels_width_scale = 1

		self.last_point = QPointF(0,0)
		self.mouse_pressed = False
		self.selected_label_id = None
		self.label_items = {}
		self.scene_interaction = None
		self._layout_hover = None
		self._layout_drag = None
		self._exporting = False
		self._layout_render_frame = None
		self._annotation_hover = None
		self._annotation_drag = None
		self._legacy_free_labels = False
		super().__init__()
		self.setMouseTracking(True)
		self.installEventFilter(self)

	def enable_common_mouse_events(self):
		self.common_mouse_events_enabled = True

	def enable_legacy_free_labels(self):
		self._legacy_free_labels = True

	def width(self):
		if self._layout_render_frame is not None:
			return max(1, int(round(self._layout_render_frame.width)))
		return super().width()

	def height(self):
		if self._layout_render_frame is not None:
			return max(1, int(round(self._layout_render_frame.height)))
		return super().height()

	def resize_after_render(self, x, y):
		if self.shemetype.page_layout is not None:
			return
		self.resize_after_render_data = (x, y)

	def apply_resize_after_render(self):
		self.resize_after_render_queued = False
		size = self.resize_after_render_data
		self.resize_after_render_data = None
		if size is None:
			return
		if common.PAINT_CONTAINER.curwidget is not self:
			return
		width, height = int(size[0]), int(size[1])
		if self.width() == width and self.height() == height:
			return
		common.PAINT_CONTAINER.resize(width, height)

	def resizeEvent(self, ev):
		if getattr(self, "shemetype", None) is not None:
			self._clamp_page_layout()
			self.shemetype.canvas_size = (self.width(), self.height())
		blockers = (
			QSignalBlocker(self.shemetype.width_getter.obj),
			QSignalBlocker(self.shemetype.height_getter.obj),
		)
		try:
			self.shemetype.width_getter.set(self.width())
			self.shemetype.height_getter.set(self.height())
		finally:
			del blockers

		self.shemetype.updateSizeFields()

	def _clamp_page_layout(self):
		layout = self.shemetype.page_layout
		if layout is None:
			return
		canvas_width = max(1, super().width())
		canvas_height = max(1, super().height())
		for frame in (layout.task_frame, layout.note_frame):
			frame.width = min(max(1, frame.width), canvas_width)
			frame.height = min(max(1, frame.height), canvas_height)
			frame.x = min(max(0, frame.x), canvas_width - frame.width)
			frame.y = min(max(0, frame.y), canvas_height - frame.height)

	def make_image(self):
		img = QImage(self.size(), QImage.Format_ARGB32)
		self._exporting = True
		try:
			with QPainter(img) as painter:
				self.render(painter)
		finally:
			self._exporting = False

		return img

	def _derived_page_layout(self):
		width = max(1, self.width())
		height = max(1, self.height())
		current_font = self.font
		font = QFont(current_font() if callable(current_font) else current_font)
		font.setPointSize(self.shemetype.font_size.get())
		lines = self.shemetype.texteditor.toPlainText().splitlines()
		note_height = max(50, QFontMetrics(font).height() * max(1, len(lines)) + 20)
		note_height = min(note_height, max(1, height // 2))
		margin = min(20, max(0, width // 8), max(0, height // 8))
		note_y = max(margin, height - note_height - margin)
		task_height = max(1, note_y - margin * 2)
		return PageLayout(
			task_frame=PageFrame(
				margin,
				margin,
				max(1, width - margin * 2),
				task_height,
			),
			note_frame=PageFrame(
				margin,
				note_y,
				max(1, width - margin * 2),
				max(1, height - note_y - margin),
			),
		)

	def page_layout(self):
		return self.shemetype.page_layout

	def activate_page_layout(self):
		if self.shemetype.page_layout is None:
			self.shemetype.page_layout = self._derived_page_layout()
			self.page_layout_state_changed()
		return self.shemetype.page_layout

	def page_layout_state_changed(self):
		self._layout_hover = None
		self._layout_drag = None
		self.unsetCursor()
		self.update()

	def _layout_frame_rect(self, frame_name):
		frame = getattr(self.shemetype.page_layout, frame_name)
		return QRectF(frame.x, frame.y, frame.width, frame.height)

	def _layout_grip_rect(self, rect):
		return QRectF(rect.center().x() - 11, rect.top() + 7, 22, 9)

	def _layout_handle_rects(self, rect):
		points = {
			"nw": rect.topLeft(),
			"n": QPointF(rect.center().x(), rect.top()),
			"ne": rect.topRight(),
			"e": QPointF(rect.right(), rect.center().y()),
			"se": rect.bottomRight(),
			"s": QPointF(rect.center().x(), rect.bottom()),
			"sw": rect.bottomLeft(),
			"w": QPointF(rect.left(), rect.center().y()),
		}
		return {
			name: QRectF(point.x() - 4, point.y() - 4, 8, 8)
			for name, point in points.items()
		}

	def _layout_hit_test(self, point):
		if self.shemetype.page_layout is None:
			return None
		for frame_name in ("note_frame", "task_frame"):
			rect = self._layout_frame_rect(frame_name)
			for handle, handle_rect in self._layout_handle_rects(rect).items():
				if handle_rect.contains(point):
					return frame_name, "resize", handle
			if self._layout_grip_rect(rect).contains(point):
				return frame_name, "move", None
		for frame_name in ("note_frame", "task_frame"):
			if self._layout_frame_rect(frame_name).contains(point):
				return frame_name, "hover", None
		return None

	def _layout_cursor(self, hit):
		if hit is None or hit[1] == "hover":
			return Qt.ArrowCursor
		if hit[1] == "move":
			return Qt.SizeAllCursor
		handle = hit[2]
		if handle in ("n", "s"):
			return Qt.SizeVerCursor
		if handle in ("e", "w"):
			return Qt.SizeHorCursor
		if handle in ("nw", "se"):
			return Qt.SizeFDiagCursor
		return Qt.SizeBDiagCursor

	def _start_layout_drag(self, point, hit):
		layout = self.shemetype.page_layout
		frame = getattr(layout, hit[0])
		self._layout_drag = {
			"frame": hit[0],
			"action": hit[1],
			"handle": hit[2],
			"start": QPointF(point),
			"original": PageFrame(frame.x, frame.y, frame.width, frame.height),
		}
		self._layout_hover = hit[0]
		self.setCursor(self._layout_cursor(hit))
		self.update()

	def _update_layout_drag(self, point):
		drag = self._layout_drag
		if drag is None:
			return
		delta = point - drag["start"]
		original = drag["original"]
		x, y = original.x, original.y
		width, height = original.width, original.height
		if drag["action"] == "move":
			x = min(max(0, x + delta.x()), self.width() - width)
			y = min(max(0, y + delta.y()), self.height() - height)
		else:
			handle = drag["handle"]
			right = original.x + original.width
			bottom = original.y + original.height
			if "w" in handle:
				x = min(max(0, original.x + delta.x()), right - 40)
				width = right - x
			if "e" in handle:
				width = min(max(40, original.width + delta.x()), self.width() - x)
			if "n" in handle:
				y = min(max(0, original.y + delta.y()), bottom - 40)
				height = bottom - y
			if "s" in handle:
				height = min(max(40, original.height + delta.y()), self.height() - y)
		frame = getattr(self.shemetype.page_layout, drag["frame"])
		frame.x, frame.y, frame.width, frame.height = x, y, width, height
		self.update()

	def eventFilter(self, watched, event):
		if watched is not self:
			return False
		event_type = event.type()
		if event_type == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
			hit = self._layout_hit_test(QPointF(event.pos()))
			if hit is not None and hit[1] in ("move", "resize"):
				self._start_layout_drag(event.pos(), hit)
				return True
			if self._annotation_press(event.pos()):
				return True
		if (
			event_type == QEvent.MouseButtonPress
			and event.button() == Qt.RightButton
			and self._show_annotation_context_menu(event)
		):
			return True
		if (
			event_type == QEvent.MouseButtonDblClick
			and event.button() == Qt.LeftButton
			and self._annotation_double_click(event.pos())
		):
			return True
		if event_type == QEvent.MouseMove:
			if self._layout_drag is not None:
				self._update_layout_drag(event.pos())
				return True
			if self._annotation_move(event.pos()):
				return True
			hit = self._layout_hit_test(QPointF(event.pos()))
			hover = hit[0] if hit is not None else None
			if hover != self._layout_hover:
				self._layout_hover = hover
				self.update()
			if self._annotation_hover is not None:
				self.setCursor(Qt.SizeAllCursor)
			else:
				self.setCursor(self._layout_cursor(hit))
			return False
		if event_type == QEvent.MouseButtonRelease and self._layout_drag is not None:
			self._update_layout_drag(event.pos())
			self._layout_drag = None
			self.unsetCursor()
			self.update()
			return True
		if event_type == QEvent.MouseButtonRelease and self._annotation_release():
			return True
		if event_type == QEvent.Leave and self._layout_drag is None:
			if self._layout_hover is not None:
				self._layout_hover = None
				self.update()
			if self._annotation_hover is not None:
				self._annotation_hover = None
				self.update()
			self.unsetCursor()
		return False

	def _uses_legacy_free_labels(self):
		return self.common_mouse_events_enabled or self._legacy_free_labels

	def _annotation_records(self, create=False):
		if self._uses_legacy_free_labels():
			return None
		task = getattr(getattr(self, "shemetype", None), "task", None)
		if not isinstance(task, dict):
			return None
		records = task.get("annotations")
		if records is None and create:
			records = []
			task["annotations"] = records
		return records if isinstance(records, list) else None

	def _annotation_value(self, record, name, default=None):
		if isinstance(record, dict):
			return record.get(name, default)
		return getattr(record, name, default)

	def _annotation_font(self):
		current = self.font
		font = QFont(current() if callable(current) else current)
		scheme = getattr(self, "shemetype", None)
		font_size = getattr(scheme, "font_size", None)
		if font_size is not None:
			font.setPointSize(font_size.get())
		font.setItalic(True)
		return font

	def _annotation_local_point(self, qt_point):
		point = QPointF(qt_point)
		scheme = getattr(self, "shemetype", None)
		if scheme is None:
			return None
		layout = scheme.page_layout
		if layout is None:
			return point
		frame = layout.task_frame
		if not QRectF(frame.x, frame.y, frame.width, frame.height).contains(point):
			return None
		return QPointF(point.x() - frame.x, point.y() - frame.y)

	def _annotation_bounds(self, record):
		pos = self._annotation_value(record, "pos")
		if not isinstance(pos, (list, tuple)) or len(pos) != 2:
			return None
		try:
			point = QPointF(float(pos[0]), float(pos[1]))
		except (TypeError, ValueError):
			return None
		text = paintool.greek(str(self._annotation_value(record, "text", "")))
		metrics = QFontMetrics(self._annotation_font())
		width = max(5, metrics.horizontalAdvance(text) + 5)
		height = max(1, metrics.height())
		return QRectF(
			point.x() - width / 2,
			point.y() - height / 2,
			width,
			height,
		)

	def _annotation_hit(self, point):
		if point is None:
			return None
		records = self._annotation_records()
		if records is None:
			return None
		for index in range(len(records) - 1, -1, -1):
			bounds = self._annotation_bounds(records[index])
			if bounds is not None and bounds.contains(point):
				return index
		return None

	def _annotation_press(self, qt_point):
		if self._uses_legacy_free_labels():
			return False
		point = self._annotation_local_point(qt_point)
		index = self._annotation_hit(point)
		if index is None:
			return False
		self._annotation_hover = index
		self._annotation_drag = {
			"index": index,
			"last": point,
		}
		self.update()
		return True

	def _annotation_move(self, qt_point):
		if self._uses_legacy_free_labels():
			return False
		point = self._annotation_local_point(qt_point)
		if self._annotation_drag is not None:
			if point is None:
				return True
			records = self._annotation_records()
			index = self._annotation_drag["index"]
			if records is None or not 0 <= index < len(records):
				self._annotation_drag = None
				return True
			record = records[index]
			pos = self._annotation_value(record, "pos", (0, 0))
			diff = point - self._annotation_drag["last"]
			new_pos = [float(pos[0]) + diff.x(), float(pos[1]) + diff.y()]
			if isinstance(record, dict):
				record["pos"] = new_pos
			else:
				record.pos = new_pos
			self._annotation_drag["last"] = point
			self._annotation_hover = index
			self.update()
			return True
		index = self._annotation_hit(point)
		if index != self._annotation_hover:
			self._annotation_hover = index
			self.update()
		return False

	def _annotation_release(self):
		if self._annotation_drag is None:
			return False
		self._annotation_drag = None
		self.update()
		return True

	def _annotation_double_click(self, qt_point):
		if self._uses_legacy_free_labels():
			return False
		index = self._annotation_hit(self._annotation_local_point(qt_point))
		if index is None:
			return False
		self._annotation_hover = index
		self.edit_annotation(index)
		return True

	def _show_annotation_context_menu(self, event):
		if self._uses_legacy_free_labels():
			return False
		point = self._annotation_local_point(event.pos())
		if point is None:
			return False
		index = self._annotation_hit(point)
		self._annotation_hover = index
		menu = QMenu(self)
		if index is None:
			menu.addAction(
				self.Action(
					"Создать метку",
					self,
					functools.partial(self.create_annotation, point, "Text"),
				)
			)
		else:
			menu.addAction(
				self.Action(
					"Редактировать текст",
					self,
					functools.partial(self.edit_annotation, index),
				)
			)
			menu.addAction(
				self.Action(
					"Удалить метку",
					self,
					functools.partial(self.delete_annotation, index),
				)
			)
			menu.addAction(
				self.Action(
					"Клонировать метку",
					self,
					functools.partial(self.clone_annotation, point, index),
				)
			)
		menu.popup(self.mapToGlobal(event.pos()))
		return True

	def create_annotation(self, pos, text="Text"):
		records = self._annotation_records(create=True)
		if records is None:
			return
		records.append(
			{
				"text": str(text),
				"pos": [float(pos.x()), float(pos.y())],
			}
		)
		self._annotation_hover = len(records) - 1
		self.update()

	def edit_annotation(self, index):
		records = self._annotation_records()
		if records is None or not 0 <= index < len(records):
			return
		record = records[index]
		text, accepted = QInputDialog.getText(
			self,
			"Текст",
			"Введите текст:",
			text=str(self._annotation_value(record, "text", "")),
		)
		if accepted:
			if isinstance(record, dict):
				record["text"] = text
			else:
				record.text = text
			self.update()

	def delete_annotation(self, index):
		records = self._annotation_records()
		if records is None or not 0 <= index < len(records):
			return
		del records[index]
		self._annotation_hover = None
		self._annotation_drag = None
		self.update()

	def clone_annotation(self, pos, index):
		records = self._annotation_records()
		if records is None or not 0 <= index < len(records):
			return
		text = self._annotation_value(records[index], "text", "")
		self.create_annotation(QPointF(pos.x() + 30, pos.y()), text)

	def _paint_annotations(self):
		records = self._annotation_records()
		if not records:
			return
		self.painter.save()
		try:
			self.painter.setFont(self._annotation_font())
			for index, record in enumerate(records):
				bounds = self._annotation_bounds(record)
				if bounds is None:
					continue
				if index == self._annotation_hover and not self._exporting:
					self.painter.setPen(QPen(Qt.black))
					self.painter.setBrush(QColor(0, 255, 0, 179))
					self.painter.drawRect(bounds)
				self.painter.setPen(self.pen)
				self.painter.setBrush(Qt.NoBrush)
				self.painter.drawText(
					bounds,
					Qt.AlignCenter,
					paintool.greek(
						str(self._annotation_value(record, "text", ""))
					),
				)
		finally:
			self.painter.restore()

	def _paint_layout_overlay(self):
		if (
			self._exporting
			or self.shemetype.page_layout is None
			or self._layout_hover is None
		):
			return
		rect = self._layout_frame_rect(self._layout_hover)
		self.painter.save()
		pen = QPen(QColor(35, 120, 210, 210), 1, Qt.DashLine)
		self.painter.setPen(pen)
		self.painter.setBrush(Qt.NoBrush)
		self.painter.drawRect(rect)
		self.painter.setPen(QPen(QColor(35, 120, 210), 1))
		self.painter.setBrush(QColor(255, 255, 255, 235))
		for handle_rect in self._layout_handle_rects(rect).values():
			self.painter.drawRect(handle_rect)
		grip = self._layout_grip_rect(rect)
		self.painter.setBrush(QColor(35, 120, 210, 220))
		self.painter.drawRoundedRect(grip, 2, 2)
		self.painter.setPen(QPen(Qt.white, 1))
		for offset in (-5, 0, 5):
			x = grip.center().x() + offset
			self.painter.drawLine(
				QPointF(x, grip.top() + 2),
				QPointF(x, grip.bottom() - 2),
			)
		self.painter.restore()

	def framed_scene(self, scene, recompose=False):
		if self.shemetype.page_layout is None:
			return scene
		objects = tuple(
			item
			for item in scene.objects
			if getattr(item, "object_id", None) != "viewport-border"
		)
		if not recompose:
			if len(objects) == len(scene.objects):
				return scene
			return type(scene)(
				scene.viewport,
				objects,
				content_bounds=scene.content_bounds,
				background=scene.background,
			)
		width = self.width()
		height = self.height()
		source = scene.viewport
		offset = Point(
			(width - source.width) / 2 - source.x,
			(height - source.height) / 2 - source.y,
		)
		content_bounds = (
			scene.content_bounds.translated(offset)
			if scene.content_bounds is not None
			else source.translated(offset)
		)
		return Scene(
			Rect(0, 0, width, height),
			(Group(objects, offset=offset),),
			content_bounds=content_bounds,
			background=scene.background,
		)

	def predraw_dialog(self):
		PaintPreDialog(self).exec()

	def save_image(self, path):
		self.make_image().save(path)
		
	def paintEventCommon(self):
		font_size = self.shemetype.font_size.get()
		lwidth = self.shemetype.line_width.get()

		painter = QPainter(self)
		painter.setRenderHints(QPainter.Antialiasing)
		self.font = painter.font()
		self.font.setItalic(True)
		self.font.setPointSize(font_size)
		painter.setFont(self.font)

		self.default_pen = QPen()
		self.pen = self.default_pen
		self.default_pen.setWidth(lwidth)
		painter.setPen(self.default_pen)
		paintool.pen = self.default_pen

		self.halfpen = QPen()
		self.halfpen.setWidth((int)(lwidth/2))
		paintool.halfpen = self.halfpen

		self.doublepen = QPen()
		self.doublepen.setWidth((int)(lwidth*2))
		paintool.doublepen = self.doublepen

		self.axpen = QPen(Qt.DashDotLine)
		self.axpen.setWidth((int)(lwidth/2))
		paintool.axpen = self.axpen

		self.widegreen = QPen()
		self.widegreen.setWidth((int)(lwidth*2))
		self.widegreen.setColor(Qt.green)
		paintool.widegreen = self.widegreen

		self.green = QPen()
		self.green.setWidth(lwidth)
		self.green.setColor(Qt.green)
		paintool.green = self.green

		self.blue = QPen()
		self.blue.setWidth(lwidth)
		self.blue.setColor(Qt.blue)
		paintool.blue = self.blue

		self.halfgreen = QPen()
		self.halfgreen.setWidth((int)(lwidth/2))
		self.halfgreen.setColor(Qt.green)
		paintool.halfgreen = self.halfgreen

		self.dashgreen = QPen(Qt.DashDotLine)
		self.dashgreen.setWidth(lwidth*2)
		self.dashgreen.setColor(Qt.green)
		paintool.dashgreen = self.dashgreen
		
		self.default_brush = QBrush(Qt.SolidPattern)
		self.default_brush.setColor(Qt.white)
		painter.setBrush(self.default_brush)

		painter.setPen(Qt.NoPen)
		painter.setBrush(Qt.white)
		painter.drawRect(QRectF(0,0,self.width(),self.height()))
		painter.setPen(self.pen)
		painter.setBrush(Qt.white)
		self.painter = painter
		
	def eval_hcenter(self):
		if self.shemetype.page_layout is not None:
			self.hcenter = self.height() / 2
			self.text_height = 0
			return
		if not self.no_text_render:
			addtext = self.shemetype.texteditor.toPlainText()
			self.hcenter = self.height()/2 - QFontMetrics(self.font).height() * len(addtext.splitlines()) / 2
			self.text_height = QFontMetrics(self.font).height() * len(addtext.splitlines())

	def _paint_task_contents(self, ev):
		self.eval_hcenter()
		self.paintEventImplementation(ev)
		self._paint_annotations()
		if self.scene_interaction is not None:
			self.scene_interaction.set_device_origin(
				self._layout_render_frame.x if self._layout_render_frame else 0,
				self._layout_render_frame.y if self._layout_render_frame else 0,
			)
		if self.common_mouse_events_enabled:
			self.common_scene.addRect(
				0,
				0,
				self.width(),
				self.height(),
				pen=QPen(Qt.NoPen),
			)
			self.common_scene.render(self.painter)

	def _paint_note(self, frame=None):
		addtext = self.shemetype.texteditor.toPlainText()
		self.painter.setPen(self.pen)
		self.painter.setFont(self.font)
		self.painter.setBrush(Qt.black)
		if frame is not None:
			self.painter.drawText(
				QRectF(frame.x, frame.y, frame.width, frame.height),
				Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap,
				paintool.greek(addtext),
			)
			return
		n = len(addtext.splitlines())
		for i, line in enumerate(addtext.splitlines()):
			self.painter.drawText(
				QPointF(
					40,
					self.height() - QFontMetrics(self.font).height() * (n - i),
				),
				paintool.greek(line),
			)

	def paintEvent(self, ev):
		self.common_scene = QGraphicsScene()

		try:
			self.paintEventCommon()
			layout = self.shemetype.page_layout
			if layout is None:
				self._paint_task_contents(ev)
				if not self.no_text_render:
					self._paint_note()
			else:
				frame = layout.task_frame
				self.painter.save()
				self.painter.setClipRect(
					QRectF(frame.x, frame.y, frame.width, frame.height)
				)
				self.painter.setViewport(
					int(round(frame.x)),
					int(round(frame.y)),
					max(1, int(round(frame.width))),
					max(1, int(round(frame.height))),
				)
				self.painter.setWindow(
					0,
					0,
					max(1, int(round(frame.width))),
					max(1, int(round(frame.height))),
				)
				self._layout_render_frame = frame
				try:
					self._paint_task_contents(ev)
				finally:
					self._layout_render_frame = None
					self.painter.restore()
				self._paint_note(layout.note_frame)

			self._paint_layout_overlay()
			
			self.painter.end()
	
			if self.resize_after_render_data is not None:
				if not self.resize_after_render_queued:
					self.resize_after_render_queued = True
					QTimer.singleShot(0, self.apply_resize_after_render)

		except Exception as ex:
			self._layout_render_frame = None
			if EXIT_ON_EXCEPT:
				traceback.print_exc()				
				exit(0)

			txt = traceback.format_exc()
			if ERROR_REPORTER is not None:
				ERROR_REPORTER("render", str(ex), txt)
				if hasattr(self, "painter") and self.painter.isActive():
					self.painter.end()
				return

			msg = QMessageBox()
			msg.setText("Возникла ошибка при отрисовке задачи:")
			msg.setInformativeText(txt)
			msg.setStandardButtons(QMessageBox.Ok)

			print(txt)
			msg.exec()

			self.painter.end()

	def sections(self):
		return self.shemetype.task["sections"]

	def bsections(self):
		return self.shemetype.task["betsect"]

	def sectforce(self):
		return self.shemetype.task["sectforce"]

	def sectforces(self):
		return self.sectforce()





	def mousePressEvent(self, ev):
		if not self.common_mouse_events_enabled:
			return

		if self.scene_interaction is not None:
			self.track_point = self.scene_interaction.point(ev.pos())
		else:
			self.track_point = QPointF(ev.pos().x(), ev.pos().y()) + self.offset

		create_label = self.Action("Создать метку", self, functools.partial(self.create_label, self.track_point))
		if ev.button() == Qt.RightButton:
			if self.selected_label_id:
				menu = QMenu(self)
				acts = [
					 self.Action("Редактировать текст", self, functools.partial(self.edit_text)),
					 self.Action("Удалить метку", self, functools.partial(self.delete_label)),
					 self.Action("Клонировать метку", self, functools.partial(self.clone_label, self.track_point)),
				]
				for a in acts:
					menu.addAction(a)

				menu.popup(self.mapToGlobal(ev.pos()))
				return
			
			menu = QMenu(self)
			acts = [
				 self.Action("Создать метку", self, functools.partial(self.create_label, self.track_point)),
			]
			for a in acts:
				menu.addAction(a)

			menu.popup(self.mapToGlobal(ev.pos()))
			return

		self.mouse_pressed=True
		self.update()

	def delete_label(self):
		label = self.selected_label_record()
		if label is not None:
			self.shemetype.task["labels"].remove(label)
			self.selected_label_id = None

	def edit_text(self):
		label = self.selected_label_record()
		if label is None:
			return
		text, ok = QInputDialog.getText(
			self,
			"Текст",
			"Введите текст:",
			text=label.text,
		)
		if ok and label is not None:
			label.text = text
		self.update()

	def create_label(self, pos):
		pos = pos - self.labels_center
		self.shemetype.task["labels"].append(self.shemetype.confwidget.label("Text", (pos.x()/self.labels_width_scale, pos.y())))

	def clone_label(self, pos):
		pos = pos - self.labels_center
		label = self.selected_label_record()
		if label is not None:
			self.shemetype.task["labels"].append(self.shemetype.confwidget.label(label.text, ((pos.x() + 30)/self.labels_width_scale, pos.y())))

	def selected_label_record(self):
		if self.selected_label_id is None:
			return None
		if self.scene_interaction is not None:
			entry = self.scene_interaction.index.get(self.selected_label_id)
			if entry is None:
				return None
			index = entry.metadata_value("index")
			if not isinstance(index, int):
				return None
			labels = self.shemetype.task["labels"]
			return labels[index] if 0 <= index < len(labels) else None
		item = self.label_items.get(self.selected_label_id)
		return item.label if item is not None else None

	def mouseReleaseEvent(self, ev):
		if not self.common_mouse_events_enabled:
			return

		self.mouse_pressed = False
		self.update()

	def mouseMoveEvent(self, ev):
		if not self.common_mouse_events_enabled:
			return

		if self.scene_interaction is not None:
			self.track_point = self.scene_interaction.point(ev.pos())
		else:
			self.track_point = QPointF(ev.pos().x(), ev.pos().y()) + self.offset
		diff = self.track_point - self.last_point

		if not self.mouse_pressed:
			if self.scene_interaction is not None:
				hit = self.scene_interaction.hit_test(ev.pos(), kinds=("label",))
				self.selected_label_id = hit.object_id if hit is not None else None
			else:
				self.selected_label_id = None
				for k, h in self.label_items.items():
					if h.boundingRect().contains(self.track_point):
						self.selected_label_id = k
						self.hovered_sect = None
						self.hovered_node = None
						break
		else:
			if self.selected_label_id:
				label = self.selected_label_record()
				if label is not None:
					label.move2(QPointF(diff.x()/self.labels_width_scale, diff.y()))

		self.last_point = self.track_point 
		self.repaint()

	def Action(self, name, parent, trig=None):
		act = QAction(name, parent)
		if trig:
			act.triggered.connect(trig)

		return act

	def draw_labels(self):
		self.label_items = {}
		# Тексты
		for s in self.shemetype.task["labels"]:
			self.draw_label(
				paintool.greek(s.text), 
				(
					s.pos[0]*self.labels_width_scale+self.labels_center.x(),
				  	s.pos[1]+self.labels_center.y() 
				), label=s)

	def draw_label(self, text, pos, label):
		item = TextItem(
			text, 
			self.font, 
			QPointF(*pos), 
			self.pen)

		item.label = label
		self.label_items[id(label)] = item
		if (self.selected_label_id == id(label)):
			self.common_scene.addRect(item.boundingRect(), brush=Qt.green)

		self.common_scene.addItem(item)
