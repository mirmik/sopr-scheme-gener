"""Qt-independent bounds queries and hit-testing for Scene objects."""

import math
from dataclasses import dataclass

from .model import (
	Arc,
	Arrow,
	Ellipse,
	Group,
	Line,
	Point,
	Polygon,
	Polyline,
	Rect,
	Rectangle,
	Scene,
	Text,
	TextAnchor,
)


def _union(bounds, other):
	return other if bounds is None else bounds.union(other)


def _expanded(bounds, amount):
	if not amount:
		return bounds
	return Rect(
		bounds.x - amount,
		bounds.y - amount,
		bounds.width + amount * 2,
		bounds.height + amount * 2,
	)


def _translated(bounds, offset):
	return Rect(
		bounds.x + offset.x,
		bounds.y + offset.y,
		bounds.width,
		bounds.height,
	)


def _metadata_value(item, name, default=None):
	for key, value in item.metadata:
		if key == name:
			return value
	return default


def _rotated_bounds(bounds, center, degrees):
	if not degrees:
		return bounds
	angle = math.radians(degrees)
	cosine = math.cos(angle)
	sine = math.sin(angle)
	points = []
	for point in (
		Point(bounds.left, bounds.top),
		Point(bounds.right, bounds.top),
		Point(bounds.right, bounds.bottom),
		Point(bounds.left, bounds.bottom),
	):
		dx = point.x - center.x
		dy = point.y - center.y
		points.append(
			Point(
				center.x + dx * cosine - dy * sine,
				center.y + dx * sine + dy * cosine,
			)
		)
	return Rect.around(points)


def _text_bounds(item, text_metrics):
	measurement = text_metrics.measure(item.value, item.style)
	x = item.position.x
	y = item.position.y
	if item.anchor == TextAnchor.TOP_LEFT:
		bounds = Rect(x, y, measurement.width + 5, measurement.height)
	elif item.anchor == TextAnchor.BASELINE_LEFT:
		bounds = Rect(
			x,
			y - measurement.ascent,
			measurement.width + 5,
			measurement.height,
		)
	elif item.anchor == TextAnchor.BASELINE_CENTER:
		bounds = Rect(
			x - measurement.width / 2,
			y - measurement.ascent,
			measurement.width + 5,
			measurement.height,
		)
	elif item.anchor == TextAnchor.BASELINE_RIGHT:
		bounds = Rect(
			x - measurement.width,
			y - measurement.ascent,
			measurement.width + 5,
			measurement.height,
		)
	elif item.anchor == TextAnchor.CENTER:
		bounds = Rect(
			x - measurement.width / 2,
			y - measurement.height / 2,
			measurement.width + 5,
			measurement.height,
		)
	else:
		raise ValueError("Unsupported text anchor: {!r}".format(item.anchor))
	return _rotated_bounds(bounds, item.position, item.rotation_degrees)


def _arrow_bounds(item):
	dx = item.end.x - item.start.x
	dy = item.end.y - item.start.y
	length = math.hypot(dx, dy)
	ux, uy = dx / length, dy / length
	normal_x, normal_y = uy, -ux
	base = Point(
		item.end.x - ux * item.head_length,
		item.end.y - uy * item.head_length,
	)
	half_width = item.head_width / 2
	points = (
		item.start,
		item.end,
		Point(
			base.x + normal_x * half_width,
			base.y + normal_y * half_width,
		),
		Point(
			base.x - normal_x * half_width,
			base.y - normal_y * half_width,
		),
	)
	head_width = item.head_stroke.width if item.head_stroke is not None else 0
	return _expanded(
		Rect.around(points),
		max(item.stroke.width, head_width) / 2,
	)


