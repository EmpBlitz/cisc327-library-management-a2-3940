from unittest.mock import Mock
from services.payment_service import PaymentGateway
from datetime import datetime, timedelta
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

## pay_late_fees tests
def test_pay_late_fees_success(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 5.0, "days_overdue": 3, "status": "OK"})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 1, "title": "Clean Code", "available_copies": 1, "total_copies": 1})
    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (True, "txn_123", "OK")

    success, msg, txn = pay_late_fees("123456", 1, gateway)
    assert success is True
    assert txn == "txn_123"
    gateway.process_payment.assert_called_once()

def test_pay_late_fees_no_fee(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 0.0, "days_overdue": 0, "status": "OK"})
    gateway = Mock(spec=PaymentGateway)
    success, msg, txn = pay_late_fees("123456", 1, gateway)
    assert success is False
    assert "no late fee" in msg.lower()
    assert txn is None
    gateway.process_payment.assert_not_called()

def test_pay_late_fees_declined(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 4.0, "days_overdue": 2, "status": "OK"})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 1, "title": "DDD", "available_copies": 1, "total_copies": 1})
    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (False, "", "declined")
    success, msg, txn = pay_late_fees("123456", 1, gateway)
    assert success is False
    assert txn is None
    gateway.process_payment.assert_called_once()

def test_pay_late_fees_invalid_patron_id():
    gateway = Mock(spec=PaymentGateway)
    success, msg, txn = pay_late_fees("ABCDEF", 1, gateway)  # not 6 digits
    assert success is False
    assert txn is None
    gateway.process_payment.assert_not_called()

def test_pay_late_fees_zero(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 0.0, "days_overdue": 0, "status": "OK"})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 1, "title": "X", "available_copies": 1, "total_copies": 1})

    gateway = Mock(spec=PaymentGateway)

    success, msg, txn = pay_late_fees("123456", 1, gateway)

    assert success is False
    assert txn is None
    gateway.process_payment.assert_not_called()

def test_pay_late_fees_network_error (mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 7.0, "days_overdue": 5, "status": "OK"})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 1, "title": "Refactoring", "available_copies": 1, "total_copies": 1})

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.side_effect = Exception("Network error")

    success, msg, txn = pay_late_fees("123456", 1, gateway)

    assert success is False
    assert txn is None
    gateway.process_payment.assert_called_once()

def test_pay_late_fees_book_not_found(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 4.0, "days_overdue": 2, "status": "OK"})
    mocker.patch("services.library_service.get_book_by_id", return_value=None)

    gateway = Mock(spec=PaymentGateway)
    success, msg, txn = pay_late_fees("123456", 999, gateway)

    assert success is False and txn is None
    assert "book not found" in msg.lower()
    gateway.process_payment.assert_not_called()

def test_pay_late_fees_bad_info_missing(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"days_overdue": 3, "status": "OK"})  # missing 'fee_amount'

    gateway = Mock(spec=PaymentGateway)
    success, msg, txn = pay_late_fees("123456", 1, gateway)

    assert success is False and txn is None
    assert "unable to calculate late fees" in msg.lower()
    gateway.process_payment.assert_not_called()

## refund_late_fee_payment tests
def test_refund_success():
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (True, "OK")
    success, msg = refund_late_fee_payment("txn_123", 5.0, gateway)
    assert success is True
    gateway.refund_payment.assert_called_once_with("txn_123", 5.0)

def test_refund_invalid_transaction_id():
    gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("", 5.0, gateway)
    assert success is False
    gateway.refund_payment.assert_not_called()

def test_refund_negative_amount_rejected():
    gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("txn_123", -1.0, gateway)
    assert success is False
    gateway.refund_payment.assert_not_called()

def test_refund_zero_amount_rejected():
    gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("txn_123", 0.0, gateway)
    assert success is False
    gateway.refund_payment.assert_not_called()

def test_refund_exceeds_max_rejected():
    gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("txn_123", 16.0, gateway)
    assert success is False
    gateway.refund_payment.assert_not_called()

def test_refund_success_at_max():
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (True, "OK")
    success, msg = refund_late_fee_payment("txn_123", 15.0, gateway)
    assert success is True
    gateway.refund_payment.assert_called_once_with("txn_123", 15.0)

def test_refund_invalid_transaction_id_format_not_called():
    gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("abc123", 5.0, gateway)
    assert success is False
    assert "invalid transaction id" in msg.lower()
    gateway.refund_payment.assert_not_called()

