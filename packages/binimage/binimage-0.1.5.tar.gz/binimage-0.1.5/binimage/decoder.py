from __future__ import annotations

import io
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageOps  # pillow
import numpy as np

from .utils import chunk_bits, normalize_bits

# OCR is optional to جلوگیری از خطا در سیستم‌هایی که tesseract ندارند
try:
    import pytesseract  # type: ignore
    _HAS_TESS = True
except Exception:
    _HAS_TESS = False


@dataclass
class DecodeResult:
    bits: str
    data: bytes
    text: str
    encoding: str
    mode: str  # "ocr" | "grid" | "lsb" | "auto"


def _to_gray(img: Image.Image) -> Image.Image:
    if img.mode != "L":
        return img.convert("L")
    return img


def _otsu_threshold(arr: np.ndarray) -> int:
    """Compute Otsu threshold on uint8 grayscale array."""
    hist, _ = np.histogram(arr, bins=256, range=(0, 256))
    total = arr.size
    sum_total = np.dot(np.arange(256), hist)
    sum_b = 0.0
    w_b = 0.0
    max_var, thresh = 0.0, 0
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f
        var_between = w_b * w_f * (m_b - m_f) ** 2
        if var_between > max_var:
            max_var = var_between
            thresh = t
    return thresh


def extract_bits_ocr(
    image_path: str | Path | Image.Image,
    ocr_lang: str = "eng",
) -> str:
    """
    OCR mode: از تصویر، کاراکترهای 0/1 را با OCR بخوان.
    نیازمند pytesseract و نصب بودن tesseract در سیستم است.
    """
    if not _HAS_TESS:
        raise RuntimeError(
            "OCR mode requires 'pytesseract' and a system Tesseract install."
        )
    if isinstance(image_path, (str, Path)):
        with Image.open(image_path) as opened:
            img = opened.copy()
    else:
        img = image_path

    # کمی پیش‌پردازش برای بهبود OCR
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    # به Tesseract بگو فقط 0 و 1 را تشخیص بده
    custom = r"-c tessedit_char_whitelist=01 --psm 6"
    text = pytesseract.image_to_string(img, lang=ocr_lang, config=custom)
    bits = normalize_bits(text)
    return bits


def _grid_cells_to_bits(
    arr: np.ndarray,
    rows: int,
    cols: int,
    invert: bool = False,
) -> str:
    """
    آرایه دودویی (0/255) را به شبکه rows x cols تقسیم و برای هر سلول میانگین می‌گیرد.
    مقدار تیره -> 1 ، روشن -> 0 (یا برعکس با invert).
    """
    h, w = arr.shape
    cell_h = h / rows
    cell_w = w / cols
    bits = []
    for r in range(rows):
        r0 = int(round(r * cell_h))
        r1 = int(round((r + 1) * cell_h))
        for c in range(cols):
            c0 = int(round(c * cell_w))
            c1 = int(round((c + 1) * cell_w))
            cell = arr[r0:r1, c0:c1]
            mean = cell.mean() if cell.size else 255
            # در تصویر باینری 0=سیاه ، 255=سفید
            bit = 1 if mean < 128 else 0
            if invert:
                bit ^= 1
            bits.append(str(bit))
    return "".join(bits)


def _binarize(img: Image.Image) -> np.ndarray:
    """Grayscale + Otsu threshold -> آرایه 0/255"""
    g = _to_gray(img)
    arr = np.asarray(g, dtype=np.uint8)
    t = _otsu_threshold(arr)
    bin_arr = (arr > t).astype(np.uint8) * 255
    return bin_arr


def extract_bits_lsb(
    image_path: str | Path | Image.Image,
    channels: str = "RGB",
    bit_index: int = 0,
    step: int = 1,
    max_bits: Optional[int] = None,
) -> str:
    """
    LSB mode: استخراج بیت‌ها از بیت کم‌اهمیت کانال‌های رنگ تصویر.
    - channels: زیرمجموعه‌ای از R/G/B (مثلاً "R", "RG" یا "RGB")
    - bit_index: شماره بیت از هر کانال (0 = LSB)
    - step: هر چند کانال یک‌بار نمونه‌برداری شود (1 یعنی همه)
    - max_bits: حداکثر تعداد بیت خروجی (None یعنی بدون محدودیت)
    """
    if isinstance(image_path, (str, Path)):
        with Image.open(image_path) as opened:
            img = opened.convert("RGB").copy()
    else:
        img = image_path.convert("RGB")

    arr = np.asarray(img, dtype=np.uint8)
    h, w, _ = arr.shape

    selected = [c for c in channels.upper() if c in ("R", "G", "B")]
    if not selected:
        selected = ["R", "G", "B"]
    ch_idx = {"R": 0, "G": 1, "B": 2}

    bits: list[str] = []
    counter = 0
    for r in range(h):
        for c in range(w):
            for ch in selected:
                if step > 1 and (counter % step) != 0:
                    counter += 1
                    continue
                value = arr[r, c, ch_idx[ch]]
                b = (value >> bit_index) & 1
                bits.append("1" if b else "0")
                counter += 1
                if max_bits is not None and len(bits) >= max_bits:
                    return "".join(bits)
    return "".join(bits)


