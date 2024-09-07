from pathlib import Path

APP_NAME = "1CKomunikator"

root = Path.cwd()
if root.name == APP_NAME:
    pass  # ok
elif root.parent.name == APP_NAME:
    root = root.parent
else:
    for parent in root.parents:
        if parent.name == APP_NAME:
            root = parent
            break
    else:
        raise ValueError(f"cannot find project root {root}")

