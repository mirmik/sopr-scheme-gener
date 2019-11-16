from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import paintool
from paintool import deg

storoni = [
	"слева", "справа", "сверху", "снизу", 
	"слева сверху", "справа сверху",
	"слева снизу", "справа снизу",
	]

men_arr = ["нет", "слева +", "слева -", "справа +", "справа -", "сверху +", "сверху -", "снизу +", "снизу -"]
fen_arr = ["нет", "слева от", "слева к", "справа от", "справа к", "сверху от", "сверху к", "снизу от", "снизу к"]
sharn_arr = ["нет", 
"слева шарн1", "справа шарн1", "сверху шарн1", "снизу шарн1",
"слева шарн2", "справа шарн2", "сверху шарн2", "снизу шарн2",
"заделка"]


storoni_angles = {
	"слева":deg(180), 
	"справа":deg(0), 
	"сверху":deg(90), 
	"снизу":deg(270), 
	"слева сверху":deg(135), 
	"справа сверху":deg(45),
	"слева снизу":deg(225), 
	"справа снизу":deg(315),
}

torq_delta = paintool.deg(30)

force_angle = {
	"слева от": deg(180), 
	"слева к": deg(180), 
	"справа от": deg(0), 
	"справа к": deg(0), 
	"сверху от": deg(90), 
	"сверху к": deg(90), 
	"снизу от": deg(270), 
	"снизу к": deg(270)
}

torq_angle = {
	"слева +": deg(180) - torq_delta, 
	"слева -": deg(180) + torq_delta, 
	"справа +": deg(0) - torq_delta, 
	"справа -": deg(0) + torq_delta, 
	"сверху +": deg(90) - torq_delta, 
	"сверху -": deg(90) + torq_delta, 
	"снизу +": deg(270) - torq_delta, 
	"снизу -": deg(270) + torq_delta
}

torq_angle2 = {
	"слева +": deg(180) + torq_delta, 
	"слева -": deg(180) - torq_delta, 
	"справа +": deg(0) + torq_delta, 
	"справа -": deg(0) - torq_delta, 
	"сверху +": deg(90) + torq_delta, 
	"сверху -": deg(90) - torq_delta, 
	"снизу +": deg(270) + torq_delta, 
	"снизу -": deg(270) - torq_delta
}

def torq_textpolicy(type, font, txt):
	if type == "слева +": return ("left", QPointF(-10-QFontMetrics(font).width(txt),QFontMetrics(font).height()/4))
	if type == "слева -": return ("left", QPointF(-10-QFontMetrics(font).width(txt),QFontMetrics(font).height()/4))
	if type == "справа +":return ("right", QPointF(15,QFontMetrics(font).height()/4))
	if type == "справа -":return ("right", QPointF(15,QFontMetrics(font).height()/4))
	if type == "сверху +":return ("center", QPointF(0,-10))
	if type == "сверху -":return ("center", QPointF(0,-10))
	if type == "снизу +": return ("center", QPointF(0,QFontMetrics(font).height()))
	if type == "снизу -": return ("center", QPointF(0,QFontMetrics(font).height()))

def force_textpolicy(type, font, txt):
	if type == "слева к": return ("center", QPointF(0,QFontMetrics(font).height()-2))
	if type == "слева от": return ("center", QPointF(0,QFontMetrics(font).height()-2))
	if type == "справа к":return ("center", QPointF(0,QFontMetrics(font).height()-2))
	if type == "справа от":return ("center", QPointF(0,QFontMetrics(font).height()-2))
	if type == "сверху к":return ("left", QPointF(-QFontMetrics(font).width(txt)-7,QFontMetrics(font).height()/4))
	if type == "сверху от":return ("left", QPointF(-QFontMetrics(font).width(txt)-7,QFontMetrics(font).height()/4))
	if type == "снизу к": return ("left", QPointF(-QFontMetrics(font).width(txt)-7,QFontMetrics(font).height()/4))
	if type == "снизу от": return ("left", QPointF(-QFontMetrics(font).width(txt)-7,QFontMetrics(font).height()/4))

def force_textpolicy_alt(type, font, txt):
	if type == "слева к": return ("center", QPointF(0,-7))
	if type == "слева от": return ("center", QPointF(0,-7))
	if type == "справа к":return ("center", QPointF(0,-7))
	if type == "справа от":return ("center", QPointF(0,-7))
	if type == "сверху к":return ("left", QPointF(7,QFontMetrics(font).height()/4))
	if type == "сверху от":return ("left", QPointF(7,QFontMetrics(font).height()/4))
	if type == "снизу к": return ("left", QPointF(7,QFontMetrics(font).height()/4))
	if type == "снизу от": return ("left", QPointF(7,QFontMetrics(font).height()/4))

