import sqlite3

from flask import current_app, g


# g is per-request state


def get_db() -> sqlite3.Connection:
    """
    zwraca uchwyt do bazy danych dzięki któremu można wykonać zmiany w bazie danych
    :return: Bazę danych
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db():
    """
    Zamyka uchwyt do bazy danych
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """
    czyści bazę danych i ją tworzy
    """
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def add_user(username, password):
    """
    dodaje użytkownika
    :param username: Nazwa użytkownika
    :param password: Hasło użytkownika
    :return:
    """
    db = get_db()
    # todo: replace with jinja2 template
    db.executescript(f"""
INSERT INTO users (username, password)
VALUES ('{username}', '{password}');
""")


def print_table():
    """
    Wypisuje całą tabelę użytkowników w formacie csv
    :return:
    """
    db = get_db()
    rows: list[sqlite3.Row] = db.execute("SELECT * FROM users;").fetchall()
    for key in rows[0].keys():
        print(key, end=", ")
    print()
    for row in rows:
        for key in row.keys():
            print(row[key], end=", ")
        print()


def print_help():
    """
    Wypisuje sposób użycia programu
    :return:
    """
    print("""Usage:
db.py clear                 - clears the database
db.py add <user> <password> - adds a user
db.py print_table           - prints all users
""")


def main():
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

        if argv[1] == "print_table":
            print("Printing table")
            print_table()
            return

        print_help()


if __name__ == '__main__':
    main()
