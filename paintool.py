from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import common

halfpen = None
pen = None

def deg(arg):
	return math.pi * arg / 180

def deg2rad(arg):
	return arg / 180 * math.pi

def rad2deg(arg):
	return arg * 180 / math.pi

def rotate(angle, pnt):
	return QPointF(pnt.x() * math.cos(angle) - pnt.y() * math.sin(angle), pnt.y() * math.cos(angle) + pnt.x() * math.sin(angle))

#def leftArrow(self, painter, basepoint):
#	arrow_size = self.shemetype.datasettings.arrow_size
#	arrow_head_size = self.shemetype.datasettings.arrow_head_size		
#
#	painter.drawLine(basepoint, QPointF(basepoint.x() - arrow_size, basepoint.y()))
#
#	points = [
#		(basepoint.x() - arrow_size - 2 * arrow_head_size, basepoint.y()), 
#		(basepoint.x() - arrow_size, basepoint.y() - arrow_head_size), 
#		(basepoint.x() - arrow_size, basepoint.y() + arrow_head_size)
#	]
#	qpoints = [QPointF(x, y) for (x, y) in points]
#	polygon = QPolygonF(qpoints)
#
#	painter.drawConvexPolygon(polygon)
#
#def rightArrow(self, painter, basepoint):
#	arrow_size = self.shemetype.datasettings.arrow_size
#	arrow_head_size = self.shemetype.datasettings.arrow_head_size
#
#	painter.drawLine(basepoint, QPointF(basepoint.x() + arrow_size, basepoint.y()))
#
#	points = [
#		(basepoint.x() + arrow_size + 2 * arrow_head_size, basepoint.y()), 
#		(basepoint.x() + arrow_size, basepoint.y() - arrow_head_size), 
#		(basepoint.x() + arrow_size, basepoint.y() + arrow_head_size)
#	]
#	qpoints = [QPointF(x, y) for (x, y) in points]
#	polygon = QPolygonF(qpoints)
#
#	painter.drawConvexPolygon(polygon)

def down_arrow_points(x, y, s):
	return [
		(x, 		y),
		(x + s/3, 	y), 
		(x, 		y + s), 
		(x - s/3, 	y)
	]

def up_arrow_points(x, y, s):
	return [
		(x, 		y),
		(x + s/3, 	y), 
		(x, 		y - s), 
		(x - s/3, 	y)
	]

def down_arrow_points_top(x, y, s):
	return [
		(x, 		y-s),
		(x + s/3, 	y-s), 
		(x, 		y), 
		(x - s/3, 	y-s)
	]

def up_arrow_points_top(x, y, s):
	return [
		(x, 		y+s),
		(x + s/3, 	y+s), 
		(x, 		y), 
		(x - s/3, 	y+s)
	]

def left_arrow_points_top(x, y, s):
	return [
		(x, 		y),
		(x + s, 	y+s/3),
		(x + s, 	y-s/3)
	]

def right_arrow_points_top(x, y, s):
	return [
		(x+0.5, 		y+0.5),
		(x - s+0.5, 	y+s/3+0.5),
		(x - s+0.5, 	y-s/3+0.5)
	]

def angled_arrow_points_top(x, y, a, s):
	return [
		(x, 		y),
		(x - s * math.cos(a) + s/3 * math.sin(a), 	y + s * math.sin(a) + s/3 * math.cos(a)),
		(x - s * math.cos(a) - s/3 * math.sin(a), 	y + s * math.sin(a) - s/3 * math.cos(a))
	]


def paint_arrow(painter, points):
	qpoints = [QPointF(x, y) for (x, y) in points]
	polygon = QPolygonF(qpoints)
	painter.setBrush(Qt.black)
	painter.drawConvexPolygon(polygon)

def down_arrow_head(painter, x, y, s): paint_arrow(painter, down_arrow_points(x, y, s))
def up_arrow_head(painter, x, y, s): paint_arrow(painter, up_arrow_points(x, y, s))
def right_arrow_head(painter, x, y, s): paint_arrow(painter, right_arrow_points(x, y, s))
def left_arrow_head(painter, x, y, s): paint_arrow(painter, left_arrow_points(x, y, s))

def down_arrow_head_top(painter, x, y, s): paint_arrow(painter, down_arrow_points_top(x, y, s))
def up_arrow_head_top(painter, x, y, s): paint_arrow(painter, up_arrow_points_top(x, y, s))
def right_arrow_head_top(painter, x, y, s): paint_arrow(painter, right_arrow_points_top(x, y, s))
def left_arrow_head_top(painter, x, y, s): paint_arrow(painter, left_arrow_points_top(x, y, s))

