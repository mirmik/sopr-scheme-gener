import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def _set_records(records, values):
	for record, fields in zip(records, values):
		for name, value in fields.items():
			setattr(record, name, value)


def _image_bytes(image):
	bits = image.bits()
	return bits.asstring(image.sizeInBytes())


def _render_scene(canvas):
	image = canvas.make_image()
	assert canvas.last_scene.objects
	return image


def test_all_beams_scene_features_render():
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

		assert _image_bytes(_render_scene(context.canvas))

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

		assert _image_bytes(_render_scene(context.canvas))

		task["labels"] = [
			scheme.confwidget.label("Label \\alpha", (0.13, -22))
		]
		context.app.processEvents()

		assert _image_bytes(_render_scene(context.canvas))
		assert len(context.canvas.label_items) == 1
		assert any(
			item.object_id == "label/0"
			for item in context.canvas.last_scene.walk()
		)

		task["labels"] = []
		for section_type in ("Тонкая труба", "Треугольник"):
			scheme.section_container.section_type.set(section_type)
			context.app.processEvents()

			assert _image_bytes(_render_scene(context.canvas))

		scheme.section_container.section_type.set("Сечение общего типа")
		general = scheme.section_container.main_section_0
		for outer_type in (
			"Прямоугольник",
			"Квадрат",
			"Квадрат повёрнутый 45 град",
			"Круг",
		):
			for inner_type in (
				"Нет",
				"Квадрат",
				"Квадрат повёрнутый 45 град",
				"Круг",
			):
				general.outer_type.set(outer_type)
				general.inner_type.set(inner_type)
				context.app.processEvents()

				assert _image_bytes(_render_scene(context.canvas))

		scheme.section_container.section_type.set(
			"Прямоугольник с прямоугольным отверстием"
		)
		rect = scheme.section_container.rect_minus_rect
		for offset, edge in (
			((False, "s", 20), "Нет"),
			((True, "s", 20), "Нет"),
			((False, "s", 20), "Верх"),
			((False, "s", 20), "Низ"),
		):
			rect.s.set(offset)
			rect.edge.set(edge)
			context.app.processEvents()

			assert _image_bytes(_render_scene(context.canvas))

		scheme.section_container.section_type.set("H - профиль")
		for rotated in (False, True):
			scheme.section_container.hrect.orient.set(rotated)
			context.app.processEvents()

			assert _image_bytes(_render_scene(context.canvas))
	finally:
		context.window.close()
		context.app.processEvents()
