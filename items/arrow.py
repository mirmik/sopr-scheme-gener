from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math

class ArrowItem(QGraphicsItem):
	def __init__(self, p1, p2, arrow_size, pen, brush, reverse=False):
		super().__init__()
		self.p1 = p1
		self.p2 = p2
		if reverse:
			self.p1, self.p2 = self.p2, self.p1
		self.arrow_size = arrow_size[0]
		self.arrow_size_2 = arrow_size[1]
		self.pen = pen
		self.brush = brush

	def boundingRect(self):
		return QRectF(self.p1, self.p2)


	def paint(self, painter, option, widget):
		painter.setPen(self.pen)
		painter.setBrush(self.brush)
		painter.drawLine(self.p1, self.p2)

		diff = self.p2 - self.p1
		diff = diff / (math.sqrt(diff.x()**2 + diff.y()**2))

		normal = QPointF(diff.y(), -diff.x())
		p3 = self.p2 - diff * self.arrow_size 

		painter.drawPolygon(QPolygonF([self.p2, p3 + normal*self.arrow_size_2, p3 - normal*self.arrow_size_2]))