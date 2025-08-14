from __future__ import annotations
from typing import Iterable

def chunk_bits(bitstring: str, size: int) -> Iterable[str]:
    """Yield fixed-size chunks from a string of bits."""
    for i in range(0, len(bitstring), size):
        yield bitstring[i:i+size]

def normalize_bits(s: str) -> str:
    """Keep only 0/1 characters."""
    return "".join(ch for ch in s if ch in ("0", "1"))

def bytes_to_bits(data: bytes, bits_per_byte: int = 8, msb_first: bool = True) -> str:
    """Convert bytes to a bitstring."""
    if bits_per_byte <= 0:
        raise ValueError("bits_per_byte must be positive")
    parts: list[str] = []
    for b in data:
        bitstr = format(b, f"0{bits_per_byte}b")
        if not msb_first:
            bitstr = bitstr[::-1]
        parts.append(bitstr)
    return "".join(parts)