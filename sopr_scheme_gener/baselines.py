"""Capture deterministic default render fixtures for the legacy task types."""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

import numpy
from PyQt5.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
from PyQt5.QtGui import QImage

from .task_registry import TASK_SPECS
from .legacy_storage import load_trusted_pickle


BASELINE_SCHEMA_VERSION = 1
DEFAULT_PROFILE = "linux-qt5"


def repository_root():
	return Path(__file__).resolve().parent.parent


def default_baseline_dir():
	return repository_root() / "tests" / "baselines" / DEFAULT_PROFILE


def environment_fingerprint():
	return {
		"platform": platform.system().lower(),
		"python": platform.python_version(),
		"qt": QT_VERSION_STR,
		"pyqt": PYQT_VERSION_STR,
		"numpy": numpy.__version__,
		"qpa_platform": "offscreen",
	}


def image_metrics(path):
	data = path.read_bytes()
	image = QImage.fromData(data, "PNG")
	if image.isNull():
		raise RuntimeError("Invalid PNG produced for {}".format(path))

	non_white_pixels = 0
	for y in range(image.height()):
		for x in range(image.width()):
			color = image.pixelColor(x, y)
			if color.alpha() and (color.red(), color.green(), color.blue()) != (255, 255, 255):
				non_white_pixels += 1

	return {
		"width": image.width(),
		"height": image.height(),
		"sha256": hashlib.sha256(data).hexdigest(),
		"non_white_pixels": non_white_pixels,
		"bytes": len(data),
	}


def capture_one(task_id, output, fixture=None):
	# Imports happen after the caller has selected the offscreen Qt backend.
	from .app import build_parser, create_runtime
	from .devapi import DevBridge

	args = build_parser().parse_args(
		["--type", task_id, "--no-maximize", "--error"]
	)
	runtime = create_runtime(args)
	try:
		bridge = DevBridge(runtime)
		if fixture is not None:
			document = load_trusted_pickle(fixture)
			runtime.window.cw.current_scheme().deserialize(document)
			bridge.dispatch("wait.idle", {})
		result = bridge.dispatch("screenshot", {"target": "canvas"})
		output.parent.mkdir(parents=True, exist_ok=True)
		output.write_bytes(base64.b64decode(result["png_base64"]))
	finally:
		runtime.window.close()
		runtime.app.processEvents()


def _capture_subprocess(task_id, output, timeout, fixture=None):
	env = os.environ.copy()
	env["QT_QPA_PLATFORM"] = "offscreen"
	command = [
		sys.executable,
		"-m",
		"sopr_scheme_gener.baselines",
		"_capture-one",
		task_id,
		str(output),
	]
	if fixture is not None:
		command.extend(["--fixture", str(fixture)])
	completed = subprocess.run(
		command,
		cwd=repository_root(),
		env=env,
		text=True,
		capture_output=True,
		timeout=timeout,
	)
	if completed.returncode != 0 or not output.exists():
		raise RuntimeError(
			"Baseline capture failed for {} (exit {}):\nstdout:\n{}\nstderr:\n{}".format(
				task_id,
				completed.returncode,
				completed.stdout,
				completed.stderr,
			)
		)


def trusted_fixtures():
	root = repository_root()
	paths = sorted((root / ".save").glob("*.dat"))
	paths.extend(sorted((root / "saves" / ".save").glob("*.dat")))
	spec_by_title = {spec.title: spec for spec in TASK_SPECS}
	fixtures = []
	for path in paths:
		document = load_trusted_pickle(path)
		if not isinstance(document, list) or not document or document[0][0] != "name":
			raise RuntimeError("Malformed trusted fixture: {}".format(path))
		title = document[0][1]
		try:
			spec = spec_by_title[title]
		except KeyError:
			raise RuntimeError(
				"Trusted fixture {} uses an unregistered task title {!r}".format(path, title)
			)
		fixtures.append((spec, path))
	return fixtures