def left_arrow(painter, pnt, length, headsize):
	painter.drawLine(pnt, QPointF(pnt.x()-length, pnt.y()))
	left_arrow_head_top(painter, pnt.x()-length, pnt.y(), headsize)

def left_arrow_double(painter, pnt, length, headsize, h):
	apnt = pnt + QPointF(0, h/2)
	bpnt = pnt + QPointF(0, -h/2)
	painter.setPen(pen)
	left_arrow(painter, apnt, length, headsize)
	left_arrow(painter, bpnt, length, headsize)
	painter.setPen(halfpen)
	painter.drawLine(apnt, bpnt)

def right_arrow(painter, pnt, length, headsize):
	painter.drawLine(pnt, QPointF(pnt.x()+length, pnt.y()))
	right_arrow_head_top(painter, pnt.x()+length, pnt.y(), headsize)

def right_arrow_double(painter, pnt, length, headsize, h):
	apnt = pnt + QPointF(0, h/2)
	bpnt = pnt + QPointF(0, -h/2)
	painter.setPen(pen)
	right_arrow(painter, apnt, length, headsize)
	right_arrow(painter, bpnt, length, headsize)
	painter.setPen(halfpen)
	painter.drawLine(apnt, bpnt)

def up_arrow(painter, pnt, length, headsize):
	tgt = pnt + QPointF(0, length)
	painter.drawLine(pnt, tgt)
	up_arrow_head_top(painter, tgt.x(), tgt.y(), headsize)

def down_arrow(painter, pnt, length, headsize):
	tgt = pnt + QPointF(0, -length)
	painter.drawLine(pnt, tgt)
	down_arrow_head_top(painter, tgt.x(), tgt.y(), headsize)

def angled_arrow_head_top(painter, pnt, angle, headsize):
	paint_arrow(painter, angled_arrow_points_top(pnt.x(), pnt.y(), angle, headsize))

def common_arrow(painter, spnt, fpnt, arrow_size):
	diff = fpnt - spnt
	angle = math.atan2(-diff.y(), diff.x())

	angled_arrow_head_top(painter, fpnt, angle, arrow_size)
	painter.drawLine(spnt, fpnt)

def arrow_head(painter, pnt, angle, headsize):
	return angled_arrow_head_top(painter, pnt, angle, headsize)

def circular_arrow_base(painter, rect, inverse = False, head_size=12):
	assert rect.width() == rect.height()
	
	lx = rect.x()
	ly = rect.y()
	w = rect.width()
	h = rect.height()

	rrr = w/2#w / 2 / math.sqrt(2)
	
	angle = (115)
	arc_angle = 60
	rangle = angle / 180 * math.pi

	if not inverse:
		painter.drawLine(
			(rect.center()+QPointF(rrr*math.cos(rangle),-rrr*math.sin(rangle))), 
			(rect.center()+QPointF(-rrr*math.cos(rangle),+rrr*math.sin(rangle))))
	
		painter.drawArc(rect, angle*16, arc_angle*16)
		painter.drawArc(rect, angle*16 + 180*16, arc_angle*16)
		
		angled_arrow_head_top(painter, 
			rect.center()+QPointF(rrr*math.cos(rangle+deg(arc_angle)),-rrr*math.sin(rangle+deg(arc_angle))), rangle+deg(130), head_size)
		angled_arrow_head_top(painter, 
			rect.center()+QPointF(-rrr*math.cos(rangle+deg(arc_angle))+1,-rrr*math.sin(-rangle-deg(arc_angle))), rangle+deg(130+180), head_size)
	
	else:
		painter.drawLine(
			(rect.center()+QPointF(rrr*math.cos(rangle),rrr*math.sin(rangle))), 
			(rect.center()+QPointF(-rrr*math.cos(rangle),-rrr*math.sin(rangle))))
	
		painter.drawArc(rect, -angle*16, -arc_angle*16)
		painter.drawArc(rect, -angle*16 - 180*16, -arc_angle*16)
		
		angled_arrow_head_top(painter, 
			rect.center()+QPointF(rrr*math.cos(-rangle-deg(arc_angle)),-rrr*math.sin(-rangle-deg(arc_angle))), -rangle-deg(130), head_size)
		angled_arrow_head_top(painter, 
			rect.center()+QPointF(-rrr*math.cos(-rangle-deg(arc_angle))+1,-rrr*math.sin(+rangle+deg(arc_angle))), -rangle-deg(130+180), head_size)


