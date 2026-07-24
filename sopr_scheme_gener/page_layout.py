"""Optional page-layout model shared by storage, rendering, and the dev API."""

from dataclasses import dataclass
import math
import numbers


PAGE_LAYOUT_VERSION = 1


class PageLayoutError(ValueError):
	pass


@dataclass
class PageFrame:
	x: float
	y: float
	width: float
	height: float

	def to_data(self):
		return {
			"x": self.x,
			"y": self.y,
			"width": self.width,
			"height": self.height,
		}


@dataclass
class PageLayout:
	task_frame: PageFrame
	note_frame: PageFrame
	version: int = PAGE_LAYOUT_VERSION

	def to_data(self):
		return {
			"version": self.version,
			"task_frame": self.task_frame.to_data(),
			"note_frame": self.note_frame.to_data(),
		}


def _number(value, path):
	if (
		not isinstance(value, numbers.Real)
		or isinstance(value, bool)
		or not math.isfinite(float(value))
	):
		raise PageLayoutError("{} must be a finite number".format(path))
	return value


def _frame_from_data(value, path, canvas_width, canvas_height):
	if not isinstance(value, dict) or set(value) != {"x", "y", "width", "height"}:
		raise PageLayoutError(
			"{} must contain x, y, width, and height".format(path)
		)
	frame = PageFrame(
		x=_number(value["x"], "{}/x".format(path)),
		y=_number(value["y"], "{}/y".format(path)),
		width=_number(value["width"], "{}/width".format(path)),
		height=_number(value["height"], "{}/height".format(path)),
	)
	if frame.x < 0 or frame.y < 0:
		raise PageLayoutError("{} must start inside the canvas".format(path))
	if frame.width <= 0 or frame.height <= 0:
		raise PageLayoutError("{} dimensions must be positive".format(path))
	if frame.x + frame.width > canvas_width or frame.y + frame.height > canvas_height:
		raise PageLayoutError("{} must fit inside the canvas".format(path))
	return frame


def page_layout_from_data(value, canvas_width, canvas_height):
	if not isinstance(value, dict) or set(value) != {
		"version",
		"task_frame",
		"note_frame",
	}:
		raise PageLayoutError(
			"page_layout must contain version, task_frame, and note_frame"
		)
	if value["version"] != PAGE_LAYOUT_VERSION:
		raise PageLayoutError(
			"Unsupported page_layout version: {!r}".format(value["version"])
		)
	return PageLayout(
		version=PAGE_LAYOUT_VERSION,
		task_frame=_frame_from_data(
			value["task_frame"],
			"page_layout/task_frame",
			canvas_width,
			canvas_height,
		),
		note_frame=_frame_from_data(
			value["note_frame"],
			"page_layout/note_frame",
			canvas_width,
			canvas_height,
		),
	)


def validate_page_layout(layout, canvas_width, canvas_height):
	if not isinstance(layout, PageLayout):
		raise PageLayoutError("layout must be a PageLayout")
	return page_layout_from_data(layout.to_data(), canvas_width, canvas_height)
