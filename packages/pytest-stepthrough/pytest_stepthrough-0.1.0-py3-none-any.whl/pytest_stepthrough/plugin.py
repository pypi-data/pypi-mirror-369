import pytest

_STEP_ENABLED = False
_CONFIG = None  # stash config for capture access


def pytest_addoption(parser):
    parser.addoption(
        "--step",
        action="store_true",
        help="Pause after each test and wait for Enter.",
    )


def pytest_configure(config):
    # cache for later use and quick check
    global _STEP_ENABLED, _CONFIG
    _STEP_ENABLED = bool(config.getoption("--step"))
    _CONFIG = config


def _pause_for_input(msg: str):
    """Suspend capture so input() works with or without -s, then resume."""
    capman = _CONFIG.pluginmanager.getplugin("capturemanager") if _CONFIG else None
    if capman is not None:
        capman.suspend_global_capture(in_=True)
    try:
        input(msg)
    except EOFError:
        # Non-interactive (CI, pipes) — ignore the pause
        pass
    finally:
        if capman is not None:
            capman.resume_global_capture()


# Run *after* terminalreporter prints the status, so PASSED/FAILED is visible first
@pytest.hookimpl(trylast=True)
def pytest_runtest_logreport(report):
    if not _STEP_ENABLED:
        return
    if report.when != "call":
        return

    # Status label similar to pytest's (handles xfail/xpass)
    if report.outcome == "passed" and getattr(report, "wasxfail", None):
        status = "XPASS"
    elif report.outcome == "skipped" and getattr(report, "wasxfail", None):
        status = "XFAIL"
    else:
        status = report.outcome.upper()

    _pause_for_input(f"\n[{status}] {report.nodeid} — Press Enter for the next test...")
