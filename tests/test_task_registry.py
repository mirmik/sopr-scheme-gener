from pathlib import Path

from sopr_scheme_gener.task_registry import TASK_SPECS, TASK_SPECS_BY_ID


def test_task_registry_has_unique_stable_ids():
	identifiers = [spec.identifier for spec in TASK_SPECS]
	assert len(identifiers) == 11
	assert len(identifiers) == len(set(identifiers))
	assert set(identifiers) == set(TASK_SPECS_BY_ID)


def test_task_registry_titles_are_not_used_as_ids():
	assert all(spec.identifier != spec.title for spec in TASK_SPECS)


def test_task_module_names_follow_public_identifiers():
	assert all(
		spec.module == "tasks." + spec.identifier.replace("-", "_")
		for spec in TASK_SPECS
	)


def test_legacy_task_module_files_are_gone():
	tasks = Path(__file__).resolve().parents[1] / "tasks"
	old_names = {
		"task0.py",
		"balki.py",
		"sharn_sterhen.py",
		"star.py",
		"plastina.py",
		"fermes.py",
		"ar3d2.py",
		"kosoi.py",
		"cube.py",
		"vali.py",
		"balki3d.py",
	}
	assert not old_names.intersection(path.name for path in tasks.iterdir())
