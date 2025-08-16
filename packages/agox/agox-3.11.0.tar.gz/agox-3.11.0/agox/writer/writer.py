from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from rich import style

default_writer_settings = {
    "width": 80
}

global writer_settings
writer_settings = None

global writer_verbosity
writer_verbosity = None

def get_writer_settings() -> dict:
    global writer_settings
    if writer_settings is None:
        writer_settings = default_writer_settings
    return writer_settings

def update_writer_settings(**kwargs) -> None:
    global writer_settings
    writer_settings = get_writer_settings()
    writer_settings.update(kwargs)

def get_writer_verbosity() -> int:
    global writer_verbosity
    return writer_verbosity

def set_writer_verbosity(verbosity: int) -> None:
    global writer_verbosity
    writer_verbosity = verbosity

class Writer:

    DEBUG = 1
    STANDARD = 0

    styles = {
        DEBUG: style.Style(color="dark_orange"),
        STANDARD: style.Style(color="white"),
    }
    
    def __init__(self, verbosity: int = STANDARD, **kwargs) -> None:
        self.console_kwargs = get_writer_settings()
        self.console_kwargs.update(kwargs)
        self._verbosity = verbosity


    def writer(self, string: str, *args, verbosity: int = STANDARD, **kwargs) -> None:
        if verbosity <= self.verbosity:
            console = Console(**self.console_kwargs)
            console.print(string, *args, **kwargs, style=self.styles[verbosity])    

    def __call__(self, string: str, *args, **kwargs) -> None:
        self.writer(string, *args, verbosity=self.STANDARD, **kwargs)

    def debug(self, string: str, *args, **kwargs) -> None:
        self.writer(string, *args, verbosity=self.DEBUG, **kwargs)

    def write_header(self, string: str) -> None:
        console = Console(**self.console_kwargs)
        console.rule(string)

    def write_table(self, table_columns: List, table_rows: List, **table_kwargs) -> None:
        console = Console(**self.console_kwargs)

        table = Table(**table_kwargs)
        for column in table_columns:
            table.add_column(column)

        for row in table_rows:
            table.add_row(*row)

        console.print(table)

    def write_panel(self, panel_content: str, panel_title: Optional[str] = None) -> None:
        console = Console(**self.console_kwargs)
        panel = Panel(panel_content, title=panel_title)
        console.print(panel)

    @staticmethod
    def update_settings(**kwargs) -> None:
        update_writer_settings(**kwargs)

    @property
    def verbosity(self) -> int:
        global_writer_verbosity = get_writer_verbosity()

        if global_writer_verbosity is None:
            verbosity = self._verbosity
        elif global_writer_verbosity > self._verbosity:
            verbosity = global_writer_verbosity
        else:
            verbosity = self._verbosity

        return verbosity


    