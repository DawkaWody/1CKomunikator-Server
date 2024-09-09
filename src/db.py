import sys

import pathlib
import sqlite3
import typing
import collections.abc

import jinja2

from utils import root

tt_sql_escapes: dict[int, str] = {
    0: '\\0',
    8: '\\b',
    9: '\\t',
    10: '\\n',
    13: '\\r',
    26: '\\z',
    34: '',
    37: '\\%',
    39: '',
    92: '\\\\'
}

class DbManager:
    def __init__(
            self,
            db_path: pathlib.Path,
            sql_script_templates_env: typing.Optional[jinja2.Environment] = None,
            template_add_user: typing.Optional[jinja2.Template] = None,
            template_get_password: typing.Optional[jinja2.Template] = None,
            template_clear: typing.Optional[jinja2.Template] = None
    ):
        self.db_path = db_path
        self.sql_script_templates_env = sql_script_templates_env or jinja2.Environment(
            loader=jinja2.FileSystemLoader(root / "sql_functions"),
            autoescape=jinja2.select_autoescape(),
            cache_size=0,
        )

        self.template_add_user = template_add_user or \
                                 self.sql_script_templates_env.get_template("add_user.sql")
        self.template_get_password = template_get_password or \
                                      self.sql_script_templates_env.get_template("get_password.sql")
        self.template_clear = template_clear or \
                              self.sql_script_templates_env.get_template("clear.sql")
        # type : ignore
        self._db: typing.Optional[sqlite3.Connection] = None

    def get_db(self) -> None:
        """
        aktualizuje uchwyt do bazy danych dzięki któremu można wykonać zmiany w bazie danych
        :return: Bazę danych
        """
        self._db = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            autocommit=True,
        )
        self._db.row_factory = sqlite3.Row

    def close_db(self) -> None:
        """
        Zamyka uchwyt do bazy danych
        """
        if self._db is not None:
            self._db.close()
            self._db = None

    @property
    def db(self) -> sqlite3.Connection:
        """
        Atrybut bazy danych
        """
        if self._db is None:
            # Mypy inaczej nie działa poprawnie
            self._db = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES,
                autocommit=True
            )
            self._db.row_factory = sqlite3.Row
        return self._db

    @db.deleter
    def db(self) -> None:
        """
        Zamyka bazę danych
        """
        self.close_db()

    @db.setter
    def db(self, value: typing.Any) -> None:
        """
        Zamyka bazę danych + assertuje `value is None`
        """
        self.close_db()
        assert value is None

    def init_db(self) -> None:
        """
        czyści bazę danych i ją tworzy
        """
        self.db.executescript(self.template_clear.render().strip())

    def add_user(self, username: str, password: str) -> None:
        """
        dodaje użytkownika
        :param username: Nazwa użytkownika
        :param password: Hasło użytkownika
        :return:
        """
        if username is None or len(username) == 0:
            raise ValueError("Invalid name null")
        if self.get_password(username) is not None:
            raise ValueError("Such user exists")
        self.db.executescript(self.template_add_user.render(
            username=username.translate(tt_sql_escapes),
            password=password.translate(tt_sql_escapes)
        ).strip())

    def get_password(self, username: str) -> typing.Optional[str]:
        """
        zwraca hasło
        :param username: Nazwa użytkownika
        :return:
        """

        row = self.db.execute(self.template_get_password.render(
            username=username.translate(tt_sql_escapes)
        ).strip()).fetchone()
        return row["password"] if row is not None else None

    def print_table(self) -> None:
        """
        Wypisuje całą tabelę użytkowników w formacie csv
        :return:
        """
        rows: list[sqlite3.Row] = self.db.execute("SELECT * FROM users;").fetchall()
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

    db = DbManager(root / "main_db.sqlite")
    if len(sys.argv) < 2 or sys.argv[1] == "help":
        print_help()
        return

    if sys.argv[1] == "clear":
        print("Clearing database...")
        db.init_db()
        return

    if sys.argv[1] == "add":
        # program, "add", username, passwort
        assert len(sys.argv) == 4, "Usage: db.py add <user> <password>"
        print(f"Adding user {sys.argv[2]}...")
        db.add_user(sys.argv[2], sys.argv[3])
        return

    if sys.argv[1] == "get":
        # program, "get", username
        assert len(sys.argv) == 3, "Usage: db.py get <user>"
        print(f"Getting password of user {sys.argv[2]}...")
        print(db.get_password(sys.argv[2]))
        return

    if sys.argv[1] == "print_table":
        print("Printing table")
        db.print_table()
        return

    print_help()


if __name__ == '__main__':
    main()
