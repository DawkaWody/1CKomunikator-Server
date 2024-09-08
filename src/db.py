from sqlite3 import Connection, connect, PARSE_DECLTYPES, Row
from typing import Optional

from flask import current_app, g
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlescapy import sqlescape

from utils import root

# g is per-request state
sql_script_templates_env = Environment(
    loader=FileSystemLoader(root / "sql_functions"),
    autoescape=select_autoescape(),
    cache_size=0,
)

st_add_user = st_get_user = st_clear = None

def load_script_templates() -> None:
    global st_add_user, st_get_password, st_clear
    st_add_user     = sql_script_templates_env.get_template("add_user.sql"    ).render().strip()
    st_get_password = sql_script_templates_env.get_template("get_password.sql").render().strip()
    st_clear        = sql_script_templates_env.get_template("clear.sql"       ).render().strip()

def get_db() -> Connection:
    """
    zwraca uchwyt do bazy danych dzięki któremu można wykonać zmiany w bazie danych
    :return: Bazę danych
    """
    if "db" not in g:
        g.db = connect(
            current_app.config["DATABASE"],
            detect_types=PARSE_DECLTYPES,
            autocommit=True,
        )
        g.db.row_factory = Row
    return g.db


def close_db() -> None:
    """
    Zamyka uchwyt do bazy danych
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db() -> None:
    """
    czyści bazę danych i ją tworzy
    """
    get_db().executescript(st_clear)


def add_user(username, password) -> None:
    """
    dodaje użytkownika
    :param username: Nazwa użytkownika
    :param password: Hasło użytkownika
    :return:
    """
    if username is None or len(username) == 0:
        raise ValueError("Invalid name null")
    if get_password(username) is not None:
        raise ValueError("Such user exists")
    get_db().executescript(st_add_user)


def get_password(username) -> Optional[str]:
    """
    zwraca hasło
    :param username: Nazwa użytkownika
    :return:
    """

    row = get_db().execute(st_get_password).fetchone()
    return row["password"] if row else None


def print_table() -> None:
    """
    Wypisuje całą tabelę użytkowników w formacie csv
    :return:
    """
    rows: list[Row] = get_db().execute("SELECT * FROM users;").fetchall()
    for key in rows[0].keys():
        print(key, end=", ")
    print()
    for row in rows:
        for key in row.keys():
            print(row[key], end=", ")
        print()


def print_help() -> None:
    """
    Wypisuje sposób użycia programu
    :return:
    """
    print("""Usage:
db.py clear                 - clears the database
db.py add <user> <password> - adds a user
db.py print_table           - prints all users
db.py get <user>            - gets password about
""")


def main() -> None:
    """
    główna funkcja
    :return:
    """
    from sys import argv
    from main import app

    load_script_templates()

    with app.app_context():
        if len(argv) < 2 or argv[1] == "help":
            print_help()
            return

        if argv[1] == "clear":
            print("Clearing database...")
            init_db()
            return

        if argv[1] == "add":
            # program, "add", username, passwort
            assert len(argv) == 4, "Usage: db.py add <user> <password>"
            print(f"Adding user {argv[2]}...")
            add_user(argv[2], argv[3])
            return

        if argv[1] == "get":
            # program, "get", username
            assert len(argv) == 3, "Usage: db.py get <user>"
            print(f"Getting passwor of user {argv[2]}...")
            print(get_password(argv[2]))
            return

        if argv[1] == "print_table":
            print("Printing table")
            print_table()
            return

        print_help()


if __name__ == '__main__':
    main()