def _auto_rows_cols_from_projection(arr: np.ndarray) -> Tuple[int, int]:
    """
    تلاش ساده برای تخمین تعداد سطر/ستون شبکه با استفاده از پیک‌های پروجکشن.
    تضمینی نیست، اما برای شبکه‌های واضح کار می‌کند.
    """
    # معکوس کنیم تا خانه‌های تیره پیک بدهند
    inv = 255 - arr
    # پروجکشن افقی/عمودی
    proj_h = inv.sum(axis=1)
    proj_w = inv.sum(axis=0)

    def peak_count(proj: np.ndarray) -> int:
        # شمارش گذارها به ناحیه‌های تیره
        thresh = proj.mean()
        is_peak = proj > thresh
        # شمارش آغاز قطعات True
        count = 0
        prev = False
        for v in is_peak:
            if v and not prev:
                count += 1
            prev = v
        return max(count, 1)

    rows = peak_count(proj_h)
    cols = peak_count(proj_w)
    return rows, cols


def extract_bits_grid(
    image_path: str | Path | Image.Image,
    rows: Optional[int] = None,
    cols: Optional[int] = None,
    invert: bool = False,
) -> str:
    """
    Grid mode: اگر تصویر شبکه‌ای از خانه‌های تیره/روشن باشد.
    اگر rows/cols داده نشود، به‌صورت ساده تخمین می‌زند.
    """
    if isinstance(image_path, (str, Path)):
        with Image.open(image_path) as opened:
            img = opened.copy()
    else:
        img = image_path

    bin_arr = _binarize(img)

    if rows is None or cols is None:
        ar, ac = _auto_rows_cols_from_projection(bin_arr)
        rows = rows or ar
        cols = cols or ac

    # کمی padding حذف کنیم (trim) تا حاشیه‌ها اثر نگذارند
    inv = 255 - bin_arr
    ys, xs = np.where(inv > 0)
    if ys.size and xs.size:
        top, bottom = ys.min(), ys.max()
        left, right = xs.min(), xs.max()
        bin_arr = bin_arr[top:bottom + 1, left:right + 1]

    return _grid_cells_to_bits(bin_arr, rows=rows, cols=cols, invert=invert)


def bits_to_bytes(
    bits: str,
    bits_per_byte: int = 8,
    msb_first: bool = True,
    drop_incomplete: bool = True,
    pad_final_with_zeros: bool = False,
) -> bytes:
    """
    بیت‌ها را به بایت تبدیل می‌کند.
    - bits_per_byte معمولاً 8
    - msb_first اگر False باشد بیت‌ها LSB-first تفسیر می‌شوند.
    - drop_incomplete اگر True باشد چانک ناقص حذف می‌شود؛
      اگر False باشد و pad_final_with_zeros=True، با صفر پر می‌کند.
    """
    bits = normalize_bits(bits)
    out = bytearray()
    for chunk in chunk_bits(bits, bits_per_byte):
        if len(chunk) < bits_per_byte:
            if drop_incomplete and not pad_final_with_zeros:
                break
            elif pad_final_with_zeros:
                chunk = chunk.ljust(bits_per_byte, "0")
            else:
                break
        if not msb_first:
            chunk = chunk[::-1]
        out.append(int(chunk, 2))
    return bytes(out)


