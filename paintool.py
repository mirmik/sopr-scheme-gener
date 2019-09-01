from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import common

def deg(arg):
	return math.pi * arg / 180

def deg2rad(arg):
	return arg * 180 / math.pi

def rotate(angle, pnt):
	return QPoint(pnt.x() * math.cos(angle) - pnt.y() * math.sin(angle), pnt.y() * math.cos(angle) + pnt.x() * math.sin(angle))

#def leftArrow(self, painter, basepoint):
#	arrow_size = self.shemetype.datasettings.arrow_size
#	arrow_head_size = self.shemetype.datasettings.arrow_head_size		
#
#	painter.drawLine(basepoint, QPoint(basepoint.x() - arrow_size, basepoint.y()))
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
#	painter.drawLine(basepoint, QPoint(basepoint.x() + arrow_size, basepoint.y()))
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
		(x, 		y),
		(x - s, 	y+s/3),
		(x - s, 	y-s/3)
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
	painter.drawLine(pnt, QPoint(pnt.x()-length, pnt.y()))
	left_arrow_head_top(painter, pnt.x()-length, pnt.y(), headsize)

def right_arrow(painter, pnt, length, headsize):
	painter.drawLine(pnt, QPoint(pnt.x()+length, pnt.y()))
	right_arrow_head_top(painter, pnt.x()+length, pnt.y(), headsize)

def angled_arrow_head_top(painter, pnt, angle, headsize):
	paint_arrow(painter, angled_arrow_points_top(pnt.x(), pnt.y(), angle, headsize))

def common_arrow(painter, spnt, fpnt, arrow_size):
	diff = fpnt - spnt
	angle = math.atan2(-diff.y(), diff.x())

	angled_arrow_head_top(painter, fpnt, angle, arrow_size)
	painter.drawLine(spnt, fpnt)

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
			(rect.center()+QPoint(rrr*math.cos(rangle),-rrr*math.sin(rangle))), 
			(rect.center()+QPoint(-rrr*math.cos(rangle),+rrr*math.sin(rangle))))
	
		painter.drawArc(rect, angle*16, arc_angle*16)
		painter.drawArc(rect, angle*16 + 180*16, arc_angle*16)
		
		angled_arrow_head_top(painter, 
			rect.center()+QPoint(rrr*math.cos(rangle+deg(arc_angle)),-rrr*math.sin(rangle+deg(arc_angle))), rangle+deg(130), head_size)
		angled_arrow_head_top(painter, 
			rect.center()+QPoint(-rrr*math.cos(rangle+deg(arc_angle))+1,-rrr*math.sin(-rangle-deg(arc_angle))), rangle+deg(130+180), head_size)
	
	else:
		painter.drawLine(
			(rect.center()+QPoint(rrr*math.cos(rangle),rrr*math.sin(rangle))), 
			(rect.center()+QPoint(-rrr*math.cos(rangle),-rrr*math.sin(rangle))))
	
		painter.drawArc(rect, -angle*16, -arc_angle*16)
		painter.drawArc(rect, -angle*16 - 180*16, -arc_angle*16)
		
		angled_arrow_head_top(painter, 
			rect.center()+QPoint(rrr*math.cos(-rangle-deg(arc_angle)),-rrr*math.sin(-rangle-deg(arc_angle))), -rangle-deg(130), head_size)
		angled_arrow_head_top(painter, 
			rect.center()+QPoint(-rrr*math.cos(-rangle-deg(arc_angle))+1,-rrr*math.sin(+rangle+deg(arc_angle))), -rangle-deg(130+180), head_size)


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
			(pnt+QPoint(rad*math.cos(rangle),-rad*math.sin(rangle))), 
			(pnt+QPoint(-rad*math.cos(rangle),+rad*math.sin(rangle))))

		painter.drawArc(QRect(x, y, x2-x, y2-y), angle*16, arc_angle*16)
		painter.drawArc(QRect(x, y, x2-x, y2-y), angle*16 + 180*16, arc_angle*16)

		angled_arrow_head_top(painter, 
			pnt+QPoint(
				rad*math.cos(rangle+deg(arc_angle)),
				-rad*math.sin(rangle+deg(arc_angle))
			), rangle+deg(130), arrow_size)
		
		angled_arrow_head_top(painter, 
			pnt+QPoint(
				-rad*math.cos(rangle+deg(arc_angle)),
				-rad*math.sin(-rangle-deg(arc_angle))
			), rangle+deg(130+180), arrow_size)
	

	else:
		painter.drawLine(
			(pnt+QPoint(rad*math.cos(rangle),+rad*math.sin(rangle))), 
			(pnt+QPoint(-rad*math.cos(rangle),-rad*math.sin(rangle))))

		
		painter.drawArc(QRect(x, y, x2-x, y2-y), -angle*16, -arc_angle*16)
		painter.drawArc(QRect(x, y, x2-x, y2-y), -angle*16 - 180*16, -arc_angle*16)
		
		angled_arrow_head_top(painter, 
			pnt+QPoint(
				rad*math.cos(rangle+deg(arc_angle)),
				-rad*math.sin(rangle+deg(arc_angle))
			), rangle+deg(130), arrow_size)
		
		angled_arrow_head_top(painter, 
			pnt+QPoint(
				-rad*math.cos(rangle+deg(arc_angle)),
				-rad*math.sin(-rangle-deg(arc_angle))
			), rangle+deg(130+180), arrow_size)

