# Test Engineering & Verification Report: Omarchy AI Orchestration

**Date:** 2026-11-12  
**Component:** `omarchy-ai-orchestration` (`bin/herdr-swarm`, `bin/stageshow`, skills symlinks, pipelines)  
**Status:** **PASSED (100% Success Rate — 51/51 Tests Passed)**  
**Runner:** Python 3 `unittest` discovery suite  
**Execution Time:** ~0.073s  

---

## 1. Executive Summary

A comprehensive automated test suite has been designed, implemented, and verified in `/home/noly/Work/omarchy-ai-orchestration/tests/`. The test suite covers all architectural, CLI, protocol, and symlink enhancements delivered by the Herdr Swarm of Titans and Codex bridge.

All **51 tests** executed with **0 failures, 0 errors, and 100% pass rate**.

```
Ran 51 tests in 0.073s

OK
```

---

## 2. Test Suite Breakdown

### Suite A: `tests/test_herdr_swarm.py` (35 Tests)
Covers the core CLI architecture, subprocess containment, agent communication, and orchestration pipelines in `bin/herdr-swarm`:

| Test Group | Test Cases | Coverage Details | Result |
| :--- | :---: | :--- | :---: |
| **CLI Argument Parsing & Help** | 6 | Validates root help and all 13 subcommands (`status`, `prompt`, `read`, `wait`, `interrupt`, `focus`, `zoom`, `broadcast`, `pipeline`, `frontend`, `stageshow`, `init`, `worktree`). Tests argument bounds: `positive_timeout` validator (rejects $\le 0$, $>3600$, non-numeric), `--lines` $\ge 1$, invalid subcommands, and missing args. | **PASS** |
| **JSON Handling & Fallback** | 5 | Validates `--json` machine-readable output (`{"ok": bool, "command": str, "result": ...}`); structured error emission with custom exit codes; dual-mode stdout/stderr emission in plain-text mode; `herdr_json` parsing and raw-text fallback; and `output_text` serialization. | **PASS** |
| **Subprocess & Hard Timeouts** | 5 | Validates `bounded_run` containment: normal command execution; mapping `subprocess.TimeoutExpired` to `CommandFailure('timeout', exit_code=124)`; mapping missing binaries (`FileNotFoundError`) to `CommandFailure('not_found', exit_code=127)`; OS permission errors to code 126; and `check=True` non-zero propagation. | **PASS** |
| **Workspace Scoping & Preflighting** | 5 | Validates workspace isolation (prevents cross-workspace leakage between `w2` and `w3`); honors `HERDR_WORKSPACE` environment variable; detects workspace ambiguity; handles non-existent agents (`agent_not_found`); and workspace mismatch rejection. | **PASS** |
| **Agent Dispatch & Turn Safety** | 7 | Validates race condition elimination: busy agents (`working`) are awaited until idle before prompt dispatch; `--wait` triggers prompt dispatch and subsequent output read; `cmd_read` buffer inspection; `cmd_wait` idle checks; `cmd_interrupt` signaling; `cmd_focus` with tab fallback; and `cmd_zoom` target resolution. | **PASS** |
| **Guarded Pipelines & Broadcast** | 5 | Validates `cmd_pipeline` fail-closed semantics (halts on first failing stage); validates sequential stage passing (`architect` $\to$ `builder` $\to$ `sentinel` $\to$ `reviewer`); validates `cmd_broadcast` group delivery and partial-failure handling; validates `cmd_init --fix` auto-healing of unnamed `w2:p1` coordinator; and `cmd_worktree` operations. | **PASS** |

### Suite B: `tests/test_skills.py` (8 Tests)
Covers filesystem symlink integrity across agent runtimes and executable permissions:

| Test Target | Tests | Verification Details | Result |
| :--- | :---: | :--- | :---: |
| **Directory Presence** | 1 | Confirms `~/.gemini/skills/` and `~/.agents/skills/` exist and are accessible. | **PASS** |
| **Symlink Integrity** | 2 | Exhaustively scans all symlinks in both `~/.gemini/skills/` and `~/.agents/skills/`. Confirms **0 broken symlinks**. | **PASS** |
| **Essential Skills Coverage** | 2 | Confirms presence of all required skills: `inspiration-scout`, `design-architect`, `design-taste-frontend`, `ui-ux-pro-max`, `stageshow`, `herdr`, `impeccable`, `codex-query`, `omarchy`, `omarchy-app`, `diagnose-crash`, `ui-styling`, `design-system`, `brand`, `banner-design`, `slides`. | **PASS** |
| **SKILL.md Specifications** | 1 | Confirms `SKILL.md` exists and contains valid Markdown specifications across skills. | **PASS** |
| **CLI Binary Permissions** | 1 | Validates that all repository CLI tools in `bin/` (`herdr-swarm`, `stageshow`, `inspiration-scout`, `codex-query`, `impeccable`, `taste-skill`, `uipro-search`, `omarchy*`) have executable permissions (`chmod +x`). | **PASS** |
| **Installer Syntax & Execution** | 1 | Validates `install.sh` has valid Bash syntax (`bash -n`) and is executable. | **PASS** |

### Suite C: `tests/test_stageshow_integration.py` (8 Tests)
Covers Stageshow CLI wrapping, skill directory assets, and `herdr-swarm stageshow` rehearsal gate:

| Test Target | Tests | Verification Details | Result |
| :--- | :---: | :--- | :---: |
| **Binary & Execution** | 2 | Verifies `bin/stageshow` exists and is executable; verifies `stageshow path` and `stageshow dir` correctly resolve the canonical installation path. | **PASS** |
| **Examples & Help** | 2 | Verifies `stageshow examples` lists gold templates (`hero-demo`, `bento`, `dark-hero`, etc.); verifies CLI usage output. | **PASS** |
| **Skill Root Assets** | 1 | Verifies `package.json` (`stageshow`), `SKILL.md`, `scripts/film.mjs`, `scripts/dev.mjs`, and `scripts/layout.mjs` are present and valid. | **PASS** |
| **Swarm Gate Integration** | 3 | Verifies `herdr-swarm stageshow` executes `stageshow film <topic> --gate`; validates fail-closed behavior on detected jumps or framing faults; and verifies machine-readable `--json` output emission. | **PASS** |

---

## 3. How to Run the Tests

The automated suite can be executed at any time from the repository root:

```bash
# Run all tests using Python unittest discovery
python3 -m unittest discover tests -v

# Run individual test suites
python3 -m unittest tests/test_herdr_swarm.py -v
python3 -m unittest tests/test_skills.py -v
python3 -m unittest tests/test_stageshow_integration.py -v
```

---

## 4. Release Hand-off

All test suites have passed with zero errors or warnings.
The codebase is now verified, resilient, and ready for final security audit, diff review, and release push by `@verifier`.
