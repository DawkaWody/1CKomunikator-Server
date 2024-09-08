import typing
import sqlite3
import typing
import flask
import jinja2
import sqlescapy

from utils import root

# g is per-request state
sql_script_templates_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(root / "sql_functions"),
    autoescape=jinja2.select_autoescape(),
    cache_size=0,
)

template_add_user = sql_script_templates_env.get_template("add_user.sql")
template_get_password = sql_script_templates_env.get_template("get_password.sql")
template_clear = sql_script_templates_env.get_template("clear.sql")


def get_db() -> sqlite3.Connection:
    """
    zwraca uchwyt do bazy danych dzięki któremu można wykonać zmiany w bazie danych
    :return: Bazę danych
    """
    if "db" not in flask.g:
        flask.g.db = sqlite3.connect(
            flask.current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        flask.g.db.row_factory = sqlite3.Row
    return flask.g.db


def close_db() -> None:
    """
    Zamyka uchwyt do bazy danych
    """
    db = flask.g.pop('db', None)

    if db is not None:
        db.close()


def init_db() -> None:
    """
    czyści bazę danych i ją tworzy
    """
    get_db().executescript(template_clear.render().strip())


def add_user(username, password) -> None:
    """
    dodaje użytkownika
    :param username: Nazwa użytkownika
    :param password: Hasło użytkownika
    :return:
    """
    if username is None or len(username) == 0:
        raise ValueError("Invalid name null")
    if get_password(username):
        raise ValueError("Such user exists")
    get_db().executescript(template_clear.render(
        username=sqlescapy.sqlescape(username),
        password=sqlescapy.sqlescape(password)
    ).strip())


def get_password(username) -> typing.Optional[str]:
    """
    zwraca hasło
    :param username: Nazwa użytkownika
    :return:
    """

    row = get_db().execute(template_get_password.render(
        username=sqlescapy.sqlescape(username)
    ).strip()).fetchone()
    return row["password"] if row else None


def print_table() -> None:
    """
    Wypisuje całą tabelę użytkowników w formacie csv
    :return:
    """
    rows: list[sqlite3.Row] = get_db().execute("SELECT * FROM users;").fetchall()
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
            print(f"Getting password of user {argv[2]}...")
            print(get_password(argv[2]))
            return

        if argv[1] == "print_table":
            print("Printing table")
            print_table()
            return

        print_help()


if __name__ == '__main__':
    main()
