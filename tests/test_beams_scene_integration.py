import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime
import tasks.balki as balki


def _set_records(records, values):
	for record, fields in zip(records, values):
		for name, value in fields.items():
			setattr(record, name, value)


def _image_bytes(image):
	bits = image.bits()
	return bits.asstring(image.sizeInBytes())


def _legacy_and_scene_images(canvas, monkeypatch):
	with monkeypatch.context() as legacy:
		legacy.setattr(balki, "supports_scene_layout", lambda *args, **kwargs: False)
		legacy_image = canvas.make_image()
	scene_image = canvas.make_image()
	return legacy_image, scene_image


def test_migrated_beams_features_match_legacy_pixels(monkeypatch):
	args = build_parser().parse_args(["--type", "beams", "--no-maximize", "--error"])
	context = create_runtime(args)
	try:
		scheme = context.controller.current_scheme
		task = scheme.task
		_set_records(
			task["betsect"],
			[
				{
					"sharn": "Нет",
					"F": "влево",
					"FT": "H",
					"M": "Нет",
					"MT": "",
					"sectname": "A",
				},
				{
					"sharn": "Нет",
					"F": "+",
					"FT": "F1",
					"M": "+",
					"MT": "M1",
					"sectname": "B",
				},
				{
					"sharn": "Нет",
					"F": "вправо",
					"FT": "H2",
					"M": "-",
					"MT": "M2",
					"sectname": "C",
				},
				{
					"sharn": "Нет",
					"F": "-",
					"FT": "F3",
					"M": "Нет",
					"MT": "",
					"sectname": "D",
				},
			],
		)
		scheme.left_node.set("Заделка")
		scheme.right_node.set("Шарнир")
		scheme.texteditor.setPlainText("note")
		context.app.processEvents()

		legacy, scene = _legacy_and_scene_images(context.canvas, monkeypatch)
		assert _image_bytes(scene) == _image_bytes(legacy)

		_set_records(
			task["betsect"],
			[
				{
					"sharn": "Нет",
					"F": "вправо",
					"FT": "R0",
					"M": "-",
					"MT": "M0",
					"sectname": "N0",
				},
				{
					"sharn": "2",
					"F": "влево",
					"FT": "L1",
					"M": "Нет",
					"MT": "",
					"sectname": "N1",
				},
				{
					"sharn": "1",
					"F": "-",
					"FT": "D2",
					"M": "+",
					"MT": "M2",
					"sectname": "N2",
				},
				{
					"sharn": "2",
					"F": "влево",
					"FT": "L3",
					"M": "Нет",
					"MT": "",
					"sectname": "N3",
				},
			],
		)
		_set_records(
			task["sectforce"],
			[
				{"Fr": "-", "FrT": "q0"},
				{"Fr": "+", "FrT": "q1"},
				{"Fr": "Нет", "FrT": ""},
			],
		)
		scheme.left_node.set("Шарнир")
		scheme.right_node.set("Заделка")
		scheme.postfix.set((True, ", EIx"))
		scheme.texteditor.setPlainText("line1\nline2")
		context.app.processEvents()

		legacy, scene = _legacy_and_scene_images(context.canvas, monkeypatch)
		assert _image_bytes(scene) == _image_bytes(legacy)

		task["labels"] = [
			scheme.confwidget.label("Label \\alpha", (0.13, -22))
		]
		context.app.processEvents()

		legacy, scene = _legacy_and_scene_images(context.canvas, monkeypatch)
		assert _image_bytes(scene) == _image_bytes(legacy)
		assert len(context.canvas.label_items) == 1
		assert any(
			item.object_id == "label/0"
			for item in context.canvas.last_scene.walk()
		)

		task["labels"] = []
		for section_type in ("Тонкая труба", "Треугольник"):
			scheme.section_container.section_type.set(section_type)
			context.app.processEvents()

			legacy, scene = _legacy_and_scene_images(context.canvas, monkeypatch)
			assert _image_bytes(scene) == _image_bytes(legacy)
	finally:
		context.window.close()
		context.app.processEvents()
