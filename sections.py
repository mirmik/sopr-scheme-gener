from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import paintool
import common

import taskconf_menu

MAIN_SECTION_TYPE = "Сечение общего типа"

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

section_variant2=[
	MAIN_SECTION_TYPE,  
	#"Круг",  
	#"Толстая труба",
	"Тонкая труба",
	#"Прямоугольник",
	#"Квадрат повёрнутый",
	"Треугольник",
	#"Квадрат - окружность",
	"Прямоугольник с прямоугольным отверстием",
	"H - профиль",
]

section_variant_base=[
	#"Круг",  
	#"Толстая труба",
	"Тонкая труба",
	#"Прямоугольник",
	#"Квадрат повёрнутый",
	"Треугольник",
	#"Квадрат - окружность",
	"H - профиль",
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

class MainSection0(taskconf_menu.TaskConfMenu):
	def __init__(self):
		super().__init__()
		self.outer_type = self.add("Тип сечения:", "list", defval=0, 
			variant=[
				"Прямоугольник",
				"Квадрат",
				"Квадрат повёрнутый 45 град",
				"Круг"])

		self.w = self.add("Ширина:", ("str", "int"), ("a", "50"))
		self.h = self.add("Высота:", ("str", "int"), ("b", "70"))

		self.inner_type = self.add("Тип внутр. сечения:", "list", defval=0, 
			variant=[
				"Нет",
				"Квадрат",
				"Квадрат повёрнутый 45 град",
				"Круг"])

		self.iw = self.add("Ширина внутр.:", ("str", "int"), ("c", "30"))

	def draw(self,
			wdg,
			shemetype, 
			right, 
			hcenter, 
			arrow_size):

		painter = wdg.painter
		
		w=h=self.w.get()[1]
		w_text = self.w.get()[0]
		iw = self.iw.get()[1]
		iw_text = self.iw.get()[0]
		wlen = hlen = w 

		section_width = w + 120
		center = QPoint(right - 20 - 10 - w, hcenter)
		painter.setPen(wdg.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		
		if self.outer_type.get() == "Прямоугольник":
			h = self.h.get()[1]
			h_text = self.h.get()[0]
			
			painter.drawRect(
				QRect(center - QPoint(w,h), center + QPoint(w,h)))

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
			hlen = h

		elif self.outer_type.get() == "Квадрат":
			painter.drawRect(
				QRect(center - QPoint(w,w), center + QPoint(w,w)))

			paintool.draw_dimlines( # горизонтальная
				painter = painter,
				apnt = center+QPoint(w,w),
				bpnt = center+QPoint(-w,w),
				offset = QPoint(0,23),
				textoff = QPoint(0, -7),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)

		elif self.outer_type.get() == "Квадрат повёрнутый 45 град":
			painter.drawPolygon(
				QPolygon([
					center+QPoint(-w, 0),
					center+QPoint(0, w),
					center+QPoint(w, 0),
					center+QPoint(0, -w),
				])
			)
			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(0,-w),
				bpnt = center+QPoint(-w,0),
				offset = QPoint(-15, -15),
				textoff = QPoint(-10, -10),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)
			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(0,w),
				bpnt = center+QPoint(-w,0),
				offset = QPoint(-15, 15),
				textoff = QPoint(-10, 10),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)

		elif self.outer_type.get() == "Круг":
			painter.drawEllipse(
				QRect(center - QPoint(w,w), center + QPoint(w,w)))

			paintool.draw_dimlines( # горизонтальная
				painter = painter,
				apnt = center+QPoint(w,0),
				bpnt = center+QPoint(-w,0),
				offset = QPoint(0,23+w),
				textoff = QPoint(0, -7),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)

		painter.setPen(wdg.pen)
		painter.setBrush(Qt.white)
		if self.inner_type.get() == "Квадрат":
			painter.drawRect(
				QRect(center - QPoint(iw,iw), center + QPoint(iw,iw)))

			paintool.draw_dimlines( # горизонтальная
				painter = painter,
				apnt = center+QPoint(iw,iw),
				bpnt = center+QPoint(iw,-iw),
				offset = QPoint(w-iw+15, 0),
				textoff = QPoint(8, 0),
				text = iw_text,
				arrow_size = arrow_size / 3 * 2
			)

		elif self.inner_type.get() == "Квадрат повёрнутый 45 град":
			painter.drawPolygon(
				QPolygon([
					center+QPoint(-iw, 0),
					center+QPoint(0, iw),
					center+QPoint(iw, 0),
					center+QPoint(0, -iw),
				])
			)
			if self.outer_type.get() != "Квадрат повёрнутый 45 град": 
				paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPoint(0,iw),
					bpnt = center+QPoint(iw,0),
					offset = QPoint(10, 10),
					textoff = QPoint(10, 10),
					text = iw_text,
					arrow_size = arrow_size / 3 * 2
				)
				paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPoint(0,-iw),
					bpnt = center+QPoint(iw,0),
					offset = QPoint(10, -10),
					textoff = QPoint(10, -10),
					text = iw_text,
					arrow_size = arrow_size / 3 * 2
				)
			else:
				c1=(QPoint(0,w)+QPoint(w,0))/2 - (QPoint(0,iw)+QPoint(iw,0))/2
				c2=(QPoint(0,-w)+QPoint(w,0))/2 - (QPoint(0,-iw)+QPoint(iw,0))/2
				paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPoint(0,iw),
					bpnt = center+QPoint(iw,0),
					offset = c1 + QPoint(15, 15),
					textoff = QPoint(10, 10),
					text = iw_text,
					arrow_size = arrow_size / 3 * 2
				)
				paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPoint(0,-iw),
					bpnt = center+QPoint(iw,0),
					offset = c2 + QPoint(15, -15),
					textoff = QPoint(10, -10),
					text = iw_text,
					arrow_size = arrow_size / 3 * 2
				)
	
		elif self.inner_type.get() == "Круг":
			painter.drawEllipse(
				QRect(center - QPoint(iw,iw), center + QPoint(iw,iw)))

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPoint(+ math.cos(math.pi/4) * iw, + math.sin(math.pi/4) * iw),
				bpnt = center+QPoint(- math.cos(math.pi/4) * iw, - math.sin(math.pi/4) * iw),
				offset = QPoint(0,0),
				textoff = QPoint(8,-8),
				text = iw_text,
				arrow_size = arrow_size / 3 * 2
			)

		painter.setPen(wdg.axpen)
		wlen = wlen + 10
		hlen = hlen + 10

		painter.drawLine(center + QPointF(wlen,0), center + QPointF(-wlen,0))
		painter.drawLine(center + QPointF(0,-hlen), center + QPointF(0,hlen))

		return section_width

