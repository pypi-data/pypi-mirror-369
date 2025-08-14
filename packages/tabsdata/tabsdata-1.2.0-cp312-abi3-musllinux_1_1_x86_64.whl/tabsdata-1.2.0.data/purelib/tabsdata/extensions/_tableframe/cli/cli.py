#
# Copyright 2025 Tabs Data Inc.
#

from pathlib import Path

import rich_click as click

from tabsdata.extensions._tableframe.cli.style import display_frame
from tabsdata.extensions._tableframe.tools.frames import read_parquet

"""
Internal ee tool to explore, visualize and analyze provenance data.
"""


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.pass_context
@click.version_option()
def cli(_ctx: click.Context):
    pass


@cli.command()
@click.option(
    "--parquet",
    "-p",
    type=click.Path(
        exists=True,
        path_type=Path,
    ),
    required=True,
    help="Path to the parquet file to explore.",
)
@click.option(
    "--limit",
    "-l",
    type=click.IntRange(min=1),
    default=32,
    show_default=True,
    help="Maximum number of rows to explore.",
)
@click.option(
    "--layout",
    "-y",
    type=click.Choice(
        ["list", "rows"],
        case_sensitive=False,
    ),
    default="list",
    show_default=True,
    help=(
        "How to display the decoded provenance: 'list' keeps it as arrays, 'row'"
        " expands to one row per element."
    ),
)
@click.pass_context
def provenance(_ctx: click.Context, parquet: Path, layout: str, limit: int):
    # noinspection PyTypeChecker
    display_frame(
        read_parquet(
            parquet=parquet,
            limit=limit,
            layout=layout,
        )
    )


if __name__ == "__main__":
    cli()
