#!/usr/bin/env python3

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
import argparse

import task0
import common

QAPP = None

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
			common.SchemeType("Задача тип 0", 
				task0.ConfWidget_T0(), task0.PaintWidget_T0(), common.TableWidget()),
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
		#self.type_list_widget.setEditable(True)

		self.type_list_widget.activated.connect(self.type_scheme_selected)

		self.hsplitter = QSplitter(Qt.Horizontal)
		self.vsplitter = QSplitter(Qt.Vertical)
		self.confview = common.ConfView()
		common.HSPLITTER = self.hsplitter
		common.CONFVIEW = self.confview

		self.vlayout = QVBoxLayout()
		self.vlayout.addWidget(self.type_list_widget)
		self.vlayout.addWidget(self.vsplitter)
		self.set_scheme_type_no(-1)

		if tp != -1:
			self.inited = False
			self.tp = tp
		else:
			self.inited = True

		self.setLayout(self.vlayout)

	def set_scheme_type_no(self, no):    
		if no == -1:
			self.currentno = -1
			self.hsplitter.addWidget(self.stub_widget_0)
			self.hsplitter.addWidget(self.stub_widget_1)
			self.vsplitter.addWidget(self.hsplitter)
			self.vsplitter.addWidget(self.stub_widget_2)
			self.vsplitter.addWidget(self.confview)

		else:
			if self.currentno != no:
				common.SCHEMETYPE = self.scheme_types[no]
				self.hsplitter.replaceWidget(0, self.scheme_types[no].paintwidget)
				self.hsplitter.replaceWidget(1, self.scheme_types[no].tablewidget)
				self.vsplitter.replaceWidget(1, self.scheme_types[no].confwidget)
			self.currentno = no
			
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
				"<p>Данная программа составляет схемы типовых задач по дисциплине 'Сопротивление материалов'."
				"<p><h3>Обратная связь</h3>"
				"<pre>Страница проекта:\n"
				"github: https://github.com/mirmik/sopr-scheme-gener\n"
				"\n"
				"Багрепорты, замечания и предложения по программе также отсылать на\n"
				"email: mirmikns@yandex.ru\n"
				"\n"
				"Таймштамп: 04.2019<pre/>"
			),
		)


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
		self.ExitAction = self.create_action("Выход", self.close, "Выход", "Ctrl+Q")
		self.AboutAction = self.create_action("О программе", self.action_about, "Информация о приложении")

	def createMenus(self):
		self.FileMenu = self.menuBar().addMenu(self.tr("&File"))   
		self.HelpMenu = self.menuBar().addMenu(self.tr("&Help"))       
		
		self.FileMenu.addAction(self.ExitAction)
		self.HelpMenu.addAction(self.AboutAction)

parser = argparse.ArgumentParser()
parser.add_argument("--type", default="-1")
pargs = parser.parse_args()

qapp = QApplication(sys.argv[1:])
qapp.setApplicationName("sopr-sheme-gener")

QAPP = qapp

mainwindow = MainWindow(int(pargs.type))
mainwindow.resize(800, 640)
mainwindow.show()

qapp.exec()