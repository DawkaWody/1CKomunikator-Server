try:
    __import__("pytest")
except ImportError:
    raise TypeError("Please install testing requirements (pyptest and requests)")
import pathlib
import shutil
import sqlite3
import uuid

import pytest

import db
from main import app
from utils import root


@pytest.fixture
def db_handle():
    database_folder = root / "tmp" / f"test_database{uuid.uuid1().hex}"
    database_folder.mkdir(parents=True, exist_ok=True)
    app.config["DATABASE"] = str(database_folder / "test_sqlite")
    # creating the db
    handle = sqlite3.connect(app.config["DATABASE"])
    yield handle
    handle.close()
    shutil.rmtree(str(database_folder), ignore_errors=True)


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

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    tables = db_handle.execute("""SELECT * FROM sqlite_schema WHERE type="table" AND name="users" """).fetchall()
    assert len(tables) == 1, "init_db() did not create the table"
    result = db_handle.execute("SELECT * FROM users").fetchall()
    assert len(result) == 0, "init_db() did not clear all"


def test_init_db_empty(db_handle, monkeypatch):
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
    db_manager.__db = MockDb()
    db_manager.close_db()
    assert closed, "db not closed"


def test_close_db_closed(monkeypatch):
    db_manager = db.DbManager(pathlib.Path())
    db_manager.close_db()
