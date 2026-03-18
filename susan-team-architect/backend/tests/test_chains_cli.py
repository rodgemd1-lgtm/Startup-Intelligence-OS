"""Tests for chains CLI entry point."""
import subprocess
import sys

import pytest


BACKEND_DIR = str(__import__("pathlib").Path(__file__).resolve().parent.parent)


def test_chains_list():
    result = subprocess.run(
        [sys.executable, "-m", "chains", "--command", "list"],
        capture_output=True,
        text=True,
        cwd=BACKEND_DIR,
    )
    assert result.returncode == 0
    assert "competitive-response" in result.stdout
    assert "daily-cycle" in result.stdout


def test_chains_help():
    result = subprocess.run(
        [sys.executable, "-m", "chains", "--help"],
        capture_output=True,
        text=True,
        cwd=BACKEND_DIR,
    )
    assert result.returncode == 0
    assert "chains" in result.stdout.lower()
