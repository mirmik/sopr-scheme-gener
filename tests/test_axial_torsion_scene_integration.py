import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def _image_bytes(image):
	return image.bits().asstring(image.sizeInBytes())


def test_all_axial_torsion_subtypes_render_through_scene():
	args = build_parser().parse_args(
		["--type", "axial-torsion", "--no-maximize", "--error"]
	)
	context = create_runtime(args)
	try:
		scheme = context.controller.current_scheme
		for subtype in (0, 1, 2):
			if subtype:
				scheme.task_subtype.set(subtype)
				context.app.processEvents()
			task = scheme.task
			task["sections"][0].label = "S0"
			task["betsect"][0].label = "A"
			task["betsect"][0].T = "P0"
			if subtype == 0:
				task["betsect"][0].F = "+"
				task["sectforce"][0].Fr = "-"
				task["sections"][2].delta = True
			else:
				task["betsect"][0].Mkr = "+"
				task["sectforce"][0].mkr = "-"
			if subtype == 2:
				task["sections"][0].d = 1.5
				task["sections"][0].l = 0.7
				task["sections"][0].dtext = "d0"
			context.canvas.highlited_sect = ("S", 0)
			context.canvas.highlited_node = ("N", 0)
			context.app.processEvents()

			assert _image_bytes(context.canvas.make_image())
			index = context.canvas.scene_interaction.index
			assert index.get("section/0/label") is not None
			assert index.get("node/0/highlight") is not None
			if subtype == 0:
				assert index.get("node/0/force") is not None
			else:
				assert index.get("node/0/torque") is not None
			if subtype == 2:
				assert index.get("section/0/diameter") is not None
	finally:
		context.window.close()
