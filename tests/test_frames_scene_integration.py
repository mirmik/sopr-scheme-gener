import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QPoint

from sopr_scheme_gener.app import build_parser, create_runtime


class MouseEvent:
	def __init__(self, point):
		self._point = QPoint(int(point.x()), int(point.y()))

	def pos(self):
		return self._point


def _image_bytes(image):
	return image.bits().asstring(image.sizeInBytes())


def test_frames_scene_features_render_and_grid_adds_a_member():
	args = build_parser().parse_args(
		["--type", "frames", "--no-maximize", "--error"]
	)
	context = create_runtime(args)
	try:
		scheme = context.controller.current_scheme
		task = scheme.task
		task["sections"][0].rsharn = "снизу шарн1"
		task["sections"][1].lsharn = "врезанный"
		task["sections"][1].rsharn = "заделка"
		task["sectforce"][0].distrib = "+"
		task["sectforce"][0].txt = "q0"
		task["sectforce"][1].distrib = "-"
		task["betsect"][0].fenl = "сверху от"
		task["betsect"][0].fl_txt = "F0"
		task["betsect"][1].fenr = "справа к"
		task["betsect"][1].fr_txt = "F1"
		task["betsect"][1].menl = "снизу -"
		task["betsect"][1].ml_txt = "M1"
		task["label"][0].smaker = "A"
		task["label"][1].fmaker = "B"
		context.canvas.highlited_element = ("N0", 1)
		context.app.processEvents()

		assert _image_bytes(context.canvas.make_image())
		index = context.canvas.scene_interaction.index
		assert index.get("member/0/distributed") is not None
		assert index.get("member/1/start-moment") is not None
		assert index.get("member/1/start-label") is None
		assert index.get("highlight/node") is not None

		context.canvas.enterEvent(None)
		context.canvas.make_image()
		first = context.canvas._grid_point("grid/0/0")
		second = context.canvas._grid_point("grid/1/0")
		assert first is not None and second is not None

		context.canvas.mouseMoveEvent(MouseEvent(first))
		context.canvas.mousePressEvent(MouseEvent(first))
		context.canvas.mouseMoveEvent(MouseEvent(second))
		context.canvas.make_image()
		assert context.canvas.scene_interaction.index.get("preview") is not None
		before = len(task["sections"])
		context.canvas.mouseReleaseEvent(MouseEvent(second))

		assert len(task["sections"]) == before + 1
		added = task["sections"][-1]
		assert (added.xstrt, added.ystrt) == ("0", "0")
		assert (added.xfini, added.yfini) == ("1", "0")
	finally:
		context.window.close()
