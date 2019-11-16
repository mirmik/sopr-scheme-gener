from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import paintool

section_variant=[
	"Круг",  
	"Толстая труба",
	"Тонкая труба",
	"Прямоугольник",
	"Квадрат повёрнутый",
	"Треугольник",
	"Квадрат - окружность",
]

def draw_section(wdg, section_type, right, hcenter,
	arg0, arg1, arg2, txt0, txt1, txt2, arrow_size
):
	self = wdg
	painter = self.painter
	painter.setFont(self.font)
	
	if section_type == "Круг":
		center = QPoint(right - 10 -20 - arg0/2, hcenter)
		section_width = arg0 + 100
		dimlines_off = arg0 + 30
		painter.setPen(self.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		painter.drawEllipse(
			QRect(center - QPoint(arg0,arg0), center + QPoint(arg0,arg0)))
		painter.setPen(self.halfpen)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center-QPoint(arg0, 0),
			bpnt = center+QPoint(arg0, 0),
			offset = QPoint(0,dimlines_off),
			textoff = QPoint(0, -10),
			text = txt0,
			arrow_size = arrow_size / 3 * 2
		)
		painter.setPen(self.axpen)
		llen = arg0 + 10
		painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
		painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	elif section_type == "Тонкая труба":
		center = QPoint(right - 20 - 10 - arg0/2, hcenter)
		section_width = arg0 + 120
		dimlines_off = arg0 + 20
		painter.setPen(self.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		painter.drawEllipse(
			QRect(center - QPoint(arg0,arg0), center + QPoint(arg0,arg0)))
		painter.setBrush(QBrush(Qt.white))
		painter.drawEllipse(
			QRect(center - QPoint(arg1,arg1), center + QPoint(arg1,arg1)))
		painter.setBrush(QBrush(Qt.NoBrush))
		painter.setPen(self.axpen)
		painter.drawEllipse(
			QRect(center - QPoint((arg1+arg0)/2,(arg0+arg1)/2), center + QPoint((arg1+arg0)/2,(arg0+arg1)/2)))
		painter.setPen(self.halfpen)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center-QPoint(0,(arg1+arg0)/2),
			bpnt = center+QPoint(0,(arg1+arg0)/2),
			offset = QPoint(-dimlines_off,0),
			textoff = QPoint(-10, 0) - QPoint(QFontMetrics(self.font).width(txt0)/2, 0),
			text = txt0,
			arrow_size = arrow_size / 3 * 2
		)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
			bpnt = center+QPoint(+ math.cos(math.pi/4) * arg0, + math.sin(math.pi/4) * arg0),
			offset = QPoint(0,0),
			textoff = QPoint(+ math.cos(math.pi/4) * (arg0-arg1) + 15, + math.sin(math.pi/4) * (arg0-arg1)),
			text = txt1,
			arrow_size = arrow_size / 3 * 2,
			splashed=True,
			textline_from = "bpnt"
		)
		painter.setPen(self.axpen)
		llen = arg0 + 10
		painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
		painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	elif section_type == "Толстая труба":
		center = QPoint(right - 20 - 10 - arg0/2, hcenter)
		section_width = arg0 + 120
		dimlines_off = arg0 + 20
		painter.setPen(self.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		painter.drawEllipse(
			QRect(center - QPoint(arg0,arg0), center + QPoint(arg0,arg0)))
		painter.setBrush(QBrush(Qt.white))
		painter.drawEllipse(
			QRect(center - QPoint(arg1,arg1), center + QPoint(arg1,arg1)))
		painter.setPen(self.halfpen)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center-QPoint(0,arg0),
			bpnt = center+QPoint(0,arg0),
			offset = QPoint(-dimlines_off,0),
			textoff = QPoint(-10, 0) - QPoint(QFontMetrics(self.font).width(txt0)/2, 0),
			text = txt0,
			arrow_size = arrow_size / 3 * 2
		)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
			bpnt = center+QPoint(- math.cos(math.pi/4) * arg1, - math.sin(math.pi/4) * arg1),
			offset = QPoint(0,0),
			textoff = QPoint(10,-10),
			text = txt1,
			arrow_size = arrow_size / 3 * 2,
		)
		
		painter.setPen(self.axpen)
		llen = arg0 + 10
		painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
		painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	elif section_type == "Квадрат - окружность":
		center = QPoint(right - 20 - 10 - arg0/2, hcenter)
		section_width = arg0 + 120
		dimlines_off = arg0 + 20
		painter.setPen(self.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		painter.drawRect(
			QRect(center - QPoint(arg0,arg0), center + QPoint(arg0,arg0)))
		painter.setBrush(QBrush(Qt.white))
		painter.drawEllipse(
			QRect(center - QPoint(arg1,arg1), center + QPoint(arg1,arg1)))
		painter.setPen(self.halfpen)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPoint(-arg0,arg0),
			bpnt = center+QPoint(-arg0,-arg0),
			offset = QPoint(-20,0),
			textoff = QPoint(-10, 0),
			text = txt0,
			arrow_size = arrow_size / 3 * 2
		)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPoint(arg0,arg0),
			bpnt = center+QPoint(-arg0,arg0),
			offset = QPoint(0,25),
			textoff = QPoint(0, -6),
			text = txt1,
			arrow_size = arrow_size / 3 * 2
		)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
			bpnt = center+QPoint(- math.cos(math.pi/4) * arg1, - math.sin(math.pi/4) * arg1),
			offset = QPoint(0,0),
			textoff = QPoint(8,-8),
			text = txt2,
			arrow_size = arrow_size / 3 * 2
		)
		painter.setPen(self.axpen)
		llen = arg0 + 10
		painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
		painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	elif section_type == "Прямоугольник":
		center = QPoint(right - 20 - 10 - arg0/2, hcenter)
		section_width = arg1 + 120
		painter.setPen(self.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		painter.drawRect(
			QRect(center - QPoint(arg1,arg0), center + QPoint(arg1,arg0)))
		painter.setBrush(QBrush(Qt.white))

		painter.setPen(self.halfpen)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPoint(-arg1,arg0),
			bpnt = center+QPoint(-arg1,-arg0),
			offset = QPoint(-20,0),
			textoff = QPoint(-10, 0),
			text = txt0,
			arrow_size = arrow_size / 3 * 2
		)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPoint(arg1,arg0),
			bpnt = center+QPoint(-arg1,arg0),
			offset = QPoint(0,25),
			textoff = QPoint(0, -6),
			text = txt1,
			arrow_size = arrow_size / 3 * 2
		)
		#paintool.draw_dimlines(
		#	painter = painter,
		#	apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
		#	bpnt = center+QPoint(- math.cos(math.pi/4) * arg1, - math.sin(math.pi/4) * arg1),
		#	offset = QPoint(0,0),
		#	textoff = QPoint(8,-8),
		#	text = txt2,
		#	arrow_size = arrow_size / 3 * 2
		#)
		painter.setPen(self.axpen)
		llen = arg0 + 10
		painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
		painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	elif section_type == "Треугольник":
		center = QPoint(right - 20 - 10 - arg0/2, hcenter)
		section_width = arg1 + 120
		painter.setPen(self.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		painter.drawPolygon(
			QPolygon([
				center+QPoint(-arg1, arg0),
				center+QPoint(arg1, arg0),
				center+QPoint(0, -arg0),
			])
		)
		painter.setBrush(QBrush(Qt.white))

		painter.setPen(self.halfpen)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPoint(0,arg0),
			bpnt = center+QPoint(0,-arg0),
			offset = QPoint(-20-arg0,0),
			textoff = QPoint(-10, 0),
			text = txt0,
			arrow_size = arrow_size / 3 * 2
		)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPoint(arg1,arg0),
			bpnt = center+QPoint(-arg1,arg0),
			offset = QPoint(0,25),
			textoff = QPoint(0, -6),
			text = txt1,
			arrow_size = arrow_size / 3 * 2
		)
		#paintool.draw_dimlines(
		#	painter = painter,
		#	apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
		#	bpnt = center+QPoint(- math.cos(math.pi/4) * arg1, - math.sin(math.pi/4) * arg1),
		#	offset = QPoint(0,0),
		#	textoff = QPoint(8,-8),
		#	text = txt2,
		#	arrow_size = arrow_size / 3 * 2
		#)
		painter.setPen(self.axpen)
		llen = arg0 + 10
		painter.drawLine(center + QPoint(-llen,-arg0+4/3*arg0), center + QPoint(llen,-arg0+4/3*arg0))
		painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	elif section_type == "Квадрат повёрнутый":
		l = arg0/math.sqrt(2) 
		center = QPoint(right - 20 - 20 - arg0/2, hcenter)
		section_width = arg1 + 95
		painter.setPen(self.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		painter.drawPolygon(
			QPolygon([
				center+QPoint(-arg0, 0),
				center+QPoint(0, arg0),
				center+QPoint(arg0, 0),
				center+QPoint(0, -arg0),
			])
		)
		painter.setBrush(QBrush(Qt.white))

		painter.setPen(self.halfpen)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPoint(0,arg0),
			bpnt = center+QPoint(arg0,0),
			offset = QPoint(10, 10),
			textoff = QPoint(10, 10),
			text = txt0,
			arrow_size = arrow_size / 3 * 2
		)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPoint(0,-arg0),
			bpnt = center+QPoint(arg0,0),
			offset = QPoint(10, -10),
			textoff = QPoint(10, -10),
			text = txt0,
			arrow_size = arrow_size / 3 * 2
		)
		painter.setPen(self.axpen)
		llen = arg0 + 10
		painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
		painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	else:
		print("Unresolved section type:", section_type)
		exit(0)
	return section_width
