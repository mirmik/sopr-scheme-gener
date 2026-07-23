import os

import numpy

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def test_spatial_beams_feature_scene_renders_and_remains_inspectable():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "spatial-beams", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		node = scheme.task["nodes"][0]
		node.sharn = "sharn"
		node.sharn_vec = numpy.array((1, 0, 0))
		node.sharn_vec2 = numpy.array((0, 1, 0))
		node.force_x = ((-0.1, 0, 0), (-1, 0, 0))
		node.torque = ((0, 1, 0), (0, 0, 1))
		scheme.task["sections"][0].distrib = (0, 0, 1)
		scheme.task["labels"].append(
			scheme.confwidget.label("F_x", (10, 20))
		)
		context.app.processEvents()

		image = context.canvas.make_image()
		assert image.bits().asstring(image.sizeInBytes())
		index = context.canvas.scene_interaction.index
		assert index.get("node/0/support") is not None
		assert index.get("node/0/force-x") is not None
		assert index.get("node/0/torque") is not None
		assert index.get("section/0/distributed") is not None
		assert index.get("label/0") is not None
	finally:
		context.window.close()
