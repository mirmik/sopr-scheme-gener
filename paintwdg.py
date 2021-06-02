from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from items.text import *
import traceback
import common
import functools
import paintool

EXIT_ON_EXCEPT = False

def set_EXIT_ON_ERROR():
	global EXIT_ON_EXCEPT
	EXIT_ON_EXCEPT = True

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
		super().__init__()

	def enable_common_mouse_events(self):
		self.common_mouse_events_enabled = True

	def resize_after_render(self, x, y):
		self.resize_after_render_data = (x, y)

	def resizeEvent(self, ev):
		self.shemetype.width_getter.set(self.width())
		self.shemetype.height_getter.set(self.height())

		self.shemetype.updateSizeFields()

	def make_image(self):
		img = QImage(self.size(), QImage.Format_ARGB32)
		
		with QPainter(img) as painter:
			self.render(painter)

		return img

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
		self.halfpen.setWidth(lwidth/2)
		paintool.halfpen = self.halfpen

		self.doublepen = QPen()
		self.doublepen.setWidth(lwidth*2)
		paintool.doublepen = self.doublepen

		self.axpen = QPen(Qt.DashDotLine)
		self.axpen.setWidth(lwidth/2)
		paintool.axpen = self.axpen

		self.widegreen = QPen()
		self.widegreen.setWidth(lwidth*2)
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
		self.halfgreen.setWidth(lwidth/2)
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
		painter.drawRect(QRect(0,0,self.width(),self.height()))
		painter.setPen(self.pen)
		painter.setBrush(Qt.white)
		self.painter = painter
		
	def eval_hcenter(self):
		if not self.no_text_render:
			addtext = self.shemetype.texteditor.toPlainText()
			self.hcenter = self.height()/2 - QFontMetrics(self.font).height() * len(addtext.splitlines()) / 2
			self.text_height = QFontMetrics(self.font).height() * len(addtext.splitlines())

	def paintEvent(self, ev):
		self.common_scene = QGraphicsScene()

		try:
			self.paintEventCommon()			
			self.eval_hcenter()
			self.paintEventImplementation(ev)

			if self.common_mouse_events_enabled:
				self.common_scene.addRect(0,0,self.width(),self.height(), pen=QPen(Qt.NoPen))
				self.common_scene.render(self.painter)

			if not self.no_text_render:
				addtext = self.shemetype.texteditor.toPlainText()
				self.painter.setPen(self.pen)
				self.painter.setFont(self.font)
				self.painter.setBrush(Qt.black)
				n = len(addtext.splitlines())
				for i, l in enumerate(addtext.splitlines()):
					self.painter.drawText(QPoint(
					40, 
					self.height() - QFontMetrics(self.font).height()*(n-i)), 
					paintool.greek(l))
			
			self.painter.end()
	
			if self.resize_after_render_data is not None:
				common.PAINT_CONTAINER.resize(
					self.resize_after_render_data[0],
					self.resize_after_render_data[1]
				)
				self.resize_after_render_data = None

		except Exception as ex:
			if EXIT_ON_EXCEPT:
				traceback.print_exc()				
				exit(0)

			txt = traceback.format_exc()
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

		self.track_point = QPointF(ev.pos().x(), ev.pos().y()) + self.offset

		create_label = self.Action("Создать метку", self, functools.partial(self.create_label, self.track_point))
		if ev.button() == Qt.RightButton:
			if self.selected_label_id:
				label = self.label_items[self.selected_label_id]
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
		 self.shemetype.task["labels"].remove(self.label_items[self.selected_label_id].label)

	def edit_text(self):
		text, ok = QInputDialog.getText(self, 'Текст', 'Введите текст:')
		if (ok):
			self.label_items[self.selected_label_id].label.text = text
		self.update()

	def create_label(self, pos):
		pos = pos - self.labels_center
		self.shemetype.task["labels"].append(self.shemetype.confwidget.label("Text", (pos.x()/self.labels_width_scale, pos.y())))

	def clone_label(self, pos):
		pos = pos - self.labels_center
		self.shemetype.task["labels"].append(self.shemetype.confwidget.label(self.label_items[self.selected_label_id].label.text, ((pos.x() + 30)/self.labels_width_scale, pos.y())))

	def mouseReleaseEvent(self, ev):
		if not self.common_mouse_events_enabled:
			return

		self.mouse_pressed = False
		self.update()

	def mouseMoveEvent(self, ev):
		if not self.common_mouse_events_enabled:
			return

		self.track_point = QPointF(ev.pos().x(), ev.pos().y()) + self.offset
		pos = self.track_point
		diff = self.track_point - self.last_point

		if not self.mouse_pressed:
			self.selected_label_id = None
			for k, h in self.label_items.items():
				if h.boundingRect().contains(self.track_point):
					self.selected_label_id = k
					self.hovered_sect = None
					self.hovered_node = None
					break
		else:
			if self.selected_label_id:
				item = self.label_items[self.selected_label_id]
				label = item.label

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