def object_bounds(item, text_metrics):
	"""Return conservative local bounds for one non-group Scene object."""

	if isinstance(item, Line):
		return _expanded(
			Rect.around((item.start, item.end)),
			item.stroke.width / 2,
		)
	if isinstance(item, Polyline):
		return _expanded(Rect.around(item.points), item.stroke.width / 2)
	if isinstance(item, Polygon):
		width = item.stroke.width / 2 if item.stroke is not None else 0
		return _expanded(Rect.around(item.points), width)
	if isinstance(item, (Rectangle, Ellipse)):
		width = item.stroke.width / 2 if item.stroke is not None else 0
		return _expanded(item.bounds, width)
	if isinstance(item, Arc):
		return _expanded(item.bounds, item.stroke.width / 2)
	if isinstance(item, Text):
		return _text_bounds(item, text_metrics)
	if isinstance(item, Arrow):
		return _arrow_bounds(item)
	raise TypeError("Bounds are not implemented for {}".format(type(item).__name__))


@dataclass(frozen=True)
class HitEntry:
	object_id: str
	bounds: Rect
	item: object
	z_order: int
	depth: int

	@property
	def metadata(self):
		return self.item.metadata

	def metadata_value(self, name, default=None):
		return _metadata_value(self.item, name, default)


class SceneIndex:
	"""Immutable object-id index using bounds and painter order."""

	def __init__(self, scene, text_metrics):
		if not isinstance(scene, Scene):
			raise TypeError("scene must be a Scene")
		if text_metrics is None:
			raise ValueError("text_metrics is required")
		self.scene = scene
		self.text_metrics = text_metrics
		self._entries = []
		self._by_id = {}
		self._paint_order = 0
		for item in scene.objects:
			self._visit(item, Point(0, 0), 0)
		self.entries = tuple(self._entries)

	def _add_entry(self, item, bounds, depth, z_order):
		if item.object_id is None:
			return
		if item.object_id in self._by_id:
			raise ValueError("Duplicate Scene object_id: {}".format(item.object_id))
		entry = HitEntry(item.object_id, bounds, item, z_order, depth)
		self._entries.append(entry)
		self._by_id[item.object_id] = entry

	def _visit(self, item, offset, depth):
		if isinstance(item, Group):
			group_offset = Point(
				offset.x + item.offset.x,
				offset.y + item.offset.y,
			)
			bounds = None
			first_order = self._paint_order
			for child in item.children:
				child_bounds = self._visit(child, group_offset, depth + 1)
				if child_bounds is not None:
					bounds = _union(bounds, child_bounds)
			z_order = max(first_order, self._paint_order - 1)
			if bounds is not None:
				self._add_entry(item, bounds, depth, z_order)
			return bounds

		bounds = _translated(object_bounds(item, self.text_metrics), offset)
		z_order = self._paint_order
		self._paint_order += 1
		self._add_entry(item, bounds, depth, z_order)
		return bounds

	def get(self, object_id):
		return self._by_id.get(object_id)

	def bounds(self, object_id):
		entry = self.get(object_id)
		return entry.bounds if entry is not None else None

	def hit_test(self, point, kinds=None, predicate=None):
		if not isinstance(point, Point):
			raise TypeError("point must be a Point")
		kinds = None if kinds is None else frozenset(kinds)
		candidates = []
		for entry in self.entries:
			if kinds is not None and entry.metadata_value("kind") not in kinds:
				continue
			if predicate is not None and not predicate(entry):
				continue
			if (
				entry.bounds.left <= point.x <= entry.bounds.right
				and entry.bounds.top <= point.y <= entry.bounds.bottom
			):
				candidates.append(entry)
		if not candidates:
			return None
		return max(candidates, key=lambda entry: (entry.z_order, entry.depth))


@dataclass(frozen=True)
class ViewportMapping:
	viewport: Rect
	scale: float = 1.0

	def __post_init__(self):
		if self.scale <= 0 or not math.isfinite(self.scale):
			raise ValueError("scale must be a finite positive number")

	@classmethod
	def direct(cls, viewport):
		return cls(viewport, 1.0)

	@classmethod
	def aspect_fit(cls, viewport, device_width, device_height):
		if device_width <= 0 or device_height <= 0:
			raise ValueError("device dimensions must be positive")
		return cls(
			viewport,
			min(device_width / viewport.width, device_height / viewport.height),
		)

	def from_device(self, point):
		return Point(
			self.viewport.x + point.x / self.scale,
			self.viewport.y + point.y / self.scale,
		)

	def delta_from_device(self, delta):
		return Point(delta.x / self.scale, delta.y / self.scale)
