# pytest-stepthrough

Pause after each test and wait for Enter — useful for hardware/integration
flows where you want to observe output or reset something between tests.

## Install (dev)
```bash
pip install -e .
```

## Usage

```bash
pytest                 # normal run
pytest --step          # pause after each test (no need for -s)
pytest -q --step       # works with -q too
```

## Notes

* Works with pytest 6+ (tested on 6.2.5).
* We temporarily suspend output capture around the prompt, so `-s` is **not** required.
* The prompt appears **after** pytest prints PASSED/FAILED/XPASS/XFAIL.