def draw_element_torque(self, pnt, type, rad, arrow_size, txt):
	painter = self.painter
	
	angle = None
	angle2 = None

	if type == "нет":
		return

	else:
		angle = torq_angle[type]
		angle2 = torq_angle2[type]

	paintool.half_moment_arrow_common(painter, pnt, rad, angle, angle2, arrow_size)

	txt = paintool.greek(txt)
	textpnt = pnt + QPointF(rad * math.cos(angle2), - rad * math.sin(angle2))
	textpolicy = torq_textpolicy(type, self.font, txt)
	if textpolicy[0] == "center":
		paintool.draw_text_centered(painter, textpnt + textpolicy[1], txt, self.font)

	elif textpolicy[0] == "left":
		painter.setFont(self.font)
		painter.drawText(textpnt + textpolicy[1], txt)

	elif textpolicy[0] == "right":
		paintool.draw_text_centered(painter, textpnt + textpolicy[1], txt, self.font)

def draw_element_force(self, pnt, type, rad, arrow_size, txt, alt):
	painter = self.painter
	
	angle = None

	if type == "нет":
		return

	else:
		angle = force_angle[type]
		p1 = pnt
		p2 = pnt + QPointF(rad * math.cos(angle), - rad * math.sin(angle))

		if "от" not in type:
			p1, p2 = p2, p1
	
	paintool.common_arrow(painter, p1, p2, arrow_size)

	txt = paintool.greek(txt)
	textpnt = p2
	
	if not alt:
		textpolicy = force_textpolicy(type, self.font, txt)
	else:
		textpolicy = force_textpolicy_alt(type, self.font, txt)
	
	if textpolicy[0] == "center":
		paintool.draw_text_centered(painter, textpnt + textpolicy[1], txt, self.font)

	elif textpolicy[0] == "left":
		painter.setFont(self.font)
		painter.drawText(textpnt + textpolicy[1], txt)

	elif textpolicy[0] == "right":
		paintool.draw_text_centered(painter, textpnt + textpolicy[1], txt, self.font)

def draw_element_sharn(self, pnt, type, inangle):
	painter = self.painter
	
	angle=None
	if "слева" in type: angle = deg(180)
	elif "справа" in type: angle = deg(0)
	elif "сверху" in type: angle = deg(270)
	elif "снизу" in type: angle = deg(90)

	if "шарн1" in type:
		paintool.draw_sharnir_1dim(
			painter=painter, 
			pnt=pnt, 
			angle=angle, 
			rad=4, 
			termrad=15, 
			termx=15, 
			termy=10, 
			pen=self.default_pen,
			halfpen=self.halfpen)

	if "шарн2" in type:
		paintool.draw_sharnir_2dim(
			painter=painter, 
			pnt=pnt, 
			angle=angle, 
			rad=4, 
			termrad=15, 
			termx=15, 
			termy=10, 
			pen=self.default_pen,
			halfpen=self.halfpen)

	if "заделка" in type:
		paintool.draw_zadelka(painter, pnt, inangle, 15, 10, self.pen, self.halfpen, self.doublepen)

	return

def draw_text_by_points(self, strt, fini, txt, alttxt, off=10):
	if strt == fini:
		return
	painter = self.painter
	diff = (fini.x() - strt.x(), fini.y() - strt.y())
	
	length = math.sqrt(diff[0]**2 + diff[1]**2)
	udiff = (diff[0] / length, diff[1] / length)
	if alttxt:
		udiff = (-udiff[0], -udiff[1])
	angle = math.atan2(udiff[1], udiff[0])
	unorm = (-udiff[1], udiff[0])
	
	center = QPointF((strt.x() + fini.x())/2, (strt.y() + fini.y())/2 + QFontMetrics(self.font).height() / 4)
	center = center + QPointF(unorm[0] * (off+QFontMetrics(self.font).width(txt)/2), unorm[1]*off)

	#print("HERE")
	paintool.draw_text_centered(painter, center, txt, self.font)
	
def draw_element_distribload(self, type, 
					apnt, bpnt, step, 
					arrow_size, alen, txt):
	painter = self.painter

	if not type in ["+", "-"]:
		return

	draw_text_by_points(self, apnt, bpnt, paintool.greek(txt), type=="-", off=10 + alen)

	if type == "+":
		paintool.draw_distribload(painter, pen=self.halfpen, 
			apnt=apnt, 
			bpnt=bpnt, 
			step=step, 
			arrow_size=arrow_size, 
			alen=alen)

	elif type == "-":
		paintool.draw_distribload(painter, pen=self.halfpen, 
			apnt=bpnt, 
			bpnt=apnt, 
			step=step, 
			arrow_size=arrow_size, 
			alen=alen)

def draw_element_label(self, type, pnt, txt):
	center = pnt + QPointF(0, QFontMetrics(self.font).height() / 4)
	angle = storoni_angles[type]
	rad = 17
	center = center + QPointF(math.cos(angle)*rad, -math.sin(angle)*rad)

	paintool.draw_text_centered(self.painter, center, txt, self.font)