def moment_arrows(painter, pnt, rad, inverse = False, arrow_size=12):
	angle = -30
	arc_angle = 60
	rangle = angle / 180 * math.pi

	x = pnt.x() - rad
	y = pnt.y() - rad
	x2 = pnt.x() + rad
	y2 = pnt.y() + rad

	if not inverse:
		painter.drawLine(
			(pnt+QPointF(rad*math.cos(rangle),-rad*math.sin(rangle))), 
			(pnt+QPointF(-rad*math.cos(rangle),+rad*math.sin(rangle))))

		painter.drawArc(QRect(x, y, x2-x, y2-y), angle*16, arc_angle*16)
		painter.drawArc(QRect(x, y, x2-x, y2-y), angle*16 + 180*16, arc_angle*16)

		angled_arrow_head_top(painter, 
			pnt+QPointF(
				rad*math.cos(rangle+deg(arc_angle)),
				-rad*math.sin(rangle+deg(arc_angle))
			), rangle+deg(130), arrow_size)
		
		angled_arrow_head_top(painter, 
			pnt+QPointF(
				-rad*math.cos(rangle+deg(arc_angle)),
				-rad*math.sin(-rangle-deg(arc_angle))
			), rangle+deg(130+180), arrow_size)
	

	else:
		painter.drawLine(
			(pnt+QPointF(rad*math.cos(rangle),+rad*math.sin(rangle))), 
			(pnt+QPointF(-rad*math.cos(rangle),-rad*math.sin(rangle))))

		
		painter.drawArc(QRect(x, y, x2-x, y2-y), -angle*16, -arc_angle*16)
		painter.drawArc(QRect(x, y, x2-x, y2-y), -angle*16 - 180*16, -arc_angle*16)
		
		angled_arrow_head_top(painter, 
			pnt+QPointF(
				rad*math.cos(rangle+deg(arc_angle)),
				-rad*math.sin(rangle+deg(arc_angle))
			), rangle+deg(130), arrow_size)
		
		angled_arrow_head_top(painter, 
			pnt+QPointF(
				-rad*math.cos(rangle+deg(arc_angle)),
				-rad*math.sin(-rangle-deg(arc_angle))
			), rangle+deg(130+180), arrow_size)

def circular_arrow(painter, pnt, rad, angle, angle2, arrow_size):
	x = pnt.x() - rad
	y = pnt.y() - rad
	x2 = pnt.x() + rad
	y2 = pnt.y() + rad

	rangle2= angle2
	angle = rad2deg(angle)
	angle2 = rad2deg(angle2)

	painter.drawArc(QRect(x, y, x2-x, y2-y), -angle*16, -(angle2 - angle)*16)

	angled_arrow_head_top(painter, 
		pnt+QPointF(
			rad*math.cos(rangle2),
			rad*math.sin(rangle2)
		), rangle2 + deg(180), arrow_size)

def circular_arrow2(painter, pnt, rad, angle, angle2, arrow_size):
	x = pnt.x() - rad
	y = pnt.y() - rad
	x2 = pnt.x() + rad
	y2 = pnt.y() + rad

	rangle2= angle2
	angle = rad2deg(angle)
	angle2 = rad2deg(angle2)

	painter.drawArc(QRect(x, y, x2-x, y2-y), -angle*16, -(angle2 - angle)*16)

	if angle > angle2:
		aangle = - rangle2 + deg(90)
	else:
		aangle = - rangle2 - deg(90)
	

	angled_arrow_head_top(painter, 
		pnt+QPointF(
			rad*math.cos(rangle2),
			rad*math.sin(rangle2)
		), aangle, arrow_size)

def half_moment_arrow_common(painter, pnt, rad, angle, angle2, arrow_size):
	angle = -angle
	angle2 = -angle2
	pnt2 = pnt+QPointF(
			rad*math.cos(angle),
			rad*math.sin(angle)
		)
	circular_arrow2(painter, pnt, rad, angle, angle2, arrow_size)
	painter.drawLine(pnt, pnt2)

def half_moment_arrow(painter, pnt, rad, left=True, inverse = False, arrow_size=12):
	angle = -30
	arc_angle = 60
	rangle = angle / 180 * math.pi

	x = pnt.x() - rad
	y = pnt.y() - rad
	x2 = pnt.x() + rad
	y2 = pnt.y() + rad

	c30 = math.cos(deg(45))
	s30 = math.sin(deg(45))

	lu = pnt + QPointF(-c30*rad, -s30*rad)
	ld = pnt + QPointF(-c30*rad, s30*rad)
	ru = pnt + QPointF(c30*rad, -s30*rad)
	rd = pnt + QPointF(c30*rad, s30*rad)

	if     left and     inverse: 
		apnt = ld; bpnt = lu
		angle = deg(-45 + 180); angle2 = deg(45 + 180)
	
	if     left and not inverse: 
		apnt = lu; bpnt = ld
		angle = deg(45 + 180); angle2 = deg(-45 + 180)
	
	if not left and     inverse: 
		apnt = rd; bpnt = ru
		angle = deg(45); angle2 = deg(-45)

	if not left and not inverse: 
		apnt = ru; bpnt = rd
		angle = deg(-45); angle2 = deg(45)

	painter.drawLine(pnt, apnt)

	circular_arrow(painter, pnt, rad, angle, angle2, arrow_size)

	#painter.drawLine(apnt, bpnt)
	#angled_arrow_head_top(painter, bpnt, angle, arrow_size)


