import common
import paintwdg

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ShemeType(common.SchemeType):
	def __init__(self):
		super().__init__("Напряжения")
		self.setwidgets(ConfWidget(self), PaintWidget(), common.TableWidget())

class ConfWidget(common.ConfWidget):
	def __init__(self, scheme):
		super().__init__(scheme)
		
		self.shemetype.texteditor = QTextEdit()
		self.shemetype.texteditor.textChanged.connect(self.redraw)

	def create_task_structure(self):
		self.shemetype.task = {
			"sections": 
			[
			],
		}

	def inittask(self):
		return {}

class PaintWidget(paintwdg.PaintWidget):
	def __init__(self):
		super().__init__()
		pass

	def paintEventImplementation(self, ev):
		pass