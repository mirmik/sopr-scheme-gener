from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import traceback
import common
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
		super().__init__()

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
		#painter.setRenderHints(QPainter.Antialiasing)
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
		try:
			self.paintEventCommon()			
			self.eval_hcenter()
			self.paintEventImplementation(ev)

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