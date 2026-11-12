"""Unit and integration tests for bin/herdr-swarm CLI and agent dispatch."""
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

from tests.conftest import BIN_HERDR_SWARM, load_herdr_swarm


class TestHerdrSwarmCLIArgumentParsing(unittest.TestCase):
    """Test suite covering CLI argument parsing, subcommands, and help output."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_herdr_swarm()

    def test_main_help_output(self):
        """Verify root help displays all 13 subcommands and program description."""
        parser = self.mod.build_parser()
        stream = io.StringIO()
        with patch.object(sys, "stdout", stream):
            with self.assertRaises(SystemExit) as cm:
                parser.parse_args(["--help"])
            self.assertEqual(cm.exception.code, 0)

        help_text = stream.getvalue()
        self.assertIn("Workspace-aware Herdr agent orchestration", help_text)
        expected_subcommands = [
            "status", "prompt", "read", "wait", "interrupt",
            "focus", "zoom", "broadcast", "pipeline", "frontend",
            "stageshow", "init", "worktree"
        ]
        for cmd in expected_subcommands:
            self.assertIn(cmd, help_text)

    def test_subcommand_help_messages(self):
        """Verify each subcommand responds to --help with specific usage."""
        subcommands = [
            ("status", ["--workspace", "--json"]),
            ("prompt", ["agent", "prompt_text", "--wait", "--timeout", "--json"]),
            ("read", ["agent", "--source", "--lines", "--json"]),
            ("wait", ["agent", "--until", "--timeout", "--json"]),
            ("interrupt", ["agent", "--json"]),
            ("focus", ["agent_or_tab", "--json"]),
            ("zoom", ["agent_or_pane", "--json"]),
            ("broadcast", ["text", "--timeout", "--json"]),
            ("pipeline", ["task", "--timeout", "--json"]),
            ("frontend", ["topic", "kind", "type", "--timeout", "--json"]),
            ("stageshow", ["topic_or_scenario", "--timeout", "--json"]),
            ("init", ["--fix", "--json"]),
            ("worktree", ["{create,list,remove}", "args", "--timeout", "--json"]),
        ]
        for subcmd, expected_args in subcommands:
            with self.subTest(subcommand=subcmd):
                parser = self.mod.build_parser()
                stream = io.StringIO()
                with patch.object(sys, "stdout", stream):
                    with self.assertRaises(SystemExit) as cm:
                        parser.parse_args([subcmd, "--help"])
                    self.assertEqual(cm.exception.code, 0)
                sub_help = stream.getvalue()
                for arg in expected_args:
                    self.assertIn(arg, sub_help)

    def test_positive_timeout_validation(self):
        """Verify timeout validator accepts valid values and rejects <= 0, > 3600, non-floats."""
        self.assertEqual(self.mod.positive_timeout("10"), 10.0)
        self.assertEqual(self.mod.positive_timeout("0.5"), 0.5)
        self.assertEqual(self.mod.positive_timeout("3600"), 3600.0)

        with self.assertRaises(argparse.ArgumentTypeError):
            self.mod.positive_timeout("0")
        with self.assertRaises(argparse.ArgumentTypeError):
            self.mod.positive_timeout("-5")
        with self.assertRaises(argparse.ArgumentTypeError):
            self.mod.positive_timeout("3601")
        with self.assertRaises(argparse.ArgumentTypeError):
            self.mod.positive_timeout("invalid")

    def test_missing_subcommand_fails(self):
        """Invoking herdr-swarm without subcommand exits with error code 2."""
        parser = self.mod.build_parser()
        with patch.object(sys, "stderr", io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                parser.parse_args([])
            self.assertEqual(cm.exception.code, 2)

    def test_invalid_subcommand_fails(self):
        """Invoking herdr-swarm with invalid subcommand exits with code 2."""
        parser = self.mod.build_parser()
        with patch.object(sys, "stderr", io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                parser.parse_args(["nonexistent_subcmd"])
            self.assertEqual(cm.exception.code, 2)

    def test_lines_argument_validation(self):
        """Verify main() enforces --lines >= 1."""
        with patch.object(sys, "stderr", io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                self.mod.main(["read", "builder", "--lines", "0"])
            self.assertEqual(cm.exception.code, 2)


class TestHerdrSwarmJSONAndErrorFallback(unittest.TestCase):
    """Test suite covering JSON emit, fallback modes, and CommandFailure handling."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_herdr_swarm()

    def setUp(self):
        self.mod.JSON_MODE = False

    def tearDown(self):
        self.mod.JSON_MODE = False

    def test_emit_json_success(self):
        """In JSON mode, emit outputs valid JSON with ok=True, command and result."""
        self.mod.JSON_MODE = True
        stream = io.StringIO()
        with patch.object(sys, "stdout", stream):
            code = self.mod.emit(True, "test_cmd", result={"foo": "bar"})
        self.assertEqual(code, 0)
        data = json.loads(stream.getvalue())
        self.assertTrue(data["ok"])
        self.assertEqual(data["command"], "test_cmd")
        self.assertEqual(data["result"], {"foo": "bar"})

    def test_emit_json_failure(self):
        """In JSON mode, emit outputs valid JSON with ok=False and error details."""
        self.mod.JSON_MODE = True
        stream = io.StringIO()
        err = self.mod.CommandFailure("test_err", "Failure description", details={"extra": 123}, exit_code=42)
        with patch.object(sys, "stdout", stream):
            code = self.mod.emit(False, "test_cmd", error=err)
        self.assertEqual(code, 42)
        data = json.loads(stream.getvalue())
        self.assertFalse(data["ok"])
        self.assertEqual(data["command"], "test_cmd")
        self.assertEqual(data["error"]["code"], "test_err")
        self.assertEqual(data["error"]["message"], "Failure description")
        self.assertEqual(data["error"]["details"], {"extra": 123})

    def test_emit_plain_text_modes(self):
        """In text mode, output goes to stdout (for ok) or stderr (for error)."""
        self.mod.JSON_MODE = False
        out_stream = io.StringIO()
        err_stream = io.StringIO()

        with patch.object(sys, "stdout", out_stream):
            code_ok = self.mod.emit(True, "test", result="Success message")
        self.assertEqual(code_ok, 0)
        self.assertIn("Success message", out_stream.getvalue())

        err = self.mod.CommandFailure("failed", "Something went wrong", details="Trace info", exit_code=7)
        with patch.object(sys, "stderr", err_stream):
            code_err = self.mod.emit(False, "test", error=err)
        self.assertEqual(code_err, 7)
        self.assertIn("Error [failed]: Something went wrong", err_stream.getvalue())
        self.assertIn("Trace info", err_stream.getvalue())

    def test_herdr_json_parser_and_fallback(self):
        """herdr_json returns parsed dict if valid JSON, string if not JSON, raises on failure."""
        # 1. Valid JSON
        mock_proc = MagicMock(returncode=0, stdout='{"result": {"count": 3}}', stderr="")
        with patch.object(self.mod, "bounded_run", return_value=mock_proc):
            res = self.mod.herdr_json("agent", "list")
            self.assertEqual(res, {"result": {"count": 3}})

        # 2. Raw text fallback
        mock_proc_text = MagicMock(returncode=0, stdout="plain agent listing text", stderr="")
        with patch.object(self.mod, "bounded_run", return_value=mock_proc_text):
            res = self.mod.herdr_json("agent", "list")
            self.assertEqual(res, "plain agent listing text")

        # 3. Command failure
        mock_proc_fail = MagicMock(returncode=1, stdout="", stderr="herdr connection refused")
        with patch.object(self.mod, "bounded_run", return_value=mock_proc_fail):
            with self.assertRaises(self.mod.CommandFailure) as cm:
                self.mod.herdr_json("agent", "list")
            self.assertEqual(cm.exception.code, "herdr_failed")
            self.assertEqual(cm.exception.exit_code, 1)

    def test_output_text_formatting(self):
        """Verify output_text helper stringifies correctly."""
        self.assertEqual(self.mod.output_text("hello  "), "hello")
        self.assertEqual(self.mod.output_text({"a": 1}), '{"a": 1}')
        self.assertEqual(self.mod.output_text(None), "")


