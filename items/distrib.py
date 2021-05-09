from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import numpy

import items.arrow

class DistribArrowsItem(QGraphicsItem):
	def __init__(self, p1, p2, vec, arrow_size, pen, brush, n = 8):
		super().__init__()
		self.p1 = p1
		self.p2 = p2
		self.vec = vec
		self.arrow_size = arrow_size[0]
		self.arrow_size_2 = arrow_size[1]
		self.pen = pen
		self.brush = brush
		self.n = n

		self.a = self.p1
		self.b = self.p2
		self.c = self.p1 - self.vec
		self.d = self.p2 - self.vec

	def boundingRect(self):
		x0 = min(self.p1.x(), self.p2.x(), self.c.x(), self.d.x())
		x1 = max(self.p1.x(), self.p2.x(), self.c.x(), self.d.x())
		y0 = min(self.p1.y(), self.p2.y(), self.c.y(), self.d.y())
		y1 = max(self.p1.y(), self.p2.y(), self.c.y(), self.d.y())

		return QRectF(QPointF(x0, y0), QPointF(x1, y1))


	def paint(self, painter, option, widget):
		painter.setPen(self.pen)

		a = self.p1
		b = self.p2
		c = self.p1 - self.vec
		d = self.p2 - self.vec

		arr1x = numpy.linspace(a.x(), b.x(), num=self.n)
		arr1y = numpy.linspace(a.y(), b.y(), num=self.n)
		arr2x = numpy.linspace(c.x(), d.x(), num=self.n)
		arr2y = numpy.linspace(c.y(), d.y(), num=self.n)

		arr1 = [ QPointF(arr1x[i], arr1y[i]) for i in range(self.n) ]
		arr2 = [ QPointF(arr2x[i], arr2y[i]) for i in range(self.n) ]

		scene = QGraphicsScene()
		for i in range(self.n):
			arrow = items.arrow.ArrowItem(arr2[i], arr1[i], 
				(self.arrow_size, self.arrow_size_2),
				pen=self.pen,
				brush=self.brush
			)
			arrow.paint(painter, None, None)

		painter.drawLine(QLineF(c, d))