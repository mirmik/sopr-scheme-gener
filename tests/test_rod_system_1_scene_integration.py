import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def _set(record, **values):
	for name, value in values.items():
		setattr(record, name, value)


def _image_bytes(image):
	return image.bits().asstring(image.sizeInBytes())


def test_all_rod_system_1_scene_features_render():
	args = build_parser().parse_args(
		["--type", "rod-system-1", "--no-maximize", "--error"]
	)
	context = create_runtime(args)
	scheme = context.controller.current_scheme
	task = scheme.task
	task["sections"][0].label = "\\alpha"
	task["sections"][1].dims = False
	_set(
		task["betsect"][0],
		lbl="N0",
		F="-",
		Ftxt="F0",
		sharn="1",
	)
	_set(
		task["betsect"][1],
		lbl="R1",
		F="+",
		Ftxt="F1",
		F2="+",
		F2txt="Q1",
		zazor=True,
		zazor_txt="\\Delta",
		sharn="2",
		sterzn_text1="upper",
		sterzn_text2="lower",
		sterzn_text_horizontal=False,
		sterzn_text_alt=True,
	)
	_set(
		task["betsect"][2],
		F2="-",
		F2txt="Q2",
		sterzn_text_horizontal=True,
		sterzn_text_alt=False,
	)
	scheme.zadelka1.set("1")
	scheme.zadelka2.set("2")
	context.canvas.highlited_node = (None, 1)
	context.app.processEvents()

	image = context.canvas.make_image()
	assert _image_bytes(image)
	index = context.canvas.scene_interaction.index
	assert index.get("section/0/label") is not None
	assert index.get("rod/1/gap/text") is not None
	assert index.get("rod-force/1") is not None
	assert index.get("rod-force/2") is not None
	assert index.get("endpoint/left/support") is not None
	assert index.get("endpoint/right/support") is not None
