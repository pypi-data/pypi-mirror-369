from __future__ import annotations

import argparse
from pathlib import Path
from .decoder import decode_image


def main() -> None:
    p = argparse.ArgumentParser(
        prog="binimage",
        description="Extract binary from an image (OCR or grid) and decode to text, saving to results.txt",
    )
    p.add_argument("image", help="Path to input image")
    p.add_argument("--mode", choices=["auto", "ocr", "grid"], default="auto",
                   help="Decoding mode (default: auto)")
    p.add_argument("--ocr-lang", default="eng",
                   help="Tesseract language (e.g., eng, fas); requires tesseract installed")
    p.add_argument("--rows", type=int, help="Rows of grid (for grid mode)")
    p.add_argument("--cols", type=int, help="Cols of grid (for grid mode)")
    p.add_argument("--invert", action="store_true", help="Invert bit mapping (white=1, black=0)")
    p.add_argument("--bits-per-byte", type=int, default=8, help="Bits per byte (default: 8)")
    p.add_argument("--lsb-first", action="store_true", help="Interpret chunks as LSB-first")
    p.add_argument("--out", default="results.txt", help="Output file path (default: results.txt)")
    p.add_argument("--encodings", nargs="*", default=None,
                   help="Preferred decode encodings order (default: utf-8 utf-16le utf-16be latin-1)")
    p.add_argument("--errors", default="strict", choices=["strict", "ignore", "replace"],
                   help="Decoding error handling (default: strict)")
    args = p.parse_args()

    res = decode_image(
        image_path=args.image,
        mode=args.mode,
        ocr_lang=args.ocr_lang,
        rows=args.rows,
        cols=args.cols,
        invert=args.invert,
        bits_per_byte=args.bits_per_byte,
        msb_first=not args.lsb_first,
        out_file=args.out,
        encodings=tuple(args.encodings) if args.encodings else None,
        errors=args.errors,
    )

    # پیام کوتاه برای کاربر CLI
    print(f"[binimage] mode={res.mode} encoding={res.encoding} bits={len(res.bits)} saved='{args.out}'")


if __name__ == "__main__":
    main()
