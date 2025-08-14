#
# Copyright 2025 Tabs Data Inc.
#

from pathlib import Path
from typing import Literal

import polars as pl

# noinspection PyProtectedMember
from tabsdata.extensions._tableframe.tools.columns import (
    provenance_to_human_list,
    provenance_to_human_rows,
)


def read_parquet(
    parquet: Path,
    limit: int,
    layout: Literal["list", "rows"] = "list",
) -> pl.LazyFrame | None:
    lf = pl.read_parquet(parquet).lazy().limit(limit)
    match layout:
        case "list":
            return provenance_to_human_list(lf)
        case "rows":
            return provenance_to_human_rows(lf)
    return None
