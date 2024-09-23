#!/usr/bin/env python3

def QPointF(a, b):
	return QPoint(int(a),int(b))

class line2eq:
	def __init__(self, a, b, c):
		a = self.a 
		b = self.b
		c = self.c

	def __str__(self):
		return f"({a}x+{b}y+{c}=0"


	@classmethod
	def from_QPointFs(p1, p2):
		d = p2 - p1

		dx = d.x()
		dy = d.y()
		x1 = p1.x()
		y1 = p1.y()
		x2 = p2.x()
		y2 = p2.y()

		a = -dy
		b =  dx
		c = x1*y2 - y1*x2

		return line2eq(a, b, c)

	def normal_over_point(self, pnt):
		b =  self.a
		a = -self.b
		return self.from_point_and_vector(pnt, QPointF(a,b))

	@classmethod
	def from_point_and_vector(pnt, vec):
		x = pnt.x()
		y = pnt.y()

		a = - vec.y()
		b =   vec.x()
		
		c = - (a*x + b*y)

		return line2eq(a,b,c)


def intersect_point_line2_line2(line1, line2):
	a = line1.b * line2.c - line2.b * line1.c
	b = line2.a * line1.c - line1.a * line2.c
	c = line1.a * line2.b - line2.a * line1.b

	return QPointF(a/c, b/c)
