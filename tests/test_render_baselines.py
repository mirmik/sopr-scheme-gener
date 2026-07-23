from pathlib import Path
import sys

import pytest

from sopr_scheme_gener.baselines import (
	default_baseline_dir,
	environment_fingerprint,
	verify_baselines,
)

pytestmark = pytest.mark.skipif(
	not sys.platform.startswith("linux"),
	reason="The committed reference images use the linux-qt5 profile",
)


def test_default_render_baselines():
	baseline_dir = default_baseline_dir()
	assert baseline_dir == Path("tests/baselines/linux-qt5").resolve()
	assert environment_fingerprint()["platform"] == "linux"
	manifest = verify_baselines(baseline_dir)
	assert len(manifest["entries"]) == 22
