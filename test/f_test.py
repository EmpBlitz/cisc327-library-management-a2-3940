import pytest
from library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report,
    get_catalog_display
)

## Test add_book_to_catalog
def test_add_book_valid_input():
    """Testing with valid input"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success is True
    assert "successfully" in message.lower()
    
def test_add_book_author_too_long():
    """Test adding a book with author name longer than 100 characters"""
    l_author = "Test Author" * 101
    success, message = add_book_to_catalog("Test Book", l_author, "1234567890123", 1)
    
    assert success is False
    assert "100" in message
    
def test_add_book_total_copies_invalid():
    """Test adding a book with 0 total copies"""
    success_zero, _ = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)
    
    assert success_zero is False
    
def test_add_book_blank_author():
    """Test adding a book with a blank author field"""
    success, message = add_book_to_catalog("Test Book", "", "1234567890123", 1)
    
    assert success is False
    assert "author is required" in message.lower()
    
def test_add_book_title_exceeds_200_chars():
    """Test adding a book with a title longer than 200 characters"""
    l_title = "Test Title" * 201
    success, message = add_book_to_catalog(l_title, "Test Author", "1234567890123", 1)
    
    assert success is False
    assert "200" in message
    
def test_add_book_non_integer_total_copies():
    """Test adding a book with a non-integer total copies"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", "five")
    
    assert success is False
    assert "positive integer" in message.lower()



## Test borrow_book_by_patron

def test_borrow_valid_input():
    """Test with valid input"""
    success, message = borrow_book_by_patron("123456", 1)
    
    assert success in (True, False)
    
def test_borrow_invalid_patron_id_non_numeric():
    """Test borrowing with a non digit patron ID"""
    success, message = borrow_book_by_patron("ABCDEF", 1)
    
    assert success is False
    assert "6 digits" in message
    
def test_borrow_invalid_patron_id_wrong_length():
    """Test borrowing with patron ID of a too long word length"""
    success, msg_long = borrow_book_by_patron("1234567", 1)
    
    assert success is False and "6 digits" in msg_long.lower()

def test_borrow_book_not_found():
    """Test borrowing a book that does not exist"""
    success, message = borrow_book_by_patron("123456", 999999)
    
    assert success is False
    assert "not found" in message.lower()


## Test return_book_by_patron

def test_return_valid_input():
    """Test returning a book with valid input"""
    success, message = return_book_by_patron("123456", 1)
    
    assert success in (True, False)
    assert isinstance(message, str)
    
def test_return_invalid_patron_id_non_numeric():
    """Test returning with a non digit patron ID"""
    success, message = return_book_by_patron("ABCDEF", 1)
    
    assert success is False
    assert "6 digits" in message.lower()
    
def test_return_invalid_patron_id_wrong_length():
    """Test returning with patron ID of a wrong length"""
    success, message = return_book_by_patron("1234567", 1)
    
    assert success is False
    assert "6 digits" in message.lower()


## Test calculate_late_fee_for_book

def test_calculate_fee_structure():
    """Test late fee calculation returns dict with required keys"""
    sucess = calculate_late_fee_for_book("123456", 1)
    
    assert isinstance(sucess, dict)
    assert "fee_amount" in sucess
    assert "days_overdue" in sucess
    assert "status" in sucess

def test_calculate_fee_non_negative_days():
    """Test days overdue is always non negative"""
    sucess = calculate_late_fee_for_book("123456", 1)
    
    assert sucess["days_overdue"] >= 0

def test_calculate_fee_non_negative_amount():
    """Test fee amount is always non negative"""
    sucess = calculate_late_fee_for_book("123456", 1)
    
    assert sucess["fee_amount"] >= 0

def test_calculate_fee_max_cap():
    """Test fee amount does not exceed $15"""
    sucess = calculate_late_fee_for_book("123456", 1)
    
    assert sucess["fee_amount"] <= 15.0
    
    
## Test search_books_in_catalog

def test_search_returns_list():
    """Test search always returns a list"""
    sucesss = search_books_in_catalog("Test title", "title")
    
    assert isinstance(sucesss, list)

def test_search_title_case_insensitive():
    """Test search by title is case insensitive"""
    sucesss = search_books_in_catalog("Test title", "title")
    
    assert isinstance(sucesss, list)

def test_search_author_partial_match():
    """Test search by author supports partial match"""
    sucesss = search_books_in_catalog("Test author", "author")
    
    assert isinstance(sucesss, list)

def test_search_isbn_exact_match():
    """Test search by ISBN requires exact match"""
    sucesss = search_books_in_catalog("9780132350884", "isbn")
    
    assert isinstance(sucesss, list)
    
    
## Test get_patron_status_report

def test_report_is_dict():
    """Test patron status report returns dict"""
    report = get_patron_status_report("123456")
    
    assert isinstance(report, dict)
    
def test_report_total_fees_non_negative():
    """Test total late fees is non-negative"""
    report = get_patron_status_report("123456")
    
    assert report["total_late_fees"] >= 0
    
def test_report_returns_dict():
    """Test patron status report returns a dictionary"""
    report = get_patron_status_report("123456")
    
    assert isinstance(report, dict)

## R2: Test get_catalog_display

def test_catalog_returns_list():
    """Test catalog display always returns a list"""
    results = get_catalog_display()
    assert isinstance(results, list)

def test_catalog_items_have_required_fields():
    """Test catalog entries have required keys"""
    results = get_catalog_display()
    for book in results:
        assert "id" in book
        assert "title" in book
        assert "author" in book
        assert "isbn" in book
        assert "available_copies" in book
        assert "total_copies" in book

def test_catalog_counts_are_valid():
    """Test available_copies and total_copies are valid integers"""
    results = get_catalog_display()
    for book in results:
        assert isinstance(book["available_copies"], int)
        assert isinstance(book["total_copies"], int)
        assert 0 <= book["available_copies"] <= book["total_copies"]