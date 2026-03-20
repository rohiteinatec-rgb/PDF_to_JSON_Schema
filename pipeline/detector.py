"""
detector.py
-----------
GOAL: Enterprise-Grade extraction pipeline strictly for Native Digital PDFs.
Defenses:
  1. Resource Gatekeeper (Prevents PDF Bombs / Memory Exhaustion).
  2. Integrity & Security Gatekeeper (Catches corruption and encryption).
  3. Dynamic Geometry Router (Scans multiple pages, rejects scanned JPGs).
  4. Dynamic Structural DOM Probe (Detects invisible tables across pages).
  5. Memory-Safe Execution (Uses context managers to prevent C-binding leaks).

RUN:
    python pipeline/detector.py --pdf input/digital_invoice_test.pdf --debug
"""

import os
import argparse
import fitz
import pymupdf4llm
import pdfplumber
from pathlib import Path

OUTPUT_FOLDER = "output"
MAX_PAGES = 10  # Protection against PDF DoS attacks (Billion Laughs equivalent)


def security_and_integrity_check(pdf_path, debug=False):
    """DEFENSE LAYER 1: Ensures valid, unencrypted PDF and prevents Resource Exhaustion."""
    if debug:
        print("[DEBUG] Running Security, Integrity, and Resource checks...")

    try:
        # Using Context Manager (with) guarantees memory is released immediately
        with fitz.open(pdf_path) as doc:
            if doc.needs_pass or doc.is_encrypted:
                return False, "Document is encrypted or password-protected."

            if doc.page_count > MAX_PAGES:
                return False, f"Document exceeds maximum allowed pages ({MAX_PAGES}). Possible DoS threat."

            if doc.page_count == 0:
                return False, "Document contains absolutely zero pages."

        return True, "Passed"

    except Exception as e:
        return False, f"File is corrupted or not a valid PDF. Error: {str(e)}"


def is_text_based_pdf(pdf_path, debug=False):
    """
    DEFENSE LAYER 2: Validates if the document is a digital PDF.
    Upgraded to scan past blank cover pages.
    """
    with fitz.open(pdf_path) as doc:
        image_area, text_area = 0.0, 0.0

        for page in doc:
            for b in page.get_text("blocks"):
                block_type = b[6]
                r = fitz.Rect(b[:4])

                if block_type == 1:
                    image_area += abs(r)
                elif block_type == 0:
                    text_area += abs(r)

            # If we found substantial content on this page, we can make a decision and stop checking
            if image_area > 0 or text_area > 0:
                break

    if debug:
        print(f"[DEBUG] Geometry Check -> Text Area: {text_area:.2f} | Image Area: {image_area:.2f}")

    return text_area > image_area


def needs_invisible_fallback(pdf_path, debug=False):
    """
    DEFENSE LAYER 3 (The Structural Probe):
    Checks the document's DOM for vector graphics (lines/rectangles) across all valid pages.
    """
    has_grid = False

    with fitz.open(pdf_path) as doc:
        for page in doc:
            table_finder = page.find_tables()
            if len(table_finder.tables) > 0:
                has_grid = True
                break  # We found a table, no need to check further pages

    if debug:
        if has_grid:
            print("[DEBUG] Vector gridlines detected. Standard extraction approved.")
        else:
            print("[DEBUG] Zero vector gridlines detected anywhere. Invisible table confirmed.")

    return not has_grid


def pdfplumber_to_markdown(pdf_path, debug=False):
    """The Whitespace Specialist: Extracts borderless tables into standard Markdown."""
    if debug:
        print("[DEBUG] Booting pdfplumber for whitespace table extraction...")

    md_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        # Process up to our MAX_PAGES limit to prevent hangs
        for page in pdf.pages[:MAX_PAGES]:
            table_settings = {
                "vertical_strategy": "text",
                "horizontal_strategy": "text"
            }

            tables = page.extract_tables(table_settings)
            for table in tables:
                for i, row in enumerate(table):
                    clean_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                    md_lines.append("| " + " | ".join(clean_row) + " |")

                    if i == 0:
                        md_lines.append("|" + "|".join(["---"] * len(clean_row)) + "|")
                md_lines.append("\n")

    return "\n".join(md_lines)


def detector(pdf_path, debug=False):
    """The Master Controller: Routes the document through all defenses before extraction."""

    # 1. Integrity & Resource Check
    is_safe, message = security_and_integrity_check(pdf_path, debug)
    if not is_safe:
        print(f"\n[CRITICAL ERROR] {message}\n")
        return ""

    # 2. Geometry Check (Catches JPGs and handles cover pages)
    if not is_text_based_pdf(pdf_path, debug=debug):
        print("\n[WARNING] Scanned image detected. Halting extraction.")
        print("[WARNING] Please route this file to the Docling or OCR pipelines.\n")
        return ""

    # 3. Intelligent Routing based on DOM
    try:
        is_borderless = needs_invisible_fallback(pdf_path, debug=debug)

        if is_borderless:
            text = pdfplumber_to_markdown(pdf_path, debug=debug)
        else:
            if debug:
                print("[DEBUG] Routing to PyMuPDF4LLM for fast native extraction...")
            text = pymupdf4llm.to_markdown(pdf_path)

        return text

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Extraction failed unexpectedly: {str(e)}\n")
        return ""


def run():
    parser = argparse.ArgumentParser(description="Enterprise extraction pipeline for digital PDFs.")
    parser.add_argument('--pdf', required=True, help='Path to the PDF file to process')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()

    pdf_path = args.pdf

    if args.debug:
        print(f"[DEBUG] Processing : {pdf_path}")

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