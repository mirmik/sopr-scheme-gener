"""Compatibility helpers for explicitly trusted historical pickle documents."""

from importlib import import_module
import pickle
import sys
from pathlib import Path

from PyQt5 import sip


LEGACY_TASK_MODULE_ALIASES = {
	"tasks.task0": "tasks.axial_torsion",
	"tasks.balki": "tasks.beams",
	"tasks.sharn_sterhen": "tasks.rod_system_1",
	"tasks.star": "tasks.rod_system_2",
	"tasks.plastina": "tasks.plate",
	"tasks.fermes": "tasks.frames",
	"tasks.ar3d2": "tasks.oblique_bending",
	"tasks.kosoi": "tasks.eccentric_bending",
	"tasks.cube": "tasks.stress_cube",
	"tasks.vali": "tasks.shafts_pipes",
	"tasks.balki3d": "tasks.spatial_beams",
}


def install_legacy_task_module_aliases():
	"""Expose renamed task modules only for explicit trusted-pickle import."""
	for old_name, current_name in LEGACY_TASK_MODULE_ALIASES.items():
		if old_name not in sys.modules:
			sys.modules[old_name] = import_module(current_name)


def load_trusted_pickle(path):
	"""Load a legacy document that the caller has already chosen to trust.

	Pickle can execute arbitrary code. This function must never be used for
	automatic discovery or untrusted input.
	"""

	# Older PyQt5 pickles refer to the former top-level ``sip`` module. Modern
	# PyQt5 exposes it as ``PyQt5.sip``.
	sys.modules.setdefault("sip", sip)
	install_legacy_task_module_aliases()
	with Path(path).open("rb") as stream:
		return pickle.load(stream)
