import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

from taskconf_menu import Element


def test_numeric_getters_keep_last_valid_value_during_intermediate_input():
	_app = QApplication.instance() or QApplication(["taskconf-test"])
	float_element = Element("Float", "float", "2.5")
	float_getter = float_element.getter()
	int_element = Element("Int", "int", "4")
	int_getter = int_element.getter()

	assert float_getter.get() == 2.5
	assert int_getter.get() == 4

	float_element.obj.clear()
	int_element.obj.setText("-")
	assert float_getter.get() == 2.5
	assert int_getter.get() == 4

	float_element.obj.setText("3.75")
	int_element.obj.setText("-6")
	assert float_getter.get() == 3.75
	assert int_getter.get() == -6
