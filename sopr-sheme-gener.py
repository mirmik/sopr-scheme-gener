#!/usr/bin/env python3

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
import sys
import argparse

import task0
import task1
import common
import container
import paintwdg

QAPP = None

def getPaintSize():
	return (common.datasettings.width, common.datasettings.height)

class ComboBox(QComboBox):
	def __init__(self, default):
		QComboBox.__init__(self)
		self.inited = False
		self.default = default

	def paintEvent(self, evt):
		painter = QStylePainter(self)
		painter.setPen(self.palette().color(QPalette.Text))
		option = QStyleOptionComboBox()
		self.initStyleOption(option)
		painter.drawComplexControl(QStyle.CC_ComboBox, option)

		if self.inited is False:
			option.currentText = self.default
		
		painter.drawControl(QStyle.CE_ComboBoxLabel, option)

class CentralWidget(QWidget):
	def __init__(self, tp):
		super().__init__()

		self.scheme_types = [
			task0.ShemeTypeT0(),
			task1.ShemeTypeT1(),

			#SchemeType("Проверка функциональности1", ConfWidget_Stub(), PaintWidget_T0(), TableWidget())
		]

		self.stub_widget_0 = common.StubWidget("Окно отображения")
		self.stub_widget_1 = common.StubWidget("Таблица параметров")
		self.stub_widget_2 = common.StubWidget("Окно конфигурации")

		self.stub_widget_0.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.stub_widget_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.stub_widget_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		self.type_list_widget = ComboBox("Выберите тип задачи") 
		self.type_list_widget.addItems([x.name for x in self.scheme_types])
		self.type_list_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

		self.type_list_widget.activated.connect(self.type_scheme_selected)

		self.hsplitter = QSplitter(Qt.Horizontal)
		#self.vsplitter = QSplitter(Qt.Vertical)
		self.confview = common.ConfView()

		common.HSPLITTER = self.hsplitter
		common.CONFVIEW = self.confview

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.hsplitter)
		#self.hlayout = QHBoxLayout()
		#self.layout.addLayout(self.hlayout)

		self.container_paint = container.ContainerWidget(border=True, fixedSize=True, filter=True)
		self.container_settings = container.ContainerWidget(border=False, fixedSize=False, filter=False)
		
		self.settings_layout = QVBoxLayout()
		self.settings_layout.addWidget(self.type_list_widget)
		self.settings_layout.addWidget(self.confview)
		self.settings_layout.addWidget(self.container_settings)
		self.settings_layout.addStretch()
		self.settings_layout_wdg = QWidget()
		self.settings_layout_wdg.setLayout(self.settings_layout)
		self.settings_layout_wdg.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

		self.work_layout = QVBoxLayout()
		self.work_layout.addWidget(paintwdg.PaintWidgetSetter(self.container_paint))
		self.work_layout_wdg = QWidget()
		self.work_layout_wdg.setLayout(self.work_layout)

		#self.hlayout.addWidget(self.settings_layout_wdg)
		#self.hlayout.addWidget(self.work_layout_wdg)
		self.hsplitter.addWidget(self.settings_layout_wdg)
		self.hsplitter.addWidget(self.work_layout_wdg)
		self.hsplitter.setStretchFactor(0, 0)
		self.hsplitter.setStretchFactor(1, 1)

		common.PAINT_CONTAINER = self.container_paint
		self.container_paint.setFixedSize(*getPaintSize())

		#self.vlayout = QVBoxLayout()
		#self.vlayout.addWidget(self.type_list_widget)
		#self.vlayout.addWidget(self.vsplitter)
		
		self.set_scheme_type_no(-1)

		if tp != -1:
			self.inited = False
			self.tp = tp
		else:
			self.inited = True

		self.setLayout(self.layout)

	def current_scheme(self):
		return self.scheme_types[self.currentno]

	def set_scheme_type_no(self, no):    
		if no == -1:
			self.currentno = -1
			self.container_paint.replace(self.stub_widget_0)
			self.container_settings.replace(self.stub_widget_1)

		#	self.hsplitter.addWidget(self.stub_widget_0)
		#	self.hsplitter.addWidget(self.stub_widget_1)
		#	self.vsplitter.addWidget(self.hsplitter)
		#	self.vsplitter.addWidget(self.stub_widget_2)
		#	self.vsplitter.addWidget(self.confview)

		else:
			if self.currentno != no:
				common.SCHEMETYPE = self.scheme_types[no]
		#		self.hsplitter.replaceWidget(0, self.scheme_types[no].paintwidget)
		#		self.hsplitter.replaceWidget(1, self.scheme_types[no].tablewidget)
		#		self.vsplitter.replaceWidget(1, self.scheme_types[no].confwidget)
				self.container_settings.replace(self.scheme_types[no].confwidget)
				self.container_paint.replace(self.scheme_types[no].paintwidget)
			
			self.currentno = no
			common.PAINT_CONTAINER.resize(*getPaintSize())
			
	def type_scheme_selected(self, arg):
		self.type_list_widget.inited = True
		self.set_scheme_type_no(arg)

	def showEvent(self, ev):
		super().showEvent(ev)
		if self.inited == False:
			self.inited = True
			self.type_scheme_selected(self.tp)