class HRect(taskconf_menu.TaskConfMenu):
	def __init__(self):
		super().__init__()
		self.h = self.add("Габарит1:", ("str", "int"), ("b", "70"))
		self.w = self.add("Габарит2:", ("str", "int"), ("a", "50"))
		self.w1 = self.add("Ширина перекладины:", ("str", "int"), ("d", "20"))
		self.h1 = self.add("Ширина II:", ("str", "int"), ("d", "20"))
		self.orient = self.add("Ориентация:", "bool", False)

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
		
		h1 = self.h1.get()[1]
		w1 = self.w1.get()[1]
		h1_text = self.h1.get()[0]
		w1_text = self.w1.get()[0]

		painter.setPen(self.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		
		if self.orient.get():
			painter.drawPolygon(
				QPolygon([
					center+QPoint(-w, h),
					center+QPoint(-w+w1, h),

					center+QPoint(w-w1, h),
					center+QPoint(w, h),

					center+QPoint(w, -h),
					center+QPoint(w-w1, -h),
					
					center+QPoint(-w+w1, -h),
					center+QPoint(-w, -h),
				])
			)
	
class RectMinusRect(taskconf_menu.TaskConfMenu):
	def __init__(self):
		super().__init__()
		self.h = self.add("Высота:", ("str", "int"), ("b", "70"))
		self.w = self.add("Ширина:", ("str", "int"), ("a", "50"))
		self.hh = self.add("Высота отверстия:", ("str", "int"), ("d", "20"))
		self.hw = self.add("Ширина отверстия:", ("str", "int"), ("c", "30"))
		self.s = self.add("Свободное смещение:", ("bool", "str", "int"), (False, "s", "20"))
		self.edge = self.add("Смещение к краю:", "list", defval=0, variant=["Нет", "Верх", "Низ"])

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
		s_edge = self.edge.get() != "Нет"

		if self.edge.get() == "Верх":
			s = h - hh

		if self.edge.get() == "Низ":
			s = 0

		if self.s.get()[0] and not s_edge:
			s=(h-hh)/2

		center = QPoint(right - 20 - 10 - w, hcenter)
		section_width = w + 120
		painter.setPen(wdg.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		
		painter.drawRect(
			QRect(center - QPoint(w,h), center + QPoint(w,h)))
		
		painter.setBrush(QBrush(Qt.white))
		if s_edge and self.edge.get() == "Верх":
			painter.setPen(Qt.white)
			painter.drawRect(QRect(center + QPoint(0,h-s*2) - QPoint(hw,hh*2 + 3), center + QPoint(0,h-s*2) + QPoint(hw,0)))
			painter.setPen(wdg.pen)
			painter.drawLine(center + QPoint(-hw, h-s*2 - hh*2), center + QPoint(-hw,h-s*2))
			painter.drawLine(center + QPoint(hw,h-s*2), center + QPoint(-hw,h-s*2))
			painter.drawLine(center + QPoint(hw, h-s*2 - hh*2), center + QPoint(hw,h-s*2))

		elif s_edge and self.edge.get() == "Низ":
			painter.setPen(Qt.white)
			painter.drawRect(QRect(center + QPoint(0,h) - QPoint(hw,hh*2), center + QPoint(0,h) + QPoint(hw,3)))
			painter.setPen(wdg.pen)
			painter.drawLine(center + QPoint(-hw,h - hh*2), center + QPoint(-hw,h))
			painter.drawLine(center + QPoint(hw,h- hh*2), center + QPoint(-hw,h- hh*2))
			painter.drawLine(center + QPoint(hw,h - hh*2), center + QPoint(hw,h))

#		painter.setPen(wdg.pen)
		
		else:
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

		if self.edge.get() == "Низ":
			paintool.draw_dimlines( # горизонтальная
				painter = painter,
			apnt = center+QPoint(w,h-s*2-hh*2),
			bpnt = center+QPoint(-w,h-s*2-hh*2),
			offset = QPoint(0,-h*2+hh*2+s*2-16),
			textoff = QPoint(0, -7),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)

		else:
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

		if self.edge.get() == "Низ":
			paintool.draw_dimlines( # горизонтальная отв.
				painter = painter,
				apnt = center+QPoint(hw,h),
				bpnt = center+QPoint(-hw,h),
				offset = QPoint(0,23),
				textoff = QPoint(0, -7),
				text = hw_text,
				arrow_size = arrow_size / 3 * 2
			)

		else:
			paintool.draw_dimlines( # горизонтальная отв.
				painter = painter,
				apnt = center+QPoint(hw,h-s*2-hh*2),
				bpnt = center+QPoint(-hw,h-s*2-hh*2),
				offset = QPoint(0,-h*2+hh*2+s*2-16),
				textoff = QPoint(0, -7),
				text = hw_text,
				arrow_size = arrow_size / 3 * 2
			)

		if s != (h-hh)/2 and not s_edge:
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
		if s == (h-hh)/2 and not s_edge:
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

	def serialize(self):
		return {
			"section_type": self.section_type.get(),
			"base_section_widget": self.base_section_widget.serialize(), 
			"rect_minus_rect": self.rect_minus_rect.serialize(),
			"main_section_0": self.main_section_0.serialize()
		}


	def deserialize(self, dct):
		self.section_type.set(dct["section_type"])
		self.base_section_widget.deserialize(dct["base_section_widget"]) 
		self.rect_minus_rect.deserialize(dct["rect_minus_rect"])
		self.main_section_0.deserialize(dct["main_section_0"])
	
	def __init__(self, checker):
		super().__init__()

		if checker is not None:
			self.checker = checker
			self.checker.element().updated.connect(self.section_enable_handle)
		self.base_section_widget = BaseSectionType() 
		self.base_section_widget.updated.connect(self.updated)

		self.rect_minus_rect = RectMinusRect() 
		self.main_section_0 = MainSection0() 
		self.hrect = HRect() 
		self.rect_minus_rect.updated.connect(self.updated)
		self.main_section_0.updated.connect(self.updated)
		self.hrect.updated.connect(self.updated)

		self.updated.connect(self.updated_selfhandle)
		self.container = self._SectionContainerWidget()
		self.section_type = self.add("Тип сечения:", "list", defval=0, variant=section_variant2)
		self.add_widget(self.container)
		self.container.replace(self.main_section_0)
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

		elif self.section_type.get() == "Сечение общего типа":
			self.container.replace(self.main_section_0)		 

def draw_section(wdg, section_type, right, hcenter,
	arg0, arg1, arg2, txt0, txt1, txt2, arrow_size
):
	self = wdg
	painter = self.painter
	painter.setFont(self.font)
	
	#if section_type == "Круг":
	#	center = QPoint(right - 10 -20 - arg0/2, hcenter)
	#	section_width = arg0 + 100
	#	dimlines_off = arg0 + 30
	#	painter.setPen(self.pen)
	#	painter.setBrush(QBrush(Qt.BDiagPattern))
	#	painter.drawEllipse(
	#		QRect(center - QPoint(arg0,arg0), center + QPoint(arg0,arg0)))
	#	painter.setPen(self.halfpen)
	#	paintool.draw_dimlines(
	#		painter = painter,
	#		apnt = center-QPoint(arg0, 0),
	#		bpnt = center+QPoint(arg0, 0),
	#		offset = QPoint(0,dimlines_off),
	#		textoff = QPoint(0, -10),
	#		text = txt0,
	#		arrow_size = arrow_size / 3 * 2
	#	)
	#	painter.setPen(self.axpen)
	#	llen = arg0 + 10
	#	painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
	#	painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	if section_type == "Тонкая труба":
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
	#elif section_type == "Толстая труба":
	#	center = QPoint(right - 20 - 10 - arg0/2, hcenter)
	#	section_width = arg0 + 120
	#	dimlines_off = arg0 + 20
	#	painter.setPen(self.pen)
	#	painter.setBrush(QBrush(Qt.BDiagPattern))
	#	painter.drawEllipse(
	#		QRect(center - QPoint(arg0,arg0), center + QPoint(arg0,arg0)))
	#	painter.setBrush(QBrush(Qt.white))
	#	painter.drawEllipse(
	#		QRect(center - QPoint(arg1,arg1), center + QPoint(arg1,arg1)))
	#	painter.setPen(self.halfpen)
	#	paintool.draw_dimlines(
	#		painter = painter,
	#		apnt = center-QPoint(0,arg0),
	#		bpnt = center+QPoint(0,arg0),
	#		offset = QPoint(-dimlines_off,0),
	#		textoff = QPoint(-10, 0) - QPoint(QFontMetrics(self.font).width(txt0)/2, 0),
	#		text = txt0,
	#		arrow_size = arrow_size / 3 * 2
	#	)
	#	paintool.draw_dimlines(
	#		painter = painter,
	#		apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
	#		bpnt = center+QPoint(- math.cos(math.pi/4) * arg1, - math.sin(math.pi/4) * arg1),
	#		offset = QPoint(0,0),
	#		textoff = QPoint(10,-10),
	#		text = txt1,
	#		arrow_size = arrow_size / 3 * 2,
	#	)
	#	
	#	painter.setPen(self.axpen)
	#	llen = arg0 + 10
	#	painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
	#	painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	#elif section_type == "Квадрат - окружность":
	#	center = QPoint(right - 20 - 10 - arg0/2, hcenter)
	#	section_width = arg0 + 120
	#	dimlines_off = arg0 + 20
	#	painter.setPen(self.pen)
	#	painter.setBrush(QBrush(Qt.BDiagPattern))
	#	painter.drawRect(
	#		QRect(center - QPoint(arg0,arg0), center + QPoint(arg0,arg0)))
	#	painter.setBrush(QBrush(Qt.white))
	#	painter.drawEllipse(
	#		QRect(center - QPoint(arg1,arg1), center + QPoint(arg1,arg1)))
	#	painter.setPen(self.halfpen)
	#	paintool.draw_dimlines(
	#		painter = painter,
	#		apnt = center+QPoint(-arg0,arg0),
	#		bpnt = center+QPoint(-arg0,-arg0),
	#		offset = QPoint(-20,0),
	#		textoff = QPoint(-10, 0),
	#		text = txt0,
	#		arrow_size = arrow_size / 3 * 2
	#	)
	#	paintool.draw_dimlines(
	#		painter = painter,
	#		apnt = center+QPoint(arg0,arg0),
	#		bpnt = center+QPoint(-arg0,arg0),
	#		offset = QPoint(0,25),
	#		textoff = QPoint(0, -6),
	#		text = txt1,
	#		arrow_size = arrow_size / 3 * 2
	#	)
	#	paintool.draw_dimlines(
	#		painter = painter,
	#		apnt = center+QPoint(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
	#		bpnt = center+QPoint(- math.cos(math.pi/4) * arg1, - math.sin(math.pi/4) * arg1),
	#		offset = QPoint(0,0),
	#		textoff = QPoint(8,-8),
	#		text = txt2,
	#		arrow_size = arrow_size / 3 * 2
	#	)
	#	painter.setPen(self.axpen)
	#	llen = arg0 + 10
	#	painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
	#	painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	#elif section_type == "Прямоугольник":
	#	center = QPoint(right - 20 - 10 - arg0/2, hcenter)
	#	section_width = arg1 + 120
	#	painter.setPen(self.pen)
	#	painter.setBrush(QBrush(Qt.BDiagPattern))
	#	painter.drawRect(
	#		QRect(center - QPoint(arg1,arg0), center + QPoint(arg1,arg0)))
	#	painter.setBrush(QBrush(Qt.white))
#
	#	painter.setPen(self.halfpen)
	#	paintool.draw_dimlines(
	#		painter = painter,
	#		apnt = center+QPoint(-arg1,arg0),
	#		bpnt = center+QPoint(-arg1,-arg0),
	#		offset = QPoint(-20,0),
	#		textoff = QPoint(-10, 0),
	#		text = txt0,
	#		arrow_size = arrow_size / 3 * 2
	#	)
	#	paintool.draw_dimlines(
	#		painter = painter,
	#		apnt = center+QPoint(arg1,arg0),
	#		bpnt = center+QPoint(-arg1,arg0),
	#		offset = QPoint(0,25),
	#		textoff = QPoint(0, -6),
	#		text = txt1,
	#		arrow_size = arrow_size / 3 * 2
	#	)
	#	painter.setPen(self.axpen)
	#	llen = arg0 + 10
	#	painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
	#	painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
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
		painter.setPen(self.axpen)
		llen = arg0 + 10
		painter.drawLine(center + QPoint(-llen,-arg0+4/3*arg0), center + QPoint(llen,-arg0+4/3*arg0))
		painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	#elif section_type == "Квадрат повёрнутый":
	#	l = arg0/math.sqrt(2) 
	#	center = QPoint(right - 20 - 20 - arg0/2, hcenter)
	#	section_width = arg1 + 95
	#	painter.setPen(self.pen)
	#	painter.setBrush(QBrush(Qt.BDiagPattern))
	#	painter.drawPolygon(
	#		QPolygon([
	#			center+QPoint(-arg0, 0),
	#			center+QPoint(0, arg0),
	#			center+QPoint(arg0, 0),
	#			center+QPoint(0, -arg0),
	#		])
	#	)
	#	painter.setBrush(QBrush(Qt.white))
#
	#	painter.setPen(self.halfpen)
	#	paintool.draw_dimlines(
	#		painter = painter,
	#		apnt = center+QPoint(0,arg0),
	#		bpnt = center+QPoint(arg0,0),
	#		offset = QPoint(10, 10),
	#		textoff = QPoint(10, 10),
	#		text = txt0,
	#		arrow_size = arrow_size / 3 * 2
	#	)
	#	paintool.draw_dimlines(
	#		painter = painter,
	#		apnt = center+QPoint(0,-arg0),
	#		bpnt = center+QPoint(arg0,0),
	#		offset = QPoint(10, -10),
	#		textoff = QPoint(10, -10),
	#		text = txt0,
	#		arrow_size = arrow_size / 3 * 2
	#	)
	#	painter.setPen(self.axpen)
	#	llen = arg0 + 10
	#	painter.drawLine(center + QPoint(-llen,0), center + QPoint(llen,0))
	#	painter.drawLine(center + QPoint(0,-llen), center + QPoint(0,llen))
	else:
		print("Unresolved section type:", section_type)
		exit(0)
	return section_width



def draw_section_routine(self, hcenter, right):
	if hasattr(self.shemetype, "section_enable"):
		section_enable = self.shemetype.section_enable.get()
	else:
		section_enable = True

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