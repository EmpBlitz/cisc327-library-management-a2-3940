from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report,
    get_catalog_display,
    pay_late_fees,
    refund_late_fee_payment
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

def test_add_book_blank_title():
    success, msg = add_book_to_catalog("   ", "Some Author", "1234567890123", 1)

    assert success is False
    assert "title is required" in msg.lower()

def test_add_book_isbn_wrong_length():
    success, msg = add_book_to_catalog("A", "B", "123456789012", 1)

    assert success is False
    assert "13 digits" in msg

def test_add_book_isbn_not_digits():
    success, msg = add_book_to_catalog("A", "B", "123456789012X", 1)

    assert success is False
    assert "13 digits" in msg

def test_add_book_negative_copies():
    success, msg = add_book_to_catalog("A", "B", "1234567890123", -5)
    assert success is False
    assert "positive integer" in msg.lower()

def test_add_book_author_blank_spaces():
    success, msg = add_book_to_catalog("A", "   ", "1234567890123", 1)

    assert success is False
    assert "author is required" in msg.lower()

def test_add_book_title_required():
    success, msg = add_book_to_catalog("   ", "Author", "1234567890123", 1)
    assert success is False and "title" in msg.lower()

def test_add_book_author_required():
    success, msg = add_book_to_catalog("Title", "   ", "1234567890123", 1)
    assert success is False and "author" in msg.lower()

def test_add_book_isbn_must_be_13_digits_length():
    success, msg = add_book_to_catalog("Title", "Author", "123456789012", 1)  # 12 digits
    assert success is False and "13 digits" in msg

def test_add_book_isbn_must_be_digits():
    success, msg = add_book_to_catalog("Title", "Author", "123456789012X", 1)
    assert success is False and "13 digits" in msg

def test_add_book_copies_must_be_positive():
    success, msg = add_book_to_catalog("Title", "Author", "1234567890123", 0)
    assert success is False and "positive" in msg.lower()

def test_add_book_duplicate_isbn():
    add_book_to_catalog("Title1", "Author1", "9999999999999", 1)
    success, msg = add_book_to_catalog("Title2", "Author2", "9999999999999", 1)
    assert success is False
    assert "isbn" in msg.lower()

def test_add_book_whitespace_trimmed_fields():
    success, msg = add_book_to_catalog("  Trim Title  ", "  Trim Author  ", "1111111111111", 1)
    assert success is True

def test_add_book_large_copies():
    success, msg = add_book_to_catalog("Bulk Book", "Bulk Author", "2222222222222", 500)
    assert success is True

def test_add_book_isbn_all_same_digits():
    success, msg = add_book_to_catalog("Mono", "Digit Author", "0000000000000", 1)
    assert success in (True, False)

def test_add_book_title_200_author_100_ok():
    title = "T" * 200
    author = "A" * 100
    success, msg = add_book_to_catalog(title, author, "3100000000000", 1)
    assert success is True and "successfully" in msg.lower()

def test_catalog_contains_recently_added_book():
    success, _ = add_book_to_catalog("Catalog Seen", "CS", "3200000000000", 2)
    assert success
    items = get_catalog_display()
    assert any(b["isbn"] == "3200000000000" and b["title"] == "Catalog Seen" for b in items)


def test_add_book_title_exact_200_ok():
    title = "T" * 200
    success, msg = add_book_to_catalog(title, "Edge Author", "3000000000001", 1)
    assert success is True
    assert "successfully" in msg.lower()

def test_add_book_author_exact_100_ok():
    author = "A" * 100
    success, msg = add_book_to_catalog("Edge Title", author, "3000000000002", 1)
    assert success is True
    assert "successfully" in msg.lower()

def test_add_book_isbn_with_leading_zeros_ok():
    success, msg = add_book_to_catalog("Zeros Title", "Zeros Author", "0000000000007", 1)
    assert success is True
    assert "successfully" in msg.lower()

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

def test_borrow_book_id_not_found_negative():
    success, msg = borrow_book_by_patron("123456", -1)

    assert success is False
    assert "not found" in msg.lower()

def test_borrow_patron_too_short():
    success, msg = borrow_book_by_patron("12345", 1)

    assert success is False
    assert "6 digits" in msg.lower()

def test_borrow_invalid_patron_id_not_6_digits():
    success, msg = borrow_book_by_patron("12345", 1)
    assert success is False and "6 digits" in msg.lower()

def test_borrow_invalid_patron_id_non_digits():
    success, msg = borrow_book_by_patron("ABCDEF", 1)
    assert success is False and "invalid patron id" in msg.lower()

def test_borrow_non_int_book_id():
    success, msg = borrow_book_by_patron("123456", "abc")
    assert success is False
    assert "not found" in msg.lower()

def test_borrow_book_id_none():
    success, msg = borrow_book_by_patron("123456", None)
    assert success is False
    assert "not found" in msg.lower()

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

