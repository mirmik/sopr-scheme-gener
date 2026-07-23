import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QPoint, Qt

from sopr_scheme_gener.app import build_parser, create_runtime


class MouseEvent:
	def __init__(self, point):
		self._point = QPoint(int(point.x()), int(point.y()))

	def pos(self):
		return self._point

	def button(self):
		return Qt.LeftButton


def _image_bytes(image):
	return image.bits().asstring(image.sizeInBytes())


def test_all_rod_system_2_scene_features_render_and_nodes_add_a_branch():
	args = build_parser().parse_args(
		["--type", "rod-system-2", "--no-maximize", "--error"]
	)
	context = create_runtime(args)
	scheme = context.controller.current_scheme
	Section = scheme.confwidget.sect
	scheme.task["sections"] = [
		Section(force="от", ftxt="F0", addangle=30),
		Section(
			start_from=0,
			l=1.2,
			A=2,
			angle=60,
			sharn="шарн",
			force="к",
			ftxt="F1",
			alttxt=True,
			addangle=-30,
		),
		Section(
			start_from=0,
			l=0.8,
			A=3,
			angle=-45,
			sharn="нет",
			force="вдоль",
			ftxt="q",
			wide=True,
		),
		Section(
			start_from=1,
			angle=120,
			sharn="нет",
			body=False,
			force="от",
			ftxt="P",
		),
	]
	context.canvas.highlited_sect = (None, 1)
	context.app.processEvents()

	image = context.canvas.make_image()
	assert _image_bytes(image)
	index = context.canvas.scene_interaction.index
	assert index.get("section/0/angle") is not None
	assert index.get("section/2/force") is not None
	assert index.get("section/3/force") is not None

	root = context.canvas._point_for_node(0)
	context.canvas.enterEvent(None)
	context.canvas.mouseMoveEvent(MouseEvent(root))
	assert context.canvas.hovered_point_index == 0
	context.canvas.mousePressEvent(MouseEvent(root))
	target = root + QPoint(80, 0)
	context.canvas.mouseMoveEvent(MouseEvent(target))
	context.canvas.make_image()
	assert context.canvas.last_scene is not None
	assert any(
		item.object_id == "preview"
		for item in context.canvas.last_scene.walk()
	)
	context.canvas.mouseReleaseEvent(MouseEvent(target))

	added = scheme.task["sections"][-1]
	assert added.start_from == -1
	assert added.l == 1
	assert added.angle == 0
	context.window.close()
