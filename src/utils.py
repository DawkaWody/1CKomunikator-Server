"""Contains stuff that's used in db and main to avoid cycle imports."""
from pathlib import Path

APP_NAMES = ["1ckomunikator", "1ckomunikator-server"]

root = Path.cwd()
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