def test_refund_payment_invalid_txn_id(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)
    gateway = PaymentGateway()
    success, msg = gateway.refund_payment("bad_txn", 5.00)

    assert success is False
    assert msg == "Invalid transaction ID"

def test_refund_payment_empty_txn_id(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)
    gateway = PaymentGateway()
    success, msg = gateway.refund_payment("", 5.00)

    assert success is False
    assert msg == "Invalid transaction ID"
    
def test_refund_payment_amount_zero(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)
    gateway = PaymentGateway()
    success, msg = gateway.refund_payment("txn_abc", 0.0)

    assert success is False
    assert msg == "Invalid refund amount"

def test_refund_payment_amount_negative(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)
    gateway = PaymentGateway()
    success, msg = gateway.refund_payment("txn_abc", -1.0)

    assert success is False
    assert msg == "Invalid refund amount"

## add_book
def test_add_book_database_insert_failure(mocker):
    mocker.patch("services.library_service.get_book_by_isbn", return_value=None)
    mocker.patch("services.library_service.insert_book", return_value=False)
    success, msg = add_book_to_catalog("DB Err", "A", "3213213213213", 1)
    assert success is False
    assert "database error" in msg.lower()

## borrow_book
def test_borrow_book_unavailable_via_stub(mocker):
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 10, "title": "U", "available_copies": 0, "total_copies": 1})
    success, msg = borrow_book_by_patron("123456", 10)
    assert success is False and "not available" in msg.lower()

def test_borrow_reaches_limit(mocker):
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 11, "title": "L", "available_copies": 1, "total_copies": 1})
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=5)
    success, msg = borrow_book_by_patron("123456", 11)
    assert success is False and "maximum borrowing limit" in msg.lower()

def test_borrow_insert_record_failure(mocker):
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 12, "title": "I", "available_copies": 1, "total_copies": 1})
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.insert_borrow_record", return_value=False)
    success, msg = borrow_book_by_patron("123456", 12)
    assert success is False and "creating borrow record" in msg.lower()

def test_borrow_update_availability_failure(mocker):
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 13, "title": "A", "available_copies": 1, "total_copies": 1})
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.insert_borrow_record", return_value=True)
    mocker.patch("services.library_service.update_book_availability", return_value=False)
    success, msg = borrow_book_by_patron("123456", 13)
    assert success is False and "updating book availability" in msg.lower()

def test_borrow_success(mocker):
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 14, "title": "S", "available_copies": 2, "total_copies": 2})
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.insert_borrow_record", return_value=True)
    mocker.patch("services.library_service.update_book_availability", return_value=True)
    success, msg = borrow_book_by_patron("123456", 14)
    assert success is True and "successfully borrowed" in msg.lower()

## return_book
def test_return_no_borrow_stubbed(mocker):
    # Valid book, but no records
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 21, "title": "R", "available_copies": 0, "total_copies": 1})
    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[])
    success, msg = return_book_by_patron("123456", 21)
    assert success is False and "no borrow record" in msg.lower()

def test_return_update_record_failure(mocker):
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 22, "title": "T", "available_copies": 0, "total_copies": 1})
    mocker.patch("services.library_service.get_patron_borrowed_books",
                 return_value=[{"book_id": 22, "title": "T"}])
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 0.0, "days_overdue": 0, "status": "OK"})
    mocker.patch("services.library_service.update_borrow_record_return_date", return_value=False)

    success, msg = return_book_by_patron("123456", 22)
    assert success is False
    assert "recording the return" in msg.lower()

def test_return_update_availability_failure(mocker):
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 23, "title": "U", "available_copies": 0, "total_copies": 1})
    mocker.patch("services.library_service.get_patron_borrowed_books",
                 return_value=[{"book_id": 23, "title": "U"}])
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 0.0, "days_overdue": 0, "status": "OK"})
    mocker.patch("services.library_service.update_borrow_record_return_date", return_value=True)
    mocker.patch("services.library_service.update_book_availability", return_value=False)

    success, msg = return_book_by_patron("123456", 23)
    assert success is False
    assert "updating book availability" in msg.lower()

def test_return_update_success(mocker):
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 24, "title": "N", "available_copies": 0, "total_copies": 1})
    mocker.patch("services.library_service.get_patron_borrowed_books",
                 return_value=[{"book_id": 24, "title": "N"}])
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 0.0, "days_overdue": 0, "status": "OK"})
    mocker.patch("services.library_service.update_borrow_record_return_date", return_value=True)
    mocker.patch("services.library_service.update_book_availability", return_value=True)

    success, msg = return_book_by_patron("123456", 24)
    assert success is True
    assert "returned on time" in msg.lower()

