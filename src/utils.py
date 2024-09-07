from pathlib import Path

APP_NAMES = ["1CKomunikator", "1CKomunikator-server"]

root = Path.cwd()
if root.name in APP_NAMES:
    pass  # ok
elif root.parent.name in APP_NAMES:
    root = root.parent
else:
    for parent in root.parents:
        if parent.name in APP_NAMES:
            root = parent
            break
    else:
        raise ValueError("cannot find project root")

