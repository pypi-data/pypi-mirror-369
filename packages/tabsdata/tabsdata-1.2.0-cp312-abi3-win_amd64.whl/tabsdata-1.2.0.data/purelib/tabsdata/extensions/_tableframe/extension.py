#
#  Copyright 2024 Tabs Data Inc.
#

import logging
from enum import Enum
from typing import Any, Type

import polars as pl

# noinspection PyProtectedMember
import tabsdata._utils.tableframe._constants as td_constants

# noinspection PyProtectedMember
from tabsdata.extensions._features.api.features import Feature, FeaturesManager
from tabsdata.extensions._tableframe.api.api import Extension
from tabsdata.extensions._tableframe.provenance import (
    decode_src,
    encode_src,
)
from tabsdata.extensions._tableframe.version import version

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _row_default() -> pl.Expr:
    return pl.lit(0, pl.UInt64)


class SrcGenerator:
    def __init__(
        self,
        tab: int | None = None,
    ):
        self._tab = tab
        self._row = 0

    def __call__(
        self,
        _old_value: pl.String | None = None,
    ) -> pl.Expr | list[bytes]:  # pl.List(pl.Binary)
        if self._tab is None:
            return []
        row = self._row
        self._row += 1
        data = encode_src(
            ver=None,
            op=td_constants.RowOperation.ROW.value,
            tab=self._tab,
            par=None,
            row=row,
        )
        return [data]


def _src_default() -> pl.Expr:
    return pl.lit([], pl.List(pl.Binary))


class SrcAggregator:
    def __init__(
        self,
        state: td_constants.RowOperation | None = None,
    ):
        if state is None:
            self.state = td_constants.RowOperation.UNDEFINED
        else:
            self.state = state

    def __call__(
        self,
        series: Any,
    ) -> list[bytes]:
        seen = set()
        for bytes_array_list in series:
            if bytes_array_list is None:
                continue
            for bytes_array in bytes_array_list:
                _, _, op, tab, _, _ = decode_src(bytes_array)
                if op != td_constants.RowOperation.ROW.value:
                    seen.add(bytes_array)
                group_bytes_array = encode_src(
                    ver=None,
                    op=self.state.value,
                    tab=tab,
                    par=None,
                    row=None,
                )
                seen.add(group_bytes_array)
        return sorted(seen)


class ExtendedSystemColumns(Enum):
    TD_ROWINDEX = "$td.row"
    TD_PROVENANCE = "$td.src"


class ExtendedSystemColumnsMetadata(Enum):
    TD_ROWINDEX = {
        td_constants.TD_COL_DTYPE: pl.UInt64,
        td_constants.TD_COL_DEFAULT: _row_default,
        td_constants.TD_COL_GENERATOR: pl.LazyFrame.with_row_index.__name__,
        td_constants.TD_COL_INCEPTION: td_constants.Inception.REGENERATE,
        td_constants.TD_COL_AGGREGATION: None,
    }

    TD_PROVENANCE = {
        td_constants.TD_COL_DTYPE: pl.List(pl.Binary),
        td_constants.TD_COL_DEFAULT: _src_default,
        td_constants.TD_COL_GENERATOR: SrcGenerator,
        td_constants.TD_COL_INCEPTION: td_constants.Inception.PROPAGATE,
        td_constants.TD_COL_AGGREGATION: SrcAggregator,
    }


class SystemColumns(Enum):
    TD_IDENTIFIER = td_constants.StandardSystemColumns.TD_IDENTIFIER.value
    TD_ROWINDEX = ExtendedSystemColumns.TD_ROWINDEX.value
    TD_PROVENANCE = ExtendedSystemColumns.TD_PROVENANCE.value


class RequiredColumns(Enum):
    TD_IDENTIFIER = td_constants.StandardSystemColumns.TD_IDENTIFIER.value
    TD_ROWINDEX = ExtendedSystemColumns.TD_ROWINDEX.value
    TD_PROVENANCE = ExtendedSystemColumns.TD_PROVENANCE.value


