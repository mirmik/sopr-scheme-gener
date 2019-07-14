from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import common

class ContainerWidget(QWidget):
	def __init__(self, border, fixedSize, filter):
		super().__init__()
		self.border = border
		self.fixedSize = fixedSize

		self.filter = filter
		self.mtrack = False
		self.hormode=False
		self.vermode=False

		self.layout = QVBoxLayout()
		self.curwidget = QWidget()
		self.layout.addWidget(self.curwidget)
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0,0,0,0)
		self.setLayout(self.layout)

		self.setAutoFillBackground(True);
		pal = self.palette();
		#pal.setColor(QPalette.Background, Qt.gray);
		self.setPalette(pal);	

		self.resize(self.curwidget.width(), self.curwidget.height())

	def replace(self, wdg):
		self.layout.removeWidget(self.curwidget)
		self.curwidget.hide()

		self.curwidget = wdg
		self.layout.addWidget(wdg)
		self.curwidget.show()

		if self.filter:
			self.curwidget.installEventFilter(self)
			self.curwidget.setMouseTracking(True)

	def resize(self, w, h):
		if self.border:
			cw, ch = w+2, h+2
		else:
			cw, ch = w, h 

		if self.fixedSize:
			self.curwidget.setFixedSize(w,h)
			super().setFixedSize(cw,ch)
		else:
			pass

	def paintEvent(self, ev):
		"""Рисуем сцену согласно объекта задания"""

		if (self.border):
			painter = QPainter(self)
			painter.drawRect(0,0,self.width()-1,self.height()-1)

		super().paintEvent(ev)

	def mouseMoveEventHandler(self, ev):
		x = ev.pos().x()
		y = ev.pos().y()


		if self.mtrack:
			xdiff = self.lastx - x
			ydiff = self.lasty - y

		def resize_hor():
			sz = self.curwidget.width() + xdiff * self.hormode
			if sz < 10: sz = 10
			self.resize(sz, self.curwidget.height())
			self.update()
			
			if self.hormode == -1:
				self.lastx -= xdiff


		def resize_ver():
			sz = self.curwidget.height() + ydiff * self.vermode
			if sz < 10: sz = 10
			self.resize(self.curwidget.width(), sz)
			self.update()
			
			if self.vermode == -1:
				self.lasty -= ydiff


		if self.mtrack:
			if self.hormode:
				resize_hor()
				return
	
			if self.vermode:
				resize_ver()
				return

		if 1 < x < 10:
			self.setCursor(Qt.SizeHorCursor)
			if self.mtrack: 
				self.hormode = +1
				resize_hor()
			return

		if self.curwidget.width() - 1 > x > self.curwidget.width() - 10:
			self.setCursor(Qt.SizeHorCursor)
			if self.mtrack: 
				self.hormode = -1
				resize_hor()
			return

		if 1 < y < 10:
			self.setCursor(Qt.SizeVerCursor)
			if self.mtrack: 
				self.vermode = +1
				resize_ver()
			return

		if self.curwidget.height() - 1 >y > self.curwidget.height() - 10:
			self.setCursor(Qt.SizeVerCursor)
			if self.mtrack:
				self.vermode = -1 
				resize_ver()
			return

		self.setCursor(Qt.ArrowCursor)

		#->setCursor(Qt::SizeFDiagCursor);

	def mousePressEventHandler(self, ev):
		self.mtrack = True
		self.lastx = ev.pos().x()
		self.lasty = ev.pos().y()

	def mouseReleaseEventHandler(self, ev):
		self.mtrack = False
		self.hormode=False
		self.vermode=False

	def eventFilter(self, obj, event):
		if self.filter is False:
			return True
		
		if event.type() == QtCore.QEvent.MouseMove:
			self.mouseMoveEventHandler(event)
			return True

		if event.type() == QtCore.QEvent.MouseButtonPress:
			self.mousePressEventHandler(event)
			return True

		if event.type() == QtCore.QEvent.MouseButtonRelease:
			self.mouseReleaseEventHandler(event)
			return True

		return False