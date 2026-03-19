"""
detector.py
-----------
GOAL: Smart extraction pipeline strictly for Native Digital PDFs.
Validation: Uses Quantrium Tech approach to prevent silent failures on scanned images.
Extraction: Uses PyMuPDF4LLM for layout-aware Markdown extraction.

RUN:
    python pipeline/detector.py --pdf input/digital_invoice_test.pdf --debug
"""

import os
import argparse
import fitz              # PyMuPDF
import pymupdf4llm       # Advanced layout-aware extraction
from pathlib import Path

OUTPUT_FOLDER = "output"


def is_text_based_pdf(pdf_path, debug=False):
    """
    Quantrium Tech Approach:
    Calculates the geometric area of text blocks vs image blocks to validate
    if the document is actually a digital PDF.
    """
    doc = fitz.open(pdf_path)
    page = doc[0]
    image_area = 0.0
    text_area = 0.0

    for b in page.get_text("blocks"):
        block_type = b[6]
        r = fitz.Rect(b[:4])

        if block_type == 1:
            image_area += abs(r)
        elif block_type == 0:
            text_area += abs(r)

    doc.close()

    if debug:
        print(f"[DEBUG] Geometry Check -> Text Area: {text_area:.2f} | Image Area: {image_area:.2f}")

    return text_area > image_area


def detector(pdf_path, debug=False):
    """
    Validates the PDF type, then extracts structured Markdown text.
    """
    if debug:
        print("[DEBUG] Validating document composition...")

    # 1. The Gatekeeper Validation
    is_digital = is_text_based_pdf(pdf_path, debug=debug)

    if not is_digital:
        # Graceful failure instead of silent empty output
        print("\n[WARNING] This document appears to be a scanned image.")
        print("[WARNING] This specific script is designed strictly for Native Digital PDFs.")
        print("[WARNING] Halting extraction. Please route this file to the Docling or OCRmyPDF pipelines.\n")
        return ""

    # 2. The Upgraded Extraction
    if debug:
        print("[DEBUG] Digital PDF validated. Extracting structured Markdown...")

    # Grabs the text while preserving table structures natively
    text = pymupdf4llm.to_markdown(pdf_path)

    return text


def run():
    parser = argparse.ArgumentParser(description="Extract text from a native digital PDF.")
    parser.add_argument('--pdf', required=True, help='Path to the PDF file to process')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()

    pdf_path = args.pdf

    if args.debug:
        print(f"[DEBUG] Reading : {pdf_path}")

    raw_text = detector(pdf_path, debug=args.debug)

    # Only save the file if text was actually extracted (prevents saving blank files for scanned docs)
    if raw_text.strip():
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        output_file = Path(OUTPUT_FOLDER) / f"{Path(pdf_path).stem}.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(raw_text)

        print(f"Characters extracted : {len(raw_text)}")
        print(f"Saved to             : {output_file}")
    else:
        print("[INFO] No file was saved due to validation failure.")


if __name__ == "__main__":
    run()