"""Run the regression suite which replaces the initial bug reproducer.

Historical observations remain in docs/BASELINE_AUDIT.md.
Exit 0 now means the automated regression tests passed, not market readiness.
"""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
