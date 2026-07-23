from sopr_scheme_gener.task_registry import TASK_SPECS, TASK_SPECS_BY_ID


def test_task_registry_has_unique_stable_ids():
	identifiers = [spec.identifier for spec in TASK_SPECS]
	assert len(identifiers) == 11
	assert len(identifiers) == len(set(identifiers))
	assert set(identifiers) == set(TASK_SPECS_BY_ID)


def test_task_registry_titles_are_not_used_as_ids():
	assert all(spec.identifier != spec.title for spec in TASK_SPECS)
