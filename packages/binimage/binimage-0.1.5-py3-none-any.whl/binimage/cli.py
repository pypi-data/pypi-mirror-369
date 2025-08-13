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
    p.add_argument("--mode", choices=["auto", "ocr", "grid", "lsb"], default="auto",
                   help="Decoding mode (default: auto)")
    p.add_argument("--ocr-lang", default=None,
                   help="Tesseract language (e.g., eng, fas); overrides --language; requires tesseract installed")
    p.add_argument("--language", choices=["fa", "en"], default=None,
                   help="High-level language preference (fa/en) to set sensible OCR and decoding defaults")
    p.add_argument("--rows", type=int, help="Rows of grid (for grid mode)")
    p.add_argument("--cols", type=int, help="Cols of grid (for grid mode)")
    p.add_argument("--invert", action="store_true", help="Invert bit mapping (white=1, black=0)")
    p.add_argument("--bits-per-byte", type=int, default=8, help="Bits per byte (default: 8)")
    p.add_argument("--lsb-first", action="store_true", help="Interpret chunks as LSB-first")
    p.add_argument("--out", default="results.txt", help="Output file path (default: results.txt). Use empty string to skip writing")
    p.add_argument("--print-bits", action="store_true", help="Print raw extracted bits to stdout")
    p.add_argument("--encodings", nargs="*", default=None,
                   help="Preferred decode encodings order (default: utf-8 utf-16le utf-16be latin-1)")
    p.add_argument("--errors", default="strict", choices=["strict", "ignore", "replace"],
                   help="Decoding error handling (default: strict)")
    p.add_argument("--include-bits", action="store_true", help="Include raw bits before the decoded text in output file")
    # LSB options
    p.add_argument("--lsb-channels", default="RGB", help="Channels to use for LSB extraction (e.g., R, RG, RGB)")
    p.add_argument("--lsb-bit", type=int, default=0, help="Bit index to extract from each channel (0=LSB)")
    p.add_argument("--lsb-step", type=int, default=1, help="Sample every Nth channel value (default: 1)")
    p.add_argument("--lsb-max-bits", type=int, default=None, help="Maximum number of bits to extract (default: unlimited)")
    p.add_argument("--stop-at-null", action="store_true", help="Stop at first null byte before decoding text")
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
        out_file=(args.out if args.out != "" else None),
        encodings=tuple(args.encodings) if args.encodings else None,
        errors=args.errors,
        lsb_channels=args.lsb_channels,
        lsb_bit=args.lsb_bit,
        lsb_step=args.lsb_step,
        lsb_max_bits=args.lsb_max_bits,
        stop_at_null=args.stop_at_null,
        include_bits_in_output=args.include_bits,
        language=args.language,
    )

    # پیام کوتاه برای کاربر CLI
    print(f"[binimage] mode={res.mode} encoding={res.encoding} bits={len(res.bits)} saved='{args.out}'")
    if args.print_bits:
        print(res.bits)


if __name__ == "__main__":
    main()
