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
	"Нет",
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


class NoneSection(taskconf_menu.TaskConfMenu):
	def __init__(self):
		super().__init__()
	
	def draw(self,
			wdg,
			shemetype, 
			right, 
			hcenter, 
			arrow_size,
			painter = None):
		return 0

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
			arrow_size,
			painter = None):

		if painter is None:
			painter = wdg.painter
		
		w=h=self.w.get()[1]
		w_text = self.w.get()[0]
		iw = self.iw.get()[1]
		iw_text = self.iw.get()[0]
		wlen = hlen = w 

		section_width = w + 120
		center = QPointF(right - 20 - 10 - w, hcenter)
		painter.setPen(wdg.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		
		if self.outer_type.get() == "Прямоугольник":
			h = self.h.get()[1]
			h_text = self.h.get()[0]
			
			painter.drawRect(
				QRectF(center - QPointF(w,h), center + QPointF(w,h)))

			paintool.draw_dimlines( # вертикальная
				painter = painter,
				apnt = center+QPointF(-w,h),
				bpnt = center+QPointF(-w,-h),
				offset = QPointF(-18,0),
				textoff = QPointF(-10, 0),
				text = h_text,
				arrow_size = arrow_size / 3 * 2
			)

			paintool.draw_dimlines( # горизонтальная
				painter = painter,
				apnt = center+QPointF(w,h),
				bpnt = center+QPointF(-w,h),
				offset = QPointF(0,30),
				textoff = QPointF(0, -11),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)
			hlen = h

		elif self.outer_type.get() == "Квадрат":
			painter.drawRect(
				QRectF(center - QPointF(w,w), center + QPointF(w,w)))

			paintool.draw_dimlines( # горизонтальная
				painter = painter,
				apnt = center+QPointF(w,w),
				bpnt = center+QPointF(-w,w),
				offset = QPointF(0,30),
				textoff = QPointF(0, -11),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)

		elif self.outer_type.get() == "Квадрат повёрнутый 45 град":
			painter.drawPolygon(
				QPolygonF([
					center+QPointF(-w, 0),
					center+QPointF(0, w),
					center+QPointF(w, 0),
					center+QPointF(0, -w),
				])
			)
			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPointF(0,-w),
				bpnt = center+QPointF(-w,0),
				offset = QPointF(-15, -15),
				textoff = QPointF(-10, -10),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)
			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPointF(0,w),
				bpnt = center+QPointF(-w,0),
				offset = QPointF(-15, 15),
				textoff = QPointF(-10, 10),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)

		elif self.outer_type.get() == "Круг":
			painter.drawEllipse(
				QRectF(center - QPointF(w,w), center + QPointF(w,w)))

			paintool.draw_dimlines( # горизонтальная
				painter = painter,
				apnt = center+QPointF(w,0),
				bpnt = center+QPointF(-w,0),
				offset = QPointF(0,23+w),
				textoff = QPointF(0, -7),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)

		painter.setPen(wdg.pen)
		painter.setBrush(Qt.white)
		if self.inner_type.get() == "Квадрат":
			painter.drawRect(
				QRectF(center - QPointF(iw,iw), center + QPointF(iw,iw)))

			paintool.draw_dimlines( # горизонтальная
				painter = painter,
				apnt = center+QPointF(iw,iw),
				bpnt = center+QPointF(iw,-iw),
				offset = QPointF(w-iw+15, 0),
				textoff = QPointF(8, 0),
				text = iw_text,
				arrow_size = arrow_size / 3 * 2
			)

		elif self.inner_type.get() == "Квадрат повёрнутый 45 град":
			painter.drawPolygon(
				QPolygonF([
					center+QPointF(-iw, 0),
					center+QPointF(0, iw),
					center+QPointF(iw, 0),
					center+QPointF(0, -iw),
				])
			)
			if self.outer_type.get() != "Квадрат повёрнутый 45 град": 
				paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(0,iw),
					bpnt = center+QPointF(iw,0),
					offset = QPointF(10, 10),
					textoff = QPointF(10, 10),
					text = iw_text,
					arrow_size = arrow_size / 3 * 2
				)
				paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(0,-iw),
					bpnt = center+QPointF(iw,0),
					offset = QPointF(10, -10),
					textoff = QPointF(10, -10),
					text = iw_text,
					arrow_size = arrow_size / 3 * 2
				)
			else:
				c1=(QPointF(0,w)+QPointF(w,0))/2 - (QPointF(0,iw)+QPointF(iw,0))/2
				c2=(QPointF(0,-w)+QPointF(w,0))/2 - (QPointF(0,-iw)+QPointF(iw,0))/2
				paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(0,iw),
					bpnt = center+QPointF(iw,0),
					offset = c1 + QPointF(15, 15),
					textoff = QPointF(10, 10),
					text = iw_text,
					arrow_size = arrow_size / 3 * 2
				)
				paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(0,-iw),
					bpnt = center+QPointF(iw,0),
					offset = c2 + QPointF(15, -15),
					textoff = QPointF(10, -10),
					text = iw_text,
					arrow_size = arrow_size / 3 * 2
				)
	
		elif self.inner_type.get() == "Круг":
			painter.drawEllipse(
				QRectF(center - QPointF(iw,iw), center + QPointF(iw,iw)))

			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPointF(+ math.cos(math.pi/4) * iw, + math.sin(math.pi/4) * iw),
				bpnt = center+QPointF(- math.cos(math.pi/4) * iw, - math.sin(math.pi/4) * iw),
				offset = QPointF(0,0),
				textoff = QPointF(8,-8),
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
		self.h = self.add("Габарит1:", ("str", "int"), ("a", "70"))
		self.w = self.add("Габарит2:", ("str", "int"), ("b", "50"))
		self.h1 = self.add("Ширина перекладины:", ("str", "int"), ("c", "10"))
		self.w1 = self.add("Ширина II:", ("str", "int"), ("d", "10"))
		self.orient = self.add("Ориентация:", "bool", False)

	def draw(self,
			wdg,
			shemetype, 
			right, 
			hcenter, 
			arrow_size,
			painter = None):
		if painter is None:
			painter = wdg.painter

		h = self.h.get()[1]
		w = self.w.get()[1]
		h_text = self.h.get()[0]
		w_text = self.w.get()[0]

		wlen = w + 10
		hlen = h + 10

		h1 = self.h1.get()[1]
		w1 = self.w1.get()[1]
		h1_text = self.h1.get()[0]
		w1_text = self.w1.get()[0]
		section_width = w + 120
		center = QPointF(right - 20 - 10 - w, hcenter)
		painter.setPen(wdg.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		
		if self.orient.get() is False:
			painter.drawPolygon(
				QPolygonF([
					center+QPointF(-w, h),
					center+QPointF(-w+w1*2, h),

					center+QPointF(-w+w1*2, h1),
					center+QPointF( w-w1*2, h1),

					center+QPointF(w-w1*2, h),
					center+QPointF(w, h),

					center+QPointF(w, -h),
					center+QPointF(w-w1*2, -h),

					center+QPointF( w-w1*2, -h1),
					center+QPointF(-w+w1*2, -h1),
					
					center+QPointF(-w+w1*2, -h),
					center+QPointF(-w, -h),
				])
			)

			painter.setPen(wdg.axpen)
			painter.drawLine(center + QPointF(wlen,0), center + QPointF(-wlen,0))
			painter.drawLine(center + QPointF(w-w1,hlen), center + QPointF(w-w1,-hlen))
			painter.drawLine(center + QPointF(-w+w1,hlen), center + QPointF(-w+w1,-hlen))
		
			paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(-w,-h),
					bpnt = center+QPointF(-w, h),
					offset = QPointF(-20, 0),
					textoff = QPointF(-10, 0),
					text = h_text,
					arrow_size = arrow_size / 3 * 2
				)
				
			paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF( w,h),
					bpnt = center+QPointF(-w,h),
					offset = QPointF(0, 25),
					textoff = QPointF(0, -10),
					text = w_text,
					arrow_size = arrow_size / 3 * 2
				)

			paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(-w,-h),
					bpnt = center+QPointF(-w+w1*2,-h),
					offset = QPointF(0, -20),
					textoff = QPointF(0, -10),
					text = w1_text,
					arrow_size = arrow_size / 3 * 2,
					splashed=True
				)

			paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(w-w1*2,-h),
					bpnt = center+QPointF(w,-h),
					offset = QPointF(0, -20),
					textoff = QPointF(0, -10),
					text = w1_text,
					arrow_size = arrow_size / 3 * 2,
					splashed=True
				)

			paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(0,-h1),
					bpnt = center+QPointF(0, h1),
					offset = QPointF(w+20, 0),
					textoff = QPointF(10, 0),
					text = h1_text,
					arrow_size = arrow_size / 3 * 2,
					splashed=True
				)
			
		else:
			painter.drawPolygon(
				QPolygonF([
					center+QPointF(w, -h),
					center+QPointF(w, -h+w1*2),

					center+QPointF(h1, -h+w1*2),
					center+QPointF(h1, h-w1*2),

					center+QPointF(w, h-w1*2),
					center+QPointF(w, h),

					center+QPointF(-w, h),
					center+QPointF(-w, h-w1*2),

					center+QPointF(-h1, h-w1*2),
					center+QPointF(-h1, -h+w1*2),
					
					center+QPointF(-w, -h+w1*2),
					center+QPointF(-w, -h),
				])
			)
	
			painter.setPen(wdg.axpen)
			painter.drawLine(center + QPointF(0,hlen-2), center + QPointF(0,-hlen))
			painter.drawLine(center + QPointF(wlen,h-w1), center + QPointF(-wlen,h-w1))
			painter.drawLine(center + QPointF(wlen,-h+w1), center + QPointF(-wlen,-h+w1))

			paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(-w,-h),
					bpnt = center+QPointF(-w, h),
					offset = QPointF(-20, 0),
					textoff = QPointF(-10, 0),
					text = h_text,
					arrow_size = arrow_size / 3 * 2
				)
				
			paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF( w,h),
					bpnt = center+QPointF(-w,h),
					offset = QPointF(0, 25),
					textoff = QPointF(0, -10),
					text = w_text,
					arrow_size = arrow_size / 3 * 2
				)

			paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(w,h),
					bpnt = center+QPointF(w,h-w1*2),
					offset = QPointF(20,0),
					textoff = QPointF(10,0),
					text = w1_text,
					arrow_size = arrow_size / 3 * 2,
					splashed=True
				)

			paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(w,-h+w1*2),
					bpnt = center+QPointF(w,-h),
					offset = QPointF(20,0),
					textoff = QPointF(10,0),
					text = w1_text,
					arrow_size = arrow_size / 3 * 2,
					splashed=True
				)

			paintool.draw_dimlines(
					painter = painter,
					apnt = center+QPointF(-h1,0),
					bpnt = center+QPointF(h1, 0),
					offset = QPointF(0, -20-h),
					textoff = QPointF(0, -10),
					text = h1_text,
					arrow_size = arrow_size / 3 * 2,
					splashed=True
				)	
		return section_width
	
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
			arrow_size,
			painter = None):
		if painter is None:
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

		center = QPointF(right - 20 - 10 - w, hcenter)
		section_width = w + 120
		painter.setPen(wdg.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		
		painter.drawRect(
			QRectF(center - QPointF(w,h), center + QPointF(w,h)))
		
		painter.setBrush(QBrush(Qt.white))
		if s_edge and self.edge.get() == "Верх":
			painter.setPen(Qt.white)
			painter.drawRect(QRectF(center + QPointF(0,h-s*2) - QPointF(hw,hh*2 + 3), center + QPointF(0,h-s*2) + QPointF(hw,0)))
			painter.setPen(wdg.pen)
			painter.drawLine(center + QPointF(-hw, h-s*2 - hh*2), center + QPointF(-hw,h-s*2))
			painter.drawLine(center + QPointF(hw,h-s*2), center + QPointF(-hw,h-s*2))
			painter.drawLine(center + QPointF(hw, h-s*2 - hh*2), center + QPointF(hw,h-s*2))

		elif s_edge and self.edge.get() == "Низ":
			painter.setPen(Qt.white)
			painter.drawRect(QRectF(center + QPointF(0,h) - QPointF(hw,hh*2), center + QPointF(0,h) + QPointF(hw,3)))
			painter.setPen(wdg.pen)
			painter.drawLine(center + QPointF(-hw,h - hh*2), center + QPointF(-hw,h))
			painter.drawLine(center + QPointF(hw,h- hh*2), center + QPointF(-hw,h- hh*2))
			painter.drawLine(center + QPointF(hw,h - hh*2), center + QPointF(hw,h))

#		painter.setPen(wdg.pen)
		
		else:
			painter.drawRect(
				QRectF(center + QPointF(0,h-s*2) - QPointF(hw,hh*2), center + QPointF(0,h-s*2) + QPointF(hw,0)))

		painter.setPen(wdg.halfpen)

		paintool.draw_dimlines( # вертикальная
			painter = painter,
			apnt = center+QPointF(-w,h),
			bpnt = center+QPointF(-w,-h),
			offset = QPointF(-18,0),
			textoff = QPointF(-10, 0),
			text = h_text,
			arrow_size = arrow_size / 3 * 2
		)

		if self.edge.get() == "Низ":
			paintool.draw_dimlines( # горизонтальная
				painter = painter,
			apnt = center+QPointF(w,h-s*2-hh*2),
			bpnt = center+QPointF(-w,h-s*2-hh*2),
			offset = QPointF(0,-h*2+hh*2+s*2-16),
			textoff = QPointF(0, -7),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)

		else:
			paintool.draw_dimlines( # горизонтальная
				painter = painter,
				apnt = center+QPointF(w,h),
				bpnt = center+QPointF(-w,h),
				offset = QPointF(0,23),
				textoff = QPointF(0, -7),
				text = w_text,
				arrow_size = arrow_size / 3 * 2
			)


		paintool.draw_dimlines( # вертикальная отв.
			painter = painter,
			apnt = center+QPointF(hw,h-s*2-hh*2),
			bpnt = center+QPointF(hw,h-s*2),
			offset = QPointF(w-hw + 18,0),
			textoff = QPointF(10, 0),
			text = hh_text,
			arrow_size = arrow_size / 3 * 2
		)

		if self.edge.get() == "Низ":
			paintool.draw_dimlines( # горизонтальная отв.
				painter = painter,
				apnt = center+QPointF(hw,h),
				bpnt = center+QPointF(-hw,h),
				offset = QPointF(0,23),
				textoff = QPointF(0, -7),
				text = hw_text,
				arrow_size = arrow_size / 3 * 2
			)

		else:
			paintool.draw_dimlines( # горизонтальная отв.
				painter = painter,
				apnt = center+QPointF(hw,h-s*2-hh*2),
				bpnt = center+QPointF(-hw,h-s*2-hh*2),
				offset = QPointF(0,-h*2+hh*2+s*2-16),
				textoff = QPointF(0, -7),
				text = hw_text,
				arrow_size = arrow_size / 3 * 2
			)

		if s != (h-hh)/2 and not s_edge:
			paintool.draw_dimlines(
				painter = painter,
				apnt = center+QPointF(hw,h),
				bpnt = center+QPointF(hw,h-s*2),
				offset = QPointF(w-hw + 18,0),
				textoff = QPointF(10, 0),
				text = s_text,
				arrow_size = arrow_size / 3 * 2
			)

		painter.setPen(wdg.axpen)
		#llen = w + 10
		if s == (h-hh)/2 and not s_edge:
			painter.drawLine(center + QPointF(-w-10,0), center + QPointF(w+10,0))
		painter.drawLine(center + QPointF(0,-h-10), center + QPointF(0,h+10))
		
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
			"main_section_0": self.main_section_0.serialize(),
			"hrect": self.hrect.serialize()
		}


	def deserialize(self, dct):
		self.section_type.set(dct["section_type"])
		self.base_section_widget.deserialize(dct["base_section_widget"]) 
		self.rect_minus_rect.deserialize(dct["rect_minus_rect"])
		self.main_section_0.deserialize(dct["main_section_0"])
		
		if "hrect" in dct:
			self.hrect.deserialize(dct["hrect"])
	
	def __init__(self, checker):
		super().__init__()

		if checker is not None:
			self.checker = checker
			self.checker.element().updated.connect(self.section_enable_handle)
		self.base_section_widget = BaseSectionType() 
		self.base_section_widget.updated.connect(self.updated)

		self.rect_minus_rect = RectMinusRect() 
		self.none_section = NoneSection() 
		self.main_section_0 = MainSection0() 
		self.hrect = HRect() 
		self.rect_minus_rect.updated.connect(self.updated)
		self.main_section_0.updated.connect(self.updated)
		self.none_section.updated.connect(self.updated)
		self.hrect.updated.connect(self.updated)

		self.updated.connect(self.updated_selfhandle)
		self.container = self._SectionContainerWidget()
		self.section_type = self.add("Тип сечения:", "list", defval=0, variant=section_variant2)
		self.add_widget(self.container)
		self.container.replace(self.none_section)
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

		elif self.section_type.get() == "H - профиль":
			self.container.replace(self.hrect)	
			
		elif self.section_type.get() == "Нет":
			self.container.replace(self.none_section)		 

