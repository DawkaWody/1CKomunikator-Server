from pathlib import Path

APP_NAMES = ["1ckomunikator", "1ckomunikator-server"]

root = Path.cwd()

print(root.name)

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
        raise ValueError("cannot find project root")
