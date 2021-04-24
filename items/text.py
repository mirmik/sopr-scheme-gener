from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math

class TextItem(QGraphicsItem):
	def __init__(self, text, font, center, pen):
		super().__init__()
		self.text = text
		self.font = font
		self.center = center
		self.pen = pen
		self.selected=False

	def boundingRect(self):
		metrics = QFontMetrics(self.font)
		width = metrics.width(self.text)
		height = metrics.height()

		return QRectF(self.center.x() - width/2, self.center.y() - height/2, width, height)

	def paint(self, painter, option, widget):
		painter.setPen(self.pen)
		painter.setFont(self.font)

		painter.drawText(self.boundingRect(), self.text)