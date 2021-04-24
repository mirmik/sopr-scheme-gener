from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import paintool

class TextItem(QGraphicsItem):
	def __init__(self, text, font, center, pen, offset="none", rotate=False, clean=False):
		super().__init__()
		self.text = text
		self.font = font
		self.center = center
		self.pen = pen
		self.selected=False
		self.offset = offset
		self.rotate = rotate
		self.clean = clean

	def boundingRect(self):
		metrics = QFontMetrics(self.font)
		width = metrics.width(self.text)
		height = metrics.height()
		self.width = width
		self.height = height

		if self.offset == "none":
			box = QRectF(self.center.x() - width/2, self.center.y() - height/2, width, height)

		elif self.offset == "left":
			box = QRectF(self.center.x() - width, self.center.y() - height/2, width, height)

		elif self.offset == "right":
			box = QRectF(self.center.x(), self.center.y() - height/2, width, height)
	
		self.spoint = self.center + QPointF(-width/2, -height/2) 

		p1 = QPointF(box.x(), box.y())
		p2 = QPointF(box.x()+box.width(), box.y())
		p3 = QPointF(box.x(), box.y()+box.height())
		p4 = QPointF(box.x()+box.width(), box.y()+box.height())

		c = (p1 + p2 + p3 + p4)/4 

		d1 = p1 - c
		d2 = p2 - c
		d3 = p3 - c
		d4 = p4 - c

		d1 = c + paintool.rotate(self.rotate, d1)
		d2 = c + paintool.rotate(self.rotate, d2)
		d3 = c + paintool.rotate(self.rotate, d3)
		d4 = c + paintool.rotate(self.rotate, d4)

		xmin = min(d1.x(), d2.x(), d3.x(), d4.x())
		xmax = max(d1.x(), d2.x(), d3.x(), d4.x())
		ymin = min(d1.y(), d2.y(), d3.y(), d4.y())
		ymax = max(d1.y(), d2.y(), d3.y(), d4.y())

		if self.rotate:
			self.spoint = (
				self.center +
				paintool.rotate(self.rotate, QPointF(-width/2, -height/2))
			)

		return QRectF(QPointF(xmin, ymin), QPointF(xmax,ymax))

	def paint(self, painter, option, widget):
		painter.setPen(self.pen)
		painter.setFont(self.font)

		box = self.boundingRect()
		
		if self.clean:
			painter.setPen(Qt.NoPen)
			painter.drawRect(box)
			painter.setPen(self.pen)

		if self.rotate:
			box = self.boundingRect()
			painter.translate(self.spoint)
			painter.rotate(-90)
			painter.drawText(QPointF(-self.width,-self.height/4), self.text)
			painter.rotate(90)
			painter.translate(-self.spoint)
		else:
			painter.drawText(self.boundingRect(), self.text)
		
