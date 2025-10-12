"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management

    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)

    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."

    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."

    if not author or not author.strip():
        return False, "Author is required."

    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."

    if len(isbn) != 13 or not isbn.isdigit():
        return False, "ISBN must be exactly 13 digits."

    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."

    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."

    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements

    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow

    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."

    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    if book['available_copies'] <= 0:
        return False, "This book is currently not available."

    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)

    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."

    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)

    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."

    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."

    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'


def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.

    Implements R4:
      - Accepts patron ID and book ID
      - Verifies the book was borrowed by the patron (via DB update result)
      - Records return date
      - Updates available copies (not exceeding total)
      - Calculates and displays any late fees owed
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."

    # Check book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    # Verify there is an active borrow for this patron+book
    active = get_patron_borrowed_books(patron_id) or []
    is_active = False
    for record in active:
        if record.get("book_id") == book_id:
            is_active = True
            break
    if not is_active:
        return False, "No borrow record found for this patron and book"

    # Calculate late fee (do not block the return if overdue)
    fee_info = calculate_late_fee_for_book(patron_id, book_id)
    fee_amount = round(float(fee_info.get("fee_amount", 0.0)), 2)
    days_overdue = int(fee_info.get("days_overdue", 0))

    # Record return date
    return_date = datetime.now()
    if not update_borrow_record_return_date(patron_id, book_id, return_date):
        return False, "Database error occurred while recording the return."

    # Increment availability without exceeding total
    if book["available_copies"] < book["total_copies"]:
        if not update_book_availability(book_id, +1):
            return False, "Database error occurred while updating book availability."

    # Final message
    if days_overdue > 0 and fee_amount > 0:
        return True, (
            f'Book "{book["title"]}" returned. Your late fee is: '
            f'${fee_amount:.2f} for {days_overdue} overdue day(s).'
        )
    return True, f'Book "{book["title"]}" returned on time. No late fees applied.'


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Invalid patron ID'}

    # Find borrow record
    due_date = None
    for record in (get_patron_borrowed_books(patron_id) or []):
        if record.get("book_id") == book_id:
            due_date = record.get("due_date")
            break

    if not isinstance(due_date, datetime):
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Borrow record not found'}

    # Calculate overdue days
    now = datetime.now()
    days_overdue = (now.date() - due_date.date()).days
    if days_overdue < 0:
        days_overdue = 0

    # Calculate fee
    if days_overdue == 0:
        fee_amount = 0.00
    elif days_overdue <= 7:
        fee_amount = days_overdue * 0.50
    else:
        first_week_fee = 7 * 0.50
        remaining_days = days_overdue - 7
        fee_amount = first_week_fee + remaining_days * 1.00

    # Cap fee at $15
    if fee_amount > 15.00:
        fee_amount = 15.00

    return {
        'fee_amount': round(fee_amount,2),
        'days_overdue': days_overdue,
        'status': 'OK'
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.


    """
    if search_type not in {"title", "author", "isbn"}:
        return []

    # Validate search
    if search_term is None:
        return []
    term = str(search_term).strip()
    if not term:
        return []

    books = get_all_books()
    matches = []

    # Search by title
    if search_type == "title":
        t = term.lower()
        for b in books:
            title = b.get("title")
            if isinstance(title, str) and t in title.lower():
                matches.append(b)

    # Search by author
    elif search_type == "author":
        t = term.lower()
        for b in books:
            author = b.get("author")
            if isinstance(author, str) and t in author.lower():
                matches.append(b)

    # Search by ISBN (exact match)
    elif search_type == "isbn":
        for b in books:
            isbn = str(b.get("isbn"))
            if isbn == term:
                matches.append(b)

    return matches

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    ToDo: Implement borrowing history once database functions are implemented to meet requirements specification

    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            "currently_borrowed": [],
            "total_late_fees": 0.00,
            "num_currently_borrowed": 0,
            #"borrowing_history": [], # Placeholder
            "status": "Invalid patron ID"
        }

    active = get_patron_borrowed_books(patron_id)
    borrowed = []
    if active is None:
        active = []
    num_currently_borrowed = len(active)
    total_late_fees = 0.00
    #Can't implement borrowing history without database functions for it
    #borrowing_history = []  # Placeholder

    for record in active:
        fee_info = calculate_late_fee_for_book(patron_id, record.get("book_id"))
        if fee_info['status'] == 'OK':
            total_late_fees += fee_info['fee_amount']
            total_late_fees = round(total_late_fees, 2)
            borrowed.append({
                'book_id': record.get("book_id"),
                'title': record.get("title"),
                'author': record.get("author"),
                'borrow_date': record.get("borrow_date"),
                'due_date': record.get("due_date"),
                'is_overdue': fee_info['days_overdue'] > 0,
                'late_fee': fee_info['fee_amount']
            })
    return {
        "currently_borrowed": borrowed,
        "total_late_fees": round(total_late_fees,2),
        "num_currently_borrowed": num_currently_borrowed,
        #"borrowing_history": [],  # Placeholder
    }

def get_catalog_display() -> List[Dict]:
    """
    R2: returns list of books for catalog display
    """
    return get_all_books()

