import os

try:  # When installing the package we don't need to actually import.
    from agox.module import Module  # noqa
    from agox.observer import Observer
    from agox.writer import Writer
    from agox.cli.main import main
    from agox.main.state import State
    from agox.main.agox import AGOX

    __all__ = ["Module", "Observer", "Writer", "State", "AGOX", "__version__", "main"]

except ImportError as e:
    print(e)
    pass
