from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math
import paintool
import sections

class SectionItem(QGraphicsItem):
    def __init__(self, wdg):
        super().__init__()
        self.wdg = wdg
        self.right = 175
        self.width = 140
        
    def boundingRect(self):
        print(self.wdg.shemetype.section_container)
        if self.wdg.shemetype.section_container.section_type.get() == "Нет":
            return QRectF(0,0,0,0)
        else:
            return QRectF(self.right - self.width, -110, self.width, 110*2)

    def paint(self, painter, option, widget):
        section_width = sections.draw_section_routine(
            self.wdg, 
            hcenter=0, 
            right=self.right,
            painter = painter)