def test_return_with_late_fee(mocker):
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 25, "title": "L", "available_copies": 0, "total_copies": 1})
    mocker.patch("services.library_service.get_patron_borrowed_books",
                 return_value=[{"book_id": 25, "title": "L"}])
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 3.00, "days_overdue": 10, "status": "OK"})
    mocker.patch("services.library_service.update_borrow_record_return_date", return_value=True)
    mocker.patch("services.library_service.update_book_availability", return_value=True)

    success, msg = return_book_by_patron("123456", 25)
    assert success is True
    assert "your late fee is: $3.00 for 10 overdue day(s)." in msg.lower()

## calculate_late_fee
def test_calculate_late_fee_no_fee(mocker):
    future_due = datetime.now() + timedelta(days=5)
    mocker.patch("services.library_service.get_patron_borrowed_books",
                 return_value=[{"book_id": 31, "due_date": future_due}])

    info = calculate_late_fee_for_book("123456", 31)
    assert info["status"] == "OK"
    assert info["days_overdue"] == 0
    assert info["fee_amount"] == 0.0

def test_calculate_late_fee_with_fee(mocker):
    past_due = datetime.now() - timedelta(days=10)
    mocker.patch("services.library_service.get_patron_borrowed_books",
                 return_value=[{"book_id": 32, "due_date": past_due}])

    info = calculate_late_fee_for_book("123456", 32)
    assert info["status"] == "OK"
    assert info["days_overdue"] == 10
    assert info["fee_amount"] == 6.5

## search_books
def test_search_books_found(mocker):
    mocker.patch("services.library_service.get_all_books", return_value=[
        {"id": 41, "title": "Python 101", "author": "A", "isbn": "111", "available_copies": 3, "total_copies": 3},
        {"id": 42, "title": "Other", "author": "B", "isbn": "222", "available_copies": 1, "total_copies": 1},
    ])
    results = search_books_in_catalog("Python", "title")
    assert len(results) == 1
    assert results[0]["title"] == "Python 101"

def test_search_author_positive(mocker):
    mocker.patch("services.library_service.get_all_books", return_value=[
        {"id": 1, "title": "A", "author": "Martin Fowler", "isbn": "111", "available_copies": 1, "total_copies": 1},
        {"id": 2, "title": "B", "author": "Someone Else", "isbn": "222", "available_copies": 1, "total_copies": 1},
    ])
    results = search_books_in_catalog("fowler", "author")
    assert len(results) == 1 and results[0]["author"] == "Martin Fowler"

def test_search_isbn_exact_positive(mocker):
    mocker.patch("services.library_service.get_all_books", return_value=[
        {"id": 1, "title": "A", "author": "B", "isbn": "9780132350884", "available_copies": 1, "total_copies": 1},
        {"id": 2, "title": "C", "author": "D", "isbn": "1111111111111", "available_copies": 1, "total_copies": 1},
    ])
    results = search_books_in_catalog("9780132350884", "isbn")
    assert len(results) == 1 and results[0]["id"] == 1

# verify_payment_status
def test_verify_payment_valid_txn(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)
    gateway = PaymentGateway()
    status = gateway.verify_payment_status("txn_123456_1700000000")

    assert status["status"] == "completed"
    assert status["transaction_id"] == "txn_123456_1700000000"
    assert "amount" in status and isinstance(status["amount"], float)
    assert "timestamp" in status

def test_verify_payment_status_not_found_for_txn(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)
    gateway = PaymentGateway()
    status = gateway.verify_payment_status("bad_txn_id")

    assert status["status"] == "not_found"
    assert "Transaction not found" in status["message"]
    
## process_payment
def test_process_payment_exceeds_limit(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)
    gateway = PaymentGateway()
    success, txn, msg = gateway.process_payment("123456", 1000.01, "Late fees")

    assert success is False
    assert txn == ""
    assert "amount exceeds limit" in msg

def test_process_payment_invalid_patron_id(mocker):
    mocker.patch("services.payment_service.time.sleep", return_value=None)
    gateway = PaymentGateway()
    success, txn, msg = gateway.process_payment("12345", 10.0, "Late fees")  # 5 digits

    assert success is False
    assert txn == ""
    assert "Invalid patron ID format" in msg