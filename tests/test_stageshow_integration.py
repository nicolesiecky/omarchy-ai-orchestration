"""Integration and availability tests for Stageshow and herdr-swarm stageshow gate."""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.conftest import REPO_ROOT, load_herdr_swarm

STAGESHOW_BIN = REPO_ROOT / "bin" / "stageshow"
STAGESHOW_DIR = Path.home() / ".local" / "share" / "agent-skills" / "benjitaylor-skills" / "stageshow"


class TestStageshowIntegrationAndAvailability(unittest.TestCase):
    """Test suite verifying Stageshow CLI wrapper, skill root, and herdr-swarm gate."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_herdr_swarm()

    def test_stageshow_binary_exists_and_executable(self):
        """Verify bin/stageshow exists and is marked executable."""
        self.assertTrue(STAGESHOW_BIN.is_file(), f"Binary missing: {STAGESHOW_BIN}")
        self.assertTrue(subprocess.run(["test", "-x", str(STAGESHOW_BIN)]).returncode == 0, "bin/stageshow not executable")

    def test_stageshow_path_command(self):
        """Verify 'stageshow path' and 'stageshow dir' return the canonical skill directory."""
        res_path = subprocess.run([str(STAGESHOW_BIN), "path"], capture_output=True, text=True)
        self.assertEqual(res_path.returncode, 0)
        self.assertEqual(res_path.stdout.strip(), str(STAGESHOW_DIR))

        res_dir = subprocess.run([str(STAGESHOW_BIN), "dir"], capture_output=True, text=True)
        self.assertEqual(res_dir.returncode, 0)
        self.assertEqual(res_dir.stdout.strip(), str(STAGESHOW_DIR))

    def test_stageshow_examples_command(self):
        """Verify 'stageshow examples' lists standard gold and spec examples."""
        res = subprocess.run([str(STAGESHOW_BIN), "examples"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        output = res.stdout.strip()
        self.assertIn("hero-demo", output)
        self.assertIn("bento", output)

    def test_stageshow_help_output(self):
        """Verify default invocation without args prints CLI usage help."""
        res = subprocess.run([str(STAGESHOW_BIN)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Stageshow CLI (Benji Taylor)", res.stdout)
        self.assertIn("Usage: stageshow <film|dev|layout|path|examples>", res.stdout)
        self.assertIn("film <url>", res.stdout)

    def test_stageshow_directory_assets_and_manifest(self):
        """Verify package.json, SKILL.md, and core scripts exist in the skill root."""
        self.assertTrue(STAGESHOW_DIR.is_dir(), f"Stageshow directory missing: {STAGESHOW_DIR}")

        pkg_json = STAGESHOW_DIR / "package.json"
        self.assertTrue(pkg_json.is_file(), "package.json missing")
        with open(pkg_json, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(manifest.get("name"), "stageshow")

        skill_md = STAGESHOW_DIR / "SKILL.md"
        self.assertTrue(skill_md.is_file(), "SKILL.md missing")
        self.assertIn("Stageshow", skill_md.read_text(encoding="utf-8"))

        scripts_dir = STAGESHOW_DIR / "scripts"
        self.assertTrue((scripts_dir / "film.mjs").is_file(), "film.mjs missing")
        self.assertTrue((scripts_dir / "dev.mjs").is_file(), "dev.mjs missing")
        self.assertTrue((scripts_dir / "layout.mjs").is_file(), "layout.mjs missing")

    def test_herdr_swarm_stageshow_success(self):
        """Verify herdr-swarm stageshow calls stageshow film --gate and returns success."""
        args = argparse.Namespace(topic_or_scenario="hero_demo", timeout=60)
        mock_proc = MagicMock(returncode=0, stdout="rehearsal passed: 0 jumps, 0 framing faults", stderr="")

        with patch.object(self.mod, "bounded_run", return_value=mock_proc) as mock_run:
            with patch.object(sys, "stdout", io.StringIO()) as stream:
                code = self.mod.cmd_stageshow(args)
            self.assertEqual(code, 0)
            mock_run.assert_called_once_with(["stageshow", "film", "hero_demo", "--gate"], 60)
            self.assertIn("rehearsal passed", stream.getvalue())

    def test_herdr_swarm_stageshow_gate_failure(self):
        """Verify herdr-swarm stageshow returns non-zero error when gate detects jumps/framing faults."""
        args = argparse.Namespace(topic_or_scenario="broken_demo", timeout=60)
        mock_proc = MagicMock(returncode=1, stdout="", stderr="rehearsal failed: jump at 02.4s, cut by the crop")

        with patch.object(self.mod, "bounded_run", return_value=mock_proc):
            with patch.object(sys, "stderr", io.StringIO()) as stream:
                code = self.mod.cmd_stageshow(args)
            self.assertEqual(code, 1)
            self.assertIn("rehearsal failed", stream.getvalue())

    def test_herdr_swarm_stageshow_json_emission(self):
        """Verify herdr-swarm stageshow emits machine-readable JSON when --json is provided."""
        args = argparse.Namespace(topic_or_scenario="hero_demo", timeout=60)
        mock_proc = MagicMock(returncode=0, stdout="contact sheet generated: /tmp/sheet.png", stderr="")

        self.mod.JSON_MODE = True
        try:
            with patch.object(self.mod, "bounded_run", return_value=mock_proc):
                stream = io.StringIO()
                with patch.object(sys, "stdout", stream):
                    code = self.mod.cmd_stageshow(args)
                self.assertEqual(code, 0)
                data = json.loads(stream.getvalue())
                self.assertTrue(data["ok"])
                self.assertEqual(data["command"], "stageshow")
                self.assertIn("contact sheet generated", data["result"])
        finally:
            self.mod.JSON_MODE = False


if __name__ == "__main__":
    unittest.main()
