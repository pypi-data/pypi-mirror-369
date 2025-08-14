#
# Copyright 2025 Tabs Data Inc.
#

from typing import Any

import polars as pl

from tabsdata.extensions._tableframe.extension import SystemColumns
from tabsdata.extensions._tableframe.provenance import decode_src, encode_src

DECODED_SUFFIX = ".decoded"
BINARY_SUFFIX = ".binary"


def encode_provenance(
    *, ver: int | None, op: int, tab: int, par: int | None, row: int | None
) -> bytes:
    """
    Wrapper around provenance encode_src function.
    """
    return encode_src(ver=ver, op=op, tab=tab, par=par, row=row)


def decode_provenance(index: bytes) -> tuple[int, bool, int, int, int, Any]:
    """
    Wrapper around provenance decode_src function.
    """
    return decode_src(index=index)


def format_provenance(
    *, ver: int, ptd: bool, op: int, tab: int, par: int | None, row: int | None
) -> str:
    """
    Takes a tuple of the items composing a provenance specification, and produces
    a formatted string representation of it.
    """
    return f"ver={ver} ~ ptd={ptd} ~ op={op} ~ tab={tab} ~ par={par} ~ row={row}"


def format_provenance_as_bits_from_bytes(bytes_array: bytes) -> str:
    """
    Takes a provenance byte array, and formats it, to produce a string of 8-bit
    binary values separated by spaces.
    """
    return " ".join(f"{byte:08b}" for byte in bytes_array)


def format_provenance_as_bits_from_list(bytes_list: list[bytes]) -> list[str]:
    """
    Takes a list of provenance byte arrays, and formats each one, to produce a
    list of strings of 8-bit binary values separated by spaces.
    """
    strings_list = []
    for bytes_array in bytes_list:
        strings_list.append(" ".join(f"{byte:08b}" for byte in bytes_array))
    return strings_list


def decode_and_format_provenance_from_bytes(bytes_array: bytes) -> str:
    """
    Takes a provenance byte array, and decodes & formats it, to produce a
    formatted provenance string.
    """
    d_ver, d_ptd, d_op, d_tab, d_par, d_row = decode_provenance(bytes_array)
    string = format_provenance(
        ver=d_ver,
        ptd=d_ptd,
        op=d_op,
        tab=d_tab,
        par=d_par,
        row=d_row,
    )
    return string


def decode_and_format_provenance_from_list(bytes_list: list[bytes]) -> list[str]:
    """
    Takes a list of provenance byte arrays, and decodes & formats each one, to
    produce a list of formatted provenance strings.
    """
    strings_list = []
    for bytes_array in bytes_list:
        (
            d_ver,
            d_ptd,
            d_op,
            d_tab,
            d_par,
            d_row,
        ) = decode_provenance(bytes_array)
        strings_list.append(
            format_provenance(
                ver=d_ver,
                ptd=d_ptd,
                op=d_op,
                tab=d_tab,
                par=d_par,
                row=d_row,
            )
        )
    return strings_list


def provenance_to_human_list(lf: pl.LazyFrame) -> pl.LazyFrame:
    """
    Picks the TD_PROVENANCE column from a LazyFrame, decodes each provenance
    byte array, formats it, and returns a new LazyFrame with a new column with
    a new list of formatted provenance strings.
    """
    return lf.with_columns(
        [
            pl.col(SystemColumns.TD_PROVENANCE.value)
            .map_elements(
                decode_and_format_provenance_from_list,
                return_dtype=pl.List(pl.String),
            )
            .alias(f"{SystemColumns.TD_PROVENANCE.value}{DECODED_SUFFIX}"),
            pl.col(SystemColumns.TD_PROVENANCE.value)
            .map_elements(
                format_provenance_as_bits_from_list,
                return_dtype=pl.List(pl.String),
            )
            .alias(f"{SystemColumns.TD_PROVENANCE.value}{BINARY_SUFFIX}"),
        ]
    )


def provenance_to_human_rows(lf: pl.LazyFrame) -> pl.LazyFrame:
    """
    Picks the TD_PROVENANCE column from a LazyFrame, decodes each provenance
    byte array, formats it, and returns a new LazyFrame with a new column with
    as many rws per row as there are provenance entries, each containing a
    formatted provenance string.
    """
    return lf.explode(SystemColumns.TD_PROVENANCE.value).with_columns(
        [
            pl.col(SystemColumns.TD_PROVENANCE.value)
            .map_elements(
                decode_and_format_provenance_from_bytes,
                return_dtype=pl.String,
            )
            .alias(f"{SystemColumns.TD_PROVENANCE.value}{DECODED_SUFFIX}"),
            pl.col(SystemColumns.TD_PROVENANCE.value)
            .map_elements(
                format_provenance_as_bits_from_bytes,
                return_dtype=pl.String,
            )
            .alias(f"{SystemColumns.TD_PROVENANCE.value}{BINARY_SUFFIX}"),
        ]
    )
