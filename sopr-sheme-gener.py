#!/usr/bin/env python3

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys

class SchemeType:
    def __init__(self, name, confwidget, paintwidget):
        self.name = name
        self.paintwidget = paintwidget
        self.confwidget = confwidget

        self.confwidget.set_paint_widget(self.paintwidget)

class PaintWidget:
    def __init__(self):
        pass

class ConfWidgetTest:
    def __init__(self):
        pass

    def set_paint_widget(self, paintwidget):
        self.paintwidget = paintwidget

class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.scheme_types = [
            SchemeType("Проверка функциональности", ConfWidgetTest(), PaintWidget())
        ]



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

mainwindow = MainWindow()
mainwindow.show()

qapp.exec()