def capture_all(output_dir, timeout=30):
	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)
	entries = []

	for spec in TASK_SPECS:
		filename = "{}--default.png".format(spec.identifier)
		output = output_dir / filename
		_capture_subprocess(spec.identifier, output, timeout)
		metrics = image_metrics(output)
		if metrics["non_white_pixels"] == 0:
			raise RuntimeError("Baseline for {} is entirely white".format(spec.identifier))
		entries.append(
			{
				"task_id": spec.identifier,
				"title": spec.title,
				"scenario": "default",
				"file": filename,
				**metrics,
			}
		)

	for spec, fixture in trusted_fixtures():
		digest = fixture.stem[:12]
		filename = "{}--legacy-{}.png".format(spec.identifier, digest)
		output = output_dir / filename
		_capture_subprocess(spec.identifier, output, timeout, fixture=fixture)
		metrics = image_metrics(output)
		if metrics["non_white_pixels"] == 0:
			raise RuntimeError("Legacy baseline for {} is entirely white".format(fixture))
		entries.append(
			{
				"task_id": spec.identifier,
				"title": spec.title,
				"scenario": "legacy:{}".format(fixture.relative_to(repository_root())),
				"source_fixture": str(fixture.relative_to(repository_root())),
				"file": filename,
				**metrics,
			}
		)

	manifest = {
		"schema_version": BASELINE_SCHEMA_VERSION,
		"profile": DEFAULT_PROFILE,
		"environment": environment_fingerprint(),
		"entries": entries,
	}
	manifest_path = output_dir / "manifest.json"
	manifest_path.write_text(
		json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
		encoding="utf-8",
	)
	return manifest


def verify_baselines(baseline_dir, timeout=30):
	baseline_dir = Path(baseline_dir)
	expected = json.loads((baseline_dir / "manifest.json").read_text(encoding="utf-8"))
	with tempfile.TemporaryDirectory(prefix="sopr-baseline-") as temp_dir:
		actual = capture_all(temp_dir, timeout=timeout)
		actual_dir = Path(temp_dir)

		expected_by_key = {
			(entry["task_id"], entry["scenario"]): entry
			for entry in expected["entries"]
		}
		actual_by_key = {
			(entry["task_id"], entry["scenario"]): entry
			for entry in actual["entries"]
		}
		expected_ids = [spec.identifier for spec in TASK_SPECS]
		expected_default_ids = {
			task_id
			for task_id, scenario in expected_by_key
			if scenario == "default"
		}
		actual_default_ids = {
			task_id
			for task_id, scenario in actual_by_key
			if scenario == "default"
		}
		if expected_default_ids != set(expected_ids):
			raise AssertionError("Expected manifest does not cover all registered task IDs")
		if actual_default_ids != set(expected_ids):
			raise AssertionError("Actual capture does not cover all registered task IDs")
		if set(expected_by_key) != set(actual_by_key):
			raise AssertionError("Expected and actual scenario sets differ")

		mismatches = []
		for key_tuple in expected_by_key:
			task_id, scenario = key_tuple
			expected_entry = expected_by_key[key_tuple]
			actual_entry = actual_by_key[key_tuple]
			for key in ("width", "height", "sha256", "non_white_pixels"):
				if expected_entry[key] != actual_entry[key]:
					mismatches.append(
						"{} {} {}: expected {!r}, actual {!r}".format(
							task_id,
							scenario,
							key,
							expected_entry[key],
							actual_entry[key],
						)
					)
			expected_image = baseline_dir / expected_entry["file"]
			if not expected_image.exists():
				mismatches.append("{}: expected PNG is missing".format(task_id))
			actual_image = actual_dir / actual_entry["file"]
			if not actual_image.exists():
				mismatches.append("{}: actual PNG is missing".format(task_id))

		if mismatches:
			raise AssertionError(
				"Render baseline mismatch:\n- {}\n"
				"Run `python -m sopr_scheme_gener.baselines capture` "
				"only after reviewing intentional visual changes.".format(
					"\n- ".join(mismatches)
				)
			)
	return actual


def build_parser():
	parser = argparse.ArgumentParser(prog="sopr-baseline")
	subparsers = parser.add_subparsers(dest="command", required=True)

	capture = subparsers.add_parser("capture")
	capture.add_argument("--output", type=Path, default=default_baseline_dir())
	capture.add_argument("--timeout", type=int, default=30)

	verify = subparsers.add_parser("verify")
	verify.add_argument("--baseline", type=Path, default=default_baseline_dir())
	verify.add_argument("--timeout", type=int, default=30)

	hidden = subparsers.add_parser("_capture-one", help=argparse.SUPPRESS)
	hidden.add_argument("task_id")
	hidden.add_argument("output", type=Path)
	hidden.add_argument("--fixture", type=Path)
	return parser


def main(argv=None):
	args = build_parser().parse_args(argv)
	if args.command == "_capture-one":
		os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
		capture_one(args.task_id, args.output, fixture=args.fixture)
		return 0
	if args.command == "capture":
		manifest = capture_all(args.output, timeout=args.timeout)
		print(
			"Captured {} render baselines in {}".format(
				len(manifest["entries"]),
				args.output,
			)
		)
		return 0
	if args.command == "verify":
		manifest = verify_baselines(args.baseline, timeout=args.timeout)
		print("Verified {} render baselines".format(len(manifest["entries"])))
		return 0
	raise AssertionError("Unhandled command: {}".format(args.command))


if __name__ == "__main__":
	raise SystemExit(main())
