from itertools import islice
from math import floor
from typing import Optional, Iterable

import typer
from rich import box
from rich.console import Console, group
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text
from typing_extensions import Annotated

from rbase24.scheme import load_schemes
from rbase24.typedefs import Palette, SchemeDB
from rbase24.color import hex_string_to_rgb, contrast_color
from rbase24.config import Base24ViewerConfig


def print_schemes(db: SchemeDB) -> None:
    console = Console()
    column_count = int(floor(console.width / 54))

    table = Table.grid(padding=0)
    for col in range(column_count):
        table.add_column(str(col))

    chunks = [batch for batch in chunked(db.values(), column_count)]

    for schemes in chunks:
        panels = []
        for scheme in schemes:
            panels.append(
                Panel(
                    SchemeHeader(scheme),
                    width=50,
                    box=box.MINIMAL,
                )
            )
        table.add_row(*panels)

    console.print(table)


@group()
def SchemeHeader(scheme: dict):
    yield Text(f"Name: {scheme['name']}")
    yield Text(f"Author: {scheme['author']}")
    yield Text(f"File: {scheme['name']}")
    yield Text(f"Slug: {scheme['slug']}")
    yield Text(f"System: {scheme['system']}")

    if scheme["description"]:
        yield Text(f"Description: {scheme['description']}")

    yield Panel(
        SchemePalette(scheme["palette"]),
        box=box.MINIMAL,
    )


@group()
def SchemePalette(palette: Palette):
    table = Table.grid(padding=1)
    table.add_column("0")
    table.add_column("2")
    table.add_column("3")
    table.add_column("4")

    chunks = [batch for batch in chunked(palette.items(), 4)]

    for chunk in chunks:
        items = []
        for name, value in chunk:
            if not value[0] == "#":
                value = f"#{value}"
            rgb = hex_string_to_rgb(value)
            contrast = contrast_color(rgb)
            style = Style(color=contrast, bgcolor=value)

            display_name = f"{name:^10}"
            display_value = f"{value:^10}"
            items.append(Text(f"\n{display_name}\n{display_value}\n", style=style))
        table.add_row(*items)

    yield table


def chunked(iterable, n) -> Iterable:
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def go(filespec: Annotated[Optional[str], typer.Argument()] = "*"):
    if filespec is None:
        filespec = "*"

    cfg = Base24ViewerConfig()
    if cfg.scheme_dir is None or not cfg.scheme_dir.exists():
        print("No base16 scheme directory configured. Exiting")
        return

    db = load_schemes(cfg.scheme_dir, filespec)
    if not db:
        if filespec == "*":
            print(f"No schemes found in {cfg.scheme_dir}")
        else:
            print(f"No schemes matching '{filespec}' found in {cfg.scheme_dir}")
        return
    print_schemes(db)


def main():
    typer.run(go)
