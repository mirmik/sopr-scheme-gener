import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def test_shafts_feature_scene_renders_and_remains_inspectable():
	context = create_runtime(
		build_parser().parse_args(
			["--type", "shafts-pipes", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		scheme.uncentered_force.set("-")
		scheme.invert_moment.set("+")
		scheme.invert_izgmoment.set("-")
		scheme.Ltext.set("L")
		context.app.processEvents()

		image = context.canvas.make_image()
		assert image.bits().asstring(image.sizeInBytes())
		index = context.canvas.scene_interaction.index
		assert index.get("force/left") is not None
		assert index.get("torque/left-label") is not None
		assert index.get("bending/left") is not None
		assert index.get("dimension/length") is not None
	finally:
		context.window.close()