def circular_arrow(painter, pnt, rad, angle, angle2, arrow_size):
	x = pnt.x() - rad
	y = pnt.y() - rad
	x2 = pnt.x() + rad
	y2 = pnt.y() + rad

	rangle2= angle2
	angle = deg2rad(angle)
	angle2 = deg2rad(angle2)

	painter.drawArc(QRect(x, y, x2-x, y2-y), -angle*16, -(angle2 - angle)*16)

	angled_arrow_head_top(painter, 
		pnt+QPoint(
			rad*math.cos(rangle2),
			rad*math.sin(rangle2)
		), rangle2 + deg(180), arrow_size)


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

	lu = pnt + QPoint(-c30*rad, -s30*rad)
	ld = pnt + QPoint(-c30*rad, s30*rad)
	ru = pnt + QPoint(c30*rad, -s30*rad)
	rd = pnt + QPoint(c30*rad, s30*rad)

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
	
	if right:
		painter.drawLine(pnt, pnt + QPoint(-size2/2, -y))
	else:
		painter.drawLine(pnt, pnt + QPoint(size2/2, -y))
			
	painter.drawLine(pnt + QPoint(size2/2, -y), pnt + QPoint(-size2/2, -y))
	painter.drawText(pnt + QPoint(-size/2, -y-3), text)

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
		painter.drawLine(QPoint(xl, yu), QPoint(xl, yd))

	if right_border:
		painter.drawLine(QPoint(xr, yu), QPoint(xr, yd))