def draw_section(wdg, section_type, right, hcenter,
	arg0, arg1, arg2, txt0, txt1, txt2, arrow_size, painter=None
):
	self = wdg
	if painter is None:
		painter = self.painter
	painter.setFont(self.font)
	
	if section_type == "Тонкая труба":
		center = QPointF(right - 20 - 10 - arg0/2, hcenter)
		section_width = arg0 + 120
		dimlines_off = arg0 + 20
		painter.setPen(self.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		painter.drawEllipse(
			QRectF(center - QPointF(arg0,arg0), center + QPointF(arg0,arg0)))
		painter.setBrush(QBrush(Qt.white))
		painter.drawEllipse(
			QRectF(center - QPointF(arg1,arg1), center + QPointF(arg1,arg1)))
		painter.setBrush(QBrush(Qt.NoBrush))
		painter.setPen(self.axpen)
		painter.drawEllipse(
			QRectF(center - QPointF((arg1+arg0)/2,(arg0+arg1)/2), center + QPointF((arg1+arg0)/2,(arg0+arg1)/2)))
		painter.setPen(self.halfpen)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center-QPointF(0,(arg1+arg0)/2),
			bpnt = center+QPointF(0,(arg1+arg0)/2),
			offset = QPointF(-dimlines_off,0),
			textoff = QPointF(-10, 0) - QPointF(QFontMetrics(self.font).width(txt0)/2, 0),
			text = txt0,
			arrow_size = arrow_size / 3 * 2
		)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPointF(+ math.cos(math.pi/4) * arg1, + math.sin(math.pi/4) * arg1),
			bpnt = center+QPointF(+ math.cos(math.pi/4) * arg0, + math.sin(math.pi/4) * arg0),
			offset = QPointF(0,0),
			textoff = QPointF(+ math.cos(math.pi/4) * (arg0-arg1) + 15, + math.sin(math.pi/4) * (arg0-arg1)),
			text = txt1,
			arrow_size = arrow_size / 3 * 2,
			splashed=True,
			textline_from = "bpnt"
		)
		painter.setPen(self.axpen)
		llen = arg0 + 10
		painter.drawLine(center + QPointF(-llen,0), center + QPointF(llen,0))
		painter.drawLine(center + QPointF(0,-llen), center + QPointF(0,llen))

	elif section_type == "Треугольник":
		center = QPointF(right - 20 - 10 - arg0/2, hcenter)
		section_width = arg1 + 120
		painter.setPen(self.pen)
		painter.setBrush(QBrush(Qt.BDiagPattern))
		painter.drawPolygon(
			QPolygonF([
				center+QPointF(-arg1, arg0),
				center+QPointF(arg1, arg0),
				center+QPointF(0, -arg0),
			])
		)
		painter.setBrush(QBrush(Qt.white))

		painter.setPen(self.halfpen)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPointF(0,arg0),
			bpnt = center+QPointF(0,-arg0),
			offset = QPointF(-20-arg0,0),
			textoff = QPointF(-10, 0),
			text = txt0,
			arrow_size = arrow_size / 3 * 2
		)
		paintool.draw_dimlines(
			painter = painter,
			apnt = center+QPointF(arg1,arg0),
			bpnt = center+QPointF(-arg1,arg0),
			offset = QPointF(0,25),
			textoff = QPointF(0, -6),
			text = txt1,
			arrow_size = arrow_size / 3 * 2
		)
		painter.setPen(self.axpen)
		llen = arg0 + 10
		painter.drawLine(center + QPointF(-llen,-arg0+4/3*arg0), center + QPointF(llen,-arg0+4/3*arg0))
		painter.drawLine(center + QPointF(0,-llen), center + QPointF(0,llen))

	else:
		print("Unresolved section type:", section_type)
		exit(0)
	return section_width



def draw_section_routine(self, hcenter, right, painter=None):
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
			hcenter=hcenter,
			painter = painter
		)
		
	elif section_enable: # небазовый список
		section_width = self.shemetype.section_container.draw(
			wdg=self,
			shemetype=self.shemetype, 
			right=right, 
			hcenter=hcenter, 
			arrow_size=self.shemetype.arrow_size.get(),
			painter = painter)

	else:
		section_width = 0

	return section_width