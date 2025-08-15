# Heavily based on https://github.com/ValvePython/csgo/blob/master/csgo/sharecode.py

import itertools
import re
import zlib
from array import array
from collections.abc import Mapping
from dataclasses import dataclass
from functools import reduce
from typing import Final, List, NamedTuple, cast

CHARS = cast(
    Mapping[str, int], dict(zip("ABCDEFGHJKLMNOPQRSTUVWXYZabcdefhijkmnopqrstuvwxyz23456789", itertools.count()))
)


def _swap_endianness(number: int, ns: list[int] = list(range(0, 144, 8)), /) -> int:
    return reduce(lambda result, n: (result << 8) + ((number >> n) & 0xFF), ns, 0)


SHARE_CODE_RE: Final = re.compile(rf"^(CSGO)?(-?[{''.join(CHARS)}]{{5}}){{5}}$")


class ShareCode(NamedTuple):
    match_id: int
    outcome_id: int
    token: int


def decode_sharecode(code: str) -> ShareCode:
    """Decodes a match share code.

    Returns
    -------
    .. source:: ShareCode
    """
    if SHARE_CODE_RE.match(code) is None:
        raise ValueError("Invalid share code")

    full_code = _swap_endianness(
        reduce(
            lambda bits, char: (bits * len(CHARS)) + CHARS[char],
            code.removeprefix("CSGO-").replace("-", "")[::-1],
            0,
        )
    )

    return ShareCode(
        full_code & 0xFFFFFFFFFFFFFFFF,
        full_code >> 64 & 0xFFFFFFFFFFFFFFFF,
        full_code >> 128 & 0xFFFF,
    )


@dataclass
class Keychain:
    slot: int
    sticker_id: int
    pattern: int


def create_inspect_link(def_index: int, rarity: int, quality: int, paint_seed: int, keychains: list[Keychain]) -> str:
    # Create proto-like structure as bytes
    proto = bytearray([def_index & 0xFF, rarity & 0xFF, quality & 0xFF, paint_seed & 0xFF])

    for chain in keychains:
        proto.extend([chain.slot & 0xFF, chain.sticker_id & 0xFF, chain.pattern & 0xFF])

    # Create final buffer
    buffer = bytearray([0]) + proto

    # Calculate CRC
    crc = zlib.crc32(buffer) & 0xFFFFFFFF
    xored_crc = (crc & 0xFFFF) ^ (len(proto) * crc)

    # Add checksum
    checksum = array("I", [xored_crc]).tobytes()
    final_buffer = buffer + checksum

    # Format URL
    hex_string = "".join(f"{b:02X}" for b in final_buffer)
    return f"steam://rungame/730/76561202255233023/+csgo_econ_action_preview {hex_string}"


def generate_keychain_inspect_url(pattern: int, keychain_id: int) -> str:
    keychains = [Keychain(slot=0, sticker_id=keychain_id, pattern=pattern)]
    return create_inspect_link(1355, 4, 4, pattern, keychains)
