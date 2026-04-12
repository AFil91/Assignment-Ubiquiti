# conftest.py — shared setup for all tests
# Pytest automatically reads this file before running any test.

import pytest
from playwright.sync_api import sync_playwright
from helpers import dismiss_GDPR_popup

# ── Configuration ──────────────────────────────────────────────────────────
# Change BASE_URL if you want to run tests against a staging environment.
BASE_URL = "https://www.inyourpocket.com/sweden/stockholm"


# ── Browser fixture ────────────────────────────────────────────────────────
# A "fixture" in pytest is a reusable piece of setup/teardown logic.
# Every test that declares `page` as a parameter will get a fresh browser page.

@pytest.fixture(scope="function")
def page():
    """
    Launches a browser, creates a new page, and closes everything after the test.
    scope="function" means each test gets its own clean browser page.
    """
    with sync_playwright() as p:
        # headless=False means you can SEE the browser while tests run.
        # Change to headless=True to run silently in CI/CD.
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900}
        )
        page = context.new_page()
        yield page          # hand the page to the test
        browser.close()     # runs after each test, even if the test fails


# ── Helper: navigate to base URL ───────────────────────────────────────────
@pytest.fixture(scope="function")
def homepage(page):
    """Opens the Stockholm homepage, dismisses any consent popup, and waits for full load."""
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    # kill ad iframe early
    page.locator("#ad_iframe").evaluate_all(
        "els => els.forEach(el => el.remove())"
    )

    dismiss_GDPR_popup(page)
    return page
