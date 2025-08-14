#
# Copyright 2025 Tabs Data Inc.
#

import polars as pl
from rich.console import Console
from rich.table import Table

# noinspection PyProtectedMember
import tabsdata._utils.tableframe._constants as td_constants
from tabsdata.extensions._tableframe.tools.types import is_numeric_dtype

TABLE_BORDER_COLOR = "#84cc16"

TABLE_HEADER_COLOR_SYSTEM = "#f97316"
TABLE_HEADER_COLOR_REGULAR = "#fbbf24"

TABLE_CELL_COLOR_SYSTEM = "#fdba74"
TABLE_CELL_COLOR_REGULAR = "#d9f99d"

console = Console(color_system="truecolor")


def display_cell(cell) -> str:
    if isinstance(cell, list) and all(isinstance(b, bytes) for b in cell):
        value = "[" + ", ".join("0x" + b.hex() for b in cell) + "]"
    elif isinstance(cell, bytes):
        value = f"0x{cell.hex()}"
    else:
        value = str(cell)
    return value


def display_frame(lf: pl.LazyFrame):
    df = lf.collect()

    system_columns = sorted(
        [
            column
            for column in df.columns
            if column.startswith(td_constants.TD_COLUMN_PREFIX)
        ]
    )
    regular_columns = [
        column
        for column in df.columns
        if not column.startswith(td_constants.TD_COLUMN_PREFIX)
    ]

    dtypes = dict(zip(df.columns, df.dtypes))

    columns_arranged = system_columns + regular_columns
    df = df.select(columns_arranged)
    table = Table(
        show_header=True,
        border_style=TABLE_BORDER_COLOR,
    )
    for name in df.columns:
        is_system_column = name.startswith(td_constants.TD_COLUMN_PREFIX)
        header_color = (
            TABLE_HEADER_COLOR_SYSTEM
            if is_system_column
            else TABLE_HEADER_COLOR_REGULAR
        )
        table.add_column(
            name,
            header_style=header_color,
            justify="right" if is_numeric_dtype(dtypes[name]) else "left",
        )

    for row in df.iter_rows():
        styled_row = []
        for idx, cell in enumerate(row):
            name = df.columns[idx]
            is_system_column = name.startswith(td_constants.TD_COLUMN_PREFIX)
            cell_color = (
                TABLE_CELL_COLOR_SYSTEM
                if is_system_column
                else TABLE_CELL_COLOR_REGULAR
            )
            styled_row.append(f"[{cell_color}]{display_cell(cell)}[/]")
        table.add_row(*styled_row)
    console.print(table)