def radrect(pnt, rad):
	return QRect(pnt.x() - rad, pnt.y() - rad, rad*2+1, rad*2+1)

def placedtext(painter, pnt, y, size, text = "NoText", right=False):
	"""
		Текст с выносной линией.
	"""
	size2 = size
	if size2 < 18:
		size2 = 18
	
	painter.setPen(halfpen)
	if right:
		painter.drawLine(pnt, pnt + QPointF(-size2/2, -y))
	else:
		painter.drawLine(pnt, pnt + QPointF(size2/2, -y))
			
	painter.drawLine(pnt + QPointF(size2/2, -y), pnt + QPointF(-size2/2, -y))
	
	painter.setPen(pen)
	painter.drawText(pnt + QPointF(-size/2, -y-3), text)

def zadelka(painter, xl, xr, yu, yd, left_border, right_border):
	oldbrush = painter.brush()
	oldpen = painter.pen()
	brush = QBrush(Qt.BDiagPattern)
	pen = QPen(Qt.NoPen)
	painter.setBrush(brush)
	painter.setPen(pen)
	painter.drawRect(QRect(xl, yu, xr-xl, yd-yu))
	painter.setBrush(oldbrush)
	painter.setPen(oldpen)

	if left_border:
		painter.drawLine(QPointF(xl, yu), QPointF(xl, yd))

	if right_border:
		painter.drawLine(QPointF(xr, yu), QPointF(xr, yd))


def zadelka_sharnir(painter, pnt, angle, w, h, s):
	oldbrush = painter.brush()
	oldpen = painter.pen()
	brush = QBrush(Qt.BDiagPattern)
	pen = QPen(Qt.NoPen)
	painter.setBrush(brush)
	painter.setPen(pen)

	points = [
		pnt + rotate(angle, QPointF(0, w)),
		pnt + rotate(angle, QPointF(0, -w)),
		pnt + rotate(angle, QPointF(h, -w)),
		pnt + rotate(angle, QPointF(h, w))
	]

	qpoints = [QPointF(pnt.x(), pnt.y()) for pnt in points]
	polygon = QPolygonF(qpoints)
	painter.drawConvexPolygon(polygon)

	pen = QPen()
	pen.setWidth(common.getLineWidth())
	brush = QBrush(Qt.SolidPattern)
	brush.setColor(Qt.white)
	painter.setPen(pen)
	painter.setBrush(brush)
	painter.drawLine(qpoints[0], qpoints[1])

	painter.drawEllipse(radrect(pnt, s))
	
	painter.setBrush(oldbrush)
	painter.setPen(oldpen)


def zadelka_sharnir_type2(painter, pnt, angle, w, h, s):
	oldbrush = painter.brush()
	oldpen = painter.pen()
	brush = QBrush(Qt.BDiagPattern)
	pen = QPen(Qt.NoPen)
	painter.setBrush(brush)
	painter.setPen(pen)

	h2 = 30
	up = pnt + rotate(angle, QPointF(-h2, h2))
	dp = pnt + rotate(angle, QPointF(-h2, -h2))

	points = [
		pnt + rotate(angle, QPointF(-h2, w)),
		pnt + rotate(angle, QPointF(-h2, -w)),
		pnt + rotate(angle, QPointF(-h2-h, -w)),
		pnt + rotate(angle, QPointF(-h2-h, w))
	]

	qpoints = [QPointF(pnt.x(), pnt.y()) for pnt in points]
	polygon = QPolygonF(qpoints)
	painter.drawConvexPolygon(polygon)

	pen = QPen()
	pen.setWidth(common.getLineWidth())
	brush = QBrush(Qt.SolidPattern)
	brush.setColor(Qt.white)
	painter.setPen(pen)
	painter.setBrush(brush)
	painter.drawLine(qpoints[0], qpoints[1])
	painter.drawLine(pnt, up)
	painter.drawLine(pnt, dp)

	painter.drawEllipse(radrect(pnt, s))
	
	painter.setBrush(oldbrush)
	painter.setPen(oldpen)



def point_ellipse(painter, el):
	x = el.x()
	y = el.y()
	w = el.width()
	h = el.height()
	s = w/4
	brush = QBrush(Qt.white)
	painter.setBrush(brush)
	painter.drawEllipse(el)

	brush = QBrush(Qt.NoBrush)
	painter.setBrush(brush)
	painter.drawEllipse(el)

	brush = QBrush(Qt.SolidPattern)
	painter.setBrush(brush)
	painter.drawEllipse(QRect(x+w/2+0.5-s/2, y+h/2-s/2+0.5, s+0.5, s+0.5))

