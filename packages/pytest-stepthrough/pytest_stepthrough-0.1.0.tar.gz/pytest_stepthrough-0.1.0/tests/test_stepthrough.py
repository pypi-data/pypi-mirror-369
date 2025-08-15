pytest_plugins = ["pytester"]

import builtins
import pytest
from pathlib import Path
from _pytest.capture import CaptureManager


def _add_src_to_path(pytester):
    pytester.syspathinsert(Path(__file__).resolve().parents[1] / "src")


def test_step_prompts_after_each_test(pytester, monkeypatch):
    _add_src_to_path(pytester)
    pytester.makepyfile(
        test_a="""
        def test_one():
            assert True
        def test_two():
            assert True
        """,
    )
    prompts = []
    monkeypatch.setattr(builtins, "input", lambda msg="": prompts.append(msg))
    result = pytester.runpytest("--step", "-p", "pytest_stepthrough.plugin")
    result.assert_outcomes(passed=2)
    assert len(prompts) == 2
    assert "[PASSED] test_a.py::test_one" in prompts[0]


def test_without_step_does_not_prompt(pytester, monkeypatch):
    _add_src_to_path(pytester)
    pytester.makepyfile(
        """
        def test_example():
            assert True
        """
    )
    monkeypatch.setattr(
        builtins,
        "input",
        lambda *args, **kwargs: pytest.fail("should not be called"),
    )
    result = pytester.runpytest("-p", "pytest_stepthrough.plugin")
    result.assert_outcomes(passed=1)


def test_capture_suspension(pytester, monkeypatch):
    _add_src_to_path(pytester)
    pytester.makepyfile(
        """
        def test_example():
            assert True
        """
    )
    calls = []

    orig_suspend = CaptureManager.suspend_global_capture
    orig_resume = CaptureManager.resume_global_capture

    def suspend(self, in_=False):
        calls.append(("suspend", in_))
        orig_suspend(self, in_)

    def resume(self):
        calls.append(("resume",))
        orig_resume(self)

    monkeypatch.setattr(CaptureManager, "suspend_global_capture", suspend)
    monkeypatch.setattr(CaptureManager, "resume_global_capture", resume)
    monkeypatch.setattr(builtins, "input", lambda msg="": None)
    result = pytester.runpytest("--step", "-p", "pytest_stepthrough.plugin")
    result.assert_outcomes(passed=1)
    suspend_idx = next((i for i, c in enumerate(calls) if c == ("suspend", True)), None)
    resume_after = [i for i, c in enumerate(calls) if c == ("resume",) and i > suspend_idx]
    assert suspend_idx is not None and resume_after


def test_handles_eoferror(pytester, monkeypatch):
    _add_src_to_path(pytester)
    pytester.makepyfile(
        """
        def test_example():
            assert True
        """
    )
    monkeypatch.setattr(
        builtins,
        "input",
        lambda *args, **kwargs: (_ for _ in ()).throw(EOFError),
    )
    result = pytester.runpytest("--step", "-p", "pytest_stepthrough.plugin")
    result.assert_outcomes(passed=1)
