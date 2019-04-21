#!/usr/bin/env python3

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys

QAPP = None

class SchemeType:
	def __init__(self, name, confwidget, paintwidget, tablewidget):
		self.name = name
		self.paintwidget = paintwidget
		self.confwidget = confwidget
		self.tablewidget = tablewidget

		self.confwidget.set_paint_widget(self.paintwidget)
		self.confwidget.set_table_widget(self.tablewidget)

class StyleWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.setStyleSheet("border: 1px solid black");
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class StubWidget(StyleWidget):
	def __init__(self, text):
		super().__init__()
		self.text = text
		self.layout = QVBoxLayout()
		self.label = QLabel(text)
		self.layout.addWidget(self.label)
		self.setLayout(self.layout)

class TableWidget(StyleWidget):
	def __init__(self):
		super().__init__()

class PaintWidget(StyleWidget):
	def __init__(self):
		super().__init__()

class ConfWidget_Stub(StyleWidget):
	def __init__(self):
		super().__init__()
		self.text = "STUB"
		self.layout = QVBoxLayout()
		self.label = QLabel(self.text)
		self.layout.addWidget(self.label)
		self.setLayout(self.layout)

	def set_paint_widget(self, paintwidget):
		self.paintwidget = paintwidget

	def set_table_widget(self, tablewidget):
		self.tablewidget = tablewidget

class ConfWidget_Task1(StyleWidget):
	def __init__(self):
		super().__init__()

	def set_paint_widget(self, paintwidget):
		self.paintwidget = paintwidget

	def set_table_widget(self, tablewidget):
		self.tablewidget = tablewidget

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
	def __init__(self):
		super().__init__()

		self.scheme_types = [
			SchemeType("Проверка функциональности", ConfWidget_Task1(), PaintWidget(), TableWidget()),
			SchemeType("Проверка функциональности1", ConfWidget_Stub(), PaintWidget(), TableWidget())
		]

		self.stub_widget_0 = StubWidget("Окно отображения")
		self.stub_widget_1 = StubWidget("Таблица параметров")
		self.stub_widget_2 = StubWidget(
			"Окно конфигурации"
		)
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

		self.vlayout = QVBoxLayout()
		self.vlayout.addWidget(self.type_list_widget)
		self.vlayout.addWidget(self.vsplitter)
		self.set_scheme_type_no(-1)

		self.setLayout(self.vlayout)

	def set_scheme_type_no(self, no):    
		if no == -1:
			self.currentno = -1
			self.hsplitter.addWidget(self.stub_widget_0)
			self.hsplitter.addWidget(self.stub_widget_1)
			self.vsplitter.addWidget(self.hsplitter)
			self.vsplitter.addWidget(self.stub_widget_2)

		else:
			if self.currentno != no:
				self.hsplitter.replaceWidget(0, self.scheme_types[no].paintwidget)
				self.hsplitter.replaceWidget(1, self.scheme_types[no].tablewidget)
				self.vsplitter.replaceWidget(1, self.scheme_types[no].confwidget)
			self.currentno = no
			
	def type_scheme_selected(self, arg):
		self.type_list_widget.inited = True
		self.set_scheme_type_no(arg)

	#def paintEvent(self, ev):
		#self.type_list_widget.lineEdit().setPlaceholderText("A")
		#self.type_list_widget.update()

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.createActions()
		self.createMenus()

		self.cw = CentralWidget()
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

qapp = QApplication(sys.argv[1:])
QAPP = qapp

mainwindow = MainWindow()
mainwindow.resize(800, 640)
mainwindow.show()

qapp.exec()