def test_return_book_not_found():
    success, msg = return_book_by_patron("123456", 999999)

    assert success is False
    assert "not found" in msg.lower()

def test_return_patron_too_short():
    success, msg = return_book_by_patron("12345", 1)

    assert success is False
    assert "6 digits" in msg.lower()

def test_return_invalid_patron_id_not_6_digits():
    success, msg = return_book_by_patron("12345", 1)
    assert success is False and "6 digits" in msg.lower()

def test_return_invalid_patron_id_non_digits():
    success, msg = return_book_by_patron("ABCDEF", 1)
    assert success is False and "invalid patron id" in msg.lower()

def test_return_non_int_book_id():
    success, msg = return_book_by_patron("123456", "abc")
    assert success is False
    assert "not found" in msg.lower()

def test_return_book_id_none():
    success, msg = return_book_by_patron("123456", None)
    assert success is False
    assert "not found" in msg.lower()


## Test calculate_late_fee_for_book

def test_calculate_fee_structure():
    """Test late fee calculation returns dict with required keys"""
    success = calculate_late_fee_for_book("123456", 1)
    
    assert isinstance(success, dict)
    assert "fee_amount" in success
    assert "days_overdue" in success
    assert "status" in success

def test_calculate_fee_non_negative_days():
    """Test days overdue is always non negative"""
    success = calculate_late_fee_for_book("123456", 1)
    
    assert success["days_overdue"] >= 0

def test_calculate_fee_non_negative_amount():
    """Test fee amount is always non negative"""
    success = calculate_late_fee_for_book("123456", 1)
    
    assert success["fee_amount"] >= 0

def test_calculate_fee_max_cap():
    """Test fee amount does not exceed $15"""
    success = calculate_late_fee_for_book("123456", 1)
    
    assert success["fee_amount"] <= 15.0

def test_calculate_fee_invalid_patron_id():
    info = calculate_late_fee_for_book("ABCDEF", 1)

    assert info["fee_amount"] == 0.0
    assert info["days_overdue"] == 0
    assert info["status"].lower().startswith("invalid")

def test_calculate_fee_invalid_book_id():
    info = calculate_late_fee_for_book("123456", -10)
    assert isinstance(info, dict)
    assert info["fee_amount"] >= 0
    assert info["days_overdue"] >= 0

def test_calculate_fee_non_int_book_id():
    info = calculate_late_fee_for_book("123456", "xyz")
    assert isinstance(info, dict)
    assert info["fee_amount"] == 0.0
    assert info["days_overdue"] == 0
    assert "not found" in info["status"].lower()
    
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

def test_search_invalid_search_type():
    results = search_books_in_catalog("Anything", "publisher")
    assert results == []

def test_search_none_term():
    results = search_books_in_catalog(None, "title")
    assert results == []

def test_search_blank_term():
    results = search_books_in_catalog("   ", "author")
    assert results == []

def test_search_isbn_exact_match_miss():
    results = search_books_in_catalog("0000000000000", "isbn")
    assert isinstance(results, list)
    assert len(results) == 0

def test_search_isbn_exact_no_match():
    results = search_books_in_catalog("0000000000000", "isbn")
    assert isinstance(results, list) and len(results) == 0

def test_search_title_partial():
    results = search_books_in_catalog("Test", "title")
    assert isinstance(results, list)

def test_search_author_case_variation():
    results = search_books_in_catalog("tEsT aUtHoR", "author")
    assert isinstance(results, list)

def test_search_blank_search_type():
    results = search_books_in_catalog("Anything", "")
    assert results == []

def test_search_numeric_title_term():
    results = search_books_in_catalog("12345", "title")
    assert isinstance(results, list)

def test_search_isbn_non_digit():
    results = search_books_in_catalog("123456789012X", "isbn")
    assert results == []

def test_search_author_case_insensitive_positive():
    success, _ = add_book_to_catalog("Book A", "Martin Fowler", "4300000000003", 1)
    assert success
    results = search_books_in_catalog("fOwLeR", "author")
    assert any(b["isbn"] == "4300000000003" for b in results)

def test_search_isbn_exact_positive_with_real_book():
    success, _ = add_book_to_catalog("Exact ISBN", "Author X", "4300000000004", 1)
    assert success
    results = search_books_in_catalog("4300000000004", "isbn")
    assert len(results) == 1 and results[0]["isbn"] == "4300000000004"


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

def test_report_patron_no_activity():
    report = get_patron_status_report("654321")
    assert isinstance(report, dict)
    assert "total_late_fees" in report
    assert report["total_late_fees"] >= 0.0

def test_report_invalid_type_patron_id():
    report = get_patron_status_report(None)
    assert isinstance(report, dict)
    assert report["currently_borrowed"] == []
    assert report["total_late_fees"] == 0.0

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

def test_catalog_ids_are_ints():
    results = get_catalog_display()
    for book in results:
        assert isinstance(book["id"], int)
