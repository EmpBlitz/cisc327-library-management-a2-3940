## <center>Adam Elkenany, 20413940, Group 2 </center>

| Function Name              | Implementation Status | What’s Missing |
|----------------------------|------------------------|----------------|
| add_book_to_catalog        | Complete              | N/A |
| borrow_book_by_patron      | Complete              | N/A |
| return_book_by_patron      | Incomplete            | • Verify that patron actually borrowed the book <br> • Record `return_date` at the time of return <br> • Update available copies without exceeding total <br> • Calculate and return any late fees owed |
| calculate_late_fee_for_book| Incomplete            | • Apply 14-day due date rule <br> • Calculate overdue fees: $0.50/day for first 7 days, then $1.00/day after 7 days <br> • Enforce maximum fee of $15 per book <br> • Return JSON dict with `fee_amount` and `days_overdue` |
| search_books_in_catalog    | Incomplete            | • Implement case-insensitive partial matching for title and author <br> • Implement exact matching for ISBN <br> • Return results in catalog display format |
| get_patron_status_report   | Incomplete            | • Provide list of currently borrowed books with due dates <br> • Return total late fees owed <br> • Return the number of books currently borrowed <br> • Return full borrowing history <br> • Add menu option in the main interface |


# Test Summary

### 1. `add_book_to_catalog`
- Valid book is added successfully
- Author name longer than 100 characters is rejected
- Zero total copies not allowed
- Blank author field not allowed
- Title longer than 200 characters is rejected
- Non integer total copies not accepted 

---

### 2. `borrow_book_by_patron`
- Borrowing works with valid patron ID and book ID
- Patron ID must be numeric
- Patron ID must be exactly 6 digits
- Non existent book ID returns "not found"

---

### 3. `return_book_by_patron`
- Returning with valid patron ID and book ID succeeds or fails with a message  
- Patron ID must be numeric  
- Patron ID must be exactly 6 digits  

---

### 4. `calculate_late_fee_for_book`
- Returns a dictionary with keys: `fee_amount`, `days_overdue`, `status`  
- Days overdue is always non-negative  
- Fee amount is always non-negative  
- Fee amount never exceeds $15 

---

### 5. `search_books_in_catalog`
- Always returns a list  
- Search by title is case-insensitive  
- Search by author supports partial matches  
- Search by ISBN requires exact match  

---

### 6. `get_patron_status_report`
- Always returns a dictionary  
- Total late fees are non-negative
- Report structure is validated as a dictionary

---

### 7. `get_catalog_display`
- Always returns a list of dictionaries
- Each dictionary contains keys: `book_id`, `title`, `author`, `isbn`, `available_copies`, `total_copies`
- `available_copies` is always between 0 and `total_copies`