def bytes_to_text(
    data: bytes,
    encodings: Tuple[str, ...] = ("utf-8", "utf-16le", "utf-16be", "latin-1"),
    errors: str = "strict",
) -> Tuple[str, str]:
    """
    تلاش می‌کند با چند انکدینگ رایج متن را دیکد کند.
    ترتیب پیش‌فرض برای فارسی/انگلیسی مناسب است (UTF-8 ابتدا).
    خروجی: (text, encoding_used)

    پشتیبانی از BOM:
    - UTF-8 BOM -> utf-8-sig
    - UTF-16 BOM -> utf-16 (تشخیص خودکار اندین)
    """
    # تشخیص BOM برای بهبود دیکدینگ
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig", errors=errors), "utf-8-sig"
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        try:
            return data.decode("utf-16", errors=errors), "utf-16"
        except Exception:
            pass

    for enc in encodings:
        try:
            return data.decode(enc, errors=errors), enc
        except Exception:
            continue
    # آخرین تلاش: بدون خطا (جایگزینی)
    first = encodings[0] if encodings else "utf-8"
    return data.decode(first, errors="replace"), first


def decode_image(
    image_path: str | Path,
    mode: str = "auto",               # "auto" | "ocr" | "grid" | "lsb"
    ocr_lang: Optional[str] = None,
    rows: Optional[int] = None,
    cols: Optional[int] = None,
    invert: bool = False,
    bits_per_byte: int = 8,
    msb_first: bool = True,
    out_file: Optional[str | Path] = "results.txt",
    encodings: Optional[Tuple[str, ...]] = None,
    errors: str = "strict",
    # LSB-specific options
    lsb_channels: str = "RGB",
    lsb_bit: int = 0,
    lsb_step: int = 1,
    lsb_max_bits: Optional[int] = None,
    stop_at_null: bool = False,
    include_bits_in_output: bool = False,
    language: Optional[str] = None,  # "fa" | "en"
) -> DecodeResult:
    """
    مسیر تصویر را می‌گیرد، بیت‌ها را استخراج، به بایت و سپس متن تبدیل می‌کند
    و در نهایت در out_file ذخیره می‌کند.
    """
    path = Path(image_path)

    # اعمال پیش‌فرض‌های مرتبط با زبان
    if language in ("fa", "en"):
        if ocr_lang is None:
            ocr_lang = "fas" if language == "fa" else "eng"
        if encodings is None:
            if language == "fa":
                encodings = ("utf-8", "utf-16le", "utf-16be", "latin-1")
            else:
                encodings = ("utf-8", "latin-1", "utf-16le", "utf-16be")
    # اگر کاربر تعیین نکرد، مقدار پیش‌فرض OCR زبان انگلیسی است
    if ocr_lang is None:
        ocr_lang = "eng"

    # در حالت LSB فقط خروجی UTF-8 (در صورت عدم override کاربر)
    if mode == "lsb":
        encodings = ("utf-8",)

    chosen_mode = mode
    bits = ""

    if mode == "ocr":
        bits = extract_bits_ocr(path, ocr_lang=ocr_lang)
    elif mode == "grid":
        bits = extract_bits_grid(path, rows=rows, cols=cols, invert=invert)
    elif mode == "lsb":
        bits = extract_bits_lsb(
            path,
            channels=lsb_channels,
            bit_index=lsb_bit,
            step=lsb_step,
            max_bits=lsb_max_bits,
        )
    elif mode == "auto":
        # تلاش: اول OCR (اگر در دسترس بود)، اگر نتیجه ناچیز بود، Grid
        if _HAS_TESS:
            try:
                bits = extract_bits_ocr(path, ocr_lang=ocr_lang)
                if len(bits) < 8:  # خیلی کم، احتمالاً متن نبود
                    bits = ""
            except Exception:
                bits = ""
        if not bits:
            chosen_mode = "grid"
            bits = extract_bits_grid(path, rows=rows, cols=cols, invert=invert)
        if not bits:
            chosen_mode = "lsb"
            bits = extract_bits_lsb(
                path,
                channels=lsb_channels,
                bit_index=lsb_bit,
                step=lsb_step,
                max_bits=lsb_max_bits,
            )
    else:
        raise ValueError("mode must be one of: auto, ocr, grid, lsb")

    data = bits_to_bytes(bits, bits_per_byte=bits_per_byte, msb_first=msb_first)
    if stop_at_null:
        try:
            zero_index = data.index(0)
            data = data[:zero_index]
        except ValueError:
            pass
    if encodings is not None:
        text, used_enc = bytes_to_text(data, encodings=encodings, errors=errors)
    else:
        text, used_enc = bytes_to_text(data, errors=errors)

    # ذخیره (در صورت درخواست)
    if out_file:
        out_path = Path(out_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if include_bits_in_output:
            content = f"{bits}\n\n---\nDecoded ({used_enc}):\n{text}"
        else:
            content = text
        out_path.write_text(content, encoding="utf-8")

    return DecodeResult(bits=bits, data=data, text=text, encoding=used_enc, mode=chosen_mode)
