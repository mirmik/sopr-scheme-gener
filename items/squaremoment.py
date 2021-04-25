from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import paintool

def deg(x): return x / 180.0 * math.pi

class SquareMomentItem(QGraphicsItem):
	def __init__(self, center, x, y, pen=QPen(), brush=QBrush(), inverse=False, arrow_size=(15,5)):
		super().__init__()
		self.center = center
		self.arrow_size = arrow_size
		self.pen = pen
		self.brush = brush
		self.x = x
		self.y = y
		self.inverse = inverse
		
	def boundingRect(self):
		return QRectF(
			self.center + QPointF(-self.x,-self.y), 
			self.center + QPointF(self.x,self.y))

	def paint(self, painter, option, widget):
		painter.setPen(self.pen)
		painter.setBrush(self.brush)

		rect = self.boundingRect()

		painter.setPen(QPen())
		
		painter.drawLine(
			self.center + QPointF(0, self.y),
			self.center + QPointF(0, -self.y)
		)

		painter.setPen(self.pen)
		if self.inverse:
			painter.drawLine(
				self.center + QPointF(0, -self.y),
				self.center + QPointF(-self.x, -self.y)
			)			

			painter.drawLine(
				self.center + QPointF(0, self.y),
				self.center + QPointF(self.x, self.y)
			)			

			painter.drawPolygon(QPolygonF([
				self.center + QPointF(self.x, self.y),
				self.center + QPointF(self.x - self.arrow_size[0], self.y + self.arrow_size[1]),
				self.center + QPointF(self.x - self.arrow_size[0], self.y - self.arrow_size[1])]))

			painter.drawPolygon(QPolygonF([
				self.center + QPointF(-self.x, -self.y),
				self.center + QPointF(-self.x + self.arrow_size[0], -self.y + self.arrow_size[1]),
				self.center + QPointF(-self.x + self.arrow_size[0], -self.y - self.arrow_size[1])]))

		else:
			painter.drawLine(
				self.center + QPointF(0, -self.y),
				self.center + QPointF(self.x, -self.y)
			)			

			painter.drawLine(
				self.center + QPointF(0, self.y),
				self.center + QPointF(-self.x, self.y)
			)			

			painter.drawPolygon(QPolygonF([
				self.center + QPointF(self.x, -self.y),
				self.center + QPointF(self.x - self.arrow_size[0], -self.y + self.arrow_size[1]),
				self.center + QPointF(self.x - self.arrow_size[0], -self.y - self.arrow_size[1])]))

			painter.drawPolygon(QPolygonF([
				self.center + QPointF(-self.x, self.y),
				self.center + QPointF(-self.x + self.arrow_size[0], self.y + self.arrow_size[1]),
				self.center + QPointF(-self.x + self.arrow_size[0], self.y - self.arrow_size[1])]))
