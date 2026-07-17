"""Run Node tests for javascript/arl_core.js when `node` is available."""

from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

EXTENSION_ROOT = Path(__file__).resolve().parents[1]
JS_TEST = EXTENSION_ROOT / "tests" / "js" / "test_arl_core.mjs"


class JsCoreTests(unittest.TestCase):
    def test_arl_core_js(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node not available")
        result = subprocess.run(
            [node, str(JS_TEST)],
            cwd=EXTENSION_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            self.fail(
                "JS core tests failed:\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )


if __name__ == "__main__":
    unittest.main()