class TestHerdrSwarmSubprocessAndTimeouts(unittest.TestCase):
    """Test suite covering subprocess execution, hard timeouts, and error mappings."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_herdr_swarm()

    def test_bounded_run_success(self):
        """Verify bounded_run executes a command cleanly within limits."""
        res = self.mod.bounded_run([sys.executable, "-c", "print('hello from test')"], timeout=5)
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "hello from test")

    def test_bounded_run_timeout_expired(self):
        """Verify bounded_run maps subprocess.TimeoutExpired to CommandFailure('timeout', exit_code=124)."""
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=["sleep", "10"], timeout=0.1, output="partial")):
            with self.assertRaises(self.mod.CommandFailure) as cm:
                self.mod.bounded_run(["sleep", "10"], timeout=0.1)
            self.assertEqual(cm.exception.code, "timeout")
            self.assertEqual(cm.exception.exit_code, 124)
            self.assertIn("Command timed out", cm.exception.message)

    def test_bounded_run_file_not_found(self):
        """Verify bounded_run maps FileNotFoundError to CommandFailure('not_found', exit_code=127)."""
        with patch("subprocess.run", side_effect=FileNotFoundError("Executable does not exist")):
            with self.assertRaises(self.mod.CommandFailure) as cm:
                self.mod.bounded_run(["non_existent_binary_xyz"], timeout=5)
            self.assertEqual(cm.exception.code, "not_found")
            self.assertEqual(cm.exception.exit_code, 127)

    def test_bounded_run_os_error(self):
        """Verify bounded_run maps OSError to CommandFailure('os_error', exit_code=126)."""
        with patch("subprocess.run", side_effect=PermissionError("Permission denied")):
            with self.assertRaises(self.mod.CommandFailure) as cm:
                self.mod.bounded_run(["forbidden_binary"], timeout=5)
            self.assertEqual(cm.exception.code, "os_error")
            self.assertEqual(cm.exception.exit_code, 126)

    def test_bounded_run_check_flag(self):
        """Verify check=True raises CommandFailure('subprocess_failed') on non-zero exit."""
        with self.assertRaises(self.mod.CommandFailure) as cm:
            self.mod.bounded_run([sys.executable, "-c", "import sys; sys.exit(4)"], timeout=5, check=True)
        self.assertEqual(cm.exception.code, "subprocess_failed")
        self.assertEqual(cm.exception.exit_code, 4)


class TestHerdrAgentCommunicationAndOrchestration(unittest.TestCase):
    """Test suite covering workspace scoping, agent preflighting, and guarded pipelines."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_herdr_swarm()

    def setUp(self):
        self.sample_agents = [
            {"name": "coordinator", "agent": "antigravity", "workspace_id": "w2", "tab_id": "w2", "pane_id": "p1", "status": "idle"},
            {"name": "builder", "agent": "codex", "workspace_id": "w2", "tab_id": "w2", "pane_id": "p2", "status": "idle"},
            {"name": "craftsman", "agent": "antigravity", "workspace_id": "w2", "tab_id": "w2", "pane_id": "p9", "status": "idle"},
            {"name": "architect", "agent": "codex", "workspace_id": "w2", "tab_id": "w2", "pane_id": "p6", "status": "idle"},
            {"name": "reviewer", "agent": "antigravity", "workspace_id": "w2", "tab_id": "w2", "pane_id": "p5", "status": "idle"},
            {"name": "foreign_agent", "agent": "codex", "workspace_id": "w3", "tab_id": "w3", "pane_id": "p1", "status": "idle"},
        ]

    def test_workspace_scoping_and_filter(self):
        """Verify agents are correctly scoped to workspace w2 and foreign workspace w3 is isolated."""
        scoped = self.mod.filter_workspace(self.sample_agents, "w2")
        self.assertEqual(len(scoped), 5)
        names = {a["name"] for a in scoped}
        self.assertNotIn("foreign_agent", names)
        self.assertIn("builder", names)

    def test_current_workspace_detection(self):
        """Verify current_workspace honors HERDR_WORKSPACE environment variable."""
        with patch.dict("os.environ", {"HERDR_WORKSPACE": "w2"}):
            ws = self.mod.current_workspace(self.sample_agents)
            self.assertEqual(ws, "w2")

    def test_cmd_status_formatting(self):
        """Verify cmd_status prints formatted table and returns 0."""
        args = argparse.Namespace(workspace="w2")
        stream = io.StringIO()
        with patch.object(self.mod, "get_agents", return_value=self.sample_agents):
            with patch.object(sys, "stdout", stream):
                code = self.mod.cmd_status(args)
        self.assertEqual(code, 0)
        output = stream.getvalue()
        self.assertIn("Workspace: w2", output)
        self.assertIn("builder", output)
        self.assertIn("coordinator", output)

    def test_cmd_status_ambiguous_workspace(self):
        """cmd_status raises workspace_ambiguous when agents span multiple workspaces and none selected."""
        args = argparse.Namespace(workspace=None)
        with patch.object(self.mod, "get_agents", return_value=self.sample_agents):
            with patch.object(self.mod, "current_workspace", return_value=None):
                with patch.object(sys, "stderr", io.StringIO()):
                    code = self.mod.cmd_status(args)
                self.assertEqual(code, 1)

    def test_preflight_agent_not_found(self):
        """preflight_agent raises agent_not_found when target does not exist in Herdr."""
        with patch.object(self.mod, "herdr_json", return_value={"result": {"agent": None}}):
            with self.assertRaises(self.mod.CommandFailure) as cm:
                self.mod.preflight_agent("ghost_agent", timeout=5)
            self.assertEqual(cm.exception.code, "agent_not_found")

    def test_preflight_agent_workspace_mismatch(self):
        """preflight_agent rejects target if it belongs to another workspace."""
        agent_data = {"result": {"agent": {"name": "foreign_agent", "workspace_id": "w3"}}}
        with patch.object(self.mod, "herdr_json", return_value=agent_data):
            with patch.object(self.mod, "get_agents", return_value=self.sample_agents):
                with patch.object(self.mod, "current_workspace", return_value="w2"):
                    with self.assertRaises(self.mod.CommandFailure) as cm:
                        self.mod.preflight_agent("foreign_agent", timeout=5)
                    self.assertEqual(cm.exception.code, "workspace_mismatch")

    def test_preflight_busy_agent_waits_until_idle(self):
        """cmd_prompt must invoke wait_agent_idle if agent is not in idle/done state."""
        busy_agent = {"name": "builder", "workspace_id": "w2", "agent_status": "working"}
        args = argparse.Namespace(agent="builder", prompt_text="build feature", timeout=30, wait=False)

        with patch.object(self.mod, "preflight_agent", return_value=busy_agent):
            with patch.object(self.mod, "wait_agent_idle") as mock_wait:
                with patch.object(self.mod, "bounded_run", return_value=MagicMock(returncode=0, stdout="dispatched")):
                    with patch.object(sys, "stdout", io.StringIO()):
                        code = self.mod.cmd_prompt(args)
                    self.assertEqual(code, 0)
                    mock_wait.assert_called_once_with("builder", 30, "idle")

    def test_cmd_prompt_with_wait_and_read(self):
        """cmd_prompt with --wait dispatches and then reads recent agent output."""
        idle_agent = {"name": "builder", "workspace_id": "w2", "agent_status": "idle"}
        args = argparse.Namespace(agent="builder", prompt_text="build feature", timeout=30, wait=True)

        with patch.object(self.mod, "preflight_agent", return_value=idle_agent):
            with patch.object(self.mod, "bounded_run") as mock_run:
                mock_run.side_effect = [
                    MagicMock(returncode=0, stdout="turn 1"),
                    MagicMock(returncode=0, stdout="Feature built successfully")
                ]
                with patch.object(sys, "stdout", io.StringIO()):
                    code = self.mod.cmd_prompt(args)
                self.assertEqual(code, 0)
                self.assertEqual(mock_run.call_count, 2)

    def test_cmd_read_success(self):
        """cmd_read reads agent buffer and prints output."""
        args = argparse.Namespace(agent="builder", source="recent-unwrapped", lines=50)
        mock_proc = MagicMock(returncode=0, stdout="Agent output lines")
        with patch.object(self.mod, "bounded_run", return_value=mock_proc):
            with patch.object(sys, "stdout", io.StringIO()) as stream:
                code = self.mod.cmd_read(args)
            self.assertEqual(code, 0)
            self.assertIn("Agent output lines", stream.getvalue())

    def test_cmd_wait_success(self):
        """cmd_wait waits for agent idle and prints result."""
        args = argparse.Namespace(agent="builder", timeout=30, until="idle")
        with patch.object(self.mod, "wait_agent_idle", return_value="agent is idle"):
            with patch.object(sys, "stdout", io.StringIO()) as stream:
                code = self.mod.cmd_wait(args)
            self.assertEqual(code, 0)
            self.assertIn("agent is idle", stream.getvalue())

    def test_cmd_interrupt_success(self):
        """cmd_interrupt triggers agent interrupt."""
        args = argparse.Namespace(agent="builder")
        mock_proc = MagicMock(returncode=0, stdout="Interrupted")
        with patch.object(self.mod, "bounded_run", return_value=mock_proc):
            with patch.object(sys, "stdout", io.StringIO()):
                code = self.mod.cmd_interrupt(args)
            self.assertEqual(code, 0)

    def test_cmd_focus_with_tab_fallback(self):
        """cmd_focus attempts agent focus and falls back to tab focus if returncode != 0."""
        args = argparse.Namespace(agent_or_tab="w2")
        mock_proc_fail = MagicMock(returncode=1, stdout="", stderr="agent not found")
        mock_proc_ok = MagicMock(returncode=0, stdout="Focused tab w2")
        with patch.object(self.mod, "bounded_run", side_effect=[mock_proc_fail, mock_proc_ok]):
            with patch.object(sys, "stdout", io.StringIO()) as stream:
                code = self.mod.cmd_focus(args)
            self.assertEqual(code, 0)
            self.assertIn("Focused tab w2", stream.getvalue())

    def test_cmd_zoom_pane_resolution(self):
        """cmd_zoom resolves target pane and toggles zoom."""
        args = argparse.Namespace(agent_or_pane="builder")
        agent_data = {"result": {"agent": {"name": "builder", "pane_id": "w2:p2"}}}
        mock_proc = MagicMock(returncode=0, stdout="Zoomed pane w2:p2")
        with patch.object(self.mod, "herdr_json", return_value=agent_data):
            with patch.object(self.mod, "bounded_run", return_value=mock_proc):
                with patch.object(sys, "stdout", io.StringIO()) as stream:
                    code = self.mod.cmd_zoom(args)
                self.assertEqual(code, 0)
                self.assertIn("Zoomed pane w2:p2", stream.getvalue())

    def test_cmd_broadcast_success(self):
        """cmd_broadcast sends message to default agent group (builder, craftsman, architect)."""
        args = argparse.Namespace(text="Update guidelines", timeout=30)
        mock_proc = MagicMock(returncode=0, stdout="ok")
        with patch.object(self.mod, "bounded_run", return_value=mock_proc):
            with patch.object(sys, "stdout", io.StringIO()):
                code = self.mod.cmd_broadcast(args)
            self.assertEqual(code, 0)

    def test_cmd_broadcast_partial_failure(self):
        """cmd_broadcast reports partial_failure if one agent fails."""
        args = argparse.Namespace(text="Update guidelines", timeout=30)
        # builder ok, craftsman fails, architect ok
        side_effects = [
            MagicMock(returncode=0, stdout="ok"),
            MagicMock(returncode=1, stdout="", stderr="craftsman busy"),
            MagicMock(returncode=0, stdout="ok")
        ]
        with patch.object(self.mod, "bounded_run", side_effect=side_effects):
            with patch.object(sys, "stderr", io.StringIO()):
                code = self.mod.cmd_broadcast(args)
            self.assertEqual(code, 1)

    def test_pipeline_fail_closed_on_stage_error(self):
        """Pipeline must halt immediately if any stage fails and not execute downstream stages."""
        args = argparse.Namespace(task="refactor core", timeout=60)

        # architect succeeds, but builder fails
        def fake_prompt_and_read(agent, prompt, timeout, **kwargs):
            if agent == "architect":
                return "Architect design contracts and types."
            if agent == "builder":
                raise self.mod.CommandFailure("builder_crash", "Builder compilation failed", exit_code=1)
            return "Should not be reached"

        with patch.object(self.mod, "prompt_and_read", side_effect=fake_prompt_and_read):
            with patch.object(sys, "stderr", io.StringIO()):
                code = self.mod.cmd_pipeline(args)
            self.assertEqual(code, 1)

    def test_pipeline_happy_path(self):
        """Pipeline runs all 3 stages in sequence, passing architect output to builder."""
        args = argparse.Namespace(task="implement auth", timeout=60)
        captured_prompts: dict[str, str] = {}

        def fake_prompt_and_read(agent, prompt, timeout, **kwargs):
            captured_prompts[agent] = prompt
            return f"Output from {agent}"

        with patch.object(self.mod, "prompt_and_read", side_effect=fake_prompt_and_read):
            with patch.object(sys, "stderr", io.StringIO()):
                with patch.object(sys, "stdout", io.StringIO()):
                    code = self.mod.cmd_pipeline(args)
            self.assertEqual(code, 0)
            self.assertIn("architect", captured_prompts)
            self.assertIn("builder", captured_prompts)
            self.assertIn("reviewer", captured_prompts)
            self.assertNotIn("sentinel", captured_prompts)
            # Verify builder received architect contracts
            self.assertIn("ARCHITECTURE CONTRACTS:\nOutput from architect", captured_prompts["builder"])

    def test_cmd_init_fix_heals_unnamed_coordinator(self):
        """cmd_init --fix identifies unnamed w2:p1 pane and renames it to coordinator."""
        unhealed_agents = [
            {"name": None, "agent": "antigravity", "workspace_id": "w2", "tab_id": "w2", "pane_id": "p1", "status": "idle"},
            {"name": "builder", "agent": "codex", "workspace_id": "w2", "tab_id": "w2", "pane_id": "p2", "status": "idle"},
        ]
        args = argparse.Namespace(fix=True)

        rename_called = False
        def fake_bounded_run(cmd, timeout):
            nonlocal rename_called
            if cmd == ["herdr", "agent", "rename", "w2:p1", "coordinator"]:
                rename_called = True
                return MagicMock(returncode=0, stdout="renamed")
            return MagicMock(returncode=0, stdout="")

        with patch.object(self.mod, "get_agents", return_value=unhealed_agents):
            with patch.object(self.mod, "bounded_run", side_effect=fake_bounded_run):
                with patch.object(self.mod, "current_workspace", return_value="w2"):
                    with patch.object(sys, "stdout", io.StringIO()):
                        code = self.mod.cmd_init(args)
                    self.assertEqual(code, 0)
                    self.assertTrue(rename_called)
                    self.assertEqual(unhealed_agents[0]["name"], "coordinator")

    def test_cmd_worktree_actions(self):
        """cmd_worktree dispatches herdr worktree <action>."""
        args = argparse.Namespace(action="list", args=[], timeout=30)
        mock_proc = MagicMock(returncode=0, stdout="worktree-1 (main)")
        with patch.object(self.mod, "bounded_run", return_value=mock_proc):
            with patch.object(sys, "stdout", io.StringIO()) as stream:
                code = self.mod.cmd_worktree(args)
            self.assertEqual(code, 0)
            self.assertIn("worktree-1", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
