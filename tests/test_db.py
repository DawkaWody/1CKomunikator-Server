try:
    import pytest
except (ImportError, ModuleNotFoundError):
    raise TypeError("Please install testing requirements (pyptest and requests)")
import pathlib
import shutil
import sqlite3
import uuid

import sqlescapy

import db
from main import app
from utils import root

printable = "".join(chr(i) for i in range(32, 126))

PASSWORDS = ["admin123", "root", "password", printable,
             "very_long_password_to_check_for_character_limit_and_that_it_is_not_the_same_as_in_fill_db_function_"
             "because_it_will_raise_an_error_and_is_this_long_enough_or_it_needs_to_be_longer?"]

USERNAME_WRONG = [""]

USERNAMES_A = ["admin234", "12345", "very_long_name_to_check_for_character_limit_and_that_it_is_not_the_same_as_in_fill"
                                    "_db_function_because_it_will_raise_an_error_and_is_this_long_enough_or_it_needs_to"
                                    "_be_longer"]
USERNAMES_B = ["admin", "123", "test", "very_long_name_to_check_for_character_limit"]


# noinspection PyArgumentList
@pytest.fixture
def db_handle():
    database_folder = root / "tmp" / f"test_database{uuid.uuid1().hex}"
    database_folder.mkdir(parents=True, exist_ok=True)
    app.config["DATABASE"] = str(database_folder / "test_sqlite")
    # creating the db
    handle = sqlite3.connect(app.config["DATABASE"], autocommit=True)
    yield handle
    handle.close()
    path = str(database_folder)
    try:
        (database_folder / "test_db.sqlite").unlink(missing_ok=True)
    except PermissionError:
        handle = sqlite3.connect(app.config["DATABASE"], autocommit=True)
        handle.executescript("""DROP TABLE IF EXISTS users;""")
    shutil.rmtree(path, ignore_errors=True)


def fill_db(db_handle: sqlite3.Connection, usernames, passwords=None):
    if passwords is None:
        passwords = PASSWORDS
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
""", list(zip(usernames, passwords)))


def get_db_data(db_handle: sqlite3.Connection):
    rows = db_handle.execute("SELECT * FROM users").fetchall()
    result = []
    for row in rows:
        result.append((row["username"], row["password"]))
    return result


def test_init_db_full(db_handle, monkeypatch):
    fill_db(db_handle, USERNAMES_B)

    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    tables = db_handle.execute("""SELECT * FROM sqlite_schema WHERE type="table" AND name="users" """).fetchall()
    assert len(tables) == 1, "init_db() did not create the table"
    result = db_handle.execute("SELECT * FROM users").fetchall()
    assert len(result) == 0, "init_db() did not clear all"


def test_init_db_empty(db_handle: sqlite3.Connection, monkeypatch):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
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

    db_manager = db.DbManager(pathlib.Path())
    db_manager._db = MockDb()
    db_manager.close_db()
    assert closed, "db not closed"


def test_close_db_closed():
    db_manager = db.DbManager(pathlib.Path())
    db_manager.close_db()


@pytest.mark.parametrize("username", USERNAMES_A)
@pytest.mark.parametrize("password", PASSWORDS)
def test_add_user_empty(username, password, monkeypatch, db_handle: sqlite3.Connection):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)

    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    db_manager.add_user(username, password)
    assert get_db_data(db_handle) == [
        (sqlescapy.sqlescape(username), sqlescapy.sqlescape(password))], "add_user did not add user"


@pytest.mark.parametrize("username", USERNAMES_A)
@pytest.mark.parametrize("password", PASSWORDS)
def test_add_user_full(username, password, monkeypatch, db_handle: sqlite3.Connection):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    fill_db(db_handle, USERNAMES_B)
    db_manager.add_user(username, password)
    assert (sqlescapy.sqlescape(username), sqlescapy.sqlescape(password)) in get_db_data(db_handle)


@pytest.mark.parametrize("username", USERNAMES_A)
def test_add_user_invalid_exists(username, db_handle, monkeypatch):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)

    fill_db(db_handle, USERNAMES_A)
    db_manager = db.DbManager(pathlib.Path())
    with pytest.raises(ValueError):
        db_manager.add_user(username, "test")


@pytest.mark.parametrize("username", USERNAME_WRONG)
def test_add_user_invalid(username, db_handle, monkeypatch):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    with pytest.raises(ValueError):
        db_manager.add_user("", "test")


@pytest.mark.parametrize("password", PASSWORDS)
def test_get_password_exists(password, db_handle, monkeypatch):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    fill_db(db_handle, USERNAMES_A)
    fill_db(db_handle, ["test"], [password])
    assert db_manager.get_password("test") == password, "get_password got invalid password"


@pytest.mark.parametrize("username", USERNAMES_A)
def test_get_password_invalid_full(username, db_handle, monkeypatch):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    fill_db(db_handle, USERNAMES_B)
    assert db_manager.get_password(username) is None, "get_password got password when there is none"
