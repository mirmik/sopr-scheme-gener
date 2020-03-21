from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import paintool

import taskconf_menu

section_variant=[
	"Круг",  
	"Толстая труба",
	"Тонкая труба",
	"Прямоугольник",
	"Квадрат повёрнутый",
	"Треугольник",
	"Квадрат - окружность",
	"Прямоугольник с прямоугольным отверстием"
]

section_variant_base=[
	"Круг",  
	"Толстая труба",
	"Тонкая труба",
	"Прямоугольник",
	"Квадрат повёрнутый",
	"Треугольник",
	"Квадрат - окружность",
]

class BaseSectionType(taskconf_menu.TaskConfMenu):
	def __init__(self):
		super().__init__()
		self.txt0 = self.add("Сечение.Текст1:", "str", "D")
		self.txt1 = self.add("Сечение.Текст2:", "str", "d")
		self.txt2 = self.add("Сечение.Текст3:", "str", "d")
		self.arg0 = self.add("Сечение.Аргумент1:", "int", "60")
		self.arg1 = self.add("Сечение.Аргумент2:", "int", "50")
		self.arg2 = self.add("Сечение.Аргумент3:", "int", "10")

class RectMinusRect(taskconf_menu.TaskConfMenu):
	def __init__(self):
		super().__init__()
		self.h = self.add("Высота:", ("str", "int"), ("b", "70"))
		self.w = self.add("Ширина:", ("str", "int"), ("a", "50"))
		self.hh = self.add("Высота отверстия:", ("str", "int"), ("d", "20"))
		self.hw = self.add("Ширина отверстия:", ("str", "int"), ("c", "30"))
		self.s = self.add("Смещение:", ("bool", "str", "int"), (False, "s", "20"))

	def draw(self,
			wdg,
			shemetype, 
			right, 
			hcenter, 
			arrow_size):
		painter = wdg.painter

		h = self.h.get()[1]
		w = self.w.get()[1]
		h_text = self.h.get()[0]
		w_text = self.w.get()[0]

		hh = self.hh.get()[1]
		hw = self.hw.get()[1]
		hh_text = self.hh.get()[0]
		hw_text = self.hw.get()[0]

		s = self.s.get()[2]
		s_text = self.s.get()[1]

		if self.s.get()[0]:
			s=(h-hh)/2

		center = QPoint(right - 20 - 10 - w, hcenter)
		section_width = w + 120
		painter.setPen(wdg.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		
		painter.drawRect(
			QRect(center - QPoint(w,h), center + QPoint(w,h)))
		
		painter.setBrush(QBrush(Qt.white))
		painter.drawRect(
			QRect(center + QPoint(0,h-s*2) - QPoint(hw,hh*2), center + QPoint(0,h-s*2) + QPoint(hw,0)))

		painter.setPen(wdg.halfpen)

		paintool.draw_dimlines( # вертикальная
			painter = painter,
			apnt = center+QPoint(-w,h),
			bpnt = center+QPoint(-w,-h),
			offset = QPoint(-18,0),
			textoff = QPoint(-10, 0),
			text = h_text,
			arrow_size = arrow_size / 3 * 2
		)
		paintool.draw_dimlines( # горизонтальная
			painter = painter,
			apnt = center+QPoint(w,h),
			bpnt = center+QPoint(-w,h),
			offset = QPoint(0,23),
			textoff = QPoint(0, -7),
			text = w_text,
			arrow_size = arrow_size / 3 * 2
		)


		paintool.draw_dimlines( # вертикальная отв.
			painter = painter,
			apnt = center+QPoint(hw,h-s*2-hh*2),
			bpnt = center+QPoint(hw,h-s*2),
			offset = QPoint(w-hw + 18,0),
			textoff = QPoint(10, 0),
			text = hh_text,
			arrow_size = arrow_size / 3 * 2
		)
		paintool.draw_dimlines( # горизонтальная отв.
			painter = painter,
			apnt = center+QPoint(hw,h-s*2-hh*2),
			bpnt = center+QPoint(-hw,h-s*2-hh*2),
			offset = QPoint(0,-h*2+hh*2+s*2-16),
			textoff = QPoint(0, -7),
			text = hw_text,
			arrow_size = arrow_size / 3 * 2
		)

		if s != (h-hh)/2:
			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(hw,h),
				bpnt = center+QPoint(hw,h-s*2),
				offset = QPoint(w-hw + 18,0),
				textoff = QPoint(10, 0),
				text = s_text,
				arrow_size = arrow_size / 3 * 2
			)

		painter.setPen(wdg.axpen)
		#llen = w + 10
		if s == (h-hh)/2:
			painter.drawLine(center + QPoint(-w-10,0), center + QPoint(w+10,0))
		painter.drawLine(center + QPoint(0,-h-10), center + QPoint(0,h+10))
		
		return section_width


