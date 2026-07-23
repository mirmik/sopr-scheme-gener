#!/usr/bin/env python3

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
import sys
import argparse

import collections

import util

import container
import paintool
import hashlib

from .context import AppContext
from .task_registry import TASK_SPECS
from .legacy_storage import load_trusted_pickle

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
	def __init__(self, context, tp=-1):
		super().__init__()
		self.setObjectName("central_widget")
		self.context = context
		self.controller = context.controller
		context.attach_central(self)

		self.confview = context.legacy.create_common_settings()
		self.confview.setObjectName("common_settings")

		self.scheme_types = self.controller.initialize_tasks(self.confview)

		for s in self.scheme_types:
			if hasattr(s.confwidget, "serialize_list") is False:
				util.msgbox_error("Confwidget without serialize_list : " + s.name)


		self.stub_widget_0 = context.legacy.create_stub("Окно отображения")
		self.stub_widget_1 = context.legacy.create_stub("Таблица параметров")
		self.stub_widget_2 = context.legacy.create_stub("Окно конфигурации")

		self.stub_widget_0.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.stub_widget_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.stub_widget_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		self.type_list_widget = ComboBox("Выберите тип задачи") 
		self.type_list_widget.setObjectName("task_selector")
		self.type_list_widget.addItems([x.name for x in self.scheme_types])
		self.type_list_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

		self.type_list_widget.activated.connect(self.type_scheme_selected)

		self.hsplitter = QSplitter(Qt.Horizontal)
		context.legacy.bind_splitter(self.hsplitter)

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.hsplitter)

		self.container_paint = container.ContainerWidget(border=True, fixedSize=True, filter=True)
		self.container_paint.setObjectName("canvas_container")
		self.container_settings = container.ContainerWidget(border=False, fixedSize=False, filter=False)
		self.container_settings.setObjectName("task_settings_container")

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
		self.work_layout.addWidget(context.legacy.create_paint_widget_setter(self.container_paint))
		self.work_layout_wdg = QWidget()
		self.work_layout_wdg.setLayout(self.work_layout)

		self.hsplitter.addWidget(self.settings_layout_wdg)
		self.hsplitter.addWidget(self.work_layout_wdg)
		self.hsplitter.setStretchFactor(0, 150)
		self.hsplitter.setStretchFactor(1, 100)

		context.legacy.bind_canvas_container(self.container_paint)
		self.container_paint.setFixedSize(600,400)

		self.controller.bind_view(self)
		self.controller.clear()

		if tp != -1:
			self.inited = False
			self.tp = tp
		else:
			self.inited = True

		self.setLayout(self.layout)

	def current_scheme(self):
		return self.controller.current_scheme

	def current_task_spec(self):
		return self.controller.current_spec

	def select_task(self, selector):
		self.type_list_widget.inited = True
		return self.controller.select(selector)

	@property
	def currentno(self):
		return self.controller.current_index

	@property
	def task_specs(self):
		return self.controller.task_specs

	def set_scheme_type_no(self, no):
		if no == -1:
			self.controller.clear()
		else:
			self.controller.select(no)

	def display_empty(self):
		self.container_paint.replace(self.stub_widget_0)
		self.container_settings.replace(self.stub_widget_1)

	def display_scheme(self, scheme, changed):
		if changed:
			self.container_settings.replace(scheme.confwidget)
			self.container_paint.replace(scheme.paintwidget)

	def set_selected_index(self, index):
		self.type_list_widget.setCurrentIndex(index)
		self.type_list_widget.update()
			
	def type_scheme_selected(self, arg):
		self.type_list_widget.inited = True
		self.controller.select(arg)

	def showEvent(self, ev):
		super().showEvent(ev)
		if self.inited == False:
			self.inited = True
			self.select_task(self.tp)

