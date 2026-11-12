"""Unit and verification tests for skills, symlinks, and binary permissions."""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

GEMINI_SKILLS = Path.home() / ".gemini" / "skills"
AGENTS_SKILLS = Path.home() / ".agents" / "skills"


class TestSkillsAndSymlinksVerification(unittest.TestCase):
    """Test suite verifying skills directories, symlink integrity, and permissions."""

    def test_skills_directories_exist(self):
        """Verify ~/.gemini/skills and ~/.agents/skills exist and are directories."""
        self.assertTrue(GEMINI_SKILLS.exists(), f"Directory missing: {GEMINI_SKILLS}")
        self.assertTrue(GEMINI_SKILLS.is_dir(), f"Not a directory: {GEMINI_SKILLS}")
        self.assertTrue(AGENTS_SKILLS.exists(), f"Directory missing: {AGENTS_SKILLS}")
        self.assertTrue(AGENTS_SKILLS.is_dir(), f"Not a directory: {AGENTS_SKILLS}")

    def test_no_broken_symlinks_in_gemini_skills(self):
        """Verify every symlink in ~/.gemini/skills resolves to a valid existing target."""
        broken: list[tuple[str, str]] = []
        for item in GEMINI_SKILLS.iterdir():
            if item.is_symlink():
                target = os.readlink(item)
                if not item.exists():
                    broken.append((item.name, target))
        self.assertEqual(broken, [], f"Found broken symlinks in {GEMINI_SKILLS}: {broken}")

    def test_no_broken_symlinks_in_agents_skills(self):
        """Verify every symlink in ~/.agents/skills resolves to a valid existing target."""
        broken: list[tuple[str, str]] = []
        for item in AGENTS_SKILLS.iterdir():
            if item.is_symlink():
                target = os.readlink(item)
                if not item.exists():
                    broken.append((item.name, target))
        self.assertEqual(broken, [], f"Found broken symlinks in {AGENTS_SKILLS}: {broken}")

    def test_essential_skills_present_in_gemini(self):
        """Verify essential frontend and orchestration skills exist in ~/.gemini/skills."""
        expected = [
            "inspiration-scout",
            "design-architect",
            "design-taste-frontend",
            "ui-ux-pro-max",
            "stageshow",
            "herdr",
            "impeccable",
            "design-system",
            "ui-styling",
            "brand",
            "banner-design",
            "slides",
        ]
        missing = [skill for skill in expected if not (GEMINI_SKILLS / skill).exists()]
        self.assertEqual(missing, [], f"Missing skills in {GEMINI_SKILLS}: {missing}")

    def test_essential_skills_present_in_agents(self):
        """Verify essential orchestration skills exist in ~/.agents/skills."""
        expected = [
            "inspiration-scout",
            "design-architect",
            "design-taste-frontend",
            "ui-ux-pro-max",
            "stageshow",
            "herdr",
            "impeccable",
            "codex-query",
            "omarchy",
            "omarchy-app",
            "diagnose-crash",
        ]
        missing = [skill for skill in expected if not (AGENTS_SKILLS / skill).exists()]
        self.assertEqual(missing, [], f"Missing skills in {AGENTS_SKILLS}: {missing}")

    def test_skill_markdown_integrity(self):
        """Verify that essential skills contain a non-empty SKILL.md specification file."""
        skills_to_check = [
            GEMINI_SKILLS / "stageshow",
            GEMINI_SKILLS / "inspiration-scout",
            GEMINI_SKILLS / "design-architect",
            GEMINI_SKILLS / "ui-ux-pro-max",
            AGENTS_SKILLS / "codex-query",
            AGENTS_SKILLS / "omarchy",
        ]
        for skill_dir in skills_to_check:
            with self.subTest(skill=skill_dir.name):
                skill_md = skill_dir / "SKILL.md"
                self.assertTrue(skill_md.is_file(), f"SKILL.md missing in {skill_dir}")
                content = skill_md.read_text(encoding="utf-8").strip()
                self.assertGreater(len(content), 20, f"SKILL.md in {skill_dir} is too short or empty")

    def test_bin_executables_permissions(self):
        """Verify all CLI scripts in bin/ have executable bits set (chmod +x)."""
        bin_dir = REPO_ROOT / "bin"
        self.assertTrue(bin_dir.is_dir(), f"Missing bin directory: {bin_dir}")

        expected_binaries = [
            "herdr-swarm",
            "stageshow",
            "inspiration-scout",
            "codex-query",
            "impeccable",
            "taste-skill",
            "uipro-search",
            "omarchy",
            "omarchy-agent",
            "omarchy-default-agent",
            "omarchy-agent-usage-antigravity",
            "omarchy-agent-usage-update",
        ]
        for name in expected_binaries:
            with self.subTest(binary=name):
                p = bin_dir / name
                self.assertTrue(p.exists(), f"Binary missing in bin/: {name}")
                self.assertTrue(os.access(p, os.X_OK), f"Binary is not executable: {name}")

    def test_install_script_syntax_and_executable(self):
        """Verify install.sh has valid bash syntax and is executable."""
        install_sh = REPO_ROOT / "install.sh"
        self.assertTrue(install_sh.is_file(), "install.sh missing")
        self.assertTrue(os.access(install_sh, os.X_OK), "install.sh is not executable")

        res = subprocess.run(["bash", "-n", str(install_sh)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"install.sh bash syntax error: {res.stderr}")


if __name__ == "__main__":
    unittest.main()
