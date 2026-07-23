import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def _image_bytes(image):
	bits = image.bits()
	return bits.asstring(image.sizeInBytes())


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
