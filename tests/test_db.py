try:
    __import__("pytest")
    __import__("requests")
except ImportError:
    raise TypeError("Please install testing requirements (pyptest and requests)")
from sqlite3 import connect
from uuid import uuid1

import pytest

import db
from main import app
from utils import root

@pytest.fixture
def db_handle():
    database_folder = root / "tmp" / f"test_database{uuid1().hex}"
    database_folder.mkdir()
    app.config["DATABASE"] = str(database_folder / "test_db.sqlite")
    # creating the db
    handle = connect(app.config["DATABASE"])
    yield handle
    handle.close()
    (database_folder / "test_db.sqlite").unlink()
    database_folder.rmdir()

def fill_db(db_handle):
    db_handle.executescript("""
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);
""")
    db_handle.executemany("""
INSERT INTO users (username, password)
VALUES (?, ?);
""", [
        ("admin", "admin"),
        ("123", "t"),
        ("test", "password"),
        ("very_long_name_to_check_for_character_limit", "very_long_password_to_check_for_character_limit")
    ])

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

def test_init_db_empty(db_handle):
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
