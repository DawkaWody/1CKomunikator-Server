"""File for communicating db."""
import pathlib
import sqlite3

import jinja2
import sqlescapy

from utils import root


class DbManager:
    """Class for communicating db."""

    def __init__(
        self,
        db_path: pathlib.Path,
        sql_script_templates_env: jinja2.Environment | None = None,
        template_add_user: jinja2.Template | None = None,
        template_get_password: jinja2.Template | None = None,
        template_clear: jinja2.Template | None = None,
    ) -> None:
        """Class for communicating db.

        :param db_path: Path to db
        :param sql_script_templates_env: scripts env, defaults to sql_functions
        :param template_add_user: template for adding user, defaults to add_user.sql
        :param template_get_password: template for getting password, defaults to get_password.sql
        :param template_clear: template for clearing the database, defaults to clear.sql
        """
        self.db_path = db_path
        self.sql_script_templates_env = sql_script_templates_env or jinja2.Environment(
            loader=jinja2.FileSystemLoader(root / "sql_functions"),
            autoescape=jinja2.select_autoescape(),
            cache_size=0,
        )

        self.template_add_user = template_add_user or self.sql_script_templates_env.get_template("add_user.sql")
        self.template_get_password = template_get_password or self.sql_script_templates_env.get_template(
            "get_password.sql",
        )
        self.template_clear = template_clear or self.sql_script_templates_env.get_template("clear.sql")
        self._db = None

    def get_db(self) -> None:
        """Aktualizuje uchwyt do bazy danych dzięki któremu można wykonać zmiany w bazie danych."""
        self._db = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            autocommit=True,
        )
        self._db.row_factory = sqlite3.Row

    def close_db(self) -> None:
        """Zamyka uchwyt do bazy danych."""
        if self._db is not None:
            self._db.close()
            self._db = None

    @property
    def db(self) -> sqlite3.Connection:
        """Automatically refreshing database handle.

        :return:
        """
        if self._db is None:
            self.get_db()
        return self._db

    @db.deleter
    def db(self) -> None:
        self.close_db()

    @db.setter
    def db(self, value: None) -> None:
        """Close handle for database."""
        self.close_db()
        assert value is None

    def init_db(self) -> None:
        """czyści bazę danych i ją tworzy."""
        self.db.executescript(self.template_clear.render().strip())

    def add_user(self, username: str, password: str) -> None:
        """Dodaje użytkownika.

        :param username: Nazwa użytkownika
        :param password: Hasło użytkownika
        :return:
        """
        if username is None or len(username) == 0:
            msg = "Invalid name null"
            raise ValueError(msg)
        if self.get_password(username) is not None:
            msg = "Such user exists"
            raise ValueError(msg)
        self.db.executescript(
            self.template_add_user.render(
                username=sqlescapy.sqlescape(username), password=sqlescapy.sqlescape(password),
            ).strip(),
        )

    def get_password(self, username: str) -> str | None:
        """Zwraca hasło.

        :param username: Nazwa użytkownika
        :return:
        """
        row = self.db.execute(
            self.template_get_password.render(username=sqlescapy.sqlescape(username)).strip(),
        ).fetchone()
        return row["password"] if row is not None else None

    def print_table(self) -> None:
        """Wypisuje całą tabelę użytkowników w formacie csv.

        :return:
        """
        rows: list[sqlite3.Row] = self.db.execute("SELECT * FROM users;").fetchall()
        for key in rows[0]:
            print(key, end=", ")
        print()
        for row in rows:
            for key in row:
                print(row[key], end=", ")
            print()


def print_help() -> None:
    """Wypisuje sposób użycia programu.

    :return:
    """
    print("""Usage:
db.py clear                 - clears the database
db.py add <user> <password> - adds a user
db.py print_table           - prints all users
db.py get <user>            - gets password about
""")


def main() -> None:
    """Run the our cli."""
    from sys import argv

    db = DbManager(root / "main_db.sqlite")
    if len(argv) < 2 or argv[1] == "help":
        print_help()
        return

    if argv[1] == "clear":
        print("Clearing database...")
        db.init_db()
        return

    if argv[1] == "add":
        # program, "add", username, passwort
        assert len(argv) == 4, "Usage: db.py add <user> <password>"
        print(f"Adding user {argv[2]}...")
        db.add_user(argv[2], argv[3])
        return

    if argv[1] == "get":
        # program, "get", username
        assert len(argv) == 3, "Usage: db.py get <user>"
        print(f"Getting password of user {argv[2]}...")
        print(db.get_password(argv[2]))
        return

    if argv[1] == "print_table":
        print("Printing table")
        db.print_table()
        return

    print_help()


if __name__ == "__main__":
    main()