_s_id_metadata = td_constants.StandardSystemColumnsMetadata.TD_IDENTIFIER.value
_s_row_metadata = ExtendedSystemColumnsMetadata.TD_ROWINDEX.value
_s_src_metadata = ExtendedSystemColumnsMetadata.TD_PROVENANCE.value

SYSTEM_COLUMNS_METADATA = {
    SystemColumns.TD_IDENTIFIER.value: _s_id_metadata,
    SystemColumns.TD_ROWINDEX.value: _s_row_metadata,
    SystemColumns.TD_PROVENANCE.value: _s_src_metadata,
}

_r_id_metadata = td_constants.StandardSystemColumnsMetadata.TD_IDENTIFIER.value
_r_row_metadata = ExtendedSystemColumnsMetadata.TD_ROWINDEX.value
_r_src_metadata = ExtendedSystemColumnsMetadata.TD_PROVENANCE.value

REQUIRED_COLUMNS_METADATA = {
    RequiredColumns.TD_IDENTIFIER.value: _r_id_metadata,
    RequiredColumns.TD_ROWINDEX.value: _r_row_metadata,
    RequiredColumns.TD_PROVENANCE.value: _r_src_metadata,
}


def system_columns() -> list[str]:
    return [member.value for member in SystemColumns]


class TableFrameExtension(Extension):
    name = "TableFrame Extension (Enterprise)"
    version = version()

    def __init__(self) -> None:
        FeaturesManager.instance().enable(Feature.ENTERPRISE)
        logger.debug(
            f"Single instance of {Extension.__name__}: {TableFrameExtension.name} -"
            f" {TableFrameExtension.version}"
        )

    @classmethod
    def instance(cls) -> "TableFrameExtension":
        return instance

    @property
    def summary(self) -> str:
        return "Enterprise"

    @property
    def standard_system_columns(self) -> Type[Enum]:
        return td_constants.StandardSystemColumns

    @property
    def extended_system_columns(self) -> Type[Enum]:
        return ExtendedSystemColumns

    @property
    def system_columns(self) -> Type[Enum]:
        return SystemColumns

    @property
    def system_columns_metadata(self) -> dict[str, Any]:
        return SYSTEM_COLUMNS_METADATA

    @property
    def required_columns(self) -> Type[Enum]:
        return RequiredColumns

    @property
    def required_columns_metadata(self) -> dict[str, Any]:
        return REQUIRED_COLUMNS_METADATA

    def apply_system_column(
        self,
        lf: pl.LazyFrame,
        column: str,
        function: Any,
    ) -> pl.LazyFrame:
        if function == pl.LazyFrame.with_row_index.__name__:
            if column in lf.collect_schema().names():
                lf = lf.drop(column)
            lf = lf.with_row_index(name=column, offset=0).with_columns(
                pl.col(column).cast(pl.UInt64)
            )
            return lf
        else:
            raise ValueError(
                f"Invalid function to generate a new system column: {function}"
            )

    # It does the same as the standard implementation. Additionally, it merges all
    # provenance into a single one with a list of provenance values from all merged
    # columns.
    def assemble_system_columns(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        src_cols = [
            c
            for c in lf.collect_schema().names()
            if c.startswith(ExtendedSystemColumns.TD_PROVENANCE.value)
        ]
        lf = lf.with_columns(
            pl.concat_list([pl.col(c) for c in src_cols])
            .list.unique()
            .list.sort()
            .alias(ExtendedSystemColumns.TD_PROVENANCE.value)
        )
        target_cols = [
            c
            for c in lf.collect_schema().names()
            if c in system_columns() or not c.startswith(td_constants.TD_COLUMN_PREFIX)
        ]
        lf = lf.select(target_cols)
        return lf


instance = TableFrameExtension()
