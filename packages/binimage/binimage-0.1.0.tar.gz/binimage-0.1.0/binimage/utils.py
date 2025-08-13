from __future__ import annotations
from typing import Iterable

def chunk_bits(bitstring: str, size: int) -> Iterable[str]:
    """Yield fixed-size chunks from a string of bits."""
    for i in range(0, len(bitstring), size):
        yield bitstring[i:i+size]

def normalize_bits(s: str) -> str:
    """Keep only 0/1 characters."""
    return "".join(ch for ch in s if ch in ("0", "1"))
