#!/usr/bin/env python3

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
import sys
import argparse
import pickle

import collections

import util

import tasks.task0
import tasks.star
import tasks.sharn_sterhen
import tasks.star
import tasks.plastina
import tasks.fermes
import tasks.balki
import tasks.ar3d
import tasks.ar3d2
import tasks.kosoi
import common
import container
import paintwdg
import paintool

QAPP = None

def getPaintSize():
	return common.SCHEMETYPE.get_size()

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

		self.confview = common.ConfView()
		common.CONFVIEW = self.confview

		self.scheme_types = [
			tasks.task0.ShemeTypeT0(),
			#task0kr.ShemeTypeT01(),
			tasks.balki.ShemeType(),
			tasks.sharn_sterhen.ShemeTypeT2(),
			tasks.star.ShemeTypeT1(),
			tasks.plastina.ShemeTypeT3(),
			tasks.fermes.ShemeTypeT4(),
			tasks.ar3d.ShemeType(),
			tasks.ar3d2.ShemeType(),
			tasks.kosoi.ShemeType(),

			#SchemeType("Проверка функциональности1", ConfWidget_Stub(), PaintWidget_T0(), TableWidget())
		]

		for s in self.scheme_types:
			if hasattr(s.confwidget, "serialize_list") is False:
				util.msgbox_error("Confwidget without serialize_list : " + s.name)


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

		common.HSPLITTER = self.hsplitter

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.hsplitter)

		self.container_paint = container.ContainerWidget(border=True, fixedSize=True, filter=True)
		self.container_settings = container.ContainerWidget(border=False, fixedSize=False, filter=False)

		self.settings_layout = QVBoxLayout()
		self.settings_layout.addWidget(self.type_list_widget)
		self.settings_layout.addWidget(self.confview)
		self.settings_layout.addWidget(self.container_settings)
		self.settings_layout.addStretch()

		self.settings_layout_wdg_scr = QScrollArea()
		self.settings_layout_wdg = QWidget()
		self.settings_layout_wdg.setLayout(self.settings_layout)
		self.settings_layout_wdg.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
		self.settings_layout_wdg_scr.setWidget(self.settings_layout_wdg)
		self.settings_layout_wdg_scr.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
		self.settings_layout_wdg_scr.setVerticalScrollBarPolicy( Qt.ScrollBarAsNeeded)
		self.settings_layout_wdg_scr.setWidgetResizable( True )
		self.settings_layout_wdg = self.settings_layout_wdg_scr

		self.work_layout = QVBoxLayout()
		self.work_layout.addWidget(paintwdg.PaintWidgetSetter(self.container_paint))
		self.work_layout_wdg = QWidget()
		self.work_layout_wdg.setLayout(self.work_layout)

		self.hsplitter.addWidget(self.settings_layout_wdg)
		self.hsplitter.addWidget(self.work_layout_wdg)
		self.hsplitter.setStretchFactor(0, 150)
		self.hsplitter.setStretchFactor(1, 100)

		common.PAINT_CONTAINER = self.container_paint
		self.container_paint.setFixedSize(600,400)

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

		else:
			if self.currentno != no:
				common.SCHEMETYPE = self.scheme_types[no]
				self.container_settings.replace(self.scheme_types[no].confwidget)
				self.container_paint.replace(self.scheme_types[no].paintwidget)
			
			self.currentno = no
			common.SCHEMETYPE = self.scheme_types[no]
			common.PAINT_CONTAINER.resize(*getPaintSize())

		self.type_list_widget.setCurrentIndex(no)
		self.type_list_widget.update()
			
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

	def save_last_dirpath(self, lastdir):
		settings = QSettings("sopr-scheme-gener", "sopr-scheme-gener")
		settings.setValue("lastdir", lastdir)

	def get_last_dirpath(self):
		settings = QSettings("sopr-scheme-gener", "sopr-scheme-gener")
		return settings.value("lastdir", None)

	def make_picture_action(self):
		filters = "*.png;;*.jpg;;*.*"
		defaultFilter = "*.png"

		path, ext = QFileDialog.getSaveFileName(
			self, "Сохранить изображение", 
			self.get_last_dirpath(), filters, defaultFilter
		)

		if not path:
			return

		ext = os.path.splitext(ext)[1]
		if ext == '.*':
			ext = ".jpg"

		curext = os.path.splitext(path)[1]
		if curext == '':
			path = path + ext

		dir = os.path.dirname(path)
		self.save_last_dirpath(dir)

		savepath = os.path.join(dir, ".save")
		if not os.path.exists(savepath):
			os.mkdir(savepath)

		marchpath = os.path.join(savepath, os.path.basename(path) + ".dat")
		self.cw.current_scheme().serialize(marchpath)

		try:
			self.cw.current_scheme().paintwidget.save_image(path)
		except Exception as ex:
			util.msgbox_error(str(ex))


	def load_action(self):
		filters = "*.png;;*.jpg;;*.*"
		defaultFilter = "*.png"

		path, ext = QFileDialog.getOpenFileName(
			self, "Загрузить схему", 
			self.get_last_dirpath(), filters, defaultFilter
		)

		if not path:
			return

		ext = os.path.splitext(ext)[1]
		if ext == '.*':
			ext = ".jpg"

		curext = os.path.splitext(path)[1]
		if curext == '':
			path = path + ext

		dir = os.path.dirname(path)
		self.save_last_dirpath(dir)

		savepath = os.path.join(dir, ".save")

		marchpath = os.path.join(savepath, os.path.basename(path) + ".dat")
		lll = None
		try:
			lll = pickle.load(open(marchpath, "rb"))
		except FileNotFoundError as ex:
			util.msgbox_error(str(ex))


		name = lll[0][1]

		if lll[0][0] != "name":
			util.msgbox_error("wrong name field")
			return

		for i in range(len(self.cw.scheme_types)):
			if self.cw.scheme_types[i].name == name:
				self.cw.set_scheme_type_no(i)

		self.cw.current_scheme().deserialize(lll)

	def pre_picture_action(self):
		self.cw.current_scheme().paintwidget.predraw_dialog()

	def greek_action(self):
		txt = ""
		
		tbl = collections.OrderedDict()
		for t in paintool.greek_data:
			if t[1] in tbl:
				tbl[t[1]][t[0]]= t[0]
			else:
				tbl[t[1]] = collections.OrderedDict()
				tbl[t[1]][t[0]] = t[0]

		for k, v in tbl.items():
			kkk = ""
			for l in v.keys():
				kkk += "{} ".format(l)
			txt += "{} : {}\r\n".format(k, kkk) 
		
		QMessageBox.about(
			self,
			self.tr("Справка по греческому алфавиту"),
			(
				txt
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
		self.MakePictureAction = self.create_action("Сохранить изображение/схему...", self.make_picture_action, "Сохранение изображение/схему")
		self.LoadAction = self.create_action("Загрузить схему...", self.load_action, "Загрузить схему")
		self.PrePictureAction = self.create_action("Показать изображение...", self.pre_picture_action, "Показать изображение")
		self.GreekAction = self.create_action("Греческий и спецсимволы", self.greek_action, "Показать справку по греческому алфавиту и спецсимволам")
		self.ExitAction = self.create_action("Выход", self.close, "Выход", "Ctrl+Q")
		self.AboutAction = self.create_action("О программе", self.action_about, "Информация о приложении")

	def createMenus(self):
		self.FileMenu = self.menuBar().addMenu(self.tr("&File"))   
		self.HelpMenu = self.menuBar().addMenu(self.tr("&Help"))       
		
		self.FileMenu.addAction(self.MakePictureAction)
		self.FileMenu.addAction(self.LoadAction)
		self.FileMenu.addAction(self.PrePictureAction)
		self.FileMenu.addAction(self.ExitAction)
		self.HelpMenu.addAction(self.AboutAction)
		self.HelpMenu.addAction(self.GreekAction)

parser = argparse.ArgumentParser()
parser.add_argument("--type", default="-1")
parser.add_argument("--error", action="store_true")
pargs = parser.parse_args()

if pargs.error:
	paintwdg.set_EXIT_ON_ERROR()

qapp = QApplication(sys.argv[1:])
qapp.setApplicationName("sopr-sheme-gener")

QAPP = qapp
common.APP = qapp

mainwindow = MainWindow(int(pargs.type))
mainwindow.resize(800, 640)
mainwindow.showMaximized()
mainwindow.show()

qapp.exec()