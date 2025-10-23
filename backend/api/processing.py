import io
import os
import uuid
from typing import List, Dict, Tuple

import numpy as np
from PIL import Image, ImageStat
import pytesseract
import cv2


def pil_image_from_fileobj(file_obj) -> Image.Image:
    img = Image.open(file_obj)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
    return img


def _hex_color(rgb: Tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*[int(max(0, min(255, c))) for c in rgb])


def _average_text_color_from_bbox(pil_img: Image.Image, bbox: Tuple[int, int, int, int]) -> str:
    # Crop region
    x, y, w, h = bbox
    crop = pil_img.crop((x, y, x + w, y + h))

    # Convert to OpenCV for threshold / mask
    cv_img = cv2.cvtColor(np.array(crop), cv2.COLOR_RGBA2BGRA if crop.mode == "RGBA" else cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    # Adaptive threshold to separate text from background
    thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY_INV, 15, 10)
    # Use mask to compute mean color of foreground pixels
    mask = thr > 0
    if mask.sum() < 5:  # fallback
        stat = ImageStat.Stat(crop.convert("RGB"))
        avg = tuple(int(v) for v in stat.mean)
        return _hex_color(avg)

    fg_pixels = cv_img[mask]
    # Compute mean BGR, convert to RGB
    mean_bgr = fg_pixels.mean(axis=0)
    mean_rgb = mean_bgr[::-1]
    return _hex_color(tuple(int(v) for v in mean_rgb))


def _estimate_font_size_from_bbox(bbox: Tuple[int, int, int, int]) -> int:
    # Use height of bbox as proxy for font size
    _, _, _, h = bbox
    # Empirical mapping: text box height roughly 1.2x font size
    return max(8, int(h / 1.2))


def _classify_serif_sans(crop_img: Image.Image) -> str:
    """
    Very lightweight heuristic to guess serif vs sans-serif.
    Returns 'serif' or 'sans-serif'.
    """
    cv_img = cv2.cvtColor(np.array(crop_img.convert("RGB")), cv2.COLOR_RGB2GRAY)
    cv_img = cv2.GaussianBlur(cv_img, (3, 3), 0)
    edges = cv2.Canny(cv_img, 50, 150)
    # Hough lines to detect strong straight segments. Serif fonts often have extra terminals leading to more short segments.
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=30, minLineLength=5, maxLineGap=5)
    if lines is None:
        return "sans-serif"
    lengths = []
    for l in lines:
        x1, y1, x2, y2 = l[0]
        lengths.append(np.hypot(x2 - x1, y2 - y1))
    if not lengths:
        return "sans-serif"
    short_ratio = (np.array(lengths) <= 12).mean()  # more tiny segments suggests serifs
    return "serif" if short_ratio > 0.35 else "sans-serif"


def _map_font_family(serif_sans: str) -> str:
    return "Times New Roman" if serif_sans == "serif" else "Arial"


def analyze_image(pil_img: Image.Image) -> Dict:
    """
    Runs OCR and returns detected text elements with position, font size, color, and a guessed font family.
    """
    width, height = pil_img.size
    # Use Tesseract TSV to get bounding boxes and text confidences
    tsv = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DATAFRAME)
    elements: List[Dict] = []

    if tsv is None or len(tsv) == 0:
        return {"width": width, "height": height, "elements": elements}

    # Filter out low confidence or empty text
    for _, row in tsv.iterrows():
        text = str(row.get("text", "")).strip()
        conf = float(row.get("conf", -1))
        if not text or text == "nan" or conf < 50:
            continue
        x, y, w, h = int(row["left"]), int(row["top"]), int(row["width"]), int(row["height"])
        if w == 0 or h == 0:
            continue
        bbox = (x, y, w, h)
        color = _average_text_color_from_bbox(pil_img, bbox)
        font_size = _estimate_font_size_from_bbox(bbox)
        crop = pil_img.crop((x, y, x + w, y + h))
        family = _map_font_family(_classify_serif_sans(crop))

        element = {
            "id": str(uuid.uuid4()),
            "type": "text",
            "text": text,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "fontFamily": family,
            "fontSize": font_size,
            "fill": color,
        }
        elements.append(element)

    return {"width": width, "height": height, "elements": elements}