# tests/search/test_search.py
#
# SEARCH TESTS
# Covers the search dialog behaviour and recent searches tracking.
# These tests address Issues 2, 15, and 16 from the bug report.

import pytest
from helpers import dismiss_GDPR_popup


SEARCH_TERM_WITH_RESULTS = "the"    # a term known to return results
SEARCH_TERM_NO_RESULTS   = "xyzxyzxyz123"  # a term that should return nothing


class TestSearchDialog:
    """Check that the search dialog opens and that results are displayed correctly."""

    def test_search_dialog_opens_on_desktop(self, homepage):
        """
        Clicking the search icon should open a dialog.
        Basic sanity check — if this fails, everything else is skipped.
        """
        # Click the search icon/button
        homepage.get_by_role("button", name="Open search").click()

        # A search input should now be visible
        search_input = homepage.get_by_role("searchbox")
        assert search_input.is_visible(), "Search input not visible after clicking Search button"

    def test_search_returns_results_for_known_term(self, homepage):
        """
        Typing a known term should show results.
        Also a light regression check for Issue 2 (dialog proportions) —
        if the dialog is broken, results won't render at all.
        """
        homepage.get_by_role("button", name="Open search").click()
        homepage.get_by_role("searchbox").fill(SEARCH_TERM_WITH_RESULTS)
        homepage.wait_for_timeout(800)  # wait for results to appear (debounce)

        # There should be at least one result item with a title visible
        # We check for the title div, not the image — image presence is tested separately
        results = homepage.locator("li").filter(has=homepage.locator("div[class*='font-sans']"))
        results.first.wait_for(state="visible", timeout=3000)
        assert results.count() > 0, (
            f"No results shown for search term '{SEARCH_TERM_WITH_RESULTS}'"
        )

    def test_destination_results_have_images(self, homepage):
        """
        Regression test for Issue 15:
        Destination results in the search dialog should include an image.
        """
        homepage.get_by_role("button", name="Open search").click()
        homepage.get_by_role("searchbox").fill(SEARCH_TERM_WITH_RESULTS)
        homepage.wait_for_timeout(800)

        # Find all result items across all sections (articles, destinations, venues etc.)
        results = homepage.locator("li").filter(has=homepage.locator("div[class*='font-sans']"))
        results.first.wait_for(state="visible", timeout=3000)

        if results.count() == 0:
            pytest.skip("No results returned for this search term — skip image check")

        # Every result li should contain an img — loop so we know exactly which one fails
        # This is important because Issue 15 showed images missing only in Destinations,
        # not in all sections — checking only the first result would miss that bug.
        missing = []
        for i in range(results.count()):
            result = results.nth(i)
            title = result.locator("div[class*='font-sans']").inner_text()
            image = result.locator("img")
            if image.count() == 0:
                missing.append(f"Result {i + 1}: '{title}'")

        assert len(missing) == 0, (
            f"The following results are missing images (Regression of Issue 15):\n"
            + "\n".join(missing)
        )


class TestRecentSearches:
    """Check that search terms are correctly saved to Recent Searches."""

    def test_search_from_no_results_page_is_saved_to_recent(self, homepage):
        """
        Regression test for Issue 16:
        A search performed from the 'no results' page should appear in Recent Searches.

        Steps:
        1. Search for something with no results
        2. From the no-results page, search for a real term
        3. Open search again and confirm the second term is in Recent Searches
        """
        # Clear only the recent searches key from localStorage before starting
        # so previous test runs don't pollute the results.
        # The site stores recent searches under the key "1"
        homepage.evaluate("localStorage.removeItem('1')")
        homepage.reload()
        homepage.wait_for_url("**/sweden/stockholm**", timeout=5000)
        dismiss_GDPR_popup(homepage)

        # Step 1 — search for something that returns nothing
        homepage.get_by_role("button", name="Open search").click()
        homepage.get_by_role("searchbox").fill(SEARCH_TERM_NO_RESULTS)
        homepage.keyboard.press("Enter")
        homepage.wait_for_url(f"**/search?q={SEARCH_TERM_NO_RESULTS}&city=stockholm**", timeout=5000)

        # Step 2 — on the results page the search bar is different (id="search")
        # Click the search icon first to focus it, then fill the input and submit
        homepage.locator("#btn_search").click()
        homepage.locator("#search").fill(SEARCH_TERM_WITH_RESULTS)
        homepage.keyboard.press("Enter")
        homepage.wait_for_url(f"**/search?q={SEARCH_TERM_WITH_RESULTS}**", timeout=5000)

        # Step 3 — go back to Stockholm homepage and open search
        homepage.goto("https://www.inyourpocket.com/sweden/stockholm")
        homepage.wait_for_url("**/sweden/stockholm**", timeout=5000)
        dismiss_GDPR_popup(homepage)  # banner may reappear on fresh navigation
        homepage.get_by_role("button", name="Open search").click()
        homepage.wait_for_timeout(500)

        # Recent Searches are rendered as buttons containing the search term text
        # Look for a button with our search term inside the Recent searches section
        recent_search_button = homepage.locator(
            "button", has_text=SEARCH_TERM_WITH_RESULTS
        ).first
        recent_search_button.wait_for(state="visible", timeout=3000)
        assert recent_search_button.is_visible(), (
            f"BUG CONFIRMED — Issue 16: '{SEARCH_TERM_WITH_RESULTS}' was searched from "
            f"the no-results page but did not appear in Recent Searches."
        )
