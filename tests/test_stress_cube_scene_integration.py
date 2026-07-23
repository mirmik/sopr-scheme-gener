import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def _image_bytes(image):
	bits = image.bits()
	return bits.asstring(image.sizeInBytes())


def test_stress_cube_scene_renders_full_feature_matrix():
	args = build_parser().parse_args(
		["--type", "stress-cube", "--no-maximize", "--error"]
	)
	context = create_runtime(args)
	try:
		scheme = context.controller.current_scheme
		scheme.second_cube.set(True)
		context.app.processEvents()
		assert len(scheme.task["sections"]) == 2

		values = (
			("+", "-", "+", "-", "+", "-"),
			("-", "+", "-", "+", "-", "+"),
		)
		for section, directions in zip(scheme.task["sections"], values):
			for name, direction in zip(
				("qx", "qy", "qz", "mx", "my", "mz"),
				directions,
			):
				setattr(section, name, direction)
		for index, label in enumerate(scheme.task["labels"]):
			label.text = "L{}".format(index)
			label.x = index
			label.y = -index
			label.text2 = "R{}".format(index)
			label.x2 = -index
			label.y2 = index

		scheme.axonom.set(True)
		scheme.zrot.set(35)
		scheme.xrot.set(25)
		scheme.zmul.set(0.75)
		scheme.texteditor.setPlainText("note")
		context.app.processEvents()

		image = context.canvas.make_image()
		scene = context.canvas.last_scene
		ids = {item.object_id for item in scene.walk() if item.object_id}

		assert _image_bytes(image)
		assert "cube/0" in ids
		assert "cube/1" in ids
		assert "cube/0/label/qx" in ids
		assert "cube/1/label/mz" in ids
		assert "note/0" in ids
		label_ids = {
			entry.object_id
			for entry in context.canvas.scene_interaction.index.entries
			if entry.metadata_value("kind") == "label"
		}
		assert label_ids == {
			"cube/{}/label/{}".format(cube, name)
			for cube in (0, 1)
			for name in ("qx", "qy", "qz", "mx", "my", "mz")
		}
		assert not hasattr(context.canvas, "hovers")
		assert not hasattr(context.canvas, "scene")
	finally:
		context.window.close()
		context.app.processEvents()
