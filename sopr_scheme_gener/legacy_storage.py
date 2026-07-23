"""Compatibility helpers for explicitly trusted historical pickle documents."""

import pickle
import sys
from pathlib import Path

from PyQt5 import sip


def load_trusted_pickle(path):
	"""Load a legacy document that the caller has already chosen to trust.

	Pickle can execute arbitrary code. This function must never be used for
	automatic discovery or untrusted input.
	"""

	# Older PyQt5 pickles refer to the former top-level ``sip`` module. Modern
	# PyQt5 exposes it as ``PyQt5.sip``.
	sys.modules.setdefault("sip", sip)
	with Path(path).open("rb") as stream:
		return pickle.load(stream)