class SectionContainer(taskconf_menu.TaskConfMenu):
	#updated = pyqtSignal()
	class _SectionContainerWidget(QWidget):
		def __init__(self):
			super().__init__()

			self.layout = QHBoxLayout()
			self.stub = QWidget()
			self.layout.addWidget(self.stub)
			self.setLayout(self.layout)
		
		def replace(self, wdg):
			self.widget().hide()
			wdg.show()
			self.layout.removeWidget(self.layout.itemAt(0).widget())
			self.layout.addWidget(wdg)
			self.update()

		def widget(self):
			return self.layout.itemAt(0).widget()

		def set_stub(self):
			self.replace(self.stub)


	def section_enable_handle(self):
		if self.checker.get():
			self.show()
		else:
			self.hide()
	
	def __init__(self, checker):
		super().__init__()

		self.checker = checker
		self.checker.element().updated.connect(self.section_enable_handle)
		self.base_section_widget = BaseSectionType() 
		self.base_section_widget.updated.connect(self.updated)

		self.rect_minus_rect = RectMinusRect() 
		self.rect_minus_rect.updated.connect(self.updated)

		self.updated.connect(self.updated_selfhandle)
		self.container = self._SectionContainerWidget()
		self.section_type = self.add("Тип сечения:", "list", defval=4, variant=section_variant)
		self.add_widget(self.container)
		self.container.replace(self.base_section_widget)
		self.oldtype = ""

	def draw(self, *args, **kwargs):
		return self.container.widget().draw(*args, **kwargs)

	def updated_selfhandle(self):
		if self.section_type.get() == self.oldtype:
			return
		self.oldtype = self.section_type.get()

		if self.section_type.get() in section_variant_base:
			self.container.replace(self.base_section_widget)

		elif self.section_type.get() == "Прямоугольник с прямоугольным отверстием":
			self.container.replace(self.rect_minus_rect)		 

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



def draw_section_routine(self, hcenter, right):
	section_enable = self.shemetype.section_enable.get()

	if section_enable and self.shemetype.section_container.section_type.get() in section_variant_base:
		section_width = draw_section(
			wdg = self,
			section_type = self.shemetype.section_container.section_type.get(),
			arg0 = int(self.shemetype.section_container.base_section_widget.arg0.get()),
			arg1 = int(self.shemetype.section_container.base_section_widget.arg1.get()),
			arg2 = int(self.shemetype.section_container.base_section_widget.arg2.get()),
			txt0 = paintool.greek(self.shemetype.section_container.base_section_widget.txt0.get()),
			txt1 = paintool.greek(self.shemetype.section_container.base_section_widget.txt1.get()),
			txt2 = paintool.greek(self.shemetype.section_container.base_section_widget.txt2.get()),
			arrow_size = self.shemetype.arrow_size.get(),
			right = right,
			hcenter=hcenter
		)

		
	elif section_enable: # небазовый список
		section_width = self.shemetype.section_container.draw(
			wdg=self,
			shemetype=self.shemetype, 
			right=right, 
			hcenter=hcenter, 
			arrow_size=self.shemetype.arrow_size.get())

	else:
		section_width = 0

	return section_width