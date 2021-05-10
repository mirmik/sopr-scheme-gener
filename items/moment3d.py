from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import numpy
import paintool

from items.arrow import ArrowItem

def deg(x): return x / 180.0 * math.pi

class Torque3dItem(QGraphicsItem):
	def __init__(self, trans, pnt, xvec, yvec, arrow_size, pen, brush = Qt.BDiagPattern):
		super().__init__()
		self.trans = trans
		self.pnt= pnt
		self.xvec = xvec
		self.yvec = yvec
		self.brush = brush
		self.arrow_size = arrow_size
		self.pen = pen

		self.apnt = trans(pnt + xvec)
		self.bpnt = trans(pnt - xvec)
		self.cpnt = trans(pnt + xvec + yvec)
		self.dpnt = trans(pnt - xvec - yvec)

		self.points = [ self.apnt, self.bpnt, self.cpnt, self.dpnt ]
		
	def boundingRect(self):
		xmin = min(*[ p.x() for p in self.points ])
		xmax = max(*[ p.x() for p in self.points ])
		ymin = min(*[ p.y() for p in self.points ])
		ymax = max(*[ p.y() for p in self.points ])

		return QRectF(QPointF(xmin-5,ymin-5), QPointF(xmax+5,ymax+5))

	def paint(self, painter, option, widget):
		trans = self.trans
		pnt= self.pnt
		xvec = self.xvec
		yvec = self.yvec
		brush = self.brush
		pen = self.pen
		arrow_size = self.arrow_size

		painter.setPen(pen)
		painter.setBrush(brush)

		ArrowItem(self.apnt, self.cpnt, arrow_size, pen, brush).paint(painter, option, widget)
		ArrowItem(self.bpnt, self.dpnt, arrow_size, pen, brush).paint(painter, option, widget)

		painter.drawLine(self.apnt, self.bpnt)