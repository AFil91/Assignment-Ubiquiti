# IYP Stockholm — Test Automation

A lightweight Playwright + Python framework for smoke and regression testing.

## Setup (one-time)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Playwright's browsers
playwright install chromium
```

## Run tests

```bash
# Run everything
pytest

# Run only smoke tests
pytest tests/smoke/

# Run a single file
pytest tests/search/test_search.py

# Run with visible browser (default) — change headless=False to True in conftest.py to hide it
pytest

# Run and see a summary of passed/failed
pytest -v
```

## Project structure

```
automation/
├── conftest.py                  # shared browser setup (edit BASE_URL here)
├── requirements.txt
├── tests/
│   ├── smoke/
│   │   └── test_homepage.py     # page loads, sections visible, ads present, navigation
│   ├── search/
│   │   └── test_search.py       # dialog, results, images, recent searches
```

## Tips

- Tests are independent — each one gets a fresh browser page automatically.
- If a selector stops matching after a site update, inspect the element in DevTools
  and update the locator in the test.
- To run tests headlessly (no visible browser), change `headless=False` to
  `headless=True` in `conftest.py`.

## Extra Notes
the 3 failing tests are "catching" some of the bugs I've reported manualy so failing is expected
