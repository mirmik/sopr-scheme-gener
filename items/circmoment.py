from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import paintool

def deg(x): return x / 180.0 * math.pi

class CircMomentItem(QGraphicsItem):
	def __init__(self, center, rad, pen=QPen(), brush=QBrush(), arc_angle=deg(90), inverse=False, arrow_size=(15,5), angle=0):
		super().__init__()
		self.angle = angle
		self.center = center
		self.arrow_size = arrow_size
		self.pen = pen
		self.brush = brush
		self.rad = rad
		self.inverse = inverse
		self.arc_angle = arc_angle
		
	def boundingRect(self):
		return QRectF(
			self.center + QPointF(-self.rad,-self.rad), 
			self.center + QPointF(self.rad,self.rad))

	def paint(self, painter, option, widget):
		painter.setPen(self.pen)
		painter.setBrush(self.brush)

		rect = self.boundingRect()
		arc_angle = self.arc_angle / math.pi * 180
		angle = self.angle / math.pi * 180

		pnt1 = paintool.rotate(self.angle + deg(arc_angle/2), QPointF(self.rad, 0))
		pnt2 = paintool.rotate(self.angle - deg(arc_angle/2), QPointF(self.rad, 0))

		aangle = deg(90) if not self.inverse else deg(-90)
		bangle = -self.arc_angle/2 if not self.inverse else self.arc_angle/2
		polygang= self.angle  + aangle + bangle*3/4
		
		if not self.inverse:
			pnt = pnt1
			npnt = pnt2
		
		else:
			pnt = pnt2
			npnt = pnt1

		p1 = self.center + npnt 
		p2 = self.center + npnt + paintool.rotate(polygang, QPointF(self.arrow_size[0], self.arrow_size[1]))
		p3 = self.center + npnt + paintool.rotate(polygang, QPointF(self.arrow_size[0], -self.arrow_size[1]))

		painter.drawLine(self.center, self.center+pnt)
		painter.drawArc(rect, angle*16-arc_angle*16/2, arc_angle*16)

		painter.drawPolygon(QPolygonF([p1,p2,p3]))