def crest_ellipse(painter, el):
	x = el.x()
	y = el.y()
	w = el.width()
	h = el.height()
	c = w/2 / math.sqrt(2)
	brush = QBrush(Qt.white)
	painter.setBrush(brush)
	painter.drawEllipse(el)

	brush = QBrush(Qt.NoBrush)
	painter.setBrush(brush)
	painter.drawEllipse(el)
	
	painter.drawLine(QPointF(x+w/2-c+0.5, y+h/2-c+0.5), QPointF(x+w/2+c+0.5, y+h/2+c+0.5))
	painter.drawLine(QPointF(x+w/2-c+0.5, y+h/2+c+0.5), QPointF(x+w/2+c+0.5, y+h/2-c+0.5))

	#painter.drawEllipse(QRect(x+w/2-s/2, y+h/2-s/2, s, s))

def point_circ(painter, pnt, rad):
	point_ellipse(painter, QRect(pnt-QPoint(rad/2,rad/2), pnt+QPoint(rad/2,rad/2)))

def crest_circ(painter, pnt, rad):
	crest_ellipse(painter, QRect(pnt-QPoint(rad/2,rad/2), pnt+QPoint(rad/2,rad/2)))

def kr_arrow(painter, pnt, rad, circ, inverse=False):
	"""Обозначение кручения для задачи о стержне"""
	brush = QBrush()
	painter.setBrush(brush)

	if inverse:
		point_ellipse(painter, QRect(-circ + pnt.x(), pnt.y() + rad, circ*2, circ*2))
		crest_ellipse(painter, QRect(-circ + pnt.x(), pnt.y() - rad - 2*circ, circ*2, circ*2))

	else:
		crest_ellipse(painter, QRect(-circ + pnt.x(), pnt.y() + rad, circ*2, circ*2))
		point_ellipse(painter, QRect(-circ + pnt.x(), pnt.y() - rad - 2*circ, circ*2, circ*2))

	painter.setPen(halfpen)
	painter.drawLine(pnt + QPointF(0,rad), pnt + QPointF(0,-rad))

	painter.setPen(pen)

def greek(text):
	data = [
		("\\alpha", "α"),
		("\\beta", "β"),
		("\\gamma", "γ"),
		("\\sqr", "\u00B0"),
		("\\up2", "\u00B2"),
		("\\up3", "\u00B3"),
		("\\degree", "\u00B0"),
		("\\Delta", "\u0394"),
		("\\delta", "δ"),
		("\\epsilon", "ε"),
		("\\zeta", "ζ"),
		("\\eta", "η"),
		("\\theta", "θ"),
		("\\iota", "ι"),
		("\\kappa", "κ"),
		("\\lambda", "λ"),
		("\\mu", "μ"),
		("\\nu", "ν"),
		("\\ksi", "ξ"),
		("\\omicron", "ο"),
		("\\pi", "π"),
		("\\rho", "ρ"),
		("\\sigma", "σ"),
		("\\tau", "τ"),
		("\\upsilon", "υ"),
		("\\phi", "φ"),
		("\\chi", "χ"),
		("\\psi", "ψ"),
		("\\omega", "ω"),
		("\\diam", "⌀"),
	]

	for d in data:
		text=text.replace(d[0], d[1])

	return text

#	return text.replace()
#	α        Alpha        \u03B1
#	β        Beta         \u03B2
#	γ        Gamma        \u03B3
#	δ        Delta        \u03B4
#	ε        Epsilon      \u03B5
#	ζ        Zeta         \u03B6
#	η        Eta          \u03B7
#	θ        Theta        \u03B8
#	ι        Iota         \u03B9
#	κ        Kappa        \u03BA
#	λ        Lambda       \u03BB
#	μ        Mu           \u03BC
#	ν        Nu           \u03BD
#	ξ        Xi           \u03BE
#	ο        Omicron      \u03BF
#	π        Pi           \u03C0
#	ρ        Rho          \u03C1
#	σ        Sigma        \u03C3
#	τ        Tau          \u03C4
#	υ        Upsilon      \u03C5
#	φ        Phi          \u03C6
#	χ        Chi          \u03C7
#	ψ        Psi          \u03C8
#	ω        Omega        \u03C9

def dimlines(painter, p0, p1, level):
	painter.setPen(halfpen)

	pp0 = QPointF(p0.x(), level)
	pp1 = QPointF(p1.x(), level)
	pc = QPointF((p1.x() + p0.x())/2, level)
	length = p1.x() - p0.x()
	painter.drawLine(p0, pp0)
	painter.drawLine(p1, pp1)

	left_arrow(painter, pc, length/2, 10)
	right_arrow(painter, pc, length/2, 10)

	painter.setPen(pen)

