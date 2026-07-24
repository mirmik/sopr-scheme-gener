from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import common

class ContainerWidget(QWidget):
	RESIZE_MARGIN = 9

	def __init__(self, border, fixedSize, filter):
		"""
			filter - фильтровать входящие события
			fixedSize - установить фиксированный размер для виджета.
		"""

		super().__init__()
		self.border = border
		self.fixedSize = fixedSize

		self.filter = filter
		self.mtrack = False
		self.hormode=False
		self.vermode=False
		self.resize_start = None

		self.layout = QVBoxLayout()
		self.curwidget = QWidget()
		self.layout.addWidget(self.curwidget)
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0,0,0,0)
		self.setLayout(self.layout)

		self.setAutoFillBackground(True)
		pal = self.palette()
		#pal.setColor(QPalette.Background, Qt.gray);
		self.setPalette(pal)	

		self.resize(self.curwidget.width(), self.curwidget.height())

	def replace(self, wdg):
		self.layout.removeWidget(self.curwidget)
		self.curwidget.hide()

		self.curwidget = wdg
		self.layout.addWidget(wdg)
		self.resize(wdg.width(), wdg.height())		
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
			self.curwidget.setFixedSize(int(w),int(h))
			super().setFixedSize(int(cw),int(ch))
		else:
			pass

	def paintEvent(self, ev):
		"""Рисуем сцену согласно объекта задания"""

		if (self.border):
			painter = QPainter(self)
			painter.drawRect(0,0,self.width()-1,self.height()-1)

		super().paintEvent(ev)

	def _resize_disabled(self):
		if not getattr(self.curwidget, "no_resize", False):
			return False
		scheme = getattr(self.curwidget, "shemetype", None)
		return scheme is None or scheme.page_layout is None

	def _resize_hit(self, point):
		x = point.x()
		y = point.y()
		margin = self.RESIZE_MARGIN
		width = self.curwidget.width()
		height = self.curwidget.height()
		hormode = (
			1
			if x <= margin
			else -1
			if x >= width - margin
			else 0
		)
		vermode = (
			1
			if y <= margin
			else -1
			if y >= height - margin
			else 0
		)
		return hormode, vermode

	def _resize_cursor(self, hormode, vermode):
		if hormode and vermode:
			return (
				Qt.SizeFDiagCursor
				if hormode == vermode
				else Qt.SizeBDiagCursor
			)
		if hormode:
			return Qt.SizeHorCursor
		if vermode:
			return Qt.SizeVerCursor
		return Qt.ArrowCursor

	def _set_resize_cursor(self, cursor):
		self.setCursor(cursor)
		self.curwidget.setCursor(cursor)

	def mouseMoveEventHandler(self, ev):
		x = ev.pos().x()
		y = ev.pos().y()

		if self._resize_disabled():
			self.mtrack = False
			self.resize_start = None
			self.unsetCursor()
			self.curwidget.unsetCursor()
			return False

		if self.mtrack and self.resize_start is not None:
			start_x, start_y, start_width, start_height = self.resize_start
			width = start_width
			height = start_height
			if self.hormode:
				width = max(10, start_width + (start_x - x) * self.hormode)
			if self.vermode:
				height = max(10, start_height + (start_y - y) * self.vermode)
			self.resize(width, height)
			self.update()
			self._set_resize_cursor(
				self._resize_cursor(self.hormode, self.vermode)
			)
			return True

		hormode, vermode = self._resize_hit(ev.pos())
		if hormode or vermode:
			self._set_resize_cursor(self._resize_cursor(hormode, vermode))
			return True
		self.unsetCursor()
		self.curwidget.unsetCursor()
		return False

	def mousePressEventHandler(self, ev):
		if ev.button() != Qt.LeftButton:
			return False
		if self._resize_disabled():
			return False
		self.hormode, self.vermode = self._resize_hit(ev.pos())
		if not self.hormode and not self.vermode:
			return False
		self.mtrack = True
		self.resize_start = (
			ev.pos().x(),
			ev.pos().y(),
			self.curwidget.width(),
			self.curwidget.height(),
		)
		self._set_resize_cursor(
			self._resize_cursor(self.hormode, self.vermode)
		)
		self.curwidget.grabMouse()
		return True

	def mouseReleaseEventHandler(self, ev):
		handled = self.mtrack
		self.mtrack = False
		self.hormode=False
		self.vermode=False
		self.resize_start = None
		if handled:
			self.curwidget.releaseMouse()
		return handled

	def eventFilter(self, obj, event):
		if self.filter is False:
			return True
		
		if event.type() == QtCore.QEvent.MouseMove:
			return self.mouseMoveEventHandler(event)

		if event.type() == QtCore.QEvent.MouseButtonPress:
			return self.mousePressEventHandler(event)

		if event.type() == QtCore.QEvent.MouseButtonRelease:
			return self.mouseReleaseEventHandler(event)

		return False