def zadelka_sharnir(painter, pnt, angle, w, h, s):
	oldbrush = painter.brush()
	oldpen = painter.pen()
	brush = QBrush(Qt.BDiagPattern)
	pen = QPen(Qt.NoPen)
	painter.setBrush(brush)
	painter.setPen(pen)

	points = [
		pnt + rotate(angle, QPoint(0, w)),
		pnt + rotate(angle, QPoint(0, -w)),
		pnt + rotate(angle, QPoint(h, -w)),
		pnt + rotate(angle, QPoint(h, w))
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
	up = pnt + rotate(angle, QPoint(-h2, h2))
	dp = pnt + rotate(angle, QPoint(-h2, -h2))

	points = [
		pnt + rotate(angle, QPoint(-h2, w)),
		pnt + rotate(angle, QPoint(-h2, -w)),
		pnt + rotate(angle, QPoint(-h2-h, -w)),
		pnt + rotate(angle, QPoint(-h2-h, w))
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
	brush = QBrush(Qt.NoBrush)
	painter.setBrush(brush)
	painter.drawEllipse(el)
	brush = QBrush(Qt.SolidPattern)
	painter.setBrush(brush)
	painter.drawEllipse(QRect(x+w/2-s/2, y+h/2-s/2, s, s))

def crest_ellipse(painter, el):
	x = el.x()
	y = el.y()
	w = el.width()
	h = el.height()
	c = w/2 / math.sqrt(2)
	brush = QBrush(Qt.NoBrush)
	painter.setBrush(brush)
	painter.drawEllipse(el)
	
	painter.drawLine(QPoint(x+w/2-c, y+h/2-c), QPoint(x+w/2+c, y+h/2+c))
	painter.drawLine(QPoint(x+w/2-c, y+h/2+c), QPoint(x+w/2+c, y+h/2-c))

	#painter.drawEllipse(QRect(x+w/2-s/2, y+h/2-s/2, s, s))

def kr_arrow(painter, pnt, rad, circ, inverse=False):
	brush = QBrush()
	painter.setBrush(brush)

	painter.drawLine(pnt + QPoint(0,rad), pnt + QPoint(0,-rad))

	if inverse:
		point_ellipse(painter, QRect(-circ + pnt.x(), pnt.y() + rad, circ*2, circ*2))
		crest_ellipse(painter, QRect(-circ + pnt.x(), pnt.y() - rad - 2*circ, circ*2, circ*2))

	else:
		crest_ellipse(painter, QRect(-circ + pnt.x(), pnt.y() + rad, circ*2, circ*2))
		point_ellipse(painter, QRect(-circ + pnt.x(), pnt.y() - rad - 2*circ, circ*2, circ*2))


def greek(text):
	data = [
		("\\alpha", "α"),
		("\\beta", "β"),
		("\\gamma", "γ"),
		#("\\delta", "\u0394"),
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
	pp0 = QPoint(p0.x(), level)
	pp1 = QPoint(p1.x(), level)
	pc = QPoint((p1.x() + p0.x())/2, level)
	length = p1.x() - p0.x()
	painter.drawLine(p0, pp0)
	painter.drawLine(p1, pp1)

	left_arrow(painter, pc, length/2, 10)
	right_arrow(painter, pc, length/2, 10)

def draw_text_centered(painter, pnt, text, font):
	width = QFontMetrics(font).width(text)
	painter.setFont(font)
	
	painter.drawText(pnt + QPoint(-width/2,0), text)

def draw_vertical_splashed_dimlines_with_text(painter, upnt, dpnt, arrow_size, textpnt, text, font):
	"""подписать толщину"""

	painter.setFont(font)
	down_arrow_head(painter, upnt.x(), upnt.y() - arrow_size, arrow_size)
	up_arrow_head(painter, upnt.x(), dpnt.y() + arrow_size, arrow_size)
	painter.drawLine(upnt+QPoint(0,-arrow_size*1.5), dpnt+QPoint(0,+arrow_size*1.5))

	htext = QFontMetrics(font).height()
	xwtext = QFontMetrics(font).width('x')
	painter.drawText(dpnt+QPoint(xwtext/2,htext), text)

def draw_distribload(painter, apnt, bpnt, step, arrow_size, alen):
	dist = math.sqrt((apnt.x()-bpnt.x())**2 + (apnt.y()-bpnt.y())**2)
	count = int(dist / step)
	count = count - count % 2 + 1

	diff = bpnt - apnt
	norm = QPoint(-diff.y(), diff.x()) / math.sqrt(diff.y()**2 + diff.x()**2)
	norm = norm * alen

	painter.drawLine(apnt+norm, bpnt+norm)

	for i in range(count):
		koeff = i / (count - 1)
		spnt = koeff * bpnt + (1-koeff) * apnt
		fpnt = spnt + norm
		common_arrow(painter, fpnt, spnt, arrow_size)
