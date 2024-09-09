# pylint: disable=W0621,R0903
try:
    import pytest
except (ImportError, ModuleNotFoundError) as err:
    msg = "Please install testing requirements (pyptest and requests)"
    raise TypeError(msg) from err
import pathlib
import shutil
import sqlite3
import typing
import uuid

import sqlescapy

import db
from main import app
from utils import get_root

from .sample_data import PASSWORDS, USERNAME_WRONG, USERNAMES_A, USERNAMES_B

if typing.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


# noinspection PyArgumentList
@pytest.fixture
def db_handle():
    database_folder = get_root() / "tmp" / f"test_database{uuid.uuid1().hex}"
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


def fill_db(db_handle: sqlite3.Connection, usernames: list[str], passwords: list[str] | None = None):
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
    db_handle.executemany(
        """
INSERT INTO users (username, password)
VALUES (?, ?);
""",
        list(zip(usernames, passwords, strict=False)),
    )


def get_db_data(db_handle: sqlite3.Connection):
    rows = db_handle.execute("SELECT * FROM users").fetchall()
    return [(row["username"], row["password"]) for row in rows]


def test_init_db_full(db_handle: sqlite3.Connection, monkeypatch: "MonkeyPatch"):
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


def test_init_db_empty(db_handle: sqlite3.Connection, monkeypatch: "MonkeyPatch"):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    tables = db_handle.execute("""SELECT * FROM sqlite_schema WHERE type="table" AND name="users" """).fetchall()
    assert len(tables) == 1, "init_db() did not create the table"
    result = db_handle.execute("SELECT * FROM users").fetchall()
    assert len(result) == 0, "init_db() did not cleer all"


def test_close_db_opened(monkeypatch: "MonkeyPatch"):
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
def test_add_user_empty(username: str, password: str, db_handle: sqlite3.Connection, monkeypatch: "MonkeyPatch"):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)

    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    db_manager.add_user(username, password)
    assert get_db_data(db_handle) == [
        (sqlescapy.sqlescape(username), sqlescapy.sqlescape(password)),
    ], "add_user did not add user"


@pytest.mark.parametrize("username", USERNAMES_A)
@pytest.mark.parametrize("password", PASSWORDS)
def test_add_user_full(username: str, password: str, db_handle: sqlite3.Connection, monkeypatch: "MonkeyPatch"):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    fill_db(db_handle, USERNAMES_B)
    db_manager.add_user(username, password)
    assert (sqlescapy.sqlescape(username), sqlescapy.sqlescape(password)) in get_db_data(db_handle)


@pytest.mark.parametrize("username", USERNAMES_A)
def test_add_user_invalid_exists(username: str, db_handle: sqlite3.Connection, monkeypatch: "MonkeyPatch"):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)

    fill_db(db_handle, USERNAMES_A)
    db_manager = db.DbManager(pathlib.Path())
    with pytest.raises(ValueError, match="Such user exists"):
        db_manager.add_user(username, "test")


@pytest.mark.parametrize("username", USERNAME_WRONG)
def test_add_user_invalid(username: str, db_handle: sqlite3.Connection, monkeypatch: "MonkeyPatch"):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    with pytest.raises(ValueError, match=r"Invalid name .*"):
        db_manager.add_user("", "test")


@pytest.mark.parametrize("password", PASSWORDS)
def test_get_password_exists(password: str, db_handle: sqlite3.Connection, monkeypatch: "MonkeyPatch"):
    def mock_connect(*args, **kwargs):
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    fill_db(db_handle, USERNAMES_A)
    fill_db(db_handle, ["test"], [password])
    assert db_manager.get_password("test") == password, "get_password got invalid password"


@pytest.mark.parametrize("username", USERNAMES_A)
def test_get_password_invalid_full(username: str, db_handle: sqlite3.Connection, monkeypatch: "MonkeyPatch"):
    def mock_connect(*args, **kwargs) -> sqlite3.Connection:
        return db_handle

    monkeypatch.setattr("sqlite3.connect", mock_connect)
    db_manager = db.DbManager(pathlib.Path())
    db_manager.init_db()
    fill_db(db_handle, USERNAMES_B)
    assert db_manager.get_password(username) is None, "get_password got password when there is none"
