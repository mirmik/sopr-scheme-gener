from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import numpy
import paintool

def deg(x): return x / 180.0 * math.pi

class Sharn3dItem(QGraphicsItem):
	def __init__(self, trans, pnt, vec, xvec, yvec, pen, brush = Qt.BDiagPattern):
		super().__init__()
		self.trans = trans
		self.pnt= pnt
		self.vec = vec
		self.xvec = xvec
		self.yvec = yvec
		self.brush = brush
		self.pen = pen
		
	def boundingRect(self):
		return QRectF(
			self.trans(self.pnt + self.vec) + QPointF(-25,-25), 
			self.trans(self.pnt + self.vec) + QPointF(25,25))

	def paint(self, painter, option, widget):
		trans = self.trans
		pnt= self.pnt
		vec = self.vec
		xvec = self.xvec
		yvec = self.yvec
		brush = self.brush

		apnt = trans(pnt)
		bpnt = trans(numpy.array(pnt)+numpy.array(vec))

		c0pnt = trans(numpy.array(pnt)+numpy.array(vec)+numpy.array(xvec))
		c1pnt = trans(numpy.array(pnt)+numpy.array(vec)+numpy.array(xvec)+numpy.array(yvec))
		c2pnt = trans(numpy.array(pnt)+numpy.array(vec)-numpy.array(xvec)+numpy.array(yvec))
		c3pnt = trans(numpy.array(pnt)+numpy.array(vec)-numpy.array(xvec))

		circ0 = paintool.radrect(apnt, 3.5)
		circ1 = paintool.radrect(bpnt, 3.5)

		painter.setPen(self.pen)
		painter.setBrush(Qt.white)
		painter.drawLine(apnt, bpnt)

		painter.drawLine(c0pnt, c3pnt)
		painter.setPen(Qt.NoPen)
		painter.setBrush(brush)
		painter.drawPolygon(
			QPolygonF([
				c0pnt, c1pnt, c2pnt, c3pnt
			])
		)

		painter.setPen(self.pen)
		painter.setBrush(Qt.white)
		painter.drawEllipse(circ0)
		painter.drawEllipse(circ1)
		painter.setPen(self.pen)