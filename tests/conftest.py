"""Test fixtures and loader helpers for omarchy-ai-orchestration tests."""
from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parent.parent
BIN_HERDR_SWARM = REPO_ROOT / "bin" / "herdr-swarm"


def load_herdr_swarm() -> ModuleType:
    """Load bin/herdr-swarm dynamically as a python module using modern exec_module."""
    loader = SourceFileLoader("herdr_swarm", str(BIN_HERDR_SWARM))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise ImportError(f"Could not create module spec for {BIN_HERDR_SWARM}")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module
