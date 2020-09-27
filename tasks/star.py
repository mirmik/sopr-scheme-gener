import common
import paintwdg
import math

import tablewidget
import paintool
import taskconf_menu

import elements
import util
from paintool import deg

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ShemeTypeT1(common.SchemeType):
	def __init__(self):
		super().__init__("Стержневая система (Тип 2)")
		self.setwidgets(ConfWidget_T1(self), PaintWidget_T1(), common.TableWidget())

class ConfWidget_T1(common.ConfWidget):
	class sect:
		def __init__(self, l=1, A=1, angle=30, sharn="нет", insharn="шарн", body=True, force="нет", ftxt="", alttxt=False, addangle=0, start_from = -1, wide=False):
			self.start_from = start_from
			self.l = l
			self.A = A
			self.body = body
			self.sharn = sharn
			self.insharn = insharn
			self.force = force
			self.angle = angle
			self.ftxt = ftxt
			self.alttxt = alttxt
			self.addangle = addangle
			self.wide = wide
			
	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
				self.sect(l=1.5, angle=135),
				self.sect(l=1, angle=90),
				self.sect(l=1, angle=0, addangle=45),
				self.sect(l=1, angle=-90, body=False, force="к", ftxt="F")
			],
		}

	def hover_sect(self, row, column, hint):
		self.shemetype.paintwidget.highlited_sect = (hint, row)
		self.redraw()

		self.save_row = row
		self.save_hint = hint

	def table_unhover(self):
		self.shemetype.paintwidget.highlited_sect = None
		self.shemetype.paintwidget.highlited_node = None
		self.redraw()

	def update_interface(self):
		self.table = tablewidget.TableWidget(self.shemetype, "sections")
		self.table2 = tablewidget.TableWidget(self.shemetype, "sections")
		self.table.addColumn("start_from", "int", "ВыходитИз")
		self.table.addColumn("l", "float", "Длина")
		self.table.addColumn("angle", "float", "Угол")
		self.table.addColumn("wide", "bool", "Жесткий")
		self.table2.addColumn("body", "bool", "Стержень")
		self.table2.addColumn("force", "list", "Сила", variant=["нет", "к", "от", "вдоль"])
		self.table2.addColumn("ftxt", "str", "Сила")
		self.table2.addColumn("alttxt", "bool", "Пол.Ткст.")
		self.table2.addColumn("addangle", "float", "Доб.Угол")
		self.table2.addColumn("sharn", "list", "Шарн.", variant=["нет", "шарн", "шарн+заделка"])
		#self.table.addColumn("insharn", "list", "ВхШарн.", variant=["нет", "шарн"])
		self.table.updateTable()
		self.table2.updateTable()

		self.table.hover_hint.connect(self.hover_sect)
		self.table2.hover_hint.connect(self.hover_sect)
		self.table.unhover.connect(self.table_unhover)
		self.table2.unhover.connect(self.table_unhover)

		self.vlayout.addWidget(self.table)
		self.vlayout.addWidget(self.table2)
		self.vlayout.addWidget(self.sett)

		self.table.updated.connect(self.redraw)
		self.vlayout.addWidget(self.shemetype.texteditor)
		
	"""Виджет настроек задачи T0"""
	def __init__(self, sheme):
		super().__init__(sheme)
		self.sett = taskconf_menu.TaskConfMenu()
		#self.shemetype.first_dir = self.sett.add("Положение первого стержня (верт/гор):", "bool", True)
		self.shemetype.base_length = self.sett.add("Базовая длина:", "int", "80")
		self.shemetype.sharnrad = self.sett.add("Радиус шарнира:", "int", "4")
		self.sett.updated.connect(self.redraw)

		self.shemetype.font_size = common.CONFVIEW.font_size_getter
		self.shemetype.line_width = common.CONFVIEW.lwidth_getter

		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)
		
		self.update_interface()
		self.setLayout(self.vlayout)

	def add_action_impl(self):
		self.shemetype.task["sections"].append(self.sect())
		self.redraw()
		self.updateTables()

	def _add_action(self, strt, tgt, idx):
		#ssect = self.shemetype.task["sections"][hidx]
		
		xs = strt.x()
		ys = strt.y()
		xf = tgt.x()
		yf = tgt.y()
		ang = math.atan2(ys-yf, xf-xs)

		ang = ang * 180 / math.pi
		l = math.sqrt((xf-xs)**2 + (yf-ys)**2)

		ang = round((ang + 7.5) / 15) * 15
		l = round((l + 0.25) / 0.5) * 0.5

		print(ang, l)

		self.shemetype.task["sections"].append(
			self.sect(
				start_from=idx - 1,
				angle = ang,
				l = l
			)
		)
		self.redraw()
		self.updateTables()

	def insert_action_impl(self, idx):
		self.shemetype.task["sections"].insert(idx, self.sect())
		self.redraw()
		self.updateTables()

	def del_action_impl(self, idx):
		if len(self.shemetype.task["sections"]) == 0: return
		del self.shemetype.task["sections"][idx]

