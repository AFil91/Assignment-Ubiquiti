# helpers.py — reusable utility functions shared across tests

def dismiss_GDPR_popup(page):
    """
    Dismisses any GDPR data consent popup.
    Handles the GDPR data consent popup with a standard <button> (main pages)
    Safe to call even if no popup appears — it just moves on silently.
    """
    # Variant 1 — standard button popup (main pages)
    accept_labels = ["Confirm", "Consent"]
    for label in accept_labels:
        try:
            btn = page.get_by_role("button", name=label, exact=False)
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(500)
                return
        except Exception:
            continue


def dismiss_interstitial(page, timeout=2000):
    """
    Dismisses the Google vignette interstitial ad by removing its iframe from the DOM.
    The ad is rendered inside <iframe id="ad_iframe"> in the main page. Removing the
    iframe itself is simpler than navigating inside it.
    Moves on silently if no interstitial appears within the timeout.
    """
    try:
        page.wait_for_url("**#google_vignette**", timeout=timeout)
    except Exception:
        return  # no vignette appeared, move on

    iframe = page.locator("#ad_iframe")
    if iframe.count() > 0:
        iframe.evaluate("el => el.remove()")
        page.wait_for_timeout(500)
