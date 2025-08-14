"""Progress in a table."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from rich.console import RenderableType

console = Console()


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape sequences from a string.

    ANSI escape sequences are used to control formatting, color, and other
    output options on text terminals. This function removes these sequences
    to obtain the plain text content.

    Args:
        text (str): The input string containing ANSI escape sequences.

    Returns:
        str: The input string with ANSI escape sequences removed.

    """
    ansi_escape = re.compile(r"\x1b\[([0-9]+)(;[0-9]+)*m")
    return ansi_escape.sub("", text)


def get_renderable_width(renderable: Any) -> int:
    """Calculate the actual width of a renderable object.

    This function captures the rendered output of any renderable object
    (e.g., Progress, Table, Panel), removes any ANSI escape sequences
    (e.g., color codes), and calculates the maximum width of the rendered lines.
    This is useful for determining the true width of a renderable object
    when displayed in the terminal.

    Args:
        renderable (Any): Any renderable object that can be printed by
            `rich.console.Console`.

    Returns:
        int: The maximum width of the rendered object, excluding ANSI
        escape sequences.

    """
    with console.capture() as capture:
        console.print(renderable)

    lines = capture.get().splitlines()
    if not lines:
        return 0

    return max(len(strip_ansi_codes(line)) for line in lines)


def create_table(renderables: Sequence[RenderableType], padding: int = 2) -> Table:
    """Create a grid table to display multiple progress bars.

    This function organizes a list of `Progress` objects into a grid layout
    based on the available terminal width. The number of columns is dynamically
    calculated to fit the terminal width, ensuring that all progress bars are
    displayed without exceeding the terminal's boundaries.

    Args:
        renderables (Sequence[RenderableType]): A sequence of renderables to be
            displayed in the table.
        padding (int): Get padding around progress bars. Defaults to 2.

    Returns:
        Table: A `rich.Table` object containing the progress bars arranged
            in a grid layout.

    """
    table = Table.grid(padding=(0, padding))
    if not renderables:
        return table

    width = max(get_renderable_width(p) for p in renderables) + padding
    ncols = max(1, console.size.width // width)

    for i in range(0, len(renderables), ncols):
        table.add_row(*renderables[i : i + ncols])

    return table