class MainWindow(QMainWindow):
	def __init__(self, tp):
		super().__init__()

		self.createActions()
		self.createMenus()

		self.cw = CentralWidget(tp)
		self.setCentralWidget(self.cw)

	def action_about(self):
		QMessageBox.about(
			self,
			self.tr("О программе"),
			(
				"<p><h3>Что это?</h3>"
				"<p>Программа предназначена для составления рисунков к типовым задачам" 
				"<br>по дисциплине 'Сопротивление материалов'."
				"<p><h3>Исходный код</h3>"
				"github: https://github.com/mirmik/sopr-scheme-gener\n"				
				"<p><h3>Обратная связь</h3>"
				"Багрепорты, замечания и предложения по программе можно отсылать на\n"
				"<br>email: mirmikns@yandex.ru"
				"<br>github: https://github.com/mirmik/sopr-scheme-gener/issues"
				"<p>Таймштамп: 07.2019<pre/>"
			),
		)

	def make_picture_action(self):
		filters = "*.png;;*.jpg;;*.*"
		defaultFilter = "*.png"

		path, ext = QFileDialog.getSaveFileName(
			self, "Сохранить изображение", None, filters, defaultFilter
		)

		if not path:
			return

		ext = os.path.splitext(ext)[1]
		if ext == '.*':
			ext = ".png"

		curext = os.path.splitext(path)[1]
		if curext == '':
			path = path + ext

		self.cw.current_scheme().paintwidget.save_image(path)

	def pre_picture_action(self):
		self.cw.current_scheme().paintwidget.predraw_dialog()

	def create_action(self, text, action, tip, shortcut=None, checkbox=False):
		act = QAction(self.tr(text), self)
		act.setStatusTip(self.tr(tip))

		if shortcut is not None:
			act.setShortcut(self.tr(shortcut))

		if not checkbox:
			act.triggered.connect(action)
		else:
			act.setCheckable(True)
			act.toggled.connect(action)

		return act

	def createActions(self):
		self.MakePictureAction = self.create_action("Сохранить изображение...", self.make_picture_action, "Сохранение изображение")
		self.PrePictureAction = self.create_action("Показать изображение...", self.pre_picture_action, "Показать изображение")
		self.ExitAction = self.create_action("Выход", self.close, "Выход", "Ctrl+Q")
		self.AboutAction = self.create_action("О программе", self.action_about, "Информация о приложении")

	def createMenus(self):
		self.FileMenu = self.menuBar().addMenu(self.tr("&File"))   
		self.HelpMenu = self.menuBar().addMenu(self.tr("&Help"))       
		
		self.FileMenu.addAction(self.MakePictureAction)
		self.FileMenu.addAction(self.PrePictureAction)
		self.FileMenu.addAction(self.ExitAction)
		self.HelpMenu.addAction(self.AboutAction)

parser = argparse.ArgumentParser()
parser.add_argument("--type", default="-1")
pargs = parser.parse_args()

qapp = QApplication(sys.argv[1:])
qapp.setApplicationName("sopr-sheme-gener")

QAPP = qapp
common.APP = qapp

mainwindow = MainWindow(int(pargs.type))
mainwindow.resize(800, 640)
mainwindow.show()

qapp.exec()