def dimlines_vertical(painter, p0, p1, level):
	painter.setPen(halfpen)

	pp0 = QPointF(level,p0.y())
	pp1 = QPointF(level,p1.y())
	pc = QPointF(level, (p1.y() + p0.y())/2)
	length = p1.y() - p0.y()
	painter.drawLine(p0, pp0)
	painter.drawLine(p1, pp1)

	up_arrow(painter, pc, length/2, 10)
	down_arrow(painter, pc, length/2, 10)

	painter.setBrush(Qt.white)
	painter.setPen(pen)

def draw_text_centered(painter, pnt, text, font):
	width = QFontMetrics(font).width(text)
	painter.setFont(font)
	
	painter.drawText(pnt + QPointF(-width/2,0), text)

def draw_vertical_dimlines_with_text(painter, upnt, dpnt, arrow_size, textpnt, text, font):
	"""подписать толщину"""

	painter.setFont(font)
	up_arrow_head(painter, upnt.x(), upnt.y() + arrow_size, arrow_size)
	down_arrow_head(painter, upnt.x(), dpnt.y() - arrow_size, arrow_size)
	
	painter.drawLine(upnt, dpnt)

	pen = painter.pen()
	painter.setBrush(Qt.white)
	painter.setPen(Qt.NoPen)

	htext = QFontMetrics(font).height()
	xwtext = QFontMetrics(font).width('x')
	
	tpnt = (dpnt+upnt)/2 + QPointF(xwtext/2,htext/2) + textpnt

	painter.drawRect(
		tpnt.x(), tpnt.y() - QFontMetrics(font).height(), 
		QFontMetrics(font).width(text), htext
	)
	painter.setPen(pen)
	painter.drawText(tpnt, text)

def draw_textline(painter, strt, textpnt, text, font):
	htext = QFontMetrics(font).height()
	wtext = QFontMetrics(font).width(text)

	apnt = textpnt + QPointF(0, htext/8)
	bpnt = textpnt + QPointF(wtext, htext/8)

	painter.drawLine(apnt, bpnt)
	painter.drawLine(strt, apnt)

def draw_dimlines(painter, apnt, bpnt, offset, textoff, text, arrow_size, splashed=False, textline_from=None):
	"""Нарисовать размерные линии с текстом"""

	aoff = apnt + offset
	boff = bpnt + offset
	coff = aoff + (boff - aoff) / 2

	diff = boff - aoff
	angle = math.atan2(-diff.y(), diff.x())

	aang = angle if splashed else angle + math.pi
	bang = angle + math.pi if splashed else angle

	arrow_head(painter, aoff, aang, arrow_size)
	arrow_head(painter, boff, bang, arrow_size)
	painter.drawLine(aoff, boff)
	painter.drawLine(aoff, boff)
	painter.drawLine(apnt, aoff)
	painter.drawLine(bpnt, boff)

	font = painter.font()
	htext = QFontMetrics(font).height()
	wtext = QFontMetrics(font).width(text)
	textpnt = coff + textoff + QPointF(-wtext/2, htext/4)
	painter.drawText(textpnt, text)

	if textline_from == "bpnt":
		draw_textline(painter, bpnt, textpnt, text, font=font)

def draw_vertical_splashed_dimlines_with_text(painter, upnt, dpnt, arrow_size, textpnt, text, font):
	"""подписать толщину"""

	painter.setFont(font)
	down_arrow_head(painter, upnt.x(), upnt.y() - arrow_size, arrow_size)
	up_arrow_head(painter, upnt.x(), dpnt.y() + arrow_size, arrow_size)
	painter.drawLine(upnt+QPointF(0,-arrow_size*1.5), dpnt+QPointF(0,+arrow_size*1.5))

	htext = QFontMetrics(font).height()
	xwtext = QFontMetrics(font).width('x')
	painter.drawText(dpnt+QPointF(xwtext/2,htext), text)

def draw_distribload(painter, apnt, bpnt, step, arrow_size, alen, pen=None):
	if pen:
		painter.setPen(pen)

	dist = math.sqrt((apnt.x()-bpnt.x())**2 + (apnt.y()-bpnt.y())**2)
	count = int(dist / step)
	count = count - count % 2 + 1

	diff = bpnt - apnt
	norm = QPointF(-diff.y(), diff.x()) / math.sqrt(diff.y()**2 + diff.x()**2)
	norm = norm * alen

	painter.drawLine(apnt+norm, bpnt+norm)

	for i in range(count):
		koeff = i / (count - 1)
		spnt = koeff * bpnt + (1-koeff) * apnt
		fpnt = spnt + norm
		common_arrow(painter, fpnt, spnt, arrow_size)

def draw_sharnir_terminator_rect(painter, pnt, angle, termx, termy, pen, halfpen):
	angle = angle + deg(90)
	
	pnts = [
		pnt + QPointF(math.cos(angle) * termx, math.sin(angle) * termx), 
		pnt + QPointF(- math.cos(angle) * termx, - math.sin(angle) * termx),
		pnt + QPointF(- math.cos(angle) * termx, - math.sin(angle) * termx) + QPointF(math.sin(angle)*termy, -math.cos(angle)*termy),
		pnt + QPointF(math.cos(angle) * termx, math.sin(angle) * termx) + QPointF(math.sin(angle)*termy, -math.cos(angle)*termy),
	]

	polygon = QPolygonF(pnts)

	painter.setPen(Qt.NoPen)
	painter.setBrush(Qt.white)
	painter.drawPolygon(polygon)

	painter.setPen(pen)
	painter.drawLine(pnts[0], pnts[1])

	painter.setPen(Qt.NoPen)
	painter.setBrush(Qt.BDiagPattern)
	painter.drawPolygon(polygon)


def draw_sharnir_1dim(painter, pnt, angle, rad, termrad, termx, termy, pen, halfpen, doublepen=None):
	painter.setPen(halfpen)

	circrect = QRect(pnt.x()-rad, pnt.y()-rad, 2*rad , 2*rad)
	bpnt = QPointF(
		termrad*math.cos(angle), 
		termrad*math.sin(angle)) + pnt

	bpnt_draw = QPointF(
		(termrad-rad)*math.cos(angle), 
		(termrad-rad)*math.sin(angle)) + pnt

	painter.setBrush(Qt.white)
	if doublepen:
		painter.setPen(doublepen)
	else:
		painter.setPen(pen)
	painter.drawLine(pnt, bpnt)

	painter.setPen(pen)
	circrect2 = radrect(bpnt_draw, rad)
	#painter.drawLine(pnt, bpnt)

	draw_sharnir_terminator_rect(painter, bpnt, angle, termx, termy, pen, halfpen)

	painter.setPen(pen)
	painter.setBrush(Qt.white)
	painter.drawEllipse(circrect)
	painter.drawEllipse(circrect2)

def draw_zadelka(painter, pnt, angle, termx, termy, pen, halfpen, doublepen=None):
	draw_sharnir_terminator_rect(painter, pnt, angle, termx, termy, pen, halfpen)

def draw_sharnir_2dim(painter, pnt, angle, rad, termrad, termx, termy, pen, halfpen):
	painter.setPen(pen)

	circrect = radrect(pnt, rad)
	bpnt = QPointF(termrad*math.cos(angle), termrad*math.sin(angle)) + pnt
	bbpnt = QPointF((termrad-rad/3*2)*math.cos(angle), (termrad-rad/3*2)*math.sin(angle)) + pnt

	draw_sharnir_terminator_rect(painter, bpnt, angle, termx, termy, pen, halfpen)

	angle = angle + deg(90)
	b1pnt = bpnt + QPointF(math.cos(angle) * termx*2/3, math.sin(angle) * termx*2/3) 
	b2pnt = bpnt + QPointF(- math.cos(angle) * termx*2/3, - math.sin(angle) * termx*2/3)
	bb1pnt = bbpnt + QPointF(math.cos(angle) * termx*2/3, math.sin(angle) * termx*2/3) 
	bb2pnt = bbpnt + QPointF(- math.cos(angle) * termx*2/3, - math.sin(angle) * termx*2/3)

	painter.setPen(pen)
	painter.drawLine(b1pnt, b2pnt)
	painter.drawLine(pnt, b2pnt)
	painter.drawLine(pnt, b1pnt)

	painter.setBrush(Qt.white)
	painter.drawEllipse(circrect)

	#painter.drawEllipse(radrect(bbpnt, rad))

def draw_kamera(painter, lu, rd, t):
	"""Рисует камеру с измененным давлением"""
	pen = painter.pen()
	painter.setBrush(Qt.BDiagPattern)
	painter.setPen(Qt.NoPen)

	painter.drawRect(QRect(lu, rd))

	painter.setPen(pen)
	painter.setBrush(Qt.white)
	painter.drawRect(QRect(lu + QPointF(t,t), rd+QPointF(-t,-t)))

	painter.setBrush(Qt.white)
	painter.setPen(pen)

	xx=rd - lu
	xx=QPointF((xx * 2 / 3).x(), 30)

	painter.drawText(lu + xx, "p")

