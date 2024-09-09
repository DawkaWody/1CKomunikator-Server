"""Contains stuff that's used in db and main to avoid cycle imports."""
import pathlib

APP_NAMES = ["1ckomunikator", "1ckomunikator-server"]


def get_root(cwd: pathlib.Path | None = None) -> pathlib.Path:
    """Return path to app root where README is at."""
    root = cwd or pathlib.Path.cwd()
    if root.name.lower() in APP_NAMES:
        pass  # ok
    elif root.parent.name.lower() in APP_NAMES:
        root = root.parent
    else:
        for parent in root.parents:
            if parent.name in APP_NAMES:
                root = parent
                break
        else:
            msg = "cannot find project root"
            raise ValueError(msg)
    return root
