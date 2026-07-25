import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QEvent, QPointF, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QLabel

from sopr_scheme_gener.app import build_parser, create_runtime


def _image_bytes(image):
	bits = image.bits()
	return bits.asstring(image.sizeInBytes())


def _device_center(interaction, object_id):
	bounds = interaction.index.bounds(object_id)
	mapping = interaction.mapping
	return (
		(bounds.x + bounds.width / 2 - mapping.viewport.x) * mapping.scale,
		(bounds.y + bounds.height / 2 - mapping.viewport.y) * mapping.scale,
	)


def test_plate_scene_renders_full_feature_matrix():
	context = create_runtime(
		build_parser().parse_args(["--type", "plate", "--no-maximize", "--error"])
	)
	try:
		scheme = context.controller.current_scheme
		for index, section in enumerate(scheme.task["sections"]):
			section.intgran = index != 1
			section.shtrih = True
			section.dtext = "d{}".format(index)
			section.htext = "h{}".format(index)
			scheme.task["sectforce"][index].distrib = True
			node = scheme.task["betsect"][index]
			node.fen = "+" if index % 2 else "-"
			node.men = "-" if index % 2 else "+"
			node.sharn = "1" if index % 2 else "2"
		scheme.task["labels"] = [
			scheme.confwidget.label("Label", (0.1, -15))
		]
		scheme.zadelka.set(False)
		scheme.axis.set(False)
		context.app.processEvents()

		image = context.canvas.make_image()
		index = context.canvas.scene_interaction.index

		assert _image_bytes(image)
		assert index.get("load/1/right") is not None
		assert index.get("force/2") is not None
		assert index.get("moment/0/left") is not None
		assert index.get("support/1/right/1") is not None
		assert index.get("label/0") is not None
		assert context.canvas.label_items == {}
	finally:
		context.window.close()
		context.app.processEvents()


def test_plate_editor_shows_bold_right_click_label_hint():
	context = create_runtime(
		build_parser().parse_args(["--type", "plate", "--no-maximize", "--error"])
	)
	try:
		hint = context.controller.current_scheme.confwidget.findChild(
			QLabel,
			"plate_label_hint",
		)
		assert hint is not None
		assert hint.font().bold()
		assert "правой кнопкой мыши" in hint.text()
		assert "добавить метку" in hint.text()
		layout = context.controller.current_scheme.confwidget.vlayout
		assert layout.indexOf(hint) == layout.indexOf(
			context.controller.current_scheme.confwidget.table2
		) + 1
	finally:
		context.window.close()
		context.app.processEvents()


def test_plate_label_text_can_be_edited_by_double_click(monkeypatch):
	context = create_runtime(
		build_parser().parse_args(["--type", "plate", "--no-maximize", "--error"])
	)
	try:
		scheme = context.controller.current_scheme
		label = scheme.confwidget.label("before", (0.1, -15))
		scheme.task["labels"] = [label]
		context.app.processEvents()
		context.canvas.make_image()
		received = {}

		def edit_text(*args, **kwargs):
			received["text"] = kwargs.get("text")
			return "after", True

		monkeypatch.setattr("paintwdg.QInputDialog.getText", edit_text)
		point = _device_center(context.canvas.scene_interaction, "label/0")
		context.canvas.mouseDoubleClickEvent(
			QMouseEvent(
				QEvent.MouseButtonDblClick,
				QPointF(*point),
				Qt.LeftButton,
				Qt.LeftButton,
				Qt.NoModifier,
			)
		)

		assert received["text"] == "before"
		assert label.text == "after"
		assert context.canvas.selected_label_id == "label/0"
	finally:
		context.window.close()
		context.app.processEvents()
