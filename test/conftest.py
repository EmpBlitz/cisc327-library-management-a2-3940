import pytest
import os
from database import init_database

@pytest.fixture(autouse=True)
def clearData ():
    import database
    o_datab = database.DATABASE
    test_datab = "test_library.db"
    database.DATABASE = test_datab
    init_database()
    yield
    database.DATABASE = o_datab
    if os.path.exists(test_datab):
        os.remove(test_datab)
