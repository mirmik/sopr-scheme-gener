"""Immutable, Qt-independent scene values and primitives."""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Iterator, Optional, Tuple, Union

Scalar = Union[None, bool, int, float, str]
Metadata = Tuple[Tuple[str, Scalar], ...]


def metadata(**values: Scalar) -> Metadata:
	return tuple(sorted(values.items()))


def _tuple(value, name):
	try:
		return tuple(value)
	except TypeError:
		raise TypeError("{} must be iterable".format(name))


def _validate_number(value, name):
	if (
		not isinstance(value, (int, float))
		or isinstance(value, bool)
		or not math.isfinite(value)
	):
		raise ValueError("{} must be a finite number".format(name))


def _validate_metadata(value):
	result = _tuple(value, "metadata")
	keys = set()
	for item in result:
		if not isinstance(item, tuple) or len(item) != 2:
			raise TypeError("metadata entries must be (key, value) tuples")
		key, scalar = item
		if not isinstance(key, str) or not key:
			raise ValueError("metadata keys must be non-empty strings")
		if key in keys:
			raise ValueError("metadata keys must be unique")
		keys.add(key)
		if scalar is not None and not isinstance(scalar, (bool, int, float, str)):
			raise TypeError("metadata values must be JSON scalars")
		if isinstance(scalar, float) and not math.isfinite(scalar):
			raise ValueError("metadata values must be finite")
	return result


def _validate_object_fields(instance):
	if instance.object_id is not None and (
		not isinstance(instance.object_id, str) or not instance.object_id
	):
		raise ValueError("object_id must be a non-empty string or None")
	object.__setattr__(instance, "metadata", _validate_metadata(instance.metadata))


@dataclass(frozen=True)
class Point:
	x: float
	y: float

	def __post_init__(self):
		_validate_number(self.x, "x")
		_validate_number(self.y, "y")

	def translated(self, offset):
		return Point(self.x + offset.x, self.y + offset.y)


@dataclass(frozen=True)
class Rect:
	x: float
	y: float
	width: float
	height: float

	def __post_init__(self):
		for name in ("x", "y", "width", "height"):
			_validate_number(getattr(self, name), name)
		if self.width < 0 or self.height < 0:
			raise ValueError("Rect dimensions cannot be negative")

	@property
	def left(self):
		return self.x

	@property
	def top(self):
		return self.y

	@property
	def right(self):
		return self.x + self.width

	@property
	def bottom(self):
		return self.y + self.height

	def translated(self, offset):
		return Rect(self.x + offset.x, self.y + offset.y, self.width, self.height)

	def union(self, other):
		left = min(self.left, other.left)
		top = min(self.top, other.top)
		right = max(self.right, other.right)
		bottom = max(self.bottom, other.bottom)
		return Rect(left, top, right - left, bottom - top)

	@classmethod
	def around(cls, points: Iterable[Point]):
		points = tuple(points)
		if not points:
			raise ValueError("At least one point is required")
		left = min(point.x for point in points)
		top = min(point.y for point in points)
		right = max(point.x for point in points)
		bottom = max(point.y for point in points)
		return cls(left, top, right - left, bottom - top)


@dataclass(frozen=True)
class Color:
	red: int
	green: int
	blue: int
	alpha: int = 255

	def __post_init__(self):
		for name in ("red", "green", "blue", "alpha"):
			value = getattr(self, name)
			if (
				not isinstance(value, int)
				or isinstance(value, bool)
				or not 0 <= value <= 255
			):
				raise ValueError("{} must be an integer from 0 to 255".format(name))


BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
TRANSPARENT = Color(0, 0, 0, 0)


@dataclass(frozen=True)
class Stroke:
	color: Color = BLACK
	width: float = 1.0
	dash: Tuple[float, ...] = ()
	line_style: str = "solid"

	def __post_init__(self):
		_validate_number(self.width, "stroke width")
		if self.width <= 0:
			raise ValueError("stroke width must be positive")
		dash = _tuple(self.dash, "dash")
		for value in dash:
			_validate_number(value, "dash value")
			if value <= 0:
				raise ValueError("dash values must be positive")
		object.__setattr__(self, "dash", dash)
		if self.line_style not in ("solid", "dash-dot"):
			raise ValueError("Unsupported line style: {!r}".format(self.line_style))
		if dash and self.line_style != "solid":
			raise ValueError("dash and line_style cannot be combined")


@dataclass(frozen=True)
class Fill:
	color: Color = TRANSPARENT
	pattern: str = "solid"

	def __post_init__(self):
		if self.pattern not in ("solid", "backward-diagonal", "forward-diagonal"):
			raise ValueError("Unsupported fill pattern: {!r}".format(self.pattern))


class TextAnchor(str, Enum):
	BASELINE_LEFT = "baseline-left"
	BASELINE_CENTER = "baseline-center"
	BASELINE_RIGHT = "baseline-right"
	TOP_LEFT = "top-left"
	CENTER = "center"


@dataclass(frozen=True)
class TextStyle:
	color: Color = BLACK
	family: str = ""
	point_size: float = 12.0
	bold: bool = False
	italic: bool = False

	def __post_init__(self):
		if not isinstance(self.family, str):
			raise TypeError("font family must be a string")
		_validate_number(self.point_size, "point_size")
		if self.point_size <= 0:
			raise ValueError("point_size must be positive")


@dataclass(frozen=True)
class Line:
	start: Point
	end: Point
	stroke: Stroke = Stroke()
	object_id: Optional[str] = None
	metadata: Metadata = ()

	def __post_init__(self):
		_validate_object_fields(self)


