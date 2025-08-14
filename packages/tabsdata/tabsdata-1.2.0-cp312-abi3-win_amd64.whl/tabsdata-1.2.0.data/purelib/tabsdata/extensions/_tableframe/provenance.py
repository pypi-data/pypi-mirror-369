#
#  Copyright 2025 Tabs Data Inc.
#

import logging

# noinspection PyProtectedMember
import tabsdata._utils.tableframe._constants as td_constants

logger = logging.getLogger(__name__)

BYTE_BITS = 8

BYTE_MAX_VALUE = 255

VERSION = 0

SPEC_VERSION_BITS = 4
SPEC_MIN_VERSION = 0
SPEC_MAX_VERSION = 15

SPEC_PREFIX_BITS = 0
SPEC_SUFFIX_BITS = BYTE_BITS - SPEC_PREFIX_BITS
SPEC_BYTES = 1
SPEC_MIN_BYTES = 1
SPEC_MAX_BYTES = 1

OP_PREFIX_BITS = 1
OP_SUFFIX_BITS = BYTE_BITS - OP_PREFIX_BITS
OP_MIN_BYTES = 1
OP_MAX_BYTES = 2

TAB_PREFIX_BITS = 1
TAB_SUFFIX_BITS = BYTE_BITS - TAB_PREFIX_BITS
TAB_MIN_BYTES = 1
TAB_MAX_BYTES = 2

PAR_PREFIX_BITS = 1
PAR_SUFFIX_BITS = BYTE_BITS - PAR_PREFIX_BITS
PAR_MIN_BYTES = 1
PAR_MAX_BYTES = 2

ROW_PREFIX_BITS = 2
ROW_SUFFIX_BITS = BYTE_BITS - ROW_PREFIX_BITS
ROW_MIN_BYTES = 3
ROW_MAX_BYTES = 6


ver_ = int
ptd_ = bool
op_ = int
tab_ = int
par_ = int
row_ = int | None