def draw_inkamera(painter, lu, rd, t):
	"""Рисует камеру с измененным давлением"""
	pen = painter.pen()
	painter.setBrush(Qt.BDiagPattern)
	#painter.setPen(Qt.NoPen)

	painter.drawRect(QRect(lu, rd))

	painter.setPen(pen)
	painter.setBrush(Qt.white)
	painter.drawRect(QRect(lu + QPointF(t,t), rd+QPointF(-t,-t)))

	painter.setBrush(Qt.white)
	painter.setPen(pen)

	xx=rd - lu
	xx=QPointF((xx * 2 / 3).x(), 40)

	painter.drawText(lu + xx, "p")

def razrez(painter, a, b):
	c = (a + b) / 2
	ac = (c + a) / 2 + QPointF(6, 0)
	bc = (c + b) / 2 + QPointF(-6, 0)

	painter.drawLine(a,ac)
	painter.drawLine(ac,c)
	painter.drawLine(c,bc)
	painter.drawLine(bc,b)

def draw_rectangle(painter,x,y,xl,yl,zleft=False,zright=False):
	pen = painter.pen()
	painter.setPen(Qt.NoPen)
	painter.drawRect(x,y,xl,yl)

	painter.setPen(pen)	
	
	painter.drawLine(QPointF(x,y), QPointF(x+xl, y))
	painter.drawLine(QPointF(x,y+yl), QPointF(x+xl, y+yl))
	
	if zleft:
		razrez(painter,QPointF(x,y), QPointF(x, y+yl))
	else:
		painter.drawLine(QPointF(x,y), QPointF(x, y+yl))

	if zright:
		razrez(painter,QPointF(x+xl,y), QPointF(x+xl, y+yl))
	else:
		painter.drawLine(QPointF(x+xl,y), QPointF(x+xl, y+yl))

def raspred_torsion(painter, apnt, bpnt, alen, step, rad, tp):
	if pen:
		painter.setPen(pen)

	dist = math.sqrt((apnt.x()-bpnt.x())**2 + (apnt.y()-bpnt.y())**2)
	count = int(dist / step)
	count = count - count % 2 + 1

	diff = bpnt - apnt
	norm = QPointF(-diff.y(), diff.x()) / math.sqrt(diff.y()**2 + diff.x()**2)
	norm = norm * alen

	#painter.drawLine(apnt+norm, bpnt+norm)

	for i in range(count):
		koeff = i / (count - 1)
		spnt = koeff * bpnt + (1-koeff) * apnt
		fpnt = spnt + norm

		spnt = QPoint(spnt.x(), spnt.y())
		fpnt = QPoint(fpnt.x(), fpnt.y())
		
		painter.setPen(halfpen)
		painter.drawLine(spnt, fpnt)

		painter.setPen(pen)
		if tp:
			point_circ(painter, fpnt, rad)

		else:
			crest_circ(painter, fpnt, rad)
		#common_arrow(painter, fpnt, spnt, arrow_size)

def raspred_force(painter, apnt, bpnt, step, tp):
	if pen:
		painter.setPen(pen)

	dist = math.sqrt((apnt.x()-bpnt.x())**2 + (apnt.y()-bpnt.y())**2)
	count = int(dist / step)
	count = count - count % 2 + 1

	diff = bpnt - apnt
	#norm = QPointF(-diff.y(), diff.x()) / math.sqrt(diff.y()**2 + diff.x()**2)
	#norm = norm * alen

	#painter.drawLine(apnt+norm, bpnt+norm)

	pnts = []
	for i in range(count):
		koeff = i / (count - 1)
		spnt = koeff * bpnt + (1-koeff) * apnt
		spnt = QPointF(spnt.x()+0.5, spnt.y()+0.5)
		pnts.append(spnt)

	painter.setPen(pen)
	for i in range(len(pnts) - 1):
		if tp:
			right_arrow(painter, pnts[i], step, 12)
		else:
			left_arrow(painter, pnts[i+1], step, 12)
		
def raspred_force_vertical(painter, apnt, bpnt, step, offset, dim, arrow_size):
	dist = math.sqrt((apnt.x()-bpnt.x())**2 + (apnt.y()-bpnt.y())**2)
	count = int(dist / step)
	count = count - count % 2 + 1
	diff = bpnt - apnt

	pnts = []
	for i in range(count):
		koeff = i / (count - 1)
		spnt = koeff * bpnt + (1-koeff) * apnt
		spnt = QPointF(spnt.x()+0.5, spnt.y()+0.5)
		pnts.append(spnt)

	painter.setPen(halfpen)
	painter.drawLine(apnt, bpnt)
	painter.drawLine(apnt+offset, bpnt+offset)
	for p in pnts:
		if dim:
			common_arrow(painter, p, p+offset, arrow_size)
		else:
			common_arrow(painter, p+offset, p, arrow_size)
		