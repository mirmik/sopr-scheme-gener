import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def test_oblique_bending_feature_scene_renders():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "oblique-bending", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		node = scheme.task["betsect"][0]
		node.xF, node.xFtxt = "+1", "Fx"
		node.yF, node.yFtxt = "-2", "Fy"
		node.xM, node.xMtxt = "+", "Mx"
		node.yM, node.yMtxt = "-", "My"
		node.xS, node.yS, node.zS = "+1", "-2", "+1"
		load = scheme.task["sectforce"][0]
		load.xF, load.xFtxt = "+", "qx"
		load.yF, load.yFtxt = "-", "qy"
		scheme.axonom.set(True)
		context.app.processEvents()

		image = context.canvas.make_image()
		assert image.bits().asstring(image.sizeInBytes())
		index = context.canvas.scene_interaction.index
		assert index.get("node/0/force-x") is not None
		assert index.get("node/0/moment-y") is not None
		assert index.get("section/0/distributed-y") is not None
		assert index.get("node/0/support-z") is not None
	finally:
		context.window.close()