def encode_src(  # noqa: C901
    *, ver: int | None = VERSION, op: int, tab: int, par: int | None, row: int | None
) -> bytes:
    """
    Encodes a TableFrame operation, table index and row index into a provenance index.

    Args:
        ver (int | None): Version of the provenance data.
            It will default to system provenance version.
        op (int): Operation performed on the provenance row.
        tab (int): Table index of the provenance data.
        par (int | None): Partition index. If the table is not partitioned, this
            parameter should be None.
        row (int | None): Row index. If the operation is not ROW, this parameter should
            be None.

    The provenance index is formed by:

    - Specification Block: 1 byte specifying global metadat of the provenance data, with
        the structure:
        - Bits 1 to 4: Version of the provenance data as an unsigned integer.
        - Bit 5: Partition data:
            - 0: Table is not partitioned.
            - 1: Table is partitioned.
        - Bits 6 to 8: Reserved for future use.
    - Operation Block: 1 to 2 bytes, this being specified in first byte's leading bit.
        (0 indicates 1 byte, 1 indicates 2 bytes)
        This is kept potentially large as it could code udf's in the future.
    - Table Block: 1 to 2 bytes, this being specified in first byte's leading bit.
        (0 indicates 1 byte, 1 indicates 2 bytes)
    - Partition Block: 1 to 2 bytes, this being specified in first byte's leading bit.
        (0 indicates 1 byte, 1 indicates 2 bytes)
    - Row Block: 3 to 6 bytes, this being specified in first byte's leading bit.
        (0 indicates 3 bytes, 3 indicates 6 bytes)
        If operation is 0 (ROW operation), no row block is encoded.

    All five blocks are encoded in base 2 binary representation.

    Binary operations are used instead of arithmetic operations to improve performance.

    Examples:

    - ver=0, op=0, tab=0, par=0, row=0 (all min values) gets encode like:

        Byte 00: 00001000 (0x08) [specification blocks]

        Byte 01: 00000000 (0x00) [operation blocks]

        Byte 02: 00000000 (0x00) [table blocks]

        Byte 03: 00000000 (0x00) [partition blocks]

        Byte 04: 00000000 (0x00) [row blocks]
        Byte 05: 00000000 (0x00)
        Byte 06: 00000000 (0x00)

     - ver=15, op=32767, tab=32767, par=32767, row=32767 (all max values) gets encoded
        like:

        Byte 00: 11111000 (0xf8) [specification blocks]

        Byte 01: 11111111 (0xff) [operation blocks]
        Byte 02: 11111111 (0xff)

        Byte 03: 11111111 (0xff) [table blocks]
        Byte 04: 11111111 (0xff)

        Byte 05: 11111111 (0xff) [partition blocks]
        Byte 06: 11111111 (0xff)

        Please note that the row block is not encoded, as the operation is not 0.

    - ver=5, op=63, tab=32123, par=32456, row=32789 gets encoded like

        Byte 00: 01011000 (0x58) [specification blocks]

        Byte 01: 00111111 (0x3f) [operation blocks]

        Byte 02: 11111101 (0xfd) [table blocks]
        Byte 03: 01111011 (0x7b)

        Byte 04: 11111110 (0xfe) [partition blocks]
        Byte 05: 11001000 (0xc8)

        - Specification Block: This block gets encoded as:

            Byte 00: 01011000

            That can be broken into:

                - 0101: (version bits), indicates the version is 5, as 5 is 0101 in
                    binary when using 4 bits.

                - 1: (partitioned bit) indicates the operation is on a partition.

                - 000 (unused bits)1. The remaining bits are all set to 0 as currently
                    they are unused.

        - Operation Block: As 63 can be encoded using 7 bits (8 bits - 1 prefix bit,
            as the operation block uses a single bit prefix - OP_PREFIX_BITS), the first
            byte is:

            Byte 01: 00111111

            That can be broken into:

                - 0: (initial bit), indicates a single byte is used in the operation
                    block.

                - 0111111: (remaining bits) indicates the operation is 63, as
                    63 = 2^6 -1, thus fitting into 7 bits.

        - Table Block: As 32123 is [100 11001011 00101111] in binary, thus requiring 19
            bits, 2 bytes are not enough, but 3 bytes are, as 21 = 19 + 2 (2 bits prefix
            as specified by TAB_PREFIX_BITS) is smaller or equal 24 (3 * 8). Therefore,
            we have:

            Byte 02: 11111101
            Byte 03: 01111011

            That can be broken into:

                - 1: First bit of first byte, indicating used bytes is 2 (1 + 1).

                - 111110101111011: Remaining joined bits of the two bytes,
                    which is 32123 in binary once you remove leading zeroes.

        - Partition Block: As 32456 is [1111110 11001000] in binary, thus
            requiring 15 bits, 1 byte is not enough, but 2 bytes are, as 16 = 15 + 1
            (1 bit prefix as specified by TAB_PREFIX_BITS) is smaller or equal 16
            (2 * 8). Therefore, we have:

            Byte 04: 01000001
            Byte 05: 10010100
            Byte 06: 11100111
            Byte 07: 11011001

            That can be broken into:

                - 1: First bit of first byte, indicating used bytes is 2 (1 + 1).

                - 111111011001000: Remaining joined bits of the two bytes,
                    which is 32456 in binary once you remove leading zeroes.

        - Row Block: Not represented, as operation is not 0.

    - ver=5, op=0, tab=32123, par=32456, row=32789 gets encoded like

        Byte 00: 01011000 (0x58) [specification blocks]

        Byte 01: 00000000 (0x00) [operation blocks]

        Byte 02: 11111101 (0xfd) [table blocks]
        Byte 03: 01111011 (0x7b)

        Byte 04: 11111110 (0xfe) [partition blocks]
        Byte 05: 11001000 (0xc8)

        Byte 06: 00000000 (0x00) [row blocks]
        Byte 07: 10000000 (0x80)
        Byte 08: 00010101 (0x15)

        - Specification Block: This block gets encoded as:

            Byte 00: 01011000

            That can be broken into:

                - 0101: (version bits), indicates the version is 5, as 5 is 0101 in
                    binary when using 4 bits.

                - 1: (partitioned bit) indicates the operation is on a partition.

                - 000 (unused bits)1. The remaining bits are all set to 0 as currently
                    they are unused.

        - Operation Block: As 0 can be encoded using 7 bit (8 bits - 1 prefix bit,
            as the operation block uses a single bit prefix - OP_PREFIX_BITS), the first
            byte is:

            Byte 01: 00000000

            That can be broken into:

                - 0: (initial bit), indicates a single byte is used in the operation
                    block.

                - 0000000: (remaining bits) indicates the operation is 0, thus fitting
                    into 7 bits.

        - Table Block: As 32123 is [100 11001011 00101111] in binary, thus requiring 19
            bits, 2 bytes are not enough, but 3 bytes are, as 21 = 19 + 2 (2 bits prefix
            as specified by TAB_PREFIX_BITS) is smaller or equal 24 (3 * 8). Therefore,
            we have:

            Byte 02: 11111101
            Byte 03: 01111011

            That can be broken into:

                - 1: First bit of first byte, indicating used bytes is 2 (1 + 1).

                - 111110101111011: Remaining joined bits of the two bytes,
                    which is 32123 in binary once you remove leading zeroes.

        - Partition Block: As 32456 is [1111110 11001000] in binary, thus
            requiring 15 bits, 1 byte is not enough, but 2 bytes are, as 16 = 15 + 1
            (1 bit prefix as specified by TAB_PREFIX_BITS) is smaller or equal 16
            (2 * 8). Therefore, we have:

            Byte 04: 11111110
            Byte 05: 11001000

            That can be broken into:

                - 1: First bit of first byte, indicating used bytes is 2 (1 + 1).

                - 111111011001000: Remaining joined bits of the two bytes,
                    which is 32456 in binary once you remove leading zeroes.

        - Row Block: As 32789 is [10000000 00010101] in binary, thus
            requiring 16 bits, 2 bytes are not enough, but 3 bytes are, as 18 = 16 + 2
            (2 bits prefix as specified by ROW_PREFIX_BITS) is smaller or equal 24
            (3 * 8). Therefore, we have:

            Byte 06: 00000000 (0x00)
            Byte 07: 10000000 (0x80)
            Byte 08: 00010101 (0x15)

                - 00: First 2 bits of first byte, indicating used bytes is 3 (3 + 0).

                - 00000001000000000010101 : Remaining joined bits of the two bytes,
                    which is 32789 in binary once you remove leading zeroes.
    """

    def encode_block() -> bytes:
        if ver < SPEC_MIN_VERSION:
            raise ValueError(f"Version is too small: {ver}")
        if ver > SPEC_MAX_VERSION:
            raise ValueError(f"Version is too large: {ver}")

        specification = ver << SPEC_VERSION_BITS
        if par is not None:
            specification |= 0b00001000
        return bytes(specification.to_bytes(SPEC_BYTES, "big"))

    def encode_blocks(
        value: int,
        pre_bits: int,
        min_bytes: int,
        max_bytes: int,
    ) -> bytes:
        if not (pre_bits <= BYTE_BITS):
            raise ValueError(
                "Too many prefix bits. At most the full first byte can be used:"
                f" {pre_bits}"
            )
        for nbytes in range(min_bytes, max_bytes + 1):
            if value < (1 << (BYTE_BITS * nbytes - pre_bits)):
                break
        else:
            raise ValueError(f"Value {value} too large for {max_bytes} bytes")
        data = value.to_bytes(nbytes, "big")
        prefix = (nbytes - min_bytes) << (BYTE_BITS - pre_bits)
        head = (data[0] & ((1 << (BYTE_BITS - pre_bits)) - 1)) | prefix
        return bytes([head]) + data[1:]

    ver = ver or VERSION
    encode_spec = encode_block()

    encoded_op = encode_blocks(
        op,
        OP_PREFIX_BITS,
        OP_MIN_BYTES,
        OP_MAX_BYTES,
    )

    encoded_tab = encode_blocks(
        tab,
        TAB_PREFIX_BITS,
        TAB_MIN_BYTES,
        TAB_MAX_BYTES,
    )

    if par is not None:
        encoded_par = encode_blocks(
            par,
            PAR_PREFIX_BITS,
            PAR_MIN_BYTES,
            PAR_MAX_BYTES,
        )
    else:
        encoded_par = bytes()

    if op == td_constants.RowOperation.ROW.value:
        if row is None:
            raise ValueError("Row index cannot be None when operation is not 0")
        encoded_row = encode_blocks(
            row,
            ROW_PREFIX_BITS,
            ROW_MIN_BYTES,
            ROW_MAX_BYTES,
        )
    else:
        encoded_row = bytes()

    return encode_spec + encoded_op + encoded_tab + encoded_par + encoded_row


