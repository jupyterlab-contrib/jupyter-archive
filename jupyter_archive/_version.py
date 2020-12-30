__all__ = ["__version__"]


def _fetchVersion():
    import json
    import pathlib

    HERE = pathlib.Path(__file__).parent.resolve()

    for d in HERE.rglob("package.json"):
        try:
            with d.open() as f:
                return json.load(f)["version"]
        except FileNotFoundError:
            pass

    raise FileNotFoundError(f"Could not find package.json under dir {HERE!s}")


__version__ = _fetchVersion()
