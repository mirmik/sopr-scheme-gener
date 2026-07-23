from dataclasses import dataclass
from importlib import import_module


@dataclass(frozen=True)
class TaskSpec:
	identifier: str
	title: str
	module: str
	class_name: str

	def create(self):
		task_class = getattr(import_module(self.module), self.class_name)
		instance = task_class()
		if instance.name != self.title:
			raise RuntimeError(
				"Task registry title mismatch for {}: {!r} != {!r}".format(
					self.identifier,
					instance.name,
					self.title,
				)
			)
		return instance


TASK_SPECS = (
	TaskSpec("axial-torsion", "Растяжение/сжатие/кручение стержня", "tasks.task0", "ShemeTypeT0"),
	TaskSpec("beams", "Балки", "tasks.balki", "ShemeType"),
	TaskSpec("rod-system-1", "Стержневая система (Тип 1)", "tasks.sharn_sterhen", "ShemeTypeT2"),
	TaskSpec("rod-system-2", "Стержневая система (Тип 2)", "tasks.star", "ShemeTypeT1"),
	TaskSpec("plate", "Пластина", "tasks.plastina", "ShemeTypeT3"),
	TaskSpec("frames", "Рамы", "tasks.fermes", "ShemeTypeT4"),
	TaskSpec("oblique-bending", "Косой изгиб", "tasks.ar3d2", "ShemeType"),
	TaskSpec("eccentric-bending", "Внецентренный изгиб", "tasks.kosoi", "ShemeType"),
	TaskSpec("stress-cube", "Напряжения", "tasks.cube", "ShemeType"),
	TaskSpec("shafts-pipes", "Валы и трубки", "tasks.vali", "ShemeType"),
	TaskSpec("spatial-beams", "Пространственные балки", "tasks.balki3d", "ShemeType"),
)


TASK_SPECS_BY_ID = {spec.identifier: spec for spec in TASK_SPECS}
