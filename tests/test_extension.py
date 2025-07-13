import pytest
from playwright.sync_api import sync_playwright
import os
import re

# Define the path to your unpacked extension
EXTENSION_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        # Launch Chromium with the extension loaded
        context = p.chromium.launch_persistent_context(
            "", # Use a temporary user data directory
            headless=False, # Set to True for CI/CD, False for debugging
            args=[
                f"--disable-extensions-except={EXTENSION_PATH}",
                f"--load-extension={EXTENSION_PATH}",
            ]
        )
        yield context
        context.close()

@pytest.fixture(scope="function")
def page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()

def test_extension_loads_and_displays_ratings_on_profile_page(page):
    # Navigate to a Lichess profile page
    page.goto("https://lichess.org/@/DrNykterstein")

    # Wait for the extension to process and display ratings
    # Look for a rating element that contains the Chess.com equivalent in green
    # This assumes the extension adds a span with color #769656 and text in parentheses
    chess_com_rating_span = page.locator('span[style*="color: rgb(118, 150, 86)"]:has-text("(")').first
    
    # Assert that the element is visible, meaning the rating was added
    assert chess_com_rating_span.is_visible(), "Chess.com equivalent rating not found on profile page."

    # Optional: Further check the content of the rating (e.g., it's a number)
    rating_text = chess_com_rating_span.text_content()
    assert re.search(r'\(\d+\)', rating_text), f"Rating text format incorrect: {rating_text}"
