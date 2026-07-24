import json
import os
from pathlib import Path

import pytest
from PyQt5.QtWidgets import QFileDialog

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from sopr_scheme_gener.app import build_parser, create_runtime
from sopr_scheme_gener.baselines import trusted_fixtures
from sopr_scheme_gener.storage import (
	DocumentFormatError,
	FORMAT_NAME,
	FORMAT_VERSION,
)


@pytest.fixture
def context():
	runtime = create_runtime(build_parser().parse_args(["--no-maximize"]))
	try:
		yield runtime
	finally:
		runtime.window.close()


def test_json_document_round_trip_for_every_task(context, tmp_path):
	for spec in context.task_specs:
		context.controller.select(spec.identifier)
		before = context.storage.to_data()
		path = tmp_path / "{}.sopr.json".format(spec.identifier)

		context.storage.save(path)
		raw = path.read_bytes()
		assert not raw.startswith(b"\x80")
		assert json.loads(raw.decode("utf-8"))["format"] == FORMAT_NAME

		after = context.storage.load(path)
		assert after == before
		assert after["version"] == FORMAT_VERSION
		assert after["task_type"] == spec.identifier


def test_trusted_legacy_fixtures_convert_and_round_trip_as_json(context):
	for spec, fixture in trusted_fixtures():
		converted = context.storage.import_trusted_legacy(fixture)
		assert converted["task_type"] == spec.identifier
		serialized = json.dumps(converted, ensure_ascii=False, allow_nan=False)
		parsed = json.loads(serialized)
		assert context.storage.load_data(parsed) == converted


def test_documents_without_new_label_offsets_still_load_and_render(context):
	def remove_offsets(value):
		if isinstance(value, dict):
			for key in tuple(value):
				if key.endswith(("_offset_x", "_offset_y")):
					del value[key]
				else:
					remove_offsets(value[key])
		elif isinstance(value, list):
			for item in value:
				remove_offsets(item)

	for spec in context.task_specs:
		context.controller.select(spec.identifier)
		document = json.loads(
			json.dumps(context.storage.to_data(), ensure_ascii=False)
		)
		remove_offsets(document["task"]["payload"])

		context.storage.load_data(document)
		context.app.processEvents()
		image = context.canvas.make_image()

		assert context.controller.current_spec.identifier == spec.identifier
		assert image.bits().asstring(image.sizeInBytes())


def test_spatial_task_preserves_object_cycles_and_shared_arrays(context):
	context.controller.select("spatial-beams")
	data = context.storage.to_data()
	context.storage.load_data(data)
	task = context.controller.current_scheme.task

	assert task["sections"][0].internal_node.section is task["sections"][0]
	assert task["nodes"][0].sharn_vec is task["nodes"][1].sharn_vec
	assert context.storage.to_data() == data


def test_file_menu_saves_and_opens_json_sidecar_by_image_hash(
	context,
	tmp_path,
	monkeypatch,
):
	context.controller.select("beams")
	image_path = tmp_path / "beam.png"

	monkeypatch.setattr(
		QFileDialog,
		"getSaveFileName",
		lambda *args, **kwargs: (str(image_path), "PNG (*.png)"),
	)
	context.window.save_document_action()
	assert image_path.read_bytes().startswith(b"\x89PNG")
	json_paths, _legacy_paths = context.window.sidecar_paths(image_path)
	sidecar = Path(json_paths[0])
	assert sidecar.parent == tmp_path / ".save"
	assert json.loads(sidecar.read_text(encoding="utf-8"))["task_type"] == "beams"

	context.controller.select("stress-cube")
	monkeypatch.setattr(
		QFileDialog,
		"getOpenFileName",
		lambda *args, **kwargs: (str(image_path), "Изображения (*.png)"),
	)
	context.window.open_document_action()
	assert context.controller.current_spec.identifier == "beams"

	export_path = tmp_path / "plain.png"
	sidecars_before_export = set((tmp_path / ".save").iterdir())
	monkeypatch.setattr(
		QFileDialog,
		"getSaveFileName",
		lambda *args, **kwargs: (str(export_path), "PNG (*.png)"),
	)
	context.window.export_image_action()
	assert export_path.read_bytes().startswith(b"\x89PNG")
	assert set((tmp_path / ".save").iterdir()) == sidecars_before_export


def test_opening_old_image_loads_dat_silently_and_migrates_sidecar(
	context,
	tmp_path,
	monkeypatch,
):
	spec, fixture = next(iter(trusted_fixtures()))
	image_path = tmp_path / "legacy.png"
	image_path.write_bytes(b"legacy image bytes")
	json_paths, legacy_paths = context.window.sidecar_paths(image_path)
	legacy_path = Path(legacy_paths[0])
	legacy_path.parent.mkdir()
	legacy_path.write_bytes(fixture.read_bytes())

	context.controller.select(
		next(
			candidate.identifier
			for candidate in context.task_specs
			if candidate.identifier != spec.identifier
		)
	)
	monkeypatch.setattr(
		QFileDialog,
		"getOpenFileName",
		lambda *args, **kwargs: (str(image_path), "Изображения (*.png)"),
	)
	context.window.open_document_action()

	assert context.controller.current_spec.identifier == spec.identifier
	migrated = Path(json_paths[0])
	assert migrated.exists()
	assert json.loads(migrated.read_text(encoding="utf-8"))["task_type"] == spec.identifier


def test_invalid_documents_are_rejected_before_selection_changes(context, tmp_path):
	context.controller.select("beams")
	data = context.storage.to_data()

	future = json.loads(json.dumps(data))
	future["version"] = FORMAT_VERSION + 1
	with pytest.raises(DocumentFormatError, match="Unsupported document version"):
		context.storage.load_data(future)
	assert context.controller.current_spec.identifier == "beams"

	unknown_task = json.loads(json.dumps(data))
	unknown_task["task_type"] = "unregistered"
	with pytest.raises(DocumentFormatError, match="Unknown task type"):
		context.storage.load_data(unknown_task)
	assert context.controller.current_spec.identifier == "beams"

	future_task = json.loads(json.dumps(data))
	future_task["task"]["version"] += 1
	with pytest.raises(DocumentFormatError, match="Unsupported task schema version"):
		context.storage.load_data(future_task)
	assert context.controller.current_spec.identifier == "beams"

	invalid_setting = json.loads(json.dumps(data))
	invalid_setting["common"]["Ширина в px:"] = "very wide"
	with pytest.raises(DocumentFormatError, match="must be an integer"):
		context.storage.load_data(invalid_setting)
	assert context.controller.current_spec.identifier == "beams"

	malformed = tmp_path / "malformed.sopr.json"
	malformed.write_text('{"value": NaN}', encoding="utf-8")
	with pytest.raises(DocumentFormatError, match="Invalid JSON number"):
		context.storage.load(malformed)


def test_only_storage_compatibility_boundary_imports_pickle_loader():
	package_dir = Path(__file__).resolve().parents[1] / "sopr_scheme_gener"
	offenders = []
	for path in package_dir.glob("*.py"):
		if path.name in {"baselines.py", "legacy_storage.py", "storage.py"}:
			continue
		source = path.read_text(encoding="utf-8")
		if "load_trusted_pickle" in source or "pickle.load" in source:
			offenders.append(path.name)
	assert offenders == []
