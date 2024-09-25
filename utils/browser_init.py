from playwright.sync_api import sync_playwright

def init_browser(headless=False):
    """Initialize the browser and return a browser context."""
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context()
    return context

def close_browser(context):
    """Close the browser context."""
    context.close()