#		for s in self.shemetype.task["sections"]:
#			if s.start_from >= idx:
#				s.start_from -= 1

		self.redraw()
		self.updateTables()

	def inittask(self):
		#compat
		return {}

	def updateTables(self):
		self.table.updateTable()
		self.table2.updateTable()



class PaintWidget_T1(paintwdg.PaintWidget):
	def __init__(self):
		self.highlited_node=None
		self.highlited_sect=None
		self.grid_enabled = False

		self.hovered_point = None
		self.hovered_point_index = None
		self.target_point = QPointF(0,0)
		self.c = QPointF(0,0)
		self.mouse_pressed=False

		super().__init__()
		self.setMouseTracking(True)

	def make_off_lists(self):
		self._strt_list = []
		self._fini_list = []
		for i in range(len(self.shemetype.task["sections"])):
			sect =self.shemetype.task["sections"][i]

			if sect.start_from == -1:
				strt = QPointF(0,0)
			else:
				strt = self._fini_list[sect.start_from]

			self._fini_list.append(strt + QPointF(
				sect.l * math.cos(sect.angle / 180 * math.pi),
				sect.l * math.sin(sect.angle / 180 * math.pi)
			))

			self._strt_list.append(strt)

	def xoff(self, i):
		return self._strt_list[i].x()

	def yoff(self, i):
		return self._strt_list[i].y()

	def coordinate_of_start(self, i):
		xoff = self._strt_list[i].x() * self.base_length	
		yoff = - self._strt_list[i].y() * self.base_length

		return QPointF(xoff, yoff)

	def coordinate_of_finish(self, i):
		xoff = self._fini_list[i].x() * self.base_length	
		yoff = - self._fini_list[i].y() * self.base_length

		return QPointF(xoff, yoff)

	def paintEventImplementation(self, ev):
		sects = self.shemetype.task["sections"]

		#firstdir = self.shemetype.first_dir.get()
		#angle = deg(180) if firstdir else deg(90)
		sharnrad = self.shemetype.sharnrad.get()

		width = self.width()
		height = self.height()

		font_size = self.shemetype.font_size.get()
		lwidth = self.shemetype.line_width.get()

		base_length = self.shemetype.base_length.get()
		self.base_length = base_length
		
		# Расчитываем центр.
		xmin, ymin = 0, 0
		xmax, ymax = 0, 0

		self.make_off_lists()

		for i in range(len(sects)):
			length=0
			sect = self.sections()[i]
			if sects[i].body == True:
				length = sect.l

			elif sects[i].body == False and (sects[i].force == "к" or sects[i].force == "от"):
				length = 40 / base_length			

			elif sects[i].body == False and (sects[i].force == "нет" or sects[i].force == "вдоль"):
				continue

			angle = deg(sect.angle)

			point = (
				math.cos(angle) * (length)  + self.xoff(i),
				math.sin(angle) * (length) + self.yoff(i),
			)

			xmin, xmax = min(xmin, point[0]) , max(xmax, point[0])
			ymin, ymax = min(ymin, point[1]) , max(ymax, point[1])

		center = QPointF(width/2, self.hcenter) + \
			QPointF(-(xmax + xmin)* base_length, (ymax + ymin)* base_length)/2
		self.c = center

		def get_coord(i):
			sect = self.sections()[i]
			angle=sect.angle
			length = sect.l * base_length			
			strt = center + QPointF(base_length * self.xoff(i), base_length * self.yoff(i))
			pnt = strt + QPoint(math.cos(angle) * length, -math.sin(angle) * length)
			return pnt

		def hasnode(pnt):
			jpnt = center
			diff = math.sqrt((pnt.x()-jpnt.x())**2 + (pnt.y()-jpnt.y())**2)
			if diff < 0.1:
				return True
			
			for i in range(len(self.sections())):
				if self.sections()[i].body==False or self.sections()[i].sharn=="нет":
					continue
				jpnt = get_coord(i)
				diff = math.sqrt((pnt.x()-jpnt.x())**2 + (pnt.y()-jpnt.y())**2)
				if diff < 0.1: 
					return True

			return False


		rad = 50
		rad2 = 60
		rad3 = 70
			
		# Рисуем доб угол
		for i in range(len(sects)):
			sect = self.sections()[i]
			angle = sects[i].angle
			#strt = center + QPointF(base_length * sect.xoff, base_length * sect.yoff)
			strt = self.get_node_coordinate(sect.start_from)

			if sect.addangle != 0:
				tgtangle = sect.angle + sect.addangle

				if self.highlited_sect is not None and self.highlited_sect[1] == i:
					pen = self.dashgreen
				else:
					pen = QPen(Qt.DashDotLine)
		
				pen.setWidth(2)
				self.painter.setPen(pen)

				pnt1 = strt + rad2 * QPointF(math.cos(deg(angle)), -math.sin(deg(angle)))
				pnt2 = strt + rad2 * QPointF(math.cos(deg(tgtangle)), -math.sin(deg(tgtangle)))
				cpnt = strt + rad3 * QPointF(math.cos(deg(tgtangle+angle)/2), -math.sin(deg(tgtangle+angle)/2))

				self.painter.drawLine(strt, pnt1)
				self.painter.drawLine(strt, pnt2)


				if self.highlited_sect is not None and self.highlited_sect[1] == i:
					pen = self.halfgreen
				else:
					pen = self.halfpen

				self.painter.setPen(pen)
				self.painter.drawArc(paintool.radrect(strt, rad), 
					angle*16, 
					sect.addangle*16)

				paintool.draw_text_centered(
					painter=self.painter, 
					pnt=cpnt + QPointF(0,QFontMetrics(self.font).height()/4), 
					text=paintool.greek(str(abs(sect.addangle))+"\\degree"), 
					font=self.font)


		# Рисуем тело
		for i in range(len(sects)):
			sect = self.sections()[i]
			angle = deg(sect.angle)
			self.painter.setPen(self.pen)

			if self.highlited_sect is not None and self.highlited_sect[1] == i:
				self.painter.setPen(self.widegreen)
			else:
				self.painter.setPen(self.doublepen)

			if sect.body:
				length = sect.l * base_length	
				strt = self.c + self.coordinate_of_start(i) 
				
				if hasnode(strt):
					spnt = strt + QPoint(math.cos(angle) * 7, -math.sin(angle) * 7)
				else:
					spnt = strt

				pnt = self.c + self.coordinate_of_finish(i)
				
				if not sect.wide:
					self.painter.drawLine(strt, pnt)
				else:
					self.painter.drawLine(strt, pnt)
					self.painter.drawLine(strt + QPointF(0,8), pnt + QPointF(0,8))
					self.painter.drawLine(strt, strt + QPointF(0,8))
					self.painter.drawLine(pnt, pnt + QPointF(0,8))
					
				
				if self.highlited_sect is not None and self.highlited_sect[1] == i:
					self.painter.setPen(self.green)
				else:
					self.painter.setPen(self.pen)

				self.painter.setBrush(Qt.white)
				if sect.sharn=="шарн+заделка":
					paintool.zadelka_sharnir(self.painter, pnt, -angle, 30, 10, sharnrad)
				elif sect.sharn=="шарн":
					self.painter.setBrush(Qt.white)
					self.painter.drawEllipse(paintool.radrect(pnt,sharnrad))

				if sect.start_from != -1:
					if  self.sections()[sect.start_from].sharn != "нет":
						self.painter.drawEllipse(paintool.radrect(strt,sharnrad))						

				ltxt = util.text_prepare_ltext(sect.l, suffix="l")
				Atxt = util.text_prepare_ltext(sect.A, suffix="A")
				txt = "{},{},E".format(ltxt,Atxt)

				elements.draw_text_by_points_angled(self, strt, pnt, off=14, txt=txt, alttxt=sect.alttxt)

			self.painter.setPen(self.default_pen)

		# риуем силы
		for i in range(len(sects)):
			sect = self.sections()[i]
			angle = deg(sect.angle)
			rad = 50
			circrad = 0		
		
			strt = self.c + self.coordinate_of_start(i)

			for j in range(len(sects)):
				jsect = self.sections()[j]
				#length = jsect.l * base_length		
				#pnt = strt + QPoint(math.cos(jsect.angle) * length, -math.sin(jsect.angle) * length)
				
				if hasnode(strt):
					circrad = 6
					break
				else:
					circrad = 0

			if self.highlited_sect is not None and self.highlited_sect[1] == i:
				self.painter.setPen(self.green)
				self.painter.setBrush(Qt.green)
				pen = self.green
				brush = Qt.green
			else:
				self.painter.setPen(self.pen)
				self.painter.setBrush(Qt.black)
				pen = None
				brush = Qt.black
			
			if sect.force != "нет":
				apnt = strt + QPointF(math.cos(angle) * circrad, - math.sin(angle) * circrad)
				bpnt = strt + QPointF(math.cos(angle) * rad, - math.sin(angle) * rad)
				cpnt = strt + QPointF(math.cos(angle) * rad/2, - math.sin(angle) * rad/2)

				if sect.force == "к":
					paintool.common_arrow(
						self.painter, 
						bpnt,
						apnt, 
						arrow_size=15,
						pen=pen, brush=brush)	
				elif sect.force == "от":
					paintool.common_arrow(
						self.painter, 
						apnt, 
						bpnt,
						arrow_size=15,
						pen=pen, brush=brush)	
				elif sect.force == "вдоль":
					rad = 20
					vec = QPointF(math.cos(angle) * rad, - math.sin(angle) * rad)
					norm = QPointF(vec.y(), -vec.x())

					apnt1 = strt + norm
					bpnt1 = strt - norm
					apnt2 = strt + norm + vec
					bpnt2 = strt - norm + vec
					cpnt1 = strt 
					cpnt2 = strt + vec
					
					paintool.common_arrow(
						self.painter, 
						apnt1, 
						apnt2,
						arrow_size=10)	
					paintool.common_arrow(
						self.painter, 
						bpnt1, 
						bpnt2,
						arrow_size=10,
						pen=pen, brush=brush)	

					self.painter.drawLine(apnt1, bpnt1)


				if sect.force != "вдоль":
					elements.draw_text_by_points(
						self, 
						cpnt, 
						bpnt, 
						paintool.greek(sect.ftxt), 
						alttxt=sect.alttxt, 
						off=12, 
						polka=None)

				else:
					elements.draw_text_by_points(
						self, 
						cpnt1, 
						cpnt2, 
						paintool.greek(sect.ftxt), 
						alttxt=sect.alttxt, 
						off=12 + 15, 
						polka=None)

		self.c = center

		self.painter.setPen(self.pen)
		self.painter.setBrush(Qt.white)
		self.painter.drawEllipse(QRectF(center - QPointF(sharnrad, sharnrad), center + QPointF(sharnrad, sharnrad)))

		if self.grid_enabled:
			self.painter.setPen(self.pen)
			self.painter.setBrush(Qt.green)
			#self.painter.drawEllipse(QRect(center - QPoint(5, 5), center + QPoint(5, 5)))
				
			#for i in range(len(self.shemetype.task["sections"])):
			
			print("grid_enabled")

			if self.mouse_pressed:
				i = self.pressed_point_index

			else: 
				i = self.hovered_point_index
				
			if i is not None:
				if i > 0 and sects[i-1].body:
					self.painter.drawEllipse(QRectF(
						- QPointF(5, 5) + self.nodes_numered()[i], 
						+ QPointF(5, 5) + self.nodes_numered()[i]))
				if i == 0:
					self.painter.drawEllipse(QRectF(
						- QPointF(5, 5) + self.nodes_numered()[0], 
						+ QPointF(5, 5) + self.nodes_numered()[0]))
					

			self.painter.setPen(self.pen)
			self.painter.setBrush(Qt.white)

		if self.mouse_pressed:
			strt = self.nodes_numered()[self.pressed_point_index]
			tgt = self.target_point

			xs = strt.x()
			ys = strt.y()
			xf = tgt.x()
			yf = tgt.y()
			ang = math.atan2(ys-yf, xf-xs)

			ang = ang * 180 / math.pi
			l = math.sqrt((xf-xs)**2 + (yf-ys)**2) / self.base_length

			ang = round((ang + 7.5) / 15) * 15
			l = round((l + 0.25) / 0.5) * 0.5

			angtxt=ang
			ang = ang * math.pi / 180
			ltxt = str(l)
			l = l * self.base_length

			if self.pressed_point_index <= len(self.shemetype.task["sections"]): 
				fini = strt + QPointF(
						math.cos(ang) * l,
						-math.sin(ang) * l
					) 
				self.painter.drawLine(
					strt,
					fini					
				)
				elements.draw_text_by_points_angled(self, 
					strt, 
					fini, 
					off=14, 
					txt=ltxt + "l", 
					alttxt=False)

				self.painter.drawArc(paintool.radrect(strt, rad), 
					0*16, 
					angtxt*16)

				pnt1 = strt + rad2 * QPointF(math.cos(deg(0)), -math.sin(deg(0)))
				pnt2 = strt + rad2 * QPointF(math.cos(deg(angtxt)), -math.sin(deg(angtxt)))
				cpnt = strt + rad3 * QPointF(math.cos(deg(angtxt)/2), -math.sin(deg(angtxt)/2))

				paintool.draw_text_centered(
					painter=self.painter, 
					pnt=cpnt + QPointF(0,QFontMetrics(self.font).height()/4), 
					text=paintool.greek(str(abs(angtxt))+"\\degree"), 
					font=self.font)


	def nodes_numered(self):
		lst = [self.c]
		for i in range(len(self.shemetype.task["sections"])):
			lst.append(self.c + self.coordinate_of_finish(i))
		return lst

	def get_node_coordinate(self, i):
		return self.nodes_numered()[i+1]

	def enterEvent(self, ev):
		self.grid_enabled = True
		self.update()

	def leaveEvent(self, ev):
		self.grid_enabled = False
		self.update()

	def mouseMoveEvent(self, ev):
		pos = ev.pos()
		old_hovered_point = self.hovered_point

		if pos.x() < 10 or self.width() - pos.x() < 10: 
			self.inramka = True
			return
		
		if pos.y() < 10 or self.height() - pos.y() < 10: 
			self.inramka = True
			return

		self.inramka = False

		t = None
		idx = -1
		mindist = 10000000  
		for i in range(len(self.nodes_numered())):
			s = self.nodes_numered()[i]


			if i != 0:
				if not self.shemetype.task["sections"][i-1].body:
					continue

			xdiff = s.x() - pos.x()
			ydiff = s.y() - pos.y()
			dist = math.sqrt(xdiff**2 + ydiff**2)
			if dist < mindist:
				mindist = dist
				t = s
				idx = i
		self.hovered_point = t
		self.hovered_point_index = idx

		self.target_point = QPointF(pos.x(), pos.y())

		self.update()

	def mousePressEvent(self, ev):
		self.mouse_pressed=True
		self.pressed_point = self.hovered_point
		self.pressed_point_index = self.hovered_point_index

	def mouseReleaseEvent(self, ev):
		self.mouse_pressed=False

		if self.inramka:
			return

		if self.pressed_point is not None:
			self.shemetype.confwidget._add_action(
				(self.nodes_numered()[self.pressed_point_index] - self.c)/ self.base_length, 
				(self.target_point - self.c) / self.base_length,
				self.pressed_point_index)


#		self.release_point = self.hovered_point

#		if self.pressed_point != self.release_point:
#			if len(self.shemetype.confwidget.sections()) == 0:
#				self.hovered_point_index = (self.hovered_point_index[0] - self.pressed_point_index[0], self.hovered_point_index[1]-self.pressed_point_index[1]) 
#				self.pressed_point_index = (0,0)

#			self.pressed_point_index = (round(self.pressed_point_index[0]), round(self.pressed_point_index[1]))
#			self.hovered_point_index = (round(self.hovered_point_index[0]), round(self.hovered_point_index[1]))
			
#			self.shemetype.confwidget._add_action(self.pressed_point_index,self.hovered_point_index)

		self.update()
