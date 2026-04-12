# tests/smoke/test_homepage.py
#
# SMOKE TESTS — Homepage
# These are basic checks: "does the page load and look right?"
# Should run after every deploy to catch obvious regressions fast.

import pytest
from helpers import dismiss_GDPR_popup, dismiss_interstitial


class TestHomepageLoads:
    """Check that the homepage loads and all main sections are present."""

    def test_page_title_is_correct(self, homepage):
        """The browser tab title should mention Stockholm."""
        # homepage is the fixture from conftest.py — already on the page
        assert "Stockholm" in homepage.title(), (
            f"Unexpected page title: {homepage.title()}"
        )

    def test_main_sections_are_visible(self, homepage):
        """
        Key content sections should be visible without scrolling or interacting.
        We check for the section headings by their text content.
        """
        sections = ["See and do", "Eat", "Nightlife"]

        for section in sections:
            # get_by_text finds any element containing this text
            heading = homepage.get_by_text(section, exact=True).first
            assert heading.is_visible(), f"Section '{section}' is not visible on the page"

    def test_ad_containers_are_present(self, homepage):
        """
        Ad slots should exist in the DOM.
        This verifies just the container height -> 0 height container means something broke in layout.
        """

        # Ads load asynchronously so waiting for the first one to appear before counting
        homepage.wait_for_function(
            "document.querySelectorAll('ins.adsbygoogle').length > 0 && "
            "[...document.querySelectorAll('ins.adsbygoogle')].some(el => el.offsetHeight > 0)"
        )
        # Google AdSense inserts ads inside <ins class="adsbygoogle"> elements
        ad_slots = homepage.locator("ins.adsbygoogle")
        ads_rendered = ad_slots.count()

        count_rendered = 0
        # Check  — wait for ads to render then count visible ones (height > 0)
        for i in range(ads_rendered):
            slot = ad_slots.nth(i)
            height = slot.evaluate("el => el.offsetHeight")
            if height > 0:
                count_rendered += 1
        assert count_rendered == 6, (
            f"No ads rendered on the page."     
        )

    def test_see_and_do_shows_five_entries(self, homepage):
        """
        The 'See and do' section should show 5 place cards.
        Regression test for Issue 4 (only 3 entries shown).
        Here as the bug exists it will fail.
        Should be repeated for all sections: Articles, Nighlife, Eat etc in a smoke suite.
        """
        homepage.wait_for_selector("text=See and do")

        # Scroll the section into view so cards load
        homepage.get_by_text("See and do", exact=True).first.scroll_into_view_if_needed()
        homepage.wait_for_timeout(500)  # small wait for any lazy-loading

        # Each card is an <a> with aria-label starting with "Read article:"
        # Scoped to the See and do section to avoid matching cards from other sections
        # The section is wrapped in <div id="see-and-do"> — unique and stable
        section = homepage.locator("#see-and-do")
        cards = section.locator("a[aria-label^='Read article:']")

        count = cards.count()
        assert count == 5, (
            f"'See and do' should show 5 entries but found {count}. "
            f"Regression of Issue 4."
        )
        