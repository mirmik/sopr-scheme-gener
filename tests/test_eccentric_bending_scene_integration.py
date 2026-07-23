import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def test_eccentric_bending_feature_scene_renders_without_debug_output(capsys):
	context = create_runtime(
		build_parser().parse_args(
			["--type", "eccentric-bending", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		record = scheme.task["sections"][0]
		record.Fx, record.Fx_txt, record.Fx_txt_alttxt = "справа +", "Fx", "1"
		record.Fy, record.Fy_txt, record.Fy_txt_alttxt = "сверху -", "Fy", "5"
		record.Fz, record.Fz_txt, record.Fz_txt_alttxt = "+", "Fz", "6"
		scheme.axonom.set(True)
		context.app.processEvents()

		image = context.canvas.make_image()
		assert image.bits().asstring(image.sizeInBytes())
		index = context.canvas.scene_interaction.index
		assert index.get("point/0/force-x") is not None
		assert index.get("point/0/force-y") is not None
		assert index.get("point/0/force-z") is not None
		assert "txtpnt_type" not in capsys.readouterr().out
	finally:
		context.window.close()
