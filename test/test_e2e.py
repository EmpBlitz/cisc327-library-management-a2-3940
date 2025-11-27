import random
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://127.0.0.1:5000"

NOUNS = [
    "Dragon", "Knight", "Sorcerer", "Warlord", "King", "Queen", "Beast",
    "Wizard", "Ranger", "Bard", "Druid", "Wolf", "Griffin", "Serpent"
]

ADJECTIVES = [
    "Cursed", "Ancient", "Forgotten", "Sacred", "Burning", "Silent",
    "Shadowed", "Golden", "Iron", "Eternal", "Haunted", "Lost"
]

PLACES = [
    "Eldermoor", "Ravenpeak", "Stormhold", "Ashridge", "Duskspire",
    "Wintermere", "Blackfen"
]

def generate_test_title() -> str:
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    place = random.choice(PLACES)
    return f"[TEST] The {adj} {noun} of {place}"


BOOK_TITLE = generate_test_title()
BOOK_AUTHOR = "Test Author"
BOOK_COPIES = "3"
PATRON_ID = "123456"

def generate_unique_isbn() -> str:
    """Make a 13-digit random ISBN"""
    return str(random.randint(10**12, 10**13 - 1))


def add_book(page, title: str, author: str, isbn: str, copies: str):
    """Helper: add a book with the given data."""
    page.goto(f"{BASE_URL}/add_book", wait_until="networkidle")

    page.fill("input[name='title']", title)
    page.fill("input[name='author']", author)
    page.fill("input[name='isbn']", isbn)
    page.fill("input[name='total_copies']", copies)

    page.click("form button[type='submit']")
    page.wait_for_load_state("networkidle")

SAMPLE_TITLE = "The Great Gatsby"
SAMPLE_AUTHOR = "F. Scott Fitzgerald"
SAMPLE_ISBN = "9780743273565"


def test_add_new_book():
    """Add a new book to the catalog and check success message."""
    unique_isbn = generate_unique_isbn()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        add_book(page, BOOK_TITLE, BOOK_AUTHOR, unique_isbn, BOOK_COPIES)

        body = page.locator("body")
        expect(body).to_contain_text("successfully added to the catalog")

        browser.close()


def test_verify_book_in_catalog():
    """ Verify a known sample book """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(f"{BASE_URL}/catalog", wait_until="networkidle")

        body = page.locator("body")
        expect(body).to_contain_text(SAMPLE_TITLE)
        expect(body).to_contain_text(SAMPLE_AUTHOR)
        expect(body).to_contain_text(SAMPLE_ISBN)

        browser.close()


def test_borrow_book_with_patron_id():
    """Borrow a book from the catalog using a patron ID"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(f"{BASE_URL}/catalog", wait_until="networkidle")

        row = page.get_by_role("row", name=SAMPLE_ISBN)

        row.locator("input[name='patron_id']").fill(PATRON_ID)

        row.get_by_role("button", name="Borrow").click()
        page.wait_for_load_state("networkidle")

        body = page.locator("body")
        expect(body).to_contain_text("Successfully borrowed")

        browser.close()
