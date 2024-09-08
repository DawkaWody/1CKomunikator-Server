from sqlescapy import sqlescape

try:
    __import__("pytest")
except ImportError:
    raise TypeError("Please install testing requirements (pyptest and requests)")
from shutil import rmtree
from sqlite3 import connect, Connection
from uuid import uuid1

import pytest

import db
from main import app
from utils import root

printable = "".join(chr(i) for i in range(32, 126))

USERNAMES = ["admin234", "12345", "t"
                                  "very_long_name_to_check_for_character_limit_and_that_it_is_not_the_same_as_in_fill_db_function_because_it"
                                  "_will_raise_an_error_and_is_this_long_enough_or_it_needs_to_be_longer"]
PASSWORDS = ["admin123", "123", "root", "t", "1", "_", printable,
             "very_long_password_to_check_for_character_limit_and_that_it_is_not_the_same_as_in_fill_db_function_"
             "because_it_will_raise_an_error_and_is_this_long_enough_or_it_needs_to_be_longer?"]
FILL_DATA_USERNAMES = ["admin", "123", "test", "very_long_name_to_check_for_character_limit"]
FILL_DATA_PASSWORDS = ["admin", "t", "password", "very_long_password_to_check_for_character_limit"]


@pytest.fixture
def db_handle():
    database_folder = root / "tmp" / f"test_database{uuid1().hex}"
    database_folder.mkdir(parents=True, exist_ok=True)
    app.config["DATABASE"] = str()
    # creating the db
    handle = connect(app.config["DATABASE"], autocommit=True)
    yield handle
    handle.close()
    path = str(database_folder)
    try:
        (database_folder / "test_db.sqlite").unlink(missing_ok=True)
    except PermissionError:
        handle = connect(app.config["DATABASE"], autocommit=True)
        handle.executescript("""DROP TABLE IF EXISTS users;""")
    rmtree(path, ignore_errors=True)


def fill_db(db_handle: Connection):
    db_handle.executescript("""
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);
""")
    db_handle.executemany("""
INSERT INTO users (username, password)
VALUES (?, ?);
""", list(zip(FILL_DATA_USERNAMES, FILL_DATA_PASSWORDS)))


def get_db_data(db_handle: Connection):
    rows = db_handle.execute("SELECT * FROM users").fetchall()
    result = []
    for row in rows:
        result.append((row["username"], row["password"]))
    return result


def test_init_db_full(db_handle, monkeypatch):
    fill_db(db_handle)

    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("db.connect", mock_connect)
    with app.app_context():
        db.init_db()
    tables = db_handle.execute("""SELECT * FROM sqlite_schema WHERE type="table" AND name="users" """).fetchall()
    assert len(tables) == 1, "init_db() did not create the table"
    result = db_handle.execute("SELECT * FROM users").fetchall()
    assert len(result) == 0, "init_db() did not clear all"


def test_init_db_empty(db_handle: Connection):
    with app.app_context():
        db.init_db()
    tables = db_handle.execute("""SELECT * FROM sqlite_schema WHERE type="table" AND name="users" """).fetchall()
    assert len(tables) == 1, "init_db() did not create the table"
    result = db_handle.execute("SELECT * FROM users").fetchall()
    assert len(result) == 0, "init_db() did not cleer all"


def test_close_db_opened(monkeypatch):
    closed = False

    class MockDb:
        def close(self):
            nonlocal closed
            closed = True

    class MockG:
        def pop(self, name, default):
            return MockDb()

    monkeypatch.setattr("db.g", MockG())
    with app.app_context():
        db.close_db()

    assert closed, "db not closed"


def test_close_db_closed(monkeypatch):
    class MockG:
        def pop(self, name, default):
            return None

    monkeypatch.setattr("db.g", MockG())

    with app.app_context():
        db.close_db()


@pytest.mark.parametrize("username", USERNAMES)
@pytest.mark.parametrize("password", PASSWORDS)
def test_add_user_empty(username, password, monkeypatch, db_handle: Connection):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("db.connect", mock_connect)

    with app.app_context():
        db.init_db()
        db.add_user(username, password)
    assert get_db_data(db_handle) == [(sqlescape(username), sqlescape(password))], "add_user did not add user"


@pytest.mark.parametrize("username", USERNAMES)
@pytest.mark.parametrize("password", PASSWORDS)
def test_add_user_full(username, password, monkeypatch, db_handle: Connection):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("db.connect", mock_connect)
    with app.app_context():
        db.init_db()
        fill_db(db_handle)
        db.add_user(username, password)
    assert (sqlescape(username), sqlescape(password)) in get_db_data(db_handle)


@pytest.mark.parametrize("username", FILL_DATA_USERNAMES)
def test_add_user_invalid(username, db_handle, monkeypatch):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("db.connect", mock_connect)
    with app.app_context():
        fill_db(db_handle)
        with pytest.raises(ValueError):
            db.add_user(username, "test")


def test_add_user_no_username(db_handle, monkeypatch):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("db.connect", mock_connect)
    with app.app_context():
        db.init_db()
        with pytest.raises(ValueError):
            db.add_user("", "test")
