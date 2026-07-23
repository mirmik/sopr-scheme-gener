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
	TaskSpec(
		"axial-torsion",
		"Растяжение/сжатие/кручение стержня",
		"tasks.axial_torsion",
		"ShemeTypeT0",
	),
	TaskSpec("beams", "Балки", "tasks.beams", "ShemeType"),
	TaskSpec(
		"rod-system-1",
		"Стержневая система (Тип 1)",
		"tasks.rod_system_1",
		"ShemeTypeT2",
	),
	TaskSpec(
		"rod-system-2",
		"Стержневая система (Тип 2)",
		"tasks.rod_system_2",
		"ShemeTypeT1",
	),
	TaskSpec("plate", "Пластина", "tasks.plate", "ShemeTypeT3"),
	TaskSpec("frames", "Рамы", "tasks.frames", "ShemeTypeT4"),
	TaskSpec(
		"oblique-bending",
		"Косой изгиб",
		"tasks.oblique_bending",
		"ShemeType",
	),
	TaskSpec(
		"eccentric-bending",
		"Внецентренный изгиб",
		"tasks.eccentric_bending",
		"ShemeType",
	),
	TaskSpec("stress-cube", "Напряжения", "tasks.stress_cube", "ShemeType"),
	TaskSpec("shafts-pipes", "Валы и трубки", "tasks.shafts_pipes", "ShemeType"),
	TaskSpec(
		"spatial-beams",
		"Пространственные балки",
		"tasks.spatial_beams",
		"ShemeType",
	),
)


TASK_SPECS_BY_ID = {spec.identifier: spec for spec in TASK_SPECS}