def decode_src(  # noqa: C901
    index: bytes,
) -> tuple[ver_, ptd_, op_, tab_, par_, row_]:
    def decode_block(value: int) -> tuple[int, bool]:
        if not (0 <= value <= BYTE_MAX_VALUE):
            raise ValueError("Specification block value out of range")
        ver_value = (value >> 4) & 0b1111
        ptd_value = ((value >> 3) & 1) != 0
        return ver_value, ptd_value

    def decode_blocks(
        value: bytes,
        pre_bits: int,
        min_bytes: int,
        max_bytes: int,
    ) -> tuple[int, int]:
        """
        Decodes a TableFrame provenance index into and operation, table index and row
        index. See function `encode_src` for more details.

        When no row block is encoded, the row index is set to None.
        """
        if not (pre_bits <= BYTE_BITS):
            raise ValueError(
                "Too many prefix bits. At most the full first byte can be used:"
                f" {pre_bits}"
            )
        if not value:
            raise ValueError("Value to decode is empty")
        prefix = value[0] >> (BYTE_BITS - pre_bits)
        data_bytes = min_bytes + prefix
        if data_bytes > max_bytes:
            raise ValueError(
                f"Prefix indicates length {data_bytes}, greater than max {max_bytes}"
            )
        if len(value) < data_bytes:
            raise ValueError(
                f"Insufficient data: {data_bytes} needed, but {len(value)} gotten"
            )
        data = bytearray(value[:data_bytes])
        data[0] &= (1 << (BYTE_BITS - pre_bits)) - 1
        data_value = int.from_bytes(data, "big")
        return data_value, data_bytes

    if len(index) < OP_MIN_BYTES + TAB_MIN_BYTES:
        raise ValueError("Data too short to decode")

    spec_offset = 0
    specc_bytes = SPEC_BYTES
    ver, ptd = decode_block(
        index[spec_offset],
    )

    op_offset = spec_offset + specc_bytes
    op, op_bytes = decode_blocks(
        index[op_offset:],
        OP_PREFIX_BITS,
        OP_MIN_BYTES,
        OP_MAX_BYTES,
    )

    tab_offset = op_offset + op_bytes
    tab, tab_bytes = decode_blocks(
        index[tab_offset:],
        TAB_PREFIX_BITS,
        TAB_MIN_BYTES,
        TAB_MAX_BYTES,
    )

    if ptd:
        par_offset = tab_offset + tab_bytes
        par, par_bytes = decode_blocks(
            index[par_offset:],
            PAR_PREFIX_BITS,
            PAR_MIN_BYTES,
            PAR_MAX_BYTES,
        )
    else:
        par_offset = tab_offset
        par = None
        par_bytes = tab_bytes

    if op == td_constants.RowOperation.ROW.value:
        row_offset = par_offset + par_bytes
        if len(index) <= row_offset:
            raise ValueError("Expected row bytes, but none found")
        row, row_bytes = decode_blocks(
            index[row_offset:],
            ROW_PREFIX_BITS,
            ROW_MIN_BYTES,
            ROW_MAX_BYTES,
        )
    else:
        row = None

    return ver, ptd, op, tab, par, row
