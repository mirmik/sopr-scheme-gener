from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def text_prepare_ltext(l, suffix="l"):
	if abs(float(l) - int(l)) < 0.0001:
		text_l = "{}{}".format(int(l+0.1), suffix) if l != 1 else suffix
	else:
		text_l = "{:.3}".format(l) + suffix
	return text_l					

def clear_layout(layout):
	for i in reversed(range(layout.count())): 
		wdg = layout.itemAt(i).widget()
		if wdg is not None:
			layout.removeWidget(wdg)
			wdg.setParent(None)


def msgbox_error(txt):
	msg = QMessageBox()
	msg.setText("Возникла ошибка при отрисовке задачи:")
	msg.setInformativeText(txt)
	msg.setStandardButtons(QMessageBox.Ok)

	print(txt)
	msg.exec()