class MainWindow(QMainWindow):
	def __init__(self, context, tp=-1):
		super().__init__()
		self.setObjectName("main_window")
		self.context = context

		self.createActions()
		self.createMenus()

		self.central = CentralWidget(context, tp)
		self.cw = self.central
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

	def file_hash(self, path):
		with open(path,"rb") as f:
			h = hashlib.new('sha256')
			h.update(f.read())
			return h.hexdigest()

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
			ext = ".png"

		curext = os.path.splitext(path)[1]
		if curext == '':
			path = path + ext

		dir = os.path.dirname(path)
		self.save_last_dirpath(dir)

		savepath = os.path.join(dir, ".save")
		if not os.path.exists(savepath):
			os.mkdir(savepath)

		try:
			self.context.controller.current_scheme.paintwidget.save_image(path)
		except Exception as ex:
			util.msgbox_error(str(ex))

		h = self.file_hash(path)
		marchpath = os.path.join(savepath, os.path.basename(str(h)) + ".dat")
		self.context.controller.current_scheme.serialize(marchpath)

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
			ext = ".png"

		curext = os.path.splitext(path)[1]
		if curext == '':
			path = path + ext

		dir = os.path.dirname(path)
		self.save_last_dirpath(dir)

		print("A")
		if curext == ".dat":
			savepath = dir
		else:
			savepath = os.path.join(dir, ".save")

		h = self.file_hash(path)

		if curext != ".dat":
			marchpath = os.path.join(savepath, os.path.basename(h) + ".dat")
		else:
			marchpath = path

		#print(marchpath)
		if os.path.exists(marchpath):
			pass
		else:
			marchpath = os.path.join(savepath, os.path.basename(path) + ".dat")
	
		print(marchpath)

		if not os.path.exists(marchpath):
			util.msgbox_error("Не найден файл для загрузки")
			return
	
		try:
			lll = load_trusted_pickle(marchpath)
		except Exception as ex:
			util.msgbox_error(str(ex))
			return

		name = lll[0][1]

		if lll[0][0] != "name":
			util.msgbox_error("wrong name field")
			return

		try:
			self.context.controller.select_by_title(name)
		except ValueError:
			util.msgbox_error("Unresolved task type: {}".format(name))
			return

		self.context.controller.current_scheme.deserialize(lll)

	def pre_picture_action(self):
		self.context.controller.current_scheme.paintwidget.predraw_dialog()

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

def build_parser():
	parser = argparse.ArgumentParser(prog="sopr-scheme-gener")
	parser.add_argument("--type", default="-1", help="Task index or stable task identifier")
	parser.add_argument("--debug", action="store_true")
	parser.add_argument("--error", action="store_true")
	parser.add_argument("--no-maximize", action="store_true")
	parser.add_argument("--dev-api", action="store_true", help="Enable the TCP development API")
	parser.add_argument("--dev-host", default="127.0.0.1")
	parser.add_argument("--dev-port", type=int, default=8765)
	parser.add_argument("--dev-token")
	parser.add_argument("--dev-info-file")
	parser.add_argument(
		"--unsafe-dev-exec",
		action="store_true",
		help="Allow trusted Python code execution through the development API",
	)
	return parser


def create_runtime(args):
	qapp = QApplication.instance() or QApplication([sys.argv[0]])
	qapp.setApplicationName("sopr-scheme-gener")
	context = AppContext(app=qapp, task_specs=TASK_SPECS)
	context.legacy.configure(
		qapp,
		debug=args.debug,
		exit_on_render_error=args.error,
	)

	window = MainWindow(context, -1)
	context.attach_window(window)
	window.resize(800, 640)

	if str(args.type) != "-1":
		selector = int(args.type) if str(args.type).lstrip("-").isdigit() else args.type
		context.controller.select(selector)

	if not args.no_maximize:
		window.showMaximized()
	window.show()

	if args.dev_api:
		from .devapi import start_dev_server

		context.dev_server = start_dev_server(
			context,
			host=args.dev_host,
			port=args.dev_port,
			token=args.dev_token,
			info_file=args.dev_info_file,
			allow_unsafe_exec=args.unsafe_dev_exec,
		)
		qapp.aboutToQuit.connect(context.dev_server.close)

	return context


def main(argv=None):
	args = build_parser().parse_args(argv)
	runtime = create_runtime(args)
	try:
		return runtime.app.exec()
	finally:
		if runtime.dev_server is not None:
			runtime.dev_server.close()


if __name__ == "__main__":
	raise SystemExit(main())
