from pathlib import Path
from typing import Literal

APP_NAMES = ["1ckomunikator", "1ckomunikator-server"]

root = Path.cwd()

print(root.name)

if root.name.lower() in APP_NAMES:
    pass  # ok
elif root.name in APP_NAMES:
    root = root.parent
elif root.name == "tests":
    root = Path("../")
else:
    for parent in root.parents:
        if parent.name in APP_NAMES:
            root = parent
            break
    else:
        raise ValueError("cannot find project root")

