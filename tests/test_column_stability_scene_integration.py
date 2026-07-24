import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime


def test_column_stability_editor_renders_and_round_trips_document(tmp_path):
	context = create_runtime(
		build_parser().parse_args(
			["--type", "column-stability", "--no-maximize", "--error"]
		)
	)
	try:
		scheme = context.controller.current_scheme
		assert len(scheme.task["nodes"]) == len(scheme.task["segments"]) + 1
		context.app.processEvents()
		image = context.canvas.make_image()
		assert image.bits().asstring(image.sizeInBytes())
		index = context.canvas.scene_interaction.index
		assert index.get("node/1/support") is not None
		assert index.get("node/2/load") is not None

		path = tmp_path / "stability.sopr.json"
		before = context.storage.to_data()
		context.storage.save(path)
		assert context.storage.load(path) == before
	finally:
		context.window.close()