@dataclass(frozen=True)
class Polyline:
	points: Tuple[Point, ...]
	stroke: Stroke = Stroke()
	object_id: Optional[str] = None
	metadata: Metadata = ()

	def __post_init__(self):
		points = _tuple(self.points, "points")
		if len(points) < 2 or any(not isinstance(point, Point) for point in points):
			raise ValueError("Polyline requires at least two Point values")
		object.__setattr__(self, "points", points)
		_validate_object_fields(self)


@dataclass(frozen=True)
class Polygon:
	points: Tuple[Point, ...]
	stroke: Optional[Stroke] = Stroke()
	fill: Fill = Fill()
	object_id: Optional[str] = None
	metadata: Metadata = ()
	convex: bool = False

	def __post_init__(self):
		points = _tuple(self.points, "points")
		if len(points) < 3 or any(not isinstance(point, Point) for point in points):
			raise ValueError("Polygon requires at least three Point values")
		object.__setattr__(self, "points", points)
		if not isinstance(self.convex, bool):
			raise TypeError("convex must be a bool")
		_validate_object_fields(self)


@dataclass(frozen=True)
class Rectangle:
	bounds: Rect
	stroke: Optional[Stroke] = Stroke()
	fill: Fill = Fill()
	object_id: Optional[str] = None
	metadata: Metadata = ()

	def __post_init__(self):
		if not isinstance(self.bounds, Rect):
			raise TypeError("bounds must be a Rect")
		_validate_object_fields(self)


@dataclass(frozen=True)
class Ellipse:
	bounds: Rect
	stroke: Optional[Stroke] = Stroke()
	fill: Fill = Fill()
	object_id: Optional[str] = None
	metadata: Metadata = ()

	def __post_init__(self):
		if not isinstance(self.bounds, Rect):
			raise TypeError("bounds must be a Rect")
		_validate_object_fields(self)


@dataclass(frozen=True)
class Arc:
	bounds: Rect
	start_degrees: float
	span_degrees: float
	stroke: Stroke = Stroke()
	object_id: Optional[str] = None
	metadata: Metadata = ()

	def __post_init__(self):
		if not isinstance(self.bounds, Rect):
			raise TypeError("bounds must be a Rect")
		_validate_number(self.start_degrees, "start_degrees")
		_validate_number(self.span_degrees, "span_degrees")
		_validate_object_fields(self)


@dataclass(frozen=True)
class Text:
	position: Point
	value: str
	style: TextStyle = TextStyle()
	anchor: TextAnchor = TextAnchor.BASELINE_LEFT
	rotation_degrees: float = 0.0
	object_id: Optional[str] = None
	metadata: Metadata = ()

	def __post_init__(self):
		if not isinstance(self.value, str):
			raise TypeError("text value must be a string")
		if not isinstance(self.anchor, TextAnchor):
			raise TypeError("anchor must be a TextAnchor")
		_validate_number(self.rotation_degrees, "rotation_degrees")
		_validate_object_fields(self)


@dataclass(frozen=True)
class Arrow:
	start: Point
	end: Point
	stroke: Stroke = Stroke()
	head_length: float = 10.0
	head_width: float = 8.0
	head_stroke: Optional[Stroke] = None
	object_id: Optional[str] = None
	metadata: Metadata = ()

	def __post_init__(self):
		if self.head_stroke is not None and not isinstance(self.head_stroke, Stroke):
			raise TypeError("head_stroke must be a Stroke or None")
		for name in ("head_length", "head_width"):
			_validate_number(getattr(self, name), name)
			if getattr(self, name) <= 0:
				raise ValueError("{} must be positive".format(name))
		if self.start == self.end:
			raise ValueError("Arrow start and end must differ")
		_validate_object_fields(self)


SceneObject = Union[
	Line,
	Polyline,
	Polygon,
	Rectangle,
	Ellipse,
	Arc,
	Text,
	Arrow,
	"Group",
]


@dataclass(frozen=True)
class Group:
	children: Tuple[SceneObject, ...]
	offset: Point = Point(0.0, 0.0)
	object_id: Optional[str] = None
	metadata: Metadata = ()
	antialias: Optional[bool] = None

	def __post_init__(self):
		children = _tuple(self.children, "children")
		if any(not isinstance(child, SCENE_OBJECT_TYPES) for child in children):
			raise TypeError("Group children must be scene objects")
		if self.antialias is not None and not isinstance(self.antialias, bool):
			raise TypeError("antialias must be a bool or None")
		object.__setattr__(self, "children", children)
		_validate_object_fields(self)


SCENE_OBJECT_TYPES = (
	Line,
	Polyline,
	Polygon,
	Rectangle,
	Ellipse,
	Arc,
	Text,
	Arrow,
	Group,
)


@dataclass(frozen=True)
class Scene:
	viewport: Rect
	objects: Tuple[SceneObject, ...]
	content_bounds: Optional[Rect] = None
	background: Color = WHITE

	def __post_init__(self):
		objects = _tuple(self.objects, "objects")
		if any(not isinstance(item, SCENE_OBJECT_TYPES) for item in objects):
			raise TypeError("Scene objects must be scene primitives or groups")
		object.__setattr__(self, "objects", objects)
		if self.content_bounds is None:
			object.__setattr__(self, "content_bounds", self.viewport)

	def walk(self) -> Iterator[SceneObject]:
		return walk(self.objects)


def walk(objects: Iterable[SceneObject]) -> Iterator[SceneObject]:
	for item in objects:
		yield item
		if isinstance(item, Group):
			yield from walk